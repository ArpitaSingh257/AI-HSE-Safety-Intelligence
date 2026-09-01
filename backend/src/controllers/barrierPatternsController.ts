import { Request, Response } from 'express';
import { fetchAiBarrierPatterns, fetchAiBarrierPatternById } from '../services/aiService';

export async function getBarrierPatterns(_req: Request, res: Response) {
  const data = await fetchAiBarrierPatterns();
  if (!data) {
    return res.json({
      total_barrier_patterns: 0,
      min_support_threshold: 3,
      barrier_patterns: []
    });
  }
  res.json(data);
}

export async function getBarrierPatternById(req: Request, res: Response) {
  const pattern = await fetchAiBarrierPatternById(req.params.id);
  if (!pattern) {
    return res.status(404).json({ message: `Barrier pattern ${req.params.id} not found` });
  }
  res.json(pattern);
}
