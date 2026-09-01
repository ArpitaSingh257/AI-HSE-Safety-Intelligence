import { Router } from 'express';
import * as lsrTrendsController from '../controllers/lsrTrendsController';
import { authenticate } from '../middleware/authMiddleware';
import { asyncHandler } from '../utils/asyncHandler';

const router = Router();

router.use(authenticate);

router.get('/lsr-trends', asyncHandler(lsrTrendsController.getLsrTrendProfiles));
router.get('/lsr-trends/:rule', asyncHandler(lsrTrendsController.getLsrTrendProfileByRule));

export default router;
