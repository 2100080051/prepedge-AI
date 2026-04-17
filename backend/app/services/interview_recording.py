import uuid
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
import base64
from pathlib import Path

from app.database.models import InterviewSession, ProctoringReport, ProctoringEvent
from app.database.session import SessionLocal
from app.utils.logger import get_logger, LogCategory


class InterviewRecordingService:
    """
    Comprehensive interview session recording service
    Handles video/audio recording, streaming, storage, and playback
    """

    # Recording storage configuration
    RECORDING_DIR = "interview_recordings"
    CHUNKS_DIR = os.path.join(RECORDING_DIR, "chunks")
    COMPRESSED_DIR = os.path.join(RECORDING_DIR, "compressed")

    def __init__(self):
        self._ensure_directories()

    def _ensure_directories(self):
        """Create necessary directories for recording storage"""
        for directory in [self.RECORDING_DIR, self.CHUNKS_DIR, self.COMPRESSED_DIR]:
            Path(directory).mkdir(parents=True, exist_ok=True)

    def start_recording_session(
        self,
        session_id: int,
        user_id: int,
        recording_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Initialize a recording session
        Creates recording metadata and storage paths
        """
        try:
            db = SessionLocal()

            # Get interview session
            session = db.query(InterviewSession).filter(
                InterviewSession.id == session_id,
                InterviewSession.user_id == user_id
            ).first()

            if not session:
                return {"error": "Interview session not found"}

            # Generate unique recording ID
            recording_id = f"rec_{session_id}_{int(datetime.utcnow().timestamp())}"

            # Create recording metadata
            recording_config = recording_config or {}
            metadata = {
                "recording_id": recording_id,
                "session_id": session_id,
                "user_id": user_id,
                "company": session.company,
                "role": session.role,
                "started_at": datetime.utcnow().isoformat(),
                "video_codec": recording_config.get("video_codec", "h264"),
                "audio_codec": recording_config.get("audio_codec", "aac"),
                "bitrate": recording_config.get("bitrate", "5000k"),
                "resolution": recording_config.get("resolution", "1080p"),
                "fps": recording_config.get("fps", 30),
                "chunks": [],
                "total_duration_seconds": 0,
                "file_size_bytes": 0,
                "status": "recording"
            }

            # Create recording directory
            recording_path = os.path.join(self.RECORDING_DIR, recording_id)
            Path(recording_path).mkdir(parents=True, exist_ok=True)

            # Save metadata
            metadata_path = os.path.join(recording_path, "metadata.json")
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)

            get_logger().log_action(
                LogCategory.INTERVIEW,
                "recording_started",
                user_id=user_id,
                details={"recording_id": recording_id, "session_id": session_id}
            )

            return {
                "success": True,
                "recording_id": recording_id,
                "session_id": session_id,
                "upload_url": f"/api/v1/interview/recording/{recording_id}/chunk",
                "started_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            get_logger().log_error(LogCategory.INTERVIEW, e, user_id=user_id)
            return {"error": str(e)}
        finally:
            if 'db' in locals():
                db.close()

    def upload_recording_chunk(
        self,
        recording_id: str,
        chunk_index: int,
        chunk_data: bytes,
        chunk_duration_ms: int
    ) -> Dict[str, Any]:
        """
        Upload a chunk of recording data
        Supports incremental upload for large interviews
        """
        try:
            recording_path = os.path.join(self.RECORDING_DIR, recording_id)

            if not os.path.exists(recording_path):
                return {"error": "Recording not found"}

            # Save chunk
            chunk_path = os.path.join(recording_path, f"chunk_{chunk_index:04d}.webm")
            with open(chunk_path, "wb") as f:
                f.write(chunk_data)

            # Update metadata
            metadata_path = os.path.join(recording_path, "metadata.json")
            with open(metadata_path, "r") as f:
                metadata = json.load(f)

            metadata["chunks"].append({
                "index": chunk_index,
                "duration_ms": chunk_duration_ms,
                "size_bytes": len(chunk_data),
                "timestamp": datetime.utcnow().isoformat()
            })

            metadata["total_duration_seconds"] = sum(
                c["duration_ms"] for c in metadata["chunks"]
            ) / 1000

            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)

            return {
                "success": True,
                "recording_id": recording_id,
                "chunk_index": chunk_index,
                "chunk_size_bytes": len(chunk_data),
                "total_chunks": len(metadata["chunks"]),
                "total_duration_seconds": metadata["total_duration_seconds"]
            }

        except Exception as e:
            get_logger().log_error(LogCategory.INTERVIEW, e)
            return {"error": str(e)}

    def stop_recording_session(
        self,
        session_id: int,
        recording_id: str,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Stop recording and finalize the recording file
        """
        try:
            db = SessionLocal()

            recording_path = os.path.join(self.RECORDING_DIR, recording_id)

            if not os.path.exists(recording_path):
                return {"error": "Recording not found"}

            # Load metadata
            metadata_path = os.path.join(recording_path, "metadata.json")
            with open(metadata_path, "r") as f:
                metadata = json.load(f)

            # Merge chunks into single file
            output_path = os.path.join(recording_path, f"{recording_id}.webm")
            self._merge_chunks(recording_path, output_path)

            # Calculate file size
            file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0

            # Update metadata
            metadata["status"] = "completed"
            metadata["completed_at"] = datetime.utcnow().isoformat()
            metadata["file_size_bytes"] = file_size
            metadata["storage_path"] = output_path

            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)

            # Update InterviewSession in database
            session = db.query(InterviewSession).filter(
                InterviewSession.id == session_id
            ).first()

            if session:
                session.recording_url = output_path
                session.recording_duration_seconds = int(metadata["total_duration_seconds"])
                db.commit()

            get_logger().log_action(
                LogCategory.INTERVIEW,
                "recording_completed",
                user_id=user_id,
                details={
                    "recording_id": recording_id,
                    "session_id": session_id,
                    "duration_seconds": metadata["total_duration_seconds"],
                    "file_size_mb": round(file_size / (1024 * 1024), 2)
                }
            )

            return {
                "success": True,
                "recording_id": recording_id,
                "session_id": session_id,
                "duration_seconds": metadata["total_duration_seconds"],
                "file_size_bytes": file_size,
                "file_size_mb": round(file_size / (1024 * 1024), 2),
                "completed_at": metadata["completed_at"]
            }

        except Exception as e:
            get_logger().log_error(LogCategory.INTERVIEW, e, user_id=user_id)
            return {"error": str(e)}
        finally:
            if 'db' in locals():
                db.close()

    def _merge_chunks(self, recording_path: str, output_path: str):
        """
        Merge all recorded chunks into single file
        In production, this would use FFmpeg for proper merging
        """
        try:
            # Get all chunk files
            chunk_files = sorted([
                f for f in os.listdir(recording_path)
                if f.startswith("chunk_") and f.endswith(".webm")
            ])

            if not chunk_files:
                return

            # Merge chunks
            with open(output_path, "wb") as outfile:
                for chunk_file in chunk_files:
                    chunk_path = os.path.join(recording_path, chunk_file)
                    with open(chunk_path, "rb") as infile:
                        outfile.write(infile.read())

        except Exception as e:
            get_logger().log_error(LogCategory.INTERVIEW, e)

    def get_recording_metadata(
        self,
        recording_id: str,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Retrieve recording metadata
        """
        try:
            recording_path = os.path.join(self.RECORDING_DIR, recording_id)
            metadata_path = os.path.join(recording_path, "metadata.json")

            if not os.path.exists(metadata_path):
                return {"error": "Recording not found"}

            with open(metadata_path, "r") as f:
                metadata = json.load(f)

            # Verify user owns this recording
            if metadata.get("user_id") != user_id:
                return {"error": "Unauthorized access to recording"}

            return {
                "success": True,
                "recording_id": recording_id,
                "metadata": metadata
            }

        except Exception as e:
            get_logger().log_error(LogCategory.INTERVIEW, e, user_id=user_id)
            return {"error": str(e)}

    def get_recording_stream(
        self,
        recording_id: str,
        user_id: int,
        start_byte: int = 0,
        end_byte: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get recording file for streaming playback
        Supports range requests for efficient streaming
        """
        try:
            recording_path = os.path.join(self.RECORDING_DIR, recording_id)
            metadata_path = os.path.join(recording_path, "metadata.json")

            if not os.path.exists(metadata_path):
                return {"error": "Recording not found"}

            with open(metadata_path, "r") as f:
                metadata = json.load(f)

            # Verify user owns this recording
            if metadata.get("user_id") != user_id:
                return {"error": "Unauthorized access to recording"}

            recording_file = metadata.get("storage_path")
            if not recording_file or not os.path.exists(recording_file):
                return {"error": "Recording file not found"}

            file_size = os.path.getsize(recording_file)

            if end_byte is None:
                end_byte = file_size - 1

            return {
                "success": True,
                "recording_id": recording_id,
                "file_path": recording_file,
                "file_size_bytes": file_size,
                "content_type": "video/webm",
                "start_byte": start_byte,
                "end_byte": end_byte,
                "duration_seconds": metadata.get("total_duration_seconds")
            }

        except Exception as e:
            get_logger().log_error(LogCategory.INTERVIEW, e, user_id=user_id)
            return {"error": str(e)}

    def export_with_proctoring(
        self,
        session_id: int,
        user_id: int,
        include_violations: bool = True
    ) -> Dict[str, Any]:
        """
        Export interview recording with proctoring violations
        For compliance and review purposes
        """
        try:
            db = SessionLocal()

            # Get session
            session = db.query(InterviewSession).filter(
                InterviewSession.id == session_id,
                InterviewSession.user_id == user_id
            ).first()

            if not session:
                return {"error": "Interview session not found"}

            if not session.recording_url:
                return {"error": "No recording found for this session"}

            # Get proctoring report
            report = db.query(ProctoringReport).filter(
                ProctoringReport.session_id == session_id
            ).first()

            # Get proctoring events
            events = []
            if include_violations:
                proctoring_events = db.query(ProctoringEvent).filter(
                    ProctoringEvent.session_id == session_id
                ).order_by(ProctoringEvent.timestamp).all()

                events = [
                    {
                        "id": e.id,
                        "event_type": e.event_type,
                        "severity": e.severity,
                        "description": e.description,
                        "timestamp": e.timestamp.isoformat(),
                        "data": json.loads(e.data) if e.data else {}
                    }
                    for e in proctoring_events
                ]

            export_data = {
                "session_id": session_id,
                "user_id": user_id,
                "company": session.company,
                "role": session.role,
                "duration_minutes": session.duration_minutes,
                "score": session.score,
                "recording_url": session.recording_url,
                "recording_duration_seconds": session.recording_duration_seconds,
                "proctoring_status": session.proctoring_status,
                "is_flagged": session.is_flagged,
                "flag_reason": session.flag_reason,
                "total_violations": session.total_violations,
                "created_at": session.created_at.isoformat(),
                "proctoring_report": {
                    "total_violations": report.total_violations if report else 0,
                    "severity_rating": report.severity_rating if report else "clean",
                    "proctoring_result": report.proctoring_result if report else "CLEAN",
                    "recommendation": report.recommendation if report else ""
                } if report else None,
                "violations": events if include_violations else []
            }

            get_logger().log_action(
                LogCategory.INTERVIEW,
                "recording_export",
                user_id=user_id,
                details={"session_id": session_id, "violations_included": include_violations}
            )

            return {
                "success": True,
                "data": export_data
            }

        except Exception as e:
            get_logger().log_error(LogCategory.INTERVIEW, e, user_id=user_id)
            return {"error": str(e)}
        finally:
            if 'db' in locals():
                db.close()

    def delete_recording(
        self,
        recording_id: str,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Delete a recording (for privacy/storage management)
        """
        try:
            recording_path = os.path.join(self.RECORDING_DIR, recording_id)
            metadata_path = os.path.join(recording_path, "metadata.json")

            if not os.path.exists(metadata_path):
                return {"error": "Recording not found"}

            with open(metadata_path, "r") as f:
                metadata = json.load(f)

            # Verify user owns this recording
            if metadata.get("user_id") != user_id:
                return {"error": "Unauthorized access to recording"}

            # Delete recording directory
            import shutil
            shutil.rmtree(recording_path)

            get_logger().log_action(
                LogCategory.INTERVIEW,
                "recording_deleted",
                user_id=user_id,
                details={"recording_id": recording_id}
            )

            return {
                "success": True,
                "message": "Recording deleted successfully",
                "recording_id": recording_id
            }

        except Exception as e:
            get_logger().log_error(LogCategory.INTERVIEW, e, user_id=user_id)
            return {"error": str(e)}
