import { Router } from 'express';
import { submitFeedback, getFeedbackByReportId, getFeedbackStats, updateFeedbackStatus } from '../controllers/feedbackController';
import { authenticate } from '../middleware/authMiddleware';

const router = Router();

router.post('/', authenticate, submitFeedback);
router.get('/stats', authenticate, getFeedbackStats);
router.get('/reports/:reportId', authenticate, getFeedbackByReportId);
router.patch('/:feedbackId/status', authenticate, updateFeedbackStatus);

export default router;
