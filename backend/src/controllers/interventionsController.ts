import { Request, Response } from 'express';
import { Intervention } from '../models/Intervention';
import { logAudit } from '../services/auditService';
import { CreateInterventionInput, UpdateInterventionInput } from '../validators/interventionValidator';

export async function getInterventions(_req: Request, res: Response) {
  const interventions = await Intervention.find({}).sort({ createdDate: -1 });
  res.json(interventions.map((i) => i.toJSON()));
}

export async function getInterventionById(req: Request, res: Response) {
  const intervention = await Intervention.findById(req.params.id);
  if (!intervention) return res.status(404).json({ message: `Intervention ${req.params.id} not found` });
  res.json(intervention.toJSON());
}

export async function createIntervention(req: Request<{}, {}, CreateInterventionInput>, res: Response) {
  const payload = req.body;

  const intervention = await Intervention.create({
    ...payload,
    dueDate: new Date(payload.dueDate),
    createdDate: new Date(),
  });

  await logAudit({
    req,
    action: 'INTERVENTION_CREATED',
    entityType: 'INTERVENTION',
    entityId: (intervention._id as any).toString(),
    details: `Authorized HSE intervention "${intervention.title}" targeted for ${intervention.targetSite}`,
  });

  res.status(201).json(intervention.toJSON());
}

export async function updateIntervention(req: Request<{ id: string }, {}, UpdateInterventionInput>, res: Response) {
  const intervention = await Intervention.findById(req.params.id);
  if (!intervention) return res.status(404).json({ message: `Intervention ${req.params.id} not found` });

  const previousStatus = intervention.status;
  const updates: any = { ...req.body };
  if (updates.dueDate) updates.dueDate = new Date(updates.dueDate);
  if (updates.completionDate) updates.completionDate = new Date(updates.completionDate);
  if (updates.status === 'CLOSED' && !intervention.completionDate && !updates.completionDate) {
    updates.completionDate = new Date();
  }

  Object.assign(intervention, updates);
  await intervention.save();

  await logAudit({
    req,
    action: 'INTERVENTION_STATUS_UPDATED',
    entityType: 'INTERVENTION',
    entityId: req.params.id,
    details: `Updated intervention ${req.params.id} (${intervention.title}) status from "${previousStatus}" to "${intervention.status}"`,
    changesSummary: { before: `Status: ${previousStatus}`, after: `Status: ${intervention.status}` },
  });

  res.json(intervention.toJSON());
}

export async function deleteIntervention(req: Request, res: Response) {
  const intervention = await Intervention.findById(req.params.id);
  if (!intervention) return res.status(404).json({ message: `Intervention ${req.params.id} not found` });
  await intervention.deleteOne();
  res.json({ success: true });
}
