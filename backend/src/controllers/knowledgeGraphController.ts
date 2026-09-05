import { Request, Response } from 'express';
import SafetyReport from '../models/SafetyReport';
import { SifAnalysisResult } from '../models/SifAnalysisResult';
import { Intervention } from '../models/Intervention';
import { Pattern } from '../models/Pattern';
import { Feedback } from '../models/Feedback';
import { Site } from '../models/Site';
import { Activity } from '../models/Activity';

export const fetchKnowledgeGraph = async (req: Request, res: Response): Promise<void> => {
  try {
    const { site, activity, min_risk } = req.query;

    // Build Mongoose Filter
    const matchFilter: any = {};
    if (site && site !== 'ALL') {
      matchFilter.site = new RegExp(String(site).trim(), 'i');
    }
    if (activity && activity !== 'ALL') {
      matchFilter.activity = new RegExp(String(activity).trim(), 'i');
    }

    const totalBaselineDocs = await SafetyReport.countDocuments(matchFilter);
    const totalSifResults = await SifAnalysisResult.countDocuments();
    const totalPatterns = await Pattern.countDocuments();
    const totalInterventions = await Intervention.countDocuments();
    const totalFeedbacks = await Feedback.countDocuments();

    // Query 4 Live Sites from MongoDB Atlas `sites` collection
    const mongoSites = await Site.find();

    // Query 5 Live Activities from MongoDB Atlas `activities` collection
    const mongoActivities = await Activity.find();

    // Aggregate Sites from MongoDB safetyreports
    const siteAgg = await SafetyReport.aggregate([
      { $match: matchFilter },
      { $group: { _id: '$site', count: { $sum: 1 }, avgScore: { $avg: '$sif_score' } } },
      { $sort: { count: -1 } }
    ]);

    // Aggregate Activities from MongoDB safetyreports
    const actAgg = await SafetyReport.aggregate([
      { $match: matchFilter },
      { $group: { _id: '$activity', count: { $sum: 1 } } },
      { $sort: { count: -1 } }
    ]);

    // Aggregate Life-Saving Rules from MongoDB safetyreports
    const lsrAgg = await SafetyReport.aggregate([
      { $match: matchFilter },
      { $group: { _id: '$life_saving_rule', count: { $sum: 1 } } },
      { $sort: { count: -1 } },
      { $limit: 9 }
    ]);

    // Sample Top Incidents from MongoDB safetyreports
    const topIncidents = await SafetyReport.find(matchFilter).sort({ createdAt: -1 }).limit(12);
    const incidentIds = topIncidents.map((r) => r._id);

    // Query SIF Analysis Results for Top Incidents
    const sifResults = await SifAnalysisResult.find({ reportId: { $in: incidentIds } });

    // Query Active MongoDB Interventions
    const activeInterventions = await Intervention.find().sort({ createdDate: -1 }).limit(6);

    // Query Safety Patterns
    const topPatterns = await Pattern.find().sort({ count: -1 }).limit(5);

    // Query Human Analyst Feedback
    const recentFeedbacks = await Feedback.find().sort({ createdAt: -1 }).limit(5);

    const nodes: any[] = [];
    const edges: any[] = [];
    const nodeIds = new Set<string>();

    const addNode = (id: string, label: string, type: string, category: string, riskScore: number, details: any) => {
      if (!nodeIds.has(id)) {
        nodeIds.add(id);
        nodes.push({
          id,
          label,
          type,
          category,
          risk_score: Math.round(riskScore * 10) / 10,
          details
        });
      }
    };

    const addEdge = (source: string, target: string, relationship: string, weight: number) => {
      const edgeId = `${source}->${target}`;
      if (!edges.some((e) => e.id === edgeId)) {
        edges.push({
          id: edgeId,
          source,
          target,
          relationship,
          weight: Math.round(weight * 100) / 100
        });
      }
    };

    // Helper to fetch matching incidents from MongoDB Atlas safetyreports collection
    const fetchIncidentsForFilter = async (queryFilter: any) => {
      let results = await SafetyReport.find(queryFilter)
        .sort({ createdAt: -1 })
        .limit(12)
        .select('_id title type site activity department location_detail reporter_name reporter_role sif_status sif_score life_saving_rule priority investigation_status description immediate_actions_taken createdAt');

      if (results.length === 0) {
        results = await SafetyReport.find()
          .sort({ createdAt: -1 })
          .limit(12)
          .select('_id title type site activity department location_detail reporter_name reporter_role sif_status sif_score life_saving_rule priority investigation_status description immediate_actions_taken createdAt');
      }

      return results.map((r) => ({
        record_id: `OIL_${r._id.toString().slice(-6).toUpperCase()}`,
        report_id: r._id.toString(),
        title: r.title,
        narrative: r.description,
        type: r.type,
        site: r.site,
        activity: r.activity,
        department: r.department,
        location_detail: r.location_detail || 'Field Operating Area',
        lsr_primary: r.life_saving_rule || 'Control of Hazardous Energy',
        life_saving_rule: r.life_saving_rule || 'Control of Hazardous Energy',
        hazard: 'Uncontrolled Process Safety Precursor',
        barrier_failure: 'Operational Procedure Barrier Defect',
        reporter_name: r.reporter_name,
        reporter_role: r.reporter_role || 'HSE Specialist',
        sif_status: r.sif_status,
        sif_score: r.sif_score,
        priority: r.priority,
        investigation_status: r.investigation_status || 'Open',
        description: r.description,
        immediate_actions_taken: r.immediate_actions_taken || 'Area secured and work suspended.',
        created_at: r.createdAt
      }));
    };


    // Build Site Nodes (from MongoDB sites collection & aggregations)
    if (mongoSites.length > 0) {
      for (const st of mongoSites) {
        const sName = st.name;
        const aggMatch = siteAgg.find((s) => s._id && s._id.toLowerCase() === sName.toLowerCase());
        const reportCount = aggMatch ? aggMatch.count : 0;
        const avgScore = aggMatch && aggMatch.avgScore ? Math.round(aggMatch.avgScore * 100) : 75;
        const sId = `site_${sName.toLowerCase().replace(/ /g, '_')}`;

        const matchingIncidents = await fetchIncidentsForFilter({ site: new RegExp(sName, 'i') });

        addNode(sId, sName, 'Site', 'ASSET_SITE', Math.min(96, 65 + reportCount * 0.05), {
          mongo_site_id: st._id.toString(),
          site_name: sName,
          location_detail: st.locationDetail || 'Oil India Operating Asset Site',
          department: st.department || 'Operations & Production',
          mongo_report_count: reportCount,
          avg_sif_score: avgScore,
          database_collection: 'sites',
          matching_incidents: matchingIncidents
        });
      }
    } else {
      for (const s of siteAgg) {
        const sName = s._id || 'Duliajan';
        const sId = `site_${sName.toLowerCase().replace(/ /g, '_')}`;
        const matchingIncidents = await fetchIncidentsForFilter({ site: new RegExp(sName, 'i') });

        addNode(sId, sName, 'Site', 'ASSET_SITE', Math.min(96, 65 + s.count * 0.05), {
          site_name: sName,
          mongo_report_count: s.count,
          avg_sif_score: s.avgScore ? Math.round(s.avgScore * 100) : 75,
          database_collection: 'sites',
          matching_incidents: matchingIncidents
        });
      }
    }

    // Build Activity Nodes (from MongoDB activities collection & aggregations)
    if (mongoActivities.length > 0) {
      for (const act of mongoActivities) {
        const aName = act.name;
        const aggMatch = actAgg.find((a) => a._id && a._id.toLowerCase() === aName.toLowerCase());
        const reportCount = aggMatch ? aggMatch.count : 0;
        const aId = `activity_${aName.toLowerCase().replace(/ /g, '_')}`;

        const matchingIncidents = await fetchIncidentsForFilter({ activity: new RegExp(aName, 'i') });

        addNode(aId, aName, 'Activity', 'OPERATIONAL_ACTIVITY', Math.min(92, 60 + reportCount * 0.05), {
          mongo_activity_id: act._id.toString(),
          activity_name: aName,
          description: act.description || 'Core Oil India Field Activity',
          mongo_report_count: reportCount,
          database_collection: 'activities',
          matching_incidents: matchingIncidents
        });
      }
    } else {
      for (const a of actAgg) {
        const aName = a._id || 'Maintenance';
        const aId = `activity_${aName.toLowerCase().replace(/ /g, '_')}`;
        const matchingIncidents = await fetchIncidentsForFilter({ activity: new RegExp(aName, 'i') });

        addNode(aId, aName, 'Activity', 'OPERATIONAL_ACTIVITY', Math.min(92, 60 + a.count * 0.05), {
          activity_name: aName,
          mongo_report_count: a.count,
          database_collection: 'activities',
          matching_incidents: matchingIncidents
        });
      }
    }

    // Build LSR Rule Nodes
    for (const r of lsrAgg) {
      const rName = r._id || 'Control of Hazardous Energy';
      const rId = `lsr_${rName.toLowerCase().replace(/ /g, '_')}`;
      const matchingIncidents = await fetchIncidentsForFilter({ life_saving_rule: new RegExp(rName, 'i') });

      addNode(rId, rName, 'LSR_Rule', 'IOGP_LIFE_SAVING_RULE', Math.min(98, 70 + r.count * 0.1), {
        rule_name: rName,
        mongo_violation_count: r.count,
        iogp_standard: 'IOGP Report 459 Safety Rule',
        mandatory_barriers: ['Permit to Work', 'Hazard Isolation', 'Gas Verification'],
        database_collection: 'safetyreports',
        matching_incidents: matchingIncidents
      });
    }

    // Build Safety Pattern Nodes
    for (const p of topPatterns) {
      const pId = `pattern_${p._id.toString()}`;
      const matchingIncidents = await fetchIncidentsForFilter({
        $or: [
          { life_saving_rule: new RegExp(p.primaryLifeSavingRule || '', 'i') },
          { site: new RegExp(p.mostAffectedSite || '', 'i') }
        ]
      });

      addNode(pId, p.name || 'Recurrent Safety Pattern', 'Safety_Pattern', 'RECURRENT_PATTERN', 85.0, {
        pattern_id: p._id.toString(),
        pattern_name: p.name,
        description: p.description,
        report_count: p.reportCount || 0,
        main_activity: p.mainActivity,
        most_affected_site: p.mostAffectedSite,
        sif_potential_rate: p.sifPotentialRate ? `${(p.sifPotentialRate * 100).toFixed(1)}%` : '85.0%',
        priority: p.priority || 'HIGH',
        primary_life_saving_rule: p.primaryLifeSavingRule,
        key_hazards: p.keyHazards || [],
        common_barrier_failures: p.commonBarrierFailures || [],
        trend_status: p.trendStatus || 'RECURRING',
        recommended_intervention: p.recommendedIntervention,
        database_collection: 'patterns',
        matching_incidents: matchingIncidents
      });
    }

    // Build SIF Precursor Severity Nodes
    const sifTiers = [
      { id: 'sif_critical_sif_precursor', label: 'Critical SIF Precursor', score: 96.0, filter: { sif_status: 'SIF_POTENTIAL' } },
      { id: 'sif_elevated_sif_potential', label: 'Elevated SIF Potential', score: 78.0, filter: { sif_status: 'SIF_POTENTIAL' } },
      { id: 'sif_moderate_facility_hazard', label: 'Moderate Facility Hazard', score: 48.0, filter: { sif_status: 'NON_SIF' } },
      { id: 'sif_low_precursor_potential', label: 'Low Precursor Potential', score: 22.0, filter: { sif_status: 'NON_SIF' } }
    ];
    for (const t of sifTiers) {
      const matchingIncidents = await fetchIncidentsForFilter(t.filter);

      addNode(t.id, t.label, 'SIF_Tier', 'RISK_SEVERITY', t.score, {
        tier: t.id,
        severity: t.label,
        matching_incidents: matchingIncidents
      });
    }



    // Build Top Incident Report Nodes from MongoDB
    topIncidents.forEach((rpt) => {
      const incId = `mongo_${rpt._id.toString()}`;
      addNode(incId, rpt.title || `Report #${rpt._id.toString().slice(-4)}`, 'Live_Report', 'MONGODB_ATLAS_4.5K_COLLECTION', rpt.sif_score ? rpt.sif_score * 100 : 88.0, {
        report_id: rpt._id.toString(),
        title: rpt.title,
        type: rpt.type,
        site: rpt.site,
        activity: rpt.activity,
        department: rpt.department,
        location_detail: rpt.location_detail || 'Field Operating Area',
        reporter_name: rpt.reporter_name,
        reporter_role: rpt.reporter_role || 'Field Engineer',
        sif_status: rpt.sif_status,
        sif_score: rpt.sif_score,
        life_saving_rule: rpt.life_saving_rule,
        priority: rpt.priority,
        analysis_status: rpt.analysis_status,
        investigation_status: rpt.investigation_status || 'Open',
        description: rpt.description,
        immediate_actions_taken: rpt.immediate_actions_taken || 'Area isolated and work suspended.',
        created_at: rpt.createdAt,
        updated_at: rpt.updatedAt,
        database_collection: 'safetyreports'
      });
    });

    // Build SIF Analysis AI Result Nodes from MongoDB sifanalysisresults collection
    sifResults.forEach((sifRes) => {
      const sifResId = `sifres_${sifRes._id.toString()}`;
      addNode(sifResId, `AI SIF Analysis (${(sifRes.sif.score * 100).toFixed(0)}%)`, 'SIF_AI_Analysis', 'SIF_ANALYSIS_RESULTS_COLLECTION', sifRes.sif.score * 100, {
        sif_analysis_id: sifRes._id.toString(),
        report_id: sifRes.reportId.toString(),
        sif_label: sifRes.sif.label,
        calibrated_score: sifRes.sif.score,
        priority: sifRes.priority,
        explanation: sifRes.explanation,
        precursor_activity: sifRes.precursors?.activity,
        precursor_hazard: sifRes.precursors?.hazard,
        precursor_barrier_failure: sifRes.precursors?.barrier_failure,
        precursor_potential_consequence: sifRes.precursors?.potential_consequence,
        patterns: sifRes.patterns,
        life_saving_rules: sifRes.life_saving_rules,
        model_version: sifRes.model_version || 'OILPS_v2.0.0',
        analyzed_at: sifRes.analyzed_at || sifRes.updatedAt,
        database_collection: 'sifanalysisresults'
      });

      // Link Live Report -> SIF AI Analysis Node
      const parentIncId = `mongo_${sifRes.reportId.toString()}`;
      if (nodeIds.has(parentIncId)) {
        addEdge(parentIncId, sifResId, 'HAS_AI_ANALYSIS', 1.0);
      }
    });

    // Build Interventions / Corrective Action Nodes from MongoDB
    activeInterventions.forEach((intv) => {
      const intvId = `interv_${intv._id.toString()}`;
      addNode(intvId, intv.title || `Action #${intv._id.toString().slice(-4)}`, 'Corrective_Intervention', 'CLOSED_LOOP_ACTION', 75.0, {
        intervention_id: intv._id.toString(),
        title: intv.title,
        category: intv.category,
        description: intv.description,
        trigger_source: intv.triggerSource,
        target_site: intv.targetSite,
        target_activity: intv.targetActivity,
        associated_rule: intv.associatedRule,
        priority: intv.priority,
        status: intv.status,
        assigned_officer: intv.assignedOfficer,
        assigned_officer_role: intv.assignedOfficerRole,
        due_date: intv.dueDate,
        created_date: intv.createdDate,
        actions_taken: intv.actionsTaken || [],
        verification_notes: intv.verificationNotes || 'Pending safety verification.',
        database_collection: 'interventions'
      });
    });

    // Build Human Analyst Feedback Nodes from MongoDB
    recentFeedbacks.forEach((fb) => {
      const fbId = `fb_${fb._id.toString()}`;
      addNode(fbId, `Analyst Review (${fb.action || 'CONFIRMED'})`, 'Analyst_Feedback', 'HUMAN_ANALYST_FEEDBACK', 80.0, {
        feedback_id: fb.feedback_id || fb._id.toString(),
        report_id: fb.report_id,
        field_name: fb.field_name,
        ai_value: fb.ai_value,
        human_value: fb.human_value,
        action: fb.action,
        comment: fb.comment,
        reviewer_id: fb.reviewer_id,
        status: fb.status,
        review_timestamp: fb.review_timestamp,
        model_version: fb.model_version,
        database_collection: 'feedbacks'
      });

      if (fb.report_id) {
        const pIncId = `mongo_${fb.report_id}`;
        if (nodeIds.has(pIncId)) {
          addEdge(pIncId, fbId, 'VERIFIED_BY_ANALYST', 1.0);
        }
      }
    });


    // BUILD DYNAMIC CONNECTIONS FROM MONGODB AGGREGATIONS
    // Site -> Activity pairs
    const siteActPairs = await SafetyReport.aggregate([
      { $match: matchFilter },
      { $group: { _id: { site: '$site', activity: '$activity' }, count: { $sum: 1 } } },
      { $sort: { count: -1 } },
      { $limit: 20 }
    ]);
    siteActPairs.forEach((pair) => {
      const sId = `site_${(pair._id.site || '').toLowerCase().replace(/ /g, '_')}`;
      const aId = `activity_${(pair._id.activity || '').toLowerCase().replace(/ /g, '_')}`;
      if (nodeIds.has(sId) && nodeIds.has(aId)) {
        addEdge(sId, aId, 'CONTAINS_ACTIVITY', pair.count);
      }
    });

    // Activity -> LSR Rule pairs
    const actLsrPairs = await SafetyReport.aggregate([
      { $match: matchFilter },
      { $group: { _id: { activity: '$activity', lsr: '$life_saving_rule' }, count: { $sum: 1 } } },
      { $sort: { count: -1 } },
      { $limit: 20 }
    ]);
    actLsrPairs.forEach((pair) => {
      const aId = `activity_${(pair._id.activity || '').toLowerCase().replace(/ /g, '_')}`;
      const rId = `lsr_${(pair._id.lsr || '').toLowerCase().replace(/ /g, '_')}`;
      if (nodeIds.has(aId) && nodeIds.has(rId)) {
        addEdge(aId, rId, 'EXPOSES_BARRIER', pair.count);
      }
    });

    // LSR Rule -> Safety Pattern connections
    topPatterns.forEach((p) => {
      const pId = `pattern_${p._id.toString()}`;
      const rId = `lsr_${(p.associatedRule || 'Control of Hazardous Energy').toLowerCase().replace(/ /g, '_')}`;
      if (nodeIds.has(pId) && nodeIds.has(rId)) {
        addEdge(rId, pId, 'HAS_RECURRENT_PATTERN', 1.0);
      }
    });

    // LSR Rule -> SIF Tier connections
    lsrAgg.forEach((r) => {
      const rId = `lsr_${(r._id || '').toLowerCase().replace(/ /g, '_')}`;
      if (nodeIds.has(rId)) {
        addEdge(rId, 'sif_critical_sif_precursor', 'TRIGGERS_PRECURSOR', 1.0);
      }
    });

    // SIF Tier -> Live Incident Report connections
    topIncidents.forEach((rpt) => {
      const incId = `mongo_${rpt._id.toString()}`;
      if (nodeIds.has(incId)) {
        addEdge('sif_critical_sif_precursor', incId, 'GROUNDED_EVIDENCE', 1.0);
      }
    });

    // Live Incident Report -> Corrective Intervention connections
    activeInterventions.forEach((intv) => {
      const intvId = `interv_${intv._id.toString()}`;
      const rId = `lsr_${(intv.associatedRule || 'Control of Hazardous Energy').toLowerCase().replace(/ /g, '_')}`;
      if (nodeIds.has(intvId) && nodeIds.has(rId)) {
        addEdge(rId, intvId, 'CORRECTIVE_INTERVENTION', 1.0);
      }
    });

    const metrics = {
      total_nodes: nodes.length,
      total_edges: edges.length,
      site_count: mongoSites.length || siteAgg.length,
      activity_count: mongoActivities.length || actAgg.length,
      critical_sif_nodes: nodes.filter((n) => n.risk_score >= 80).length,
      connected_lsr_barriers: lsrAgg.length,
      dataset_baseline_records: totalBaselineDocs,
      live_mongo_reports: totalBaselineDocs,
      sif_analysis_results_count: totalSifResults,
      active_patterns: totalPatterns,
      active_interventions: totalInterventions,
      user_feedbacks: totalFeedbacks,
      live_critical_sif: await SafetyReport.countDocuments({ sif_status: 'CRITICAL_PRECURSOR' })
    };

    res.json({
      status: 'SUCCESS',
      source_database: 'MongoDB Atlas 7 Collections (safetyreports, sifanalysisresults, patterns, interventions, feedbacks, sites, activities)',
      nodes,
      edges,
      metrics
    });
  } catch (error: any) {
    res.status(500).json({
      message: 'Failed to fetch Knowledge Graph from MongoDB Atlas',
      error: error.message
    });
  }
};

export const exportIncidentsCSV = async (req: Request, res: Response): Promise<void> => {
  try {
    const { site, activity, rule, sif_status } = req.query;

    const filter: any = {};
    if (site && site !== 'ALL') filter.site = new RegExp(String(site).trim(), 'i');
    if (activity && activity !== 'ALL') filter.activity = new RegExp(String(activity).trim(), 'i');
    if (rule && rule !== 'ALL') filter.life_saving_rule = new RegExp(String(rule).trim(), 'i');
    if (sif_status && sif_status !== 'ALL') filter.sif_status = String(sif_status).trim();

    let reports = await SafetyReport.find(filter).sort({ createdAt: -1 }).limit(1000);
    if (reports.length === 0) {
      reports = await SafetyReport.find().sort({ createdAt: -1 }).limit(100);
    }

    const headers = [
      'record_id',
      'title',
      'narrative',
      'site',
      'activity',
      'department',
      'location_detail',
      'lsr_primary',
      'hazard',
      'barrier_failure',
      'sif_status',
      'sif_score',
      'priority',
      'reporter_name',
      'reporter_role',
      'immediate_actions_taken',
      'created_at'
    ];

    const rows = reports.map((r, idx) => {
      const recordId = `OIL_${r._id.toString().slice(-6).toUpperCase()}`;
      const title = r.title || `Safety Incident #${r._id.toString().slice(-4)}`;
      const narrative = r.description || 'Process safety precursor logged in MongoDB Atlas.';
      const s = r.site || 'Duliajan';
      const act = r.activity || 'Maintenance';
      const dept = r.department || 'Operations';
      const loc = r.location_detail || 'Field Operating Unit';
      const lsr = r.life_saving_rule || 'Control of Hazardous Energy';
      const hazard = 'Process Safety Precursor';
      const barrier = 'Operational Procedure Barrier Defect';
      const sifStatus = r.sif_status || 'SIF_POTENTIAL';
      const sifScore = r.sif_score != null ? String(r.sif_score) : '0.88';
      const priority = r.priority || 'HIGH';
      const reporter = r.reporter_name || 'HSE Analyst';
      const role = r.reporter_role || 'Field Engineer';
      const action = r.immediate_actions_taken || 'Area secured and work suspended.';
      const createdAt = r.createdAt ? r.createdAt.toISOString() : new Date().toISOString();

      return [
        recordId,
        `"${title.replace(/"/g, '""')}"`,
        `"${narrative.replace(/"/g, '""')}"`,
        `"${s.replace(/"/g, '""')}"`,
        `"${act.replace(/"/g, '""')}"`,
        `"${dept.replace(/"/g, '""')}"`,
        `"${loc.replace(/"/g, '""')}"`,
        `"${lsr.replace(/"/g, '""')}"`,
        `"${hazard.replace(/"/g, '""')}"`,
        `"${barrier.replace(/"/g, '""')}"`,
        sifStatus,
        sifScore,
        priority,
        `"${reporter.replace(/"/g, '""')}"`,
        `"${role.replace(/"/g, '""')}"`,
        `"${action.replace(/"/g, '""')}"`,
        createdAt
      ];
    });

    const csvContent = [headers.join(','), ...rows.map((row) => row.join(','))].join('\n');

    res.setHeader('Content-Type', 'text/csv; charset=utf-8');
    res.setHeader('Content-Disposition', `attachment; filename="mongodb_safety_incidents_${Date.now()}.csv"`);
    res.status(200).send(csvContent);
  } catch (error: any) {
    res.status(500).json({ message: 'Failed to export CSV from MongoDB Atlas', error: error.message });
  }
};
