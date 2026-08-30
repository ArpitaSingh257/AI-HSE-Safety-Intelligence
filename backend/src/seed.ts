import mongoose from 'mongoose';
import dotenv from 'dotenv';
import { faker } from '@faker-js/faker';
import { User } from './models/User';
import { Site } from './models/Site';
import { Activity } from './models/Activity';
import { SafetyReport } from './models/SafetyReport';
import { SifAnalysisResult } from './models/SifAnalysisResult';
import { Intervention } from './models/Intervention';
import { AuditLog } from './models/AuditLog';
import { Pattern } from './models/Pattern';
import { hashPassword } from './utils/password';
import { requestAnalysis } from './services/aiService';
import { regeneratePatterns } from './services/patternService';
import {
  SITE_NAMES,
  ACTIVITY_NAMES,
  REPORT_TYPES,
  INTERVENTION_CATEGORIES,
  INTERVENTION_TRIGGER_SOURCES,
  INTERVENTION_STATUSES,
} from './types';

dotenv.config();

// Sample narrative snippets that intentionally trigger the aiService's
// (stubbed) SIF keyword logic - "breaker", "weld", "confined", "crane",
// "height" - so seeded reports come out with a realistic mix of
// SIF/NON-SIF classifications instead of all-identical stub results.
const SAMPLE_DESCRIPTIONS = [
  'Technician began coupling removal on pump motor while the feeder breaker was tagged but not physically locked out and zero-voltage verification was skipped.',
  'Contractor welding crew conducted hot cutting work near a condensate line without an active combustible gas monitor running.',
  'Crew entered a confined tank space for cleaning based on a single-point gas test; multi-level H2S stratification testing was omitted.',
  'A drill collar sling slipped during a lift due to grease contamination, swinging the suspended load into an occupied rig floor area.',
  'A worker was observed on an elevated platform without a secondary lanyard tie-off while replacing a scaffold guardrail.',
  'Housekeeping debris was found blocking an emergency exit route near the control room for several hours before being reported.',
  'A vehicle exceeded the site speed limit on an internal haul road during shift changeover, nearly striking a pedestrian.',
  'PPE (safety glasses) was not worn during a minor grinding task in the workshop, observed and corrected on the spot.',
];

async function run() {
  const MONGO_URI = process.env.MONGO_URI;
  if (!MONGO_URI) {
    console.error('❌ MONGO_URI is not defined in .env');
    process.exit(1);
  }

  await mongoose.connect(MONGO_URI);
  console.log('✅ MongoDB connected for seeding');

  console.log('🧹 Clearing existing collections...');
  await Promise.all([
    User.deleteMany({}),
    Site.deleteMany({}),
    Activity.deleteMany({}),
    SafetyReport.deleteMany({}),
    SifAnalysisResult.deleteMany({}),
    Intervention.deleteMany({}),
    AuditLog.deleteMany({}),
    Pattern.deleteMany({}),
  ]);

  // --- Sites & Activities (fixed enums from types.ts) ---
  console.log('🏭 Seeding sites & activities...');
  const sites = await Site.insertMany(
    SITE_NAMES.map((name) => ({ name, department: 'HSE & Process Safety' }))
  );
  const activities = await Activity.insertMany(ACTIVITY_NAMES.map((name) => ({ name })));

  // --- Users (one per role, fixed credentials for easy demo login) ---
  console.log('👤 Seeding demo users...');
  const demoUsers = [
    { name: 'Ananya Roy', email: 'admin@oilindia.in', role: 'Admin' as const, department: 'Corporate HSE Directorate' },
    { name: 'Rajesh Sharma', email: 'manager@oilindia.in', role: 'HSE Manager' as const, department: 'HSE & Process Safety' },
    { name: 'Debojit Phukan', email: 'analyst@oilindia.in', role: 'HSE Analyst' as const, department: 'Process Safety Division' },
    { name: 'Site Field Auditor', email: 'viewer@oilindia.in', role: 'Viewer' as const, department: 'Site Operations' },
  ];
  const DEMO_PASSWORD = 'Password@123';
  const passwordHash = await hashPassword(DEMO_PASSWORD);
  const users = await User.insertMany(
    demoUsers.map((u) => ({ ...u, passwordHash, site: 'Duliajan' }))
  );

  // --- Safety Reports (randomized, spread across last 6 months) ---
  console.log('📋 Seeding safety reports (this calls the stubbed AI service for each)...');
  const reportCount = 40;
  const reporter = users[2]; // HSE Analyst submits most field reports in this demo

  for (let i = 0; i < reportCount; i++) {
    const site = faker.helpers.arrayElement(sites);
    const activity = faker.helpers.arrayElement(activities);
    const type = faker.helpers.arrayElement(REPORT_TYPES);
    const description = faker.helpers.arrayElement(SAMPLE_DESCRIPTIONS);
    const daysAgo = faker.number.int({ min: 0, max: 180 });
    const date = new Date(Date.now() - daysAgo * 24 * 60 * 60 * 1000);

    const report = await SafetyReport.create({
      title: `${type} reported during ${activity.name} at ${site.name}`,
      type,
      date,
      siteId: site._id,
      site: site.name,
      activityId: activity._id,
      activity: activity.name,
      department: site.department,
      location_detail: faker.location.streetAddress(),
      reporterId: reporter._id,
      reporter_name: reporter.name,
      reporter_role: reporter.role,
      description,
      immediate_actions_taken: 'Work paused, area made safe, supervisor notified.',
      sif_status: 'PENDING_ANALYSIS',
      sif_score: 0,
      life_saving_rule: 'Pending Evaluation',
      priority: 'MEDIUM',
      analysis_status: 'PENDING',
      investigation_status: 'Open',
    });

    // Run every report through the (stubbed, or real if AI_SERVICE_URL is
    // configured) analysis pipeline so the platform has realistic SIF data,
    // AI results, and matching patterns to display out of the box.
    const result = await requestAnalysis(report);
    await SifAnalysisResult.create({
      reportId: report._id,
      sif: result.sif,
      life_saving_rules: result.life_saving_rules,
      precursors: result.precursors,
      explanation: result.explanation,
      patterns: result.patterns,
      priority: result.priority,
      analyzed_at: new Date(),
      model_version: result.model_version,
    });

    report.sif_status = result.sif.label as any;
    report.sif_score = result.sif.score;
    report.life_saving_rule = result.life_saving_rules[0]?.name || 'Unclassified';
    report.priority = result.priority as any;
    report.analysis_status = 'COMPLETED';
    await report.save();
  }

  console.log('🔎 Regenerating patterns from seeded analysis results...');
  const patternsCreated = await regeneratePatterns();
  console.log(`   -> ${patternsCreated} pattern(s) created`);

  // --- Interventions ---
  console.log('🛠️  Seeding interventions...');
  const patterns = await Pattern.find({}).limit(5);
  const interventionSeeds = patterns.length > 0 ? patterns : [null];
  for (const pattern of interventionSeeds) {
    await Intervention.create({
      title: pattern ? `Reinforce ${pattern.primaryLifeSavingRule} controls` : 'General HSE toolbox talk rollout',
      category: faker.helpers.arrayElement(INTERVENTION_CATEGORIES),
      description: pattern ? pattern.recommendedIntervention : 'Site-wide refresher on life-saving rules.',
      triggerSource: pattern ? 'Pattern Detection' : faker.helpers.arrayElement(INTERVENTION_TRIGGER_SOURCES),
      targetSite: pattern ? pattern.mostAffectedSite : faker.helpers.arrayElement(SITE_NAMES),
      targetActivity: pattern ? pattern.mainActivity : faker.helpers.arrayElement(ACTIVITY_NAMES),
      associatedRule: pattern ? pattern.primaryLifeSavingRule : 'Work Authorization',
      priority: pattern ? pattern.priority : 'MEDIUM',
      status: faker.helpers.arrayElement(INTERVENTION_STATUSES),
      assignedOfficer: users[1].name,
      assignedOfficerRole: users[1].role,
      dueDate: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000),
      createdDate: new Date(),
      relatedReportIds: pattern ? pattern.matchedReportIds.slice(0, 3) : [],
      patternId: pattern ? (pattern._id as any).toString() : null,
    });
  }

  // --- Audit log seed events (login history) ---
  console.log('🧾 Seeding audit log entries...');
  await AuditLog.insertMany(
    users.map((u) => ({
      timestamp: new Date(),
      userId: (u._id as any).toString(),
      userName: u.name,
      userRole: u.role,
      action: 'USER_LOGIN' as const,
      entityType: 'AUTH' as const,
      entityId: (u._id as any).toString(),
      ipAddress: '127.0.0.1',
      status: 'SUCCESS' as const,
      details: `Seed script: initial demo login event for ${u.name}`,
    }))
  );

  console.log('\n✅ Seed complete!');
  console.log('   Demo login credentials (password is the same for all):');
  demoUsers.forEach((u) => console.log(`   - ${u.role.padEnd(12)} ${u.email}`));
  console.log(`   Password: ${DEMO_PASSWORD}\n`);

  await mongoose.disconnect();
  process.exit(0);
}

run().catch((err) => {
  console.error('❌ Seed failed:', err);
  process.exit(1);
});
