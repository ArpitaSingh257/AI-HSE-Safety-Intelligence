import { Request, Response } from 'express';
import { Pattern } from '../models/Pattern';
import { regeneratePatterns } from '../services/patternService';
import { logAudit } from '../services/auditService';

export async function getPatterns(_req: Request, res: Response) {
  const patterns = await Pattern.find({}).sort({ sifPotentialRate: -1 });
  res.json(patterns.map((p) => p.toJSON()));
}

export async function getPatternById(req: Request, res: Response) {
  const pattern = await Pattern.findById(req.params.id);
  if (!pattern) return res.status(404).json({ message: `Pattern ${req.params.id} not found` });
  res.json(pattern.toJSON());
}

/** Manual trigger to recompute patterns on demand (also runs automatically
 * after every /reports/:id/analyze call and on the nightly cron - see server.ts). */
export async function refreshPatterns(req: Request, res: Response) {
  const upserted = await regeneratePatterns();

  await logAudit({
    req,
    action: 'PATTERN_IDENTIFIED',
    entityType: 'PATTERN',
    details: `Pattern detection re-run manually: ${upserted} pattern(s) updated`,
  });

  res.json({ patternsUpdated: upserted });
}
