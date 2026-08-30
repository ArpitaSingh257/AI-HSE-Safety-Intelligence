import { Router } from 'express';
import * as auditController from '../controllers/auditController';
import { authenticate, authorize } from '../middleware/authMiddleware';
import { PERMISSIONS } from '../types';
import { asyncHandler } from '../utils/asyncHandler';

const router = Router();

router.use(authenticate);
router.get('/audit-logs', authorize(PERMISSIONS.canViewAuditLogs), asyncHandler(auditController.getAuditLogs));

export default router;
