import { Router } from 'express';
import * as activityRiskController from '../controllers/activityRiskController';
import { authenticate } from '../middleware/authMiddleware';
import { asyncHandler } from '../utils/asyncHandler';

const router = Router();

router.use(authenticate);

router.get('/activity-risk', asyncHandler(activityRiskController.getActivityRiskProfiles));
router.get('/activity-risk/:id', asyncHandler(activityRiskController.getActivityRiskProfileById));

export default router;
