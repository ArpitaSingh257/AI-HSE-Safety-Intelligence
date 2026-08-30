import { Request, Response } from 'express';
import * as dashboardService from '../services/dashboardService';

export async function getOverview(_req: Request, res: Response) {
  res.json(await dashboardService.getOverview());
}

export async function getSites(_req: Request, res: Response) {
  res.json(await dashboardService.getHighRiskSites());
}

export async function getActivities(_req: Request, res: Response) {
  res.json(await dashboardService.getHighRiskActivities());
}

export async function getLifeSavingRules(_req: Request, res: Response) {
  res.json(await dashboardService.getTopLifeSavingRules());
}

export async function getPrecursors(_req: Request, res: Response) {
  res.json(await dashboardService.getPrecursorFailures());
}

export async function getTrends(_req: Request, res: Response) {
  res.json(await dashboardService.getTrends());
}
