import { Request, Response } from 'express';
import { fetchAiRiskMatrix, fetchAiRiskMatrixById } from '../services/aiService';

export async function getRiskMatrix(req: Request, res: Response): Promise<void> {
  try {
    const aiRes = await fetchAiRiskMatrix();
    if (!aiRes) {
      res.status(503).json({ error: 'AI microservice risk matrix engine unavailable.' });
      return;
    }
    res.json(aiRes);
  } catch (err) {
    console.error('Error fetching 2D risk matrix dataset:', err);
    res.status(500).json({ error: 'Failed to fetch risk matrix dataset.' });
  }
}

export async function getRiskMatrixItemById(req: Request, res: Response): Promise<void> {
  try {
    const { matrixItemId } = req.params;
    const aiRes = await fetchAiRiskMatrixById(matrixItemId);
    if (!aiRes) {
      res.status(404).json({ error: `Risk matrix item '${matrixItemId}' not found.` });
      return;
    }
    res.json(aiRes);
  } catch (err) {
    console.error(`Error fetching risk matrix item ${req.params.matrixItemId}:`, err);
    res.status(500).json({ error: 'Failed to fetch risk matrix item detail.' });
  }
}
