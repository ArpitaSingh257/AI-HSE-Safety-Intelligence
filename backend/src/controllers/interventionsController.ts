import { Request, Response } from 'express';
import { Intervention } from '../models/Intervention';
import { logAudit } from '../services/auditService';
import { CreateInterventionInput, UpdateInterventionInput } from '../validators/interventionValidator';

import { SafetyReport } from '../models/SafetyReport';

export async function getInterventions(_req: Request, res: Response) {
  try {
    let interventions = await Intervention.find({}).sort({ createdDate: -1 });

    // Dynamic AI auto-generation if collection is empty
    if (!interventions || interventions.length === 0) {
      const sifReports = await SafetyReport.find({ priority: 'CRITICAL' }).limit(10).lean();

      if (sifReports && sifReports.length > 0) {
        const newInterventions: any[] = [];
        for (const rep of sifReports) {
          const created = await Intervention.create({
            title: `AI Dispatch: Reinforce ${rep.activity || 'Process Safety'} Controls at ${rep.site || 'Moran'}`,
            category: 'Engineering Control',
            description: `Automated AI intervention triggered by high SIF precursor density logged in report REP-${(rep._id as any).toString().slice(-5).toUpperCase()}.`,
            triggerSource: 'Pattern Detection',
            targetSite: rep.site || 'Moran',
            targetActivity: rep.activity || 'Maintenance',
            associatedRule: 'Work Authorization',
            priority: 'CRITICAL',
            status: 'OPEN',
            assignedOfficer: 'Rajesh Sharma',
            assignedOfficerRole: 'HSE Manager',
            dueDate: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000),
            createdDate: new Date(rep.date || Date.now()),
            relatedReportIds: [(rep._id as any).toString()],
          });
          newInterventions.push(created);
        }
        interventions = newInterventions;
      }
    }

    const priorityRank: Record<string, number> = {
      CRITICAL: 4,
      HIGH: 3,
      MEDIUM: 2,
      LOW: 1,
    };

    interventions.sort((a, b) => {
      const rankA = priorityRank[a.priority] || 0;
      const rankB = priorityRank[b.priority] || 0;
      if (rankB !== rankA) return rankB - rankA;
      return new Date(b.createdDate).getTime() - new Date(a.createdDate).getTime();
    });

    res.json(interventions.map((i) => i.toJSON()));
  } catch (err) {
    console.error('Error fetching interventions:', err);
    res.status(500).json({ error: 'Failed to fetch interventions' });
  }
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

  // If status is CLOSED, mark linked SafetyReport items as 'Closed / Resolved'
  if (updates.status === 'CLOSED' && intervention.relatedReportIds && intervention.relatedReportIds.length > 0) {
    try {
      await SafetyReport.updateMany(
        { _id: { $in: intervention.relatedReportIds } },
        { $set: { investigation_status: 'Closed / Resolved', analysis_status: 'COMPLETED' } }
      );
    } catch (err) {
      console.warn('Could not update linked reports status:', err);
    }
  }

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
