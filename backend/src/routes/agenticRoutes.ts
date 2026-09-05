import { Router } from 'express';
import { runAgenticInvestigation } from '../controllers/agenticController';
import { authenticate } from '../middleware/authMiddleware';
import { asyncHandler } from '../utils/asyncHandler';

const router = Router();

router.post('/investigate', authenticate, asyncHandler(runAgenticInvestigation));

export default router;
