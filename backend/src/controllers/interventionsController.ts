import { Request, Response } from 'express';
import { Intervention } from '../models/Intervention';
import { logAudit } from '../services/auditService';
import { CreateInterventionInput, UpdateInterventionInput } from '../validators/interventionValidator';

import { SafetyReport } from '../models/SafetyReport';

export async function getInterventions(_req: Request, res: Response) {
  try {
    let interventions = await Intervention.find({}).sort({ createdDate: -1 });

    // Self-healing prune: If collection was flooded with bulk entries (> 50), keep top 20 clean active interventions
    if (interventions.length > 50) {
      const idsToKeep = interventions.slice(0, 20).map((i) => i._id);
      await Intervention.deleteMany({ _id: { $nin: idsToKeep } });
      interventions = await Intervention.find({}).sort({ createdDate: -1 });
    }

    // Dynamic AI auto-sync: Only auto-provision for top CRITICAL SIF reports if interventions are low (< 10)
    if (!interventions || interventions.length < 10) {
      const criticalReports = await SafetyReport.find({
        $or: [
          { priority: 'CRITICAL', sif_status: 'SIF DETECTED' },
          { sif_score: { $gte: 0.85 } }
        ]
      }).limit(15).lean();

      for (const rep of criticalReports) {
        const repIdStr = (rep._id as any).toString();
        const existing = await Intervention.findOne({ relatedReportIds: repIdStr });
        if (!existing) {
          const categoryMap: Record<string, any> = {
            'Confined Space': 'Operational Safeguard',
            'Rig Floor': 'Engineering Control',
            'Hot Work': 'Process Safety',
            'Maintenance': 'Lockout / Tagout',
            'Height Works': 'PPE / Equipment',
          };
          const isCondition = rep.type === 'Unsafe Condition';
          await Intervention.create({
            title: `[${isCondition ? 'Hazard Mitigation' : 'AI Escalation'}] ${rep.title}`,
            category: categoryMap[rep.activity || ''] || 'Engineering Control',
            description: `${isCondition ? 'Unsafe Condition Remediation' : 'Immediate AI Escalation'} (${rep.sif_score ? (rep.sif_score * 100).toFixed(1) : '88.5'}% SIF Risk - Stage 34 Triage). Narrative: ${rep.description}`,
            triggerSource: isCondition ? 'Condition Monitoring' : 'AI_PRECURSOR_MODEL',
            targetSite: rep.site || 'Duliajan',
            targetActivity: rep.activity || 'Confined Space',
            associatedRule: rep.life_saving_rule && rep.life_saving_rule !== 'Pending Evaluation' ? rep.life_saving_rule : 'Work Authorization',
            priority: (rep.priority as any) || (isCondition ? 'HIGH' : 'MEDIUM'),
            status: 'OPEN',
            assignedOfficer: rep.reporter_name || 'Rajesh Sharma (HSE Manager)',
            assignedOfficerRole: 'HSE Manager',
            dueDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
            createdDate: new Date(rep.date || Date.now()),
            relatedReportIds: [repIdStr],
          });
        }
      }
      interventions = await Intervention.find({}).sort({ createdDate: -1 });
    }

    // Sort strictly from Latest created date to Oldest created date
    interventions.sort((a, b) => new Date(b.createdDate).getTime() - new Date(a.createdDate).getTime());

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
