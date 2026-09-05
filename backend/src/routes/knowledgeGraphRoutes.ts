import { Router } from 'express';
import { fetchKnowledgeGraph, exportIncidentsCSV } from '../controllers/knowledgeGraphController';
import { authenticate } from '../middleware/authMiddleware';
import { asyncHandler } from '../utils/asyncHandler';

const router = Router();

router.get('/', authenticate, asyncHandler(fetchKnowledgeGraph));
router.get('/export-incidents', asyncHandler(exportIncidentsCSV));

export default router;
