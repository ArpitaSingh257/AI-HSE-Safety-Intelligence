import { Router } from 'express';
import * as siteRiskController from '../controllers/siteRiskController';
import { authenticate } from '../middleware/authMiddleware';
import { asyncHandler } from '../utils/asyncHandler';

const router = Router();

router.use(authenticate);

router.get('/site-risk', asyncHandler(siteRiskController.getSiteRiskProfiles));
router.get('/site-risk/:id', asyncHandler(siteRiskController.getSiteRiskProfileById));

export default router;
