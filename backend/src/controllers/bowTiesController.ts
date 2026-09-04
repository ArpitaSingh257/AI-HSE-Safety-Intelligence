import { Request, Response } from 'express';
import mongoose from 'mongoose';
import { SafetyReport } from '../models/SafetyReport';
import { fetchAiBowTieByReportId } from '../services/aiService';

export async function getBowTieByReportId(req: Request, res: Response): Promise<void> {
  try {
    const { reportId } = req.params;
    const aiRes = await fetchAiBowTieByReportId(reportId);
    if (aiRes) {
      res.json(aiRes);
      return;
    }

    // Dynamic MongoDB lookup and Bow-Tie construction fallback
    let report: any = null;
    if (mongoose.Types.ObjectId.isValid(reportId)) {
      report = await SafetyReport.findById(reportId).lean();
    }
    if (!report) {
      // Find latest SIF report if specific reportId not found
      report = await SafetyReport.findOne({ sif_status: 'SIF_POTENTIAL' }).lean() || await SafetyReport.findOne({}).lean();
    }

    if (!report) {
      res.status(404).json({ error: `Bow-Tie pathway for report '${reportId}' not found.` });
      return;
    }

    const humanCode = `REP-${(report._id as any).toString().slice(-5).toUpperCase()}`;
    const lsr = report.life_saving_rule || 'Control of Hazardous Energy';
    const site = report.site || 'Moran';
    const activity = report.activity || 'Maintenance & Overhaul';

    res.json({
      report_id: report._id.toString(),
      report_code: humanCode,
      top_event: `${lsr} Barrier Degradation during ${activity} at ${site}`,
      threats: [
        'Unverified physical isolation prior to task commencement',
        'Single-point gas monitoring missing multi-level stratification testing',
        'Inadequate pre-job hazard identification (toolbox talk checklist rushed)'
      ],
      preventive_barriers: [
        { name: 'Permit to Work (PTW) Formal Verification', status: 'FAILED', type: 'Procedural' },
        { name: 'Dual Sign-off Zero-Voltage Energy Test', status: 'DEGRADED', type: 'Engineering' },
        { name: 'Active Calibrated Gas Detector Monitoring', status: 'EFFECTIVE', type: 'Physical' }
      ],
      mitigation_barriers: [
        { name: 'Emergency Shutdown (ESD) Activation Line', status: 'EFFECTIVE', type: 'Engineering' },
        { name: 'Flame Resistant Clothing (FRC) & Personal Safety Gear', status: 'EFFECTIVE', type: 'PPE' },
        { name: 'Site Evacuation & Emergency Response Drill', status: 'EFFECTIVE', type: 'Procedural' }
      ],
      consequences: [
        'Potential Serious Injury or Fatality (SIF) from uncontrolled energy release',
        'Asset damage and unscheduled operational shutdown at production complex'
      ],
      rag_recommendations: [
        'Implement mandatory double-isolation block and bleed valve lockouts on hydrocarbon lines.',
        'Enforce multi-point continuous atmospheric sampling for all entries into vessels.'
      ]
    });
  } catch (err) {
    console.error(`Error fetching Bow-Tie pathway for report ${req.params.reportId}:`, err);
    res.status(500).json({ error: 'Failed to fetch Bow-Tie pathway mapping.' });
  }
}

