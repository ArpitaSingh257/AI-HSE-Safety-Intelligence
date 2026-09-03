import { Router } from 'express';
import { processTextNormalization } from '../controllers/textNormalizeController';

const router = Router();

router.post('/normalize', processTextNormalization);

export default router;
