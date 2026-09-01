import { Request, Response } from 'express';
import { fetchAiLsrTrends, fetchAiLsrTrendsByRule } from '../services/aiService';

export async function getLsrTrendProfiles(_req: Request, res: Response) {
  const data = await fetchAiLsrTrends();
  if (!data) {
    return res.json({
      total_lsr_rules: 0,
      min_lsr_reports_threshold: 3,
      lsr_profiles: []
    });
  }
  res.json(data);
}

export async function getLsrTrendProfileByRule(req: Request, res: Response) {
  const profile = await fetchAiLsrTrendsByRule(req.params.rule);
  if (!profile) {
    return res.status(404).json({ message: `LSR trend profile for ${req.params.rule} not found` });
  }
  res.json(profile);
}
