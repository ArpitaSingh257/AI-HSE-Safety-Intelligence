import { Request, Response } from 'express';
import { fetchAiTriage } from '../services/aiService';

export async function evaluateTriage(req: Request, res: Response): Promise<void> {
  try {
    const payload = req.body;
    if (!payload || !payload.report_id) {
      res.status(400).json({ error: 'Missing required field: report_id.' });
      return;
    }

    const aiRes = await fetchAiTriage(payload);
    if (!aiRes) {
      res.status(503).json({ error: 'AI microservice confidence triage engine unavailable.' });
      return;
    }

    res.json(aiRes);
  } catch (err) {
    console.error('Error evaluating confidence-calibrated triage:', err);
    res.status(500).json({ error: 'Failed to evaluate operational safety triage.' });
  }
}
