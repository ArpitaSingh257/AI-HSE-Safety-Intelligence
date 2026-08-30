import { Request, Response } from 'express';
import { AuditLog } from '../models/AuditLog';

export async function getAuditLogs(req: Request, res: Response) {
  const limit = Math.max(1, Math.min(500, parseInt((req.query.limit as string) || '200', 10)));
  const logs = await AuditLog.find({}).sort({ timestamp: -1 }).limit(limit);
  res.json(logs.map((l) => l.toJSON()));
}
