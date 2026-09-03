import { Request, Response } from 'express';
import { normalizeReportText } from '../services/aiService';

export async function processTextNormalization(req: Request, res: Response): Promise<void> {
  try {
    const { text } = req.body;
    if (!text || typeof text !== 'string') {
      res.status(400).json({ error: 'Missing required field: text (string).' });
      return;
    }

    const result = await normalizeReportText(text);
    if (!result) {
      res.status(503).json({ error: 'AI microservice multilingual normalization engine unavailable.' });
      return;
    }

    res.json(result);
  } catch (err) {
    console.error('Error normalizing text:', err);
    res.status(500).json({ error: 'Failed to normalize multilingual text.' });
  }
}
