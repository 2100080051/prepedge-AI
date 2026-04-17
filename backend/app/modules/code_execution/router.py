"""
Code Execution Module - Handles code compilation and execution for multiple languages
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import subprocess
import tempfile
import os

router = APIRouter(prefix="/code-execution", tags=["code-execution"])


class CodeExecutionRequest(BaseModel):
    """Request model for code execution"""
    language: str
    code: str
    stdin: Optional[str] = None
    timeout: int = 10  # seconds


class CodeExecutionResponse(BaseModel):
    """Response model for code execution"""
    success: bool
    output: str
    error: str
    statusCode: int
    executionTime: float
    memory: str


# Language configurations
LANGUAGE_CONFIG = {
    'python3': {
        'extension': '.py',
        'compile_cmd': None,
        'run_cmd': ['python', '{file}']
    },
    'python2': {
        'extension': '.py',
        'compile_cmd': None,
        'run_cmd': ['python2', '{file}']
    },
    'nodejs': {
        'extension': '.js',
        'compile_cmd': None,
        'run_cmd': ['node', '{file}']
    },
    'java': {
        'extension': '.java',
        'compile_cmd': ['javac', '{file}'],
        'run_cmd': ['java', '-cp', '{dir}', 'Solution']
    },
    'cpp': {
        'extension': '.cpp',
        'compile_cmd': ['g++', '-o', '{output}', '{file}'],
        'run_cmd': ['{output}']
    },
    'c': {
        'extension': '.c',
        'compile_cmd': ['gcc', '-o', '{output}', '{file}'],
        'run_cmd': ['{output}']
    },
    'csharp': {
        'extension': '.cs',
        'compile_cmd': ['mcs', '{file}', '-out:{output}'],
        'run_cmd': ['mono', '{output}']
    },
    'php': {
        'extension': '.php',
        'compile_cmd': None,
        'run_cmd': ['php', '{file}']
    },
    'ruby': {
        'extension': '.rb',
        'compile_cmd': None,
        'run_cmd': ['ruby', '{file}']
    },
    'go': {
        'extension': '.go',
        'compile_cmd': ['go', 'build', '-o', '{output}', '{file}'],
        'run_cmd': ['{output}']
    },
    'rust': {
        'extension': '.rs',
        'compile_cmd': ['rustc', '-o', '{output}', '{file}'],
        'run_cmd': ['{output}']
    },
    'typescript': {
        'extension': '.ts',
        'compile_cmd': ['tsc', '{file}', '--outFile', '{output}.js'],
        'run_cmd': ['node', '{output}.js']
    },
    'kotlin': {
        'extension': '.kt',
        'compile_cmd': ['kotlinc', '{file}', '-include-runtime', '-d', '{output}'],
        'run_cmd': ['java', '-jar', '{output}']
    },
}


@router.post("/execute", response_model=CodeExecutionResponse)
async def execute_code(request: CodeExecutionRequest):
    """
    Execute code in the specified language.
    
    Args:
        request: CodeExecutionRequest with language, code, and optional stdin
        
    Returns:
        CodeExecutionResponse with output, errors, and execution stats
    """
    try:
        language = request.language.lower()
        
        if language not in LANGUAGE_CONFIG:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Language '{language}' not supported. Supported languages: {list(LANGUAGE_CONFIG.keys())}"
            )
        
        config = LANGUAGE_CONFIG[language]
        
        # Create temporary directory for code execution
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write code to file
            filename = os.path.join(tmpdir, f"code{config['extension']}")
            with open(filename, 'w') as f:
                f.write(request.code)
            
            # Compile if needed
            if config['compile_cmd']:
                output_file = os.path.join(tmpdir, 'output')
                compile_cmd = [
                    cmd.format(file=filename, output=output_file, dir=tmpdir)
                    for cmd in config['compile_cmd']
                ]
                
                try:
                    compile_result = subprocess.run(
                        compile_cmd,
                        capture_output=True,
                        text=True,
                        timeout=request.timeout,
                        cwd=tmpdir
                    )
                    
                    if compile_result.returncode != 0:
                        return CodeExecutionResponse(
                            success=False,
                            output="",
                            error=compile_result.stderr or "Compilation failed",
                            statusCode=1,
                            executionTime=0,
                            memory="0 MB"
                        )
                except subprocess.TimeoutExpired:
                    return CodeExecutionResponse(
                        success=False,
                        output="",
                        error="Compilation timeout",
                        statusCode=1,
                        executionTime=request.timeout,
                        memory="0 MB"
                    )
            
            # Prepare run command
            output_file = os.path.join(tmpdir, 'output')
            run_cmd = [
                cmd.format(file=filename, output=output_file, dir=tmpdir)
                for cmd in config['run_cmd']
            ]
            
            # Execute code
            try:
                import time
                start_time = time.time()
                
                result = subprocess.run(
                    run_cmd,
                    capture_output=True,
                    text=True,
                    input=request.stdin or "",
                    timeout=request.timeout,
                    cwd=tmpdir
                )
                
                execution_time = time.time() - start_time
                
                return CodeExecutionResponse(
                    success=result.returncode == 0,
                    output=result.stdout,
                    error=result.stderr,
                    statusCode=result.returncode,
                    executionTime=round(execution_time * 1000),  # Convert to ms
                    memory="N/A"  # Memory tracking requires additional tools
                )
                
            except subprocess.TimeoutExpired:
                return CodeExecutionResponse(
                    success=False,
                    output="",
                    error=f"Execution timeout (limit: {request.timeout}s)",
                    statusCode=1,
                    executionTime=request.timeout * 1000,
                    memory="0 MB"
                )
            except Exception as e:
                return CodeExecutionResponse(
                    success=False,
                    output="",
                    error=str(e),
                    statusCode=1,
                    executionTime=0,
                    memory="0 MB"
                )
    
    except HTTPException:
        raise
    except Exception as e:
        return CodeExecutionResponse(
            success=False,
            output="",
            error=f"Unexpected error: {str(e)}",
            statusCode=1,
            executionTime=0,
            memory="0 MB"
        )
