import { Router } from 'express';
import * as patternsController from '../controllers/patternsController';
import { authenticate, authorize } from '../middleware/authMiddleware';
import { PERMISSIONS } from '../types';
import { asyncHandler } from '../utils/asyncHandler';

const router = Router();

router.use(authenticate);

router.get('/patterns', asyncHandler(patternsController.getPatterns));
router.get('/patterns/:id', asyncHandler(patternsController.getPatternById));
router.post('/patterns/refresh', authorize(PERMISSIONS.canManagePatterns), asyncHandler(patternsController.refreshPatterns));

export default router;
