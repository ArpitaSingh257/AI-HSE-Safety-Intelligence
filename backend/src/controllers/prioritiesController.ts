import { Request, Response } from 'express';
import { fetchAiPriorities, fetchAiPriorityById } from '../services/aiService';

export async function getPriorities(req: Request, res: Response): Promise<void> {
  try {
    const aiRes = await fetchAiPriorities();
    if (!aiRes) {
      res.status(503).json({ error: 'AI microservice priority engine unavailable.' });
      return;
    }
    res.json(aiRes);
  } catch (err) {
    console.error('Error fetching HSE priority rankings:', err);
    res.status(500).json({ error: 'Failed to fetch HSE priority rankings.' });
  }
}

export async function getPriorityById(req: Request, res: Response): Promise<void> {
  try {
    const { priorityId } = req.params;
    const aiRes = await fetchAiPriorityById(priorityId);
    if (!aiRes) {
      res.status(404).json({ error: `HSE priority item '${priorityId}' not found.` });
      return;
    }
    res.json(aiRes);
  } catch (err) {
    console.error(`Error fetching priority item ${req.params.priorityId}:`, err);
    res.status(500).json({ error: 'Failed to fetch priority item detail.' });
  }
}
