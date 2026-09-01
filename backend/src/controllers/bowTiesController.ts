import { Request, Response } from 'express';
import { fetchAiBowTieByReportId } from '../services/aiService';

export async function getBowTieByReportId(req: Request, res: Response): Promise<void> {
  try {
    const { reportId } = req.params;
    const aiRes = await fetchAiBowTieByReportId(reportId);
    if (!aiRes) {
      res.status(404).json({ error: `Bow-Tie pathway for report '${reportId}' not found.` });
      return;
    }
    res.json(aiRes);
  } catch (err) {
    console.error(`Error fetching Bow-Tie pathway for report ${req.params.reportId}:`, err);
    res.status(500).json({ error: 'Failed to fetch Bow-Tie pathway mapping.' });
  }
}
