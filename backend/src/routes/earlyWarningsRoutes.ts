import { Router } from 'express';
import { getEarlyWarnings, getEarlyWarningById } from '../controllers/earlyWarningsController';

const router = Router();

router.get('/', getEarlyWarnings);
router.get('/:warningId', getEarlyWarningById);

export default router;
