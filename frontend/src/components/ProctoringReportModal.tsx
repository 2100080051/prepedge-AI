import { AlertTriangle, CheckCircle, AlertCircle, TrendingUp, Clock, Eye } from 'lucide-react';
import { useEffect, useState } from 'react';
import apiClient from '@/lib/api';

interface ProctoringReportProps {
  sessionId: number;
  onClose: () => void;
}

interface ProctoringReportData {
  report_id: number;
  session_id: number;
  total_violations: number;
  severity_rating: string;
  max_severity: number;
  violations_breakdown: {
    critical_multiple_faces: number;
    high_no_face_detected: number;
    critical_copy_paste: number;
    medium_tab_switches: number;
    medium_window_unfocus: number;
    low_unusual_input: number;
  };
  proctoring_result: string;
  recommendation: string;
  created_at: string;
}

export default function ProctoringReportModal({ sessionId, onClose }: ProctoringReportProps) {
  const [report, setReport] = useState<ProctoringReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const response = await apiClient.get(`/proctoring/report/${sessionId}/details`);
        setReport(response.data);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load report');
      } finally {
        setLoading(false);
      }
    };

    fetchReport();
  }, [sessionId]);

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-4 border-slate-200 border-t-indigo-600 rounded-full animate-spin"></div>
            <p className="text-slate-600 font-semibold">Generating Report...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-md">
          <div className="flex items-start gap-3 mb-4">
            <AlertTriangle className="w-6 h-6 text-red-600 flex-shrink-0" />
            <div>
              <h2 className="font-bold text-lg text-slate-900">Error Loading Report</h2>
              <p className="text-slate-600 text-sm mt-1">{error}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 rounded-lg transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    );
  }

  const getResultColor = (result: string) => {
    switch (result) {
      case 'CLEAN':
        return { bg: 'bg-green-50', border: 'border-green-200', text: 'text-green-800', icon: CheckCircle, label: 'Clean' };
      case 'CLEAN_WITH_WARNINGS':
        return { bg: 'bg-yellow-50', border: 'border-yellow-200', text: 'text-yellow-800', icon: AlertCircle, label: 'Clean with Warnings' };
      case 'NEEDS_VERIFICATION':
        return { bg: 'bg-orange-50', border: 'border-orange-200', text: 'text-orange-800', icon: AlertTriangle, label: 'Needs Verification' };
      case 'FLAGGED_FOR_REVIEW':
        return { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-800', icon: AlertTriangle, label: 'Flagged for Review' };
      default:
        return { bg: 'bg-slate-50', border: 'border-slate-200', text: 'text-slate-800', icon: AlertCircle, label: 'Unknown' };
    }
  };

  const resultStyle = getResultColor(report.proctoring_result);
  const ResultIcon = resultStyle.icon;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className={`${resultStyle.bg} border-b-2 ${resultStyle.border} px-6 py-8`}>
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-4">
              <ResultIcon className={`w-12 h-12 ${resultStyle.text} flex-shrink-0`} />
              <div>
                <h1 className={`text-3xl font-bold ${resultStyle.text}`}>
                  {resultStyle.label}
                </h1>
                <p className={`text-sm mt-1 ${resultStyle.text} opacity-75`}>
                  Proctoring Report for Interview Session
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-slate-600 font-bold text-2xl"
            >
              ×
            </button>
          </div>
        </div>

        {/* Report Content */}
        <div className="p-6 space-y-6">
          {/* Summary Stats */}
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-slate-50 rounded-lg p-4 border border-slate-200">
              <div className="flex items-center gap-2 mb-2">
                <Eye className="w-5 h-5 text-slate-600" />
                <span className="text-sm text-slate-600 font-semibold">Total Violations</span>
              </div>
              <div className="text-3xl font-bold text-slate-900">{report.total_violations}</div>
            </div>
            <div className="bg-slate-50 rounded-lg p-4 border border-slate-200">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="w-5 h-5 text-slate-600" />
                <span className="text-sm text-slate-600 font-semibold">Max Severity</span>
              </div>
              <div className={`text-2xl font-bold capitalize ${
                report.severity_rating === 'critical' ? 'text-red-600' :
                report.severity_rating === 'high' ? 'text-orange-600' :
                report.severity_rating === 'medium' ? 'text-yellow-600' :
                'text-blue-600'
              }`}>
                {report.severity_rating}
              </div>
            </div>
            <div className="bg-slate-50 rounded-lg p-4 border border-slate-200">
              <div className="flex items-center gap-2 mb-2">
                <Clock className="w-5 h-5 text-slate-600" />
                <span className="text-sm text-slate-600 font-semibold">Report Time</span>
              </div>
              <div className="text-sm font-semibold text-slate-900">
                {new Date(report.created_at).toLocaleString()}
              </div>
            </div>
          </div>

          {/* Recommendation */}
          <div className={`${resultStyle.bg} border-2 ${resultStyle.border} rounded-lg p-4`}>
            <h3 className={`font-bold ${resultStyle.text} mb-2`}>Recommendation</h3>
            <p className={`${resultStyle.text} text-sm leading-relaxed`}>
              {report.recommendation}
            </p>
          </div>

          {/* Violations Breakdown */}
          <div>
            <h3 className="font-bold text-lg text-slate-900 mb-4">Violation Details</h3>
            <div className="space-y-3">
              {report.violations_breakdown.critical_multiple_faces > 0 && (
                <div className="flex items-center justify-between p-3 bg-red-50 border border-red-200 rounded-lg">
                  <div>
                    <div className="font-semibold text-red-900">Multiple Faces Detected</div>
                    <div className="text-sm text-red-700">Possible cheating assistance</div>
                  </div>
                  <div className="text-2xl font-bold text-red-600">
                    {report.violations_breakdown.critical_multiple_faces}
                  </div>
                </div>
              )}

              {report.violations_breakdown.high_no_face_detected > 0 && (
                <div className="flex items-center justify-between p-3 bg-orange-50 border border-orange-200 rounded-lg">
                  <div>
                    <div className="font-semibold text-orange-900">No Face Detected</div>
                    <div className="text-sm text-orange-700">Candidate face not visible in frame</div>
                  </div>
                  <div className="text-2xl font-bold text-orange-600">
                    {report.violations_breakdown.high_no_face_detected}
                  </div>
                </div>
              )}

              {report.violations_breakdown.critical_copy_paste > 0 && (
                <div className="flex items-center justify-between p-3 bg-red-50 border border-red-200 rounded-lg">
                  <div>
                    <div className="font-semibold text-red-900">Copy/Paste Detected</div>
                    <div className="text-sm text-red-700">Direct answer copying detected</div>
                  </div>
                  <div className="text-2xl font-bold text-red-600">
                    {report.violations_breakdown.critical_copy_paste}
                  </div>
                </div>
              )}

              {report.violations_breakdown.medium_tab_switches > 0 && (
                <div className="flex items-center justify-between p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <div>
                    <div className="font-semibold text-yellow-900">Tab Switches</div>
                    <div className="text-sm text-yellow-700">Browser tab switched during interview</div>
                  </div>
                  <div className="text-2xl font-bold text-yellow-600">
                    {report.violations_breakdown.medium_tab_switches}
                  </div>
                </div>
              )}

              {report.violations_breakdown.medium_window_unfocus > 0 && (
                <div className="flex items-center justify-between p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <div>
                    <div className="font-semibold text-yellow-900">Window Focus Lost</div>
                    <div className="text-sm text-yellow-700">Attention diverted from interview</div>
                  </div>
                  <div className="text-2xl font-bold text-yellow-600">
                    {report.violations_breakdown.medium_window_unfocus}
                  </div>
                </div>
              )}

              {report.violations_breakdown.low_unusual_input > 0 && (
                <div className="flex items-center justify-between p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <div>
                    <div className="font-semibold text-blue-900">Unusual Input Patterns</div>
                    <div className="text-sm text-blue-700">Keyboard/mouse behavior anomalies</div>
                  </div>
                  <div className="text-2xl font-bold text-blue-600">
                    {report.violations_breakdown.low_unusual_input}
                  </div>
                </div>
              )}

              {report.total_violations === 0 && (
                <div className="flex items-center justify-center p-6 bg-green-50 border border-green-200 rounded-lg">
                  <div className="text-center">
                    <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-2" />
                    <div className="font-semibold text-green-900">No Violations Detected</div>
                    <div className="text-sm text-green-700 mt-1">
                      Interview conducted under clean proctoring conditions
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Important Notice */}
          <div className="bg-slate-50 border-l-4 border-slate-400 p-4 rounded">
            <h4 className="font-bold text-slate-900 mb-2">⚠️ Important Note</h4>
            <p className="text-sm text-slate-700">
              This automated proctoring report is generated by AI analysis. Sessions flagged for review 
              will be manually verified by administrators before final decision. The presence of violations 
              does not automatically disqualify candidates.
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4 border-t border-slate-200">
            <button
              onClick={onClose}
              className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 rounded-lg transition-colors"
            >
              Close Report
            </button>
            <button
              onClick={() => window.print()}
              className="flex-1 border-2 border-indigo-600 text-indigo-600 hover:bg-indigo-50 font-semibold py-3 rounded-lg transition-colors"
            >
              Print Report
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
