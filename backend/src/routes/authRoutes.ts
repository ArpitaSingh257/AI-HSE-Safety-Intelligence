import { Router } from 'express';
import * as authController from '../controllers/authController';
import { authenticate } from '../middleware/authMiddleware';
import { validateBody } from '../middleware/validationMiddleware';
import { loginSchema, registerSchema } from '../validators/authValidator';
import { asyncHandler } from '../utils/asyncHandler';

const router = Router();

router.post('/login', validateBody(loginSchema), asyncHandler(authController.login));
router.post('/register', validateBody(registerSchema), asyncHandler(authController.register));
router.get('/me', authenticate, asyncHandler(authController.getMe));
router.post('/logout', authenticate, asyncHandler(authController.logout));

export default router;
