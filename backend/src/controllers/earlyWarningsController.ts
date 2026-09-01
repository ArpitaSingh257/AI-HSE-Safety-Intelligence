import { Request, Response } from 'express';
import { fetchAiEarlyWarnings, fetchAiEarlyWarningById } from '../services/aiService';

export async function getEarlyWarnings(req: Request, res: Response): Promise<void> {
  try {
    const aiRes = await fetchAiEarlyWarnings();
    if (!aiRes) {
      res.status(503).json({ error: 'AI microservice early-warning detector unavailable.' });
      return;
    }
    res.json(aiRes);
  } catch (err) {
    console.error('Error fetching early warning signals:', err);
    res.status(500).json({ error: 'Failed to fetch early warning signals.' });
  }
}

export async function getEarlyWarningById(req: Request, res: Response): Promise<void> {
  try {
    const { warningId } = req.params;
    const aiRes = await fetchAiEarlyWarningById(warningId);
    if (!aiRes) {
      res.status(404).json({ error: `Early warning signal '${warningId}' not found.` });
      return;
    }
    res.json(aiRes);
  } catch (err) {
    console.error(`Error fetching early warning signal ${req.params.warningId}:`, err);
    res.status(500).json({ error: 'Failed to fetch early warning signal detail.' });
  }
}
