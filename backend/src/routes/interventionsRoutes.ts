import { Router } from 'express';
import * as interventionsController from '../controllers/interventionsController';
import { authenticate, authorize } from '../middleware/authMiddleware';
import { validateBody } from '../middleware/validationMiddleware';
import { createInterventionSchema, updateInterventionSchema } from '../validators/interventionValidator';
import { PERMISSIONS } from '../types';
import { asyncHandler } from '../utils/asyncHandler';

const router = Router();

router.use(authenticate);

router.get('/interventions', asyncHandler(interventionsController.getInterventions));
router.get('/interventions/:id', asyncHandler(interventionsController.getInterventionById));

router.post(
  '/interventions',
  authorize(PERMISSIONS.canManageInterventions),
  validateBody(createInterventionSchema),
  asyncHandler(interventionsController.createIntervention)
);

router.put(
  '/interventions/:id',
  authorize(PERMISSIONS.canManageInterventions),
  validateBody(updateInterventionSchema),
  asyncHandler(interventionsController.updateIntervention)
);

router.delete(
  '/interventions/:id',
  authorize(PERMISSIONS.canDeleteIntervention),
  asyncHandler(interventionsController.deleteIntervention)
);

export default router;
