import { Router } from 'express';
import * as dashboardController from '../controllers/dashboardController';
import { authenticate } from '../middleware/authMiddleware';
import { asyncHandler } from '../utils/asyncHandler';

const router = Router();

router.use(authenticate);

router.get('/dashboard/overview', asyncHandler(dashboardController.getOverview));
router.get('/dashboard/sites', asyncHandler(dashboardController.getSites));
router.get('/dashboard/activities', asyncHandler(dashboardController.getActivities));
router.get('/dashboard/life-saving-rules', asyncHandler(dashboardController.getLifeSavingRules));
router.get('/dashboard/precursors', asyncHandler(dashboardController.getPrecursors));
router.get('/dashboard/trends', asyncHandler(dashboardController.getTrends));

export default router;
