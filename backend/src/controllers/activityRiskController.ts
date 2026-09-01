import { Request, Response } from 'express';
import { fetchAiActivityRisk, fetchAiActivityRiskById } from '../services/aiService';

export async function getActivityRiskProfiles(_req: Request, res: Response) {
  const data = await fetchAiActivityRisk();
  if (!data) {
    return res.json({
      total_activities: 0,
      min_activity_reports_threshold: 3,
      activity_profiles: []
    });
  }
  res.json(data);
}

export async function getActivityRiskProfileById(req: Request, res: Response) {
  const profile = await fetchAiActivityRiskById(req.params.id);
  if (!profile) {
    return res.status(404).json({ message: `Activity risk profile for ${req.params.id} not found` });
  }
  res.json(profile);
}
