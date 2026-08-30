import { Request } from 'express';
import { AuditLog } from '../models/AuditLog';
import { AuditActionType, AuditEntityType, AuditStatus } from '../types';

interface LogAuditParams {
  req: Request;
  action: AuditActionType;
  entityType: AuditEntityType;
  entityId?: string;
  status?: AuditStatus;
  details: string;
  changesSummary?: { before?: string; after?: string };
  /** Explicit identity to use when req.user isn't set yet (e.g. during
   * login, before the `authenticate` middleware has run). Takes priority
   * over req.user when provided. */
  userOverride?: { userId: string; name: string; role: string };
}

function getClientIp(req: Request): string {
  const forwarded = req.headers['x-forwarded-for'];
  if (typeof forwarded === 'string' && forwarded.length > 0) {
    return forwarded.split(',')[0].trim();
  }
  return req.socket.remoteAddress || 'unknown';
}

/**
 * Writes a real AuditLog entry. Call this from route handlers on every
 * login, logout, and create/update/delete/analyze action - not just from
 * the seed script. If req.user is missing (e.g. login success/failure
 * before auth), pass `userOverride` with the known identity instead.
 */
export async function logAudit(params: LogAuditParams): Promise<void> {
  const { req, action, entityType, entityId, status = 'SUCCESS', details, changesSummary, userOverride } = params;
  try {
    await AuditLog.create({
      timestamp: new Date(),
      userId: userOverride?.userId || req.user?.userId || 'anonymous',
      userName: userOverride?.name || req.user?.name || 'Unknown',
      userRole: userOverride?.role || req.user?.role || 'Unknown',
      action,
      entityType,
      entityId,
      ipAddress: getClientIp(req),
      status,
      details,
      changesSummary,
    });
  } catch (err) {
    // Audit logging must never break the primary request flow.
    console.error('Failed to write audit log:', err);
  }
}