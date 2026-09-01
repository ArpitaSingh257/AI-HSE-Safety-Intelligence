import React, { useState, useEffect } from 'react';
import { feedbackService } from '../../api';
import type { FeedbackRecord } from '../../types/feedback';
import {
  CheckCircle2,
  Edit3,
  XCircle,
  MessageSquare,
  ShieldCheck,
  History,
  AlertTriangle,
  Info
} from 'lucide-react';

interface AnalystFeedbackPanelProps {
  reportId: string;
  fieldName: string;
  fieldLabel: string;
  aiValue: any;
}

export const AnalystFeedbackPanel: React.FC<AnalystFeedbackPanelProps> = ({
  reportId,
  fieldName,
  fieldLabel,
  aiValue
}) => {
  const [history, setHistory] = useState<FeedbackRecord[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [action, setAction] = useState<'ACCEPT' | 'CORRECT' | 'REJECT' | null>(null);
  const [humanValue, setHumanValue] = useState<string>(typeof aiValue === 'string' ? aiValue : JSON.stringify(aiValue));
  const [comment, setComment] = useState<string>('');
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const loadHistory = async () => {
    try {
      const records = await feedbackService.getFeedbackByReportId(reportId);
      const fieldRecords = records.filter((r) => r.field_name === fieldName);
      setHistory(fieldRecords);
    } catch (err) {
      console.warn('Failed to load feedback history:', err);
    }
  };

  useEffect(() => {
    loadHistory();
  }, [reportId, fieldName]);

  const handleSubmit = async (selectedAction: 'ACCEPT' | 'CORRECT' | 'REJECT') => {
    setSubmitting(true);
    setSuccessMsg(null);
    try {
      const res = await feedbackService.submitFeedback({
        report_id: reportId,
        field_name: fieldName,
        ai_value: aiValue,
        human_value: selectedAction === 'CORRECT' ? humanValue : aiValue,
        action: selectedAction,
        comment: comment
      });

      if (res) {
        setSuccessMsg(`Feedback submitted successfully! (ID: ${res.feedback_id})`);
        setAction(null);
        setComment('');
        await loadHistory();
      }
    } catch (err) {
      console.error('Failed to submit analyst feedback:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleStatusTransition = async (feedbackId: string, nextStatus: string) => {
    setSubmitting(true);
    try {
      const updated = await feedbackService.updateFeedbackStatus(feedbackId, nextStatus);
      if (updated) {
        setSuccessMsg(`Status updated to ${nextStatus}!`);
        await loadHistory();
      }
    } catch (err) {
      console.error('Failed status transition:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const latestFeedback = history.length > 0 ? history[0] : null;

  return (
    <div className="bg-slate-50 border border-slate-200 rounded-lg p-3.5 space-y-3 mt-2">
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-bold text-slate-700 uppercase flex items-center gap-1.5">
          <ShieldCheck className="h-3.5 w-3.5 text-amber-600" /> HSE Analyst Review — {fieldLabel}
        </span>
        {latestFeedback && (
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-bold bg-amber-100 text-amber-900 border border-amber-300 px-2 py-0.5 rounded">
              {latestFeedback.action} ({latestFeedback.status})
            </span>
            {latestFeedback.status === 'SUBMITTED' && (
              <button
                onClick={() => handleStatusTransition(latestFeedback.feedback_id, 'REVIEWED')}
                disabled={submitting}
                className="text-[10px] font-bold bg-blue-600 hover:bg-blue-700 text-white px-2 py-0.5 rounded transition-colors"
              >
                Mark Reviewed
              </button>
            )}
            {latestFeedback.status === 'REVIEWED' && (
              <button
                onClick={() => handleStatusTransition(latestFeedback.feedback_id, 'ACCEPTED_FOR_EVALUATION')}
                disabled={submitting}
                className="text-[10px] font-bold bg-emerald-600 hover:bg-emerald-700 text-white px-2 py-0.5 rounded transition-colors"
              >
                Accept for Evaluation
              </button>
            )}
          </div>
        )}
      </div>

      {/* Review History Overlay Banner */}
      {latestFeedback && (
        <div className="bg-white border border-slate-200 rounded p-2.5 text-xs text-slate-800 space-y-1">
          <div className="flex items-center justify-between">
            <span className="font-semibold text-slate-900">Original AI Value: <code className="bg-slate-100 px-1 py-0.5 rounded text-[11px] text-slate-700">{String(aiValue)}</code></span>
            <span className="text-[10px] text-slate-400 font-mono">{latestFeedback.review_timestamp.substring(0, 10)}</span>
          </div>
          {latestFeedback.action === 'CORRECT' && (
            <div className="text-amber-800 font-semibold">
              Human Correction: <code className="bg-amber-100 px-1 py-0.5 rounded text-[11px] text-amber-900">{String(latestFeedback.human_value)}</code>
            </div>
          )}
          {latestFeedback.comment && (
            <p className="text-slate-600 text-[11px] italic">"{latestFeedback.comment}"</p>
          )}
        </div>
      )}

      {/* Interactive Review Action Buttons */}
      <div className="flex items-center gap-2 pt-1">
        <button
          onClick={() => {
            setAction('ACCEPT');
            handleSubmit('ACCEPT');
          }}
          disabled={submitting}
          className="flex items-center gap-1 px-2.5 py-1 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded transition-colors"
        >
          <CheckCircle2 className="h-3.5 w-3.5" /> Accept AI
        </button>

        <button
          onClick={() => setAction(action === 'CORRECT' ? null : 'CORRECT')}
          disabled={submitting}
          className="flex items-center gap-1 px-2.5 py-1 bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold text-xs rounded transition-colors"
        >
          <Edit3 className="h-3.5 w-3.5" /> Correct
        </button>

        <button
          onClick={() => {
            setAction('REJECT');
            handleSubmit('REJECT');
          }}
          disabled={submitting}
          className="flex items-center gap-1 px-2.5 py-1 bg-red-600 hover:bg-red-700 text-white font-bold text-xs rounded transition-colors"
        >
          <XCircle className="h-3.5 w-3.5" /> Reject AI
        </button>
      </div>

      {/* Correction Form Input */}
      {action === 'CORRECT' && (
        <div className="bg-white border border-amber-300 rounded p-3 text-xs space-y-2.5">
          <div>
            <label className="block text-[11px] font-bold text-slate-700 uppercase mb-1">Human Corrected Value</label>
            <input
              type="text"
              value={humanValue}
              onChange={(e) => setHumanValue(e.target.value)}
              placeholder="Enter corrected value..."
              className="w-full border border-slate-300 rounded px-2.5 py-1.5 text-xs text-slate-900 focus:outline-none focus:border-amber-500"
            />
          </div>

          <div>
            <label className="block text-[11px] font-bold text-slate-700 uppercase mb-1">Analyst Review Rationale / Comment</label>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Explain why the AI prediction was corrected (optional)..."
              rows={2}
              className="w-full border border-slate-300 rounded p-2 text-xs text-slate-900 focus:outline-none focus:border-amber-500"
            />
          </div>

          <div className="flex justify-end gap-2 pt-1">
            <button
              onClick={() => setAction(null)}
              className="px-2.5 py-1 bg-slate-200 text-slate-700 font-semibold text-xs rounded"
            >
              Cancel
            </button>
            <button
              onClick={() => handleSubmit('CORRECT')}
              disabled={submitting}
              className="px-3 py-1 bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs rounded"
            >
              Submit Correction
            </button>
          </div>
        </div>
      )}

      {successMsg && (
        <p className="text-[11px] text-emerald-700 font-bold bg-emerald-50 border border-emerald-200 p-2 rounded">
          ✓ {successMsg}
        </p>
      )}
    </div>
  );
};
