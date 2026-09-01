import { Router } from 'express';
import * as barrierPatternsController from '../controllers/barrierPatternsController';
import { authenticate } from '../middleware/authMiddleware';
import { asyncHandler } from '../utils/asyncHandler';

const router = Router();

router.use(authenticate);

router.get('/barrier-patterns', asyncHandler(barrierPatternsController.getBarrierPatterns));
router.get('/barrier-patterns/:id', asyncHandler(barrierPatternsController.getBarrierPatternById));

export default router;
