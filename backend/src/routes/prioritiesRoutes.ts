import { Router } from 'express';
import { getPriorities, getPriorityById } from '../controllers/prioritiesController';

const router = Router();

router.get('/', getPriorities);
router.get('/:priorityId', getPriorityById);

export default router;
