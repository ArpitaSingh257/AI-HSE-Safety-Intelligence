import { Router } from 'express';
import * as reportsController from '../controllers/reportsController';
import { authenticate, authorize } from '../middleware/authMiddleware';
import { validateBody } from '../middleware/validationMiddleware';
import { createReportSchema, updateReportSchema } from '../validators/reportValidator';
import { PERMISSIONS } from '../types';
import { asyncHandler } from '../utils/asyncHandler';

const router = Router();

router.use(authenticate);

router.get('/reports', asyncHandler(reportsController.getReports));
router.get('/reports/:id', asyncHandler(reportsController.getReportById));

router.post(
  '/reports',
  authorize(PERMISSIONS.canCreateReport),
  validateBody(createReportSchema),
  asyncHandler(reportsController.createReport)
);

router.put(
  '/reports/:id',
  authorize(PERMISSIONS.canEditReport),
  validateBody(updateReportSchema),
  asyncHandler(reportsController.updateReport)
);

router.delete('/reports/:id', authorize(PERMISSIONS.canDeleteReport), asyncHandler(reportsController.deleteReport));

router.post(
  '/reports/:id/analyze',
  authorize(PERMISSIONS.canTriggerAIAnalysis),
  asyncHandler(reportsController.analyzeReport)
);

router.post(
  '/incidents/analyze',
  authorize(PERMISSIONS.canTriggerAIAnalysis),
  asyncHandler(reportsController.analyzeIncidentDirect)
);

router.get('/ai-results/:reportId', asyncHandler(reportsController.getAiResults));

export default router;
