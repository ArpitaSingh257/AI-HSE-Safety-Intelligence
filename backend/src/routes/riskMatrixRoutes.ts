import { Router } from 'express';
import { getRiskMatrix, getRiskMatrixItemById } from '../controllers/riskMatrixController';

const router = Router();

router.get('/', getRiskMatrix);
router.get('/:matrixItemId', getRiskMatrixItemById);

export default router;
