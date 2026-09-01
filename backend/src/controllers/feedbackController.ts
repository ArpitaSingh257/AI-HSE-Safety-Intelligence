import { Request, Response } from 'express';
import { FeedbackModel } from '../models/Feedback';
import { submitAiFeedback, fetchAiFeedbackStats } from '../services/aiService';
import crypto from 'crypto';

export async function submitFeedback(req: Request, res: Response): Promise<void> {
  try {
    const { report_id, field_name, ai_value, human_value, action, comment } = req.body;
    if (!report_id || !field_name || !action) {
      res.status(400).json({ error: 'Missing required feedback fields: report_id, field_name, and action are required.' });
      return;
    }

    const actionClean = String(action).toUpperCase();
    if (!['ACCEPT', 'CORRECT', 'REJECT', 'NEEDS_REVIEW'].includes(actionClean)) {
      res.status(400).json({ error: 'Invalid action. Must be ACCEPT, CORRECT, REJECT, or NEEDS_REVIEW.' });
      return;
    }

    // Server-side authentication reviewer identification (token payload user or fallback)
    const reviewer_id = (req as any).user?.email || (req as any).user?.id || 'HSE_ANALYST_01';
    const timestamp_str = new Date().toISOString();
    const fb_id = `FB-${crypto.createHash('md5').update(`${report_id}::${field_name}::${actionClean}::${timestamp_str}`).digest('hex').substring(0, 8).toUpperCase()}`;

    // Create MongoDB record (canonical single source of truth)
    const feedbackDoc = new FeedbackModel({
      feedback_id: fb_id,
      report_id,
      field_name,
      ai_value,
      human_value: actionClean === 'CORRECT' ? human_value : ai_value,
      action: actionClean,
      comment: comment || '',
      reviewer_id,
      review_timestamp: timestamp_str,
      model_version: 'OILPS_v2.0.0',
      pipeline_version: '2.0.0',
      schema_version: '1.0.0',
      status: 'SUBMITTED',
      revision: 1
    });

    await feedbackDoc.save();

    // Optionally sync with FastAPI microservice evaluation queue
    await submitAiFeedback({
      report_id,
      field_name,
      ai_value,
      human_value: actionClean === 'CORRECT' ? human_value : ai_value,
      action: actionClean,
      comment,
      reviewer_id
    });

    res.status(201).json(feedbackDoc);
  } catch (err) {
    console.error('Error recording analyst feedback:', err);
    res.status(500).json({ error: 'Failed to record analyst feedback.' });
  }
}

export async function getFeedbackByReportId(req: Request, res: Response): Promise<void> {
  try {
    const { reportId } = req.params;
    const records = await FeedbackModel.find({ report_id: reportId }).sort({ created_at: -1 });
    res.json(records);
  } catch (err) {
    console.error(`Error fetching feedback history for report ${req.params.reportId}:`, err);
    res.status(500).json({ error: 'Failed to fetch feedback history.' });
  }
}

export async function getFeedbackStats(req: Request, res: Response): Promise<void> {
  try {
    const records = await FeedbackModel.find();
    const total = records.length;
    const accepted = records.filter(r => r.action === 'ACCEPT').length;
    const corrected = records.filter(r => r.action === 'CORRECT').length;
    const rejected = records.filter(r => r.action === 'REJECT').length;

    res.json({
      total_feedback: total,
      accepted_count: accepted,
      corrected_count: corrected,
      rejected_count: rejected,
      accept_rate: total > 0 ? Number((accepted / total).toFixed(4)) : 1.0,
      correction_rate: total > 0 ? Number((corrected / total).toFixed(4)) : 0.0,
      reject_rate: total > 0 ? Number((rejected / total).toFixed(4)) : 0.0
    });
  } catch (err) {
    console.error('Error fetching feedback stats:', err);
    res.status(500).json({ error: 'Failed to fetch feedback statistics.' });
  }
}

export async function updateFeedbackStatus(req: Request, res: Response): Promise<void> {
  try {
    const { feedbackId } = req.params;
    const { status: targetStatus } = req.body;

    const record = await FeedbackModel.findOne({ feedback_id: feedbackId });
    if (!record) {
      res.status(404).json({ error: `Feedback record '${feedbackId}' not found.` });
      return;
    }

    const currentStatus = record.status;
    const validTransitions: Record<string, string[]> = {
      SUBMITTED: ['REVIEWED'],
      REVIEWED: ['ACCEPTED_FOR_EVALUATION'],
      ACCEPTED_FOR_EVALUATION: []
    };

    if (!validTransitions[currentStatus] || !validTransitions[currentStatus].includes(targetStatus)) {
      res.status(400).json({
        error: `Invalid status transition from '${currentStatus}' to '${targetStatus}'. Allowed: ${validTransitions[currentStatus]?.join(', ') || 'None'}`
      });
      return;
    }

    record.status = targetStatus;
    record.revision += 1;
    await record.save();

    res.json(record);
  } catch (err) {
    console.error(`Error updating status for feedback ${req.params.feedbackId}:`, err);
    res.status(500).json({ error: 'Failed to update feedback status.' });
  }
}
