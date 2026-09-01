import { Router } from 'express';
import { getBowTieByReportId } from '../controllers/bowTiesController';

const router = Router();

router.get('/:reportId', getBowTieByReportId);

export default router;
