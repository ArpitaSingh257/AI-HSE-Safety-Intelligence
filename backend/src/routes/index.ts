import { Router } from 'express';
import authRoutes from './authRoutes';
import reportsRoutes from './reportsRoutes';
import dashboardRoutes from './dashboardRoutes';
import patternsRoutes from './patternsRoutes';
import barrierPatternsRoutes from './barrierPatternsRoutes';
import siteRiskRoutes from './siteRiskRoutes';
import activityRiskRoutes from './activityRiskRoutes';
import lsrTrendsRoutes from './lsrTrendsRoutes';
import earlyWarningsRoutes from './earlyWarningsRoutes';
import prioritiesRoutes from './prioritiesRoutes';
import riskMatrixRoutes from './riskMatrixRoutes';
import bowTiesRoutes from './bowTiesRoutes';
import feedbackRoutes from './feedbackRoutes';
import interventionsRoutes from './interventionsRoutes';
import auditRoutes from './auditRoutes';

const router = Router();

router.use('/auth', authRoutes);
// These routers define their own full paths (e.g. '/reports', '/dashboard/overview')
// so they're mounted at the root of /api rather than under a sub-prefix.
router.use('/', reportsRoutes);
router.use('/', dashboardRoutes);
router.use('/', patternsRoutes);
router.use('/', barrierPatternsRoutes);
router.use('/', siteRiskRoutes);
router.use('/', activityRiskRoutes);
router.use('/', lsrTrendsRoutes);
router.use('/early-warnings', earlyWarningsRoutes);
router.use('/priorities', prioritiesRoutes);
router.use('/risk-matrix', riskMatrixRoutes);
router.use('/bow-ties', bowTiesRoutes);
router.use('/feedback', feedbackRoutes);
router.use('/', interventionsRoutes);
router.use('/', auditRoutes);

export default router;
