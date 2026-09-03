import { Router } from 'express';
import { evaluateTriage } from '../controllers/triageController';

const router = Router();

router.post('/', evaluateTriage);

export default router;
