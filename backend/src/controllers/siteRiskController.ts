import { Request, Response } from 'express';
import { fetchAiSiteRisk, fetchAiSiteRiskById } from '../services/aiService';

export async function getSiteRiskProfiles(_req: Request, res: Response) {
  const data = await fetchAiSiteRisk();
  if (!data) {
    return res.json({
      total_sites: 0,
      min_site_reports_threshold: 3,
      site_profiles: []
    });
  }
  res.json(data);
}

export async function getSiteRiskProfileById(req: Request, res: Response) {
  const profile = await fetchAiSiteRiskById(req.params.id);
  if (!profile) {
    return res.status(404).json({ message: `Site risk profile for ${req.params.id} not found` });
  }
  res.json(profile);
}
