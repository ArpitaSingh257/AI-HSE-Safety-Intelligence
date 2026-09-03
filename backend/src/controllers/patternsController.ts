import { Request, Response } from 'express';
import { Pattern } from '../models/Pattern';
import { regeneratePatterns } from '../services/patternService';
import { logAudit } from '../services/auditService';

import { fetchAiPatterns, fetchAiPatternById } from '../services/aiService';

export async function getPatterns(_req: Request, res: Response) {
  const aiPatterns = await fetchAiPatterns();
  
  const priorityWeight = {
    $switch: {
      branches: [
        { case: { $eq: ['$priority', 'CRITICAL'] }, then: 4 },
        { case: { $eq: ['$priority', 'HIGH'] }, then: 3 },
        { case: { $eq: ['$priority', 'MEDIUM'] }, then: 2 },
        { case: { $eq: ['$priority', 'LOW'] }, then: 1 },
      ],
      default: 0,
    },
  };

  const dbPatterns = await Pattern.aggregate([
    { $addFields: { priorityWeight } },
    { $sort: { priorityWeight: -1, reportCount: -1 } },
  ]);

  res.json({
    ai_patterns: aiPatterns?.patterns || [],
    db_patterns: dbPatterns.map((p: any) => ({ ...p, id: p._id.toString() })),
  });
}

export async function getPatternById(req: Request, res: Response) {
  const aiPattern = await fetchAiPatternById(req.params.id);
  if (aiPattern) {
    return res.json({ ai_pattern: aiPattern });
  }

  const pattern = await Pattern.findById(req.params.id);
  if (!pattern) return res.status(404).json({ message: `Pattern ${req.params.id} not found` });
  res.json({ db_pattern: pattern.toJSON() });
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
