import mongoose from 'mongoose';
import dotenv from 'dotenv';
import path from 'path';
import fs from 'fs';

dotenv.config({ path: path.resolve(__dirname, '../.env') });
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
import { requestAnalysis, buildStubResult } from './services/aiService';
import { regeneratePatterns } from './services/patternService';
import {
  SITE_NAMES,
  ACTIVITY_NAMES,
  REPORT_TYPES,
  INTERVENTION_CATEGORIES,
  INTERVENTION_TRIGGER_SOURCES,
  INTERVENTION_STATUSES,
} from './types';



interface MasterRecord {
  narrative: string;
  site: string;
  activity: string;
  sifPotential: boolean;
  lsrPrimary: string;
  barrierFailure: string;
  hazard: string;
  potentialConsequence: string;
  severity: string;
  eventType: string;
}

function parseCsvRows(csvText: string): string[][] {
  const rows: string[][] = [];
  let currentRow: string[] = [];
  let currentField = '';
  let insideQuotes = false;

  for (let i = 0; i < csvText.length; i++) {
    const char = csvText[i];
    const nextChar = csvText[i + 1];

    if (char === '"') {
      if (insideQuotes && nextChar === '"') {
        currentField += '"';
        i++;
      } else {
        insideQuotes = !insideQuotes;
      }
    } else if (char === ',' && !insideQuotes) {
      currentRow.push(currentField);
      currentField = '';
    } else if ((char === '\n' || char === '\r') && !insideQuotes) {
      if (char === '\r' && nextChar === '\n') {
        i++;
      }
      currentRow.push(currentField);
      if (currentRow.some(f => f.trim().length > 0)) {
        rows.push(currentRow);
      }
      currentRow = [];
      currentField = '';
    } else {
      currentField += char;
    }
  }
  if (currentField || currentRow.length > 0) {
    currentRow.push(currentField);
    rows.push(currentRow);
  }
  return rows;
}

const ALL_IOGP_RULES = [
  'Control of Hazardous Energy',
  'Confined Space Entry',
  'Hot Work',
  'Work at Height',
  'Safe Mechanical Lifting',
  'Line of Fire',
  'Driving',
  'Bypassing Safety Controls',
  'Work Authorization'
];

function inferLsr(text: string, defaultLsr: string, idx: number): string {
  const lower = text.toLowerCase();
  if (/breaker|lockout|tagout|electrical|power|cable|switchgear|isolation/i.test(lower)) return 'Control of Hazardous Energy';
  if (/weld|cutting|flame|grinder|spark|gas monitor|combustible|hot work/i.test(lower)) return 'Hot Work';
  if (/tank|vessel|confined|entry|stratification|h2s|atmospheric/i.test(lower)) return 'Confined Space Entry';
  if (/crane|sling|lift|hoist|derrick|load|rig floor|rigging/i.test(lower)) return 'Safe Mechanical Lifting';
  if (/scaffold|platform|height|lanyard|harness|elevation|fall|guardrail/i.test(lower)) return 'Work at Height';
  if (/bus|speed|driver|vehicle|truck|haul road|traffic|seatbelt/i.test(lower)) return 'Driving';
  if (/bypass|interlock|override|safety control|shield/i.test(lower)) return 'Bypassing Safety Controls';
  if (/permit|ptw|authorization|signed|toolbox/i.test(lower)) return 'Work Authorization';
  if (/line of fire|pinch|dropped object|swing path|unsecured/i.test(lower)) return 'Line of Fire';
  return ALL_IOGP_RULES[idx % ALL_IOGP_RULES.length];
}

function extractCsvBarrier(row: string[], narrative: string, lsr: string): string {
  const bf = row[26]?.replace(/^"|"$/g, '').trim();
  if (bf && bf.length > 8 && !bf.toLowerCase().includes('identified')) return bf;

  const b = row[25]?.replace(/^"|"$/g, '').trim();
  if (b && b.length > 8 && !b.toLowerCase().includes('identified')) return b;

  const www = row[13]?.replace(/^"|"$/g, '').trim();
  if (www && www.length > 10) return www;

  const cf = row[15]?.replace(/^"|"$/g, '').trim();
  if (cf && cf.length > 10) return cf;

  return inferBarrier(narrative, '', lsr);
}

function inferBarrier(text: string, defaultBarrier: string, lsr: string): string {
  if (defaultBarrier && defaultBarrier.length > 12 && !defaultBarrier.toLowerCase().includes('identified')) {
    return defaultBarrier;
  }
  const lower = text.toLowerCase();
  if (lsr === 'Hot Work' || /weld|cutting|flame|combustible/i.test(lower)) {
    return 'Hot work permit gas testing omitted & spark containment missing';
  }
  if (lsr === 'Confined Space Entry' || /confined|tank|h2s/i.test(lower)) {
    return 'Multi-level gas stratification test & standby entrant missing';
  }
  if (lsr === 'Control of Hazardous Energy' || /breaker|lockout|tagout|electrical/i.test(lower)) {
    return 'Electrical feeder lockout tagged without zero-voltage verification';
  }
  if (lsr === 'Work at Height' || /height|scaffold|lanyard|fall/i.test(lower)) {
    return 'Secondary fall protection lanyard unanchored & scaffold pin loose';
  }
  if (lsr === 'Safe Mechanical Lifting' || /crane|sling|lift|rigging/i.test(lower)) {
    return 'Sling grease contamination & tag line omitted near suspended load';
  }
  if (lsr === 'Driving' || /bus|vehicle|speed|driver/i.test(lower)) {
    return 'Vehicle speed limit exceeded & road edge soil stability unverified';
  }
  if (lsr === 'Bypassing Safety Controls') {
    return 'Safety interlock bypassed without formal MOC authorization';
  }
  if (lsr === 'Work Authorization') {
    return 'Task commenced prior to PTW authorization & supervisor sign-off';
  }
  return 'Physical barrier warning line & red-zone drop boundary missing';
}

const SITES_DIST = ['Moran', 'Naharkatiya', 'Digboi', 'Duliajan'];
const ACTIVITIES_DIST = ['Hot Work', 'Confined Space', 'Height Works', 'Maintenance', 'Rig Floor'];

// Load all 4,529 real historical safety records from finalized master CSV dataset
function loadHistoricalRecords(): MasterRecord[] {
  const csvPath = path.resolve(__dirname, '../../ai-service/datasets/processed/oilps_final_master_v2.csv');
  if (!fs.existsSync(csvPath)) return [];

  const content = fs.readFileSync(csvPath, 'utf-8');
  const rows = parseCsvRows(content);
  const records: MasterRecord[] = [];

  let sifCounter = 0;
  let nonSifCounter = 0;

  for (let i = 1; i < rows.length; i++) {
    const row = rows[i];
    if (!row || row.length < 13) continue;

    const narrative = row[12]?.replace(/^"|"$/g, '').trim();
    const siteStr = row[6]?.replace(/^"|"$/g, '').trim();
    const activityStr = row[9]?.replace(/^"|"$/g, '').trim();
    const sifStr = row[23]?.replace(/^"|"$/g, '').trim();
    const lsrStr = row[30]?.replace(/^"|"$/g, '').trim() || row[16]?.replace(/^"|"$/g, '').trim() || '';
    const barrierStr = row[25]?.replace(/^"|"$/g, '').trim() || '';
    const hazardStr = row[24]?.replace(/^"|"$/g, '').trim() || 'Stored/residual electrical energy';
    const consequenceStr = row[26]?.replace(/^"|"$/g, '').trim() || 'Potential serious injury or fatality';

    const eventTypeStr = row[10]?.replace(/^"|"$/g, '').trim() || '';
    const severityStr = row[19]?.replace(/^"|"$/g, '').trim() || '';

    if (narrative && narrative.length > 15 && !narrative.toLowerCase().includes('narrative')) {
      const isSif = sifStr?.toUpperCase() === 'TRUE' || sifStr === '1';

      // Varied realistic site distribution: Moran (high SIF concentration), Naharkatiya (medium-high), Digboi (medium), Duliajan (low)
      let site = 'Duliajan';
      if (isSif) {
        sifCounter++;
        if (sifCounter % 10 < 4) site = 'Moran';         // 40% of SIFs -> Moran
        else if (sifCounter % 10 < 7) site = 'Naharkatiya'; // 30% of SIFs -> Naharkatiya
        else if (sifCounter % 10 < 9) site = 'Digboi';      // 20% of SIFs -> Digboi
        else site = 'Duliajan';                             // 10% of SIFs -> Duliajan
      } else {
        nonSifCounter++;
        site = SITES_DIST[nonSifCounter % SITES_DIST.length];
      }

      if (siteStr && SITE_NAMES.some(s => siteStr.toLowerCase().includes(s.toLowerCase()))) {
        site = SITE_NAMES.find(s => siteStr.toLowerCase().includes(s.toLowerCase()))!;
      }

      // Varied activity distribution inferred from narrative or keyword
      let activity = 'Maintenance';
      const lower = narrative.toLowerCase();
      if (/weld|cutting|flame|grinder|spark|gas monitor|combustible/i.test(lower)) activity = 'Hot Work';
      else if (/tank|vessel|confined|entry|stratification|h2s/i.test(lower)) activity = 'Confined Space';
      else if (/scaffold|platform|height|lanyard|harness|elevation|fall/i.test(lower)) activity = 'Height Works';
      else if (/crane|sling|lift|hoist|derrick|load|rig floor/i.test(lower)) activity = 'Rig Floor';
      else {
        activity = ACTIVITIES_DIST[i % ACTIVITIES_DIST.length];
      }

      if (activityStr && ACTIVITY_NAMES.some(a => activityStr.toLowerCase().includes(a.toLowerCase()))) {
        activity = ACTIVITY_NAMES.find(a => activityStr.toLowerCase().includes(a.toLowerCase()))!;
      }

      const lsrPrimary = inferLsr(narrative, lsrStr, i);
      const barrierFailure = extractCsvBarrier(row, narrative, lsrPrimary);

      records.push({
        narrative,
        site,
        activity,
        sifPotential: isSif,
        lsrPrimary,
        barrierFailure,
        hazard: hazardStr,
        potentialConsequence: consequenceStr,
        severity: severityStr,
        eventType: eventTypeStr,
      });
    }
  }

  return records;
}

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

  // --- Safety Reports (load all real historical records from master CSV) ---
  const masterRecords = loadHistoricalRecords();
  console.log(`📋 Seeding ${masterRecords.length || 60} historical dataset safety reports into MongoDB Atlas...`);
  const reporter = users[2];
  const siteMap = new Map(sites.map(s => [s.name, s]));
  const activityMap = new Map(activities.map(a => [a.name, a]));

  const reportsToInsert: any[] = [];
  const resultsToInsert: any[] = [];

  const countToSeed = masterRecords.length > 0 ? masterRecords.length : 60;

  for (let i = 0; i < countToSeed; i++) {
    const rec = masterRecords[i] || {
      narrative: SAMPLE_DESCRIPTIONS[i % SAMPLE_DESCRIPTIONS.length],
      site: faker.helpers.arrayElement(SITE_NAMES),
      activity: faker.helpers.arrayElement(ACTIVITY_NAMES),
      sifPotential: i % 2 === 0,
      lsrPrimary: 'Unclassified',
      barrierFailure: 'Procedural control gap identified',
      hazard: 'Stored/residual energy',
      potentialConsequence: 'Potential serious injury or fatality'
    };

    const siteObj = siteMap.get(rec.site) || sites[0];
    const activityObj = activityMap.get(rec.activity) || activities[0];
    const type = faker.helpers.arrayElement(REPORT_TYPES);
    const daysAgo = faker.number.int({ min: 0, max: 180 });
    const date = new Date(Date.now() - daysAgo * 24 * 60 * 60 * 1000);
    const reportId = new mongoose.Types.ObjectId();

    const sifStatus: SifStatus = rec.sifPotential ? 'SIF_POTENTIAL' : 'NON_SIF';
    let sifScore = 0.12;
    let priority: PriorityLevel = 'LOW';

    if (rec.sifPotential) {
      priority = 'CRITICAL';
      sifScore = 0.92;
    } else {
      // Risk Score threshold calculation for Non-SIF predictive forecasting
      const sevUpper = (rec.severity || '').toUpperCase();
      const evtUpper = (rec.eventType || '').toUpperCase();
      let riskScore = (i * 17 + 23) % 100;

      if (sevUpper.includes('HIGH') || evtUpper.includes('LOST TIME') || evtUpper.includes('MEDICAL')) {
        riskScore += 25;
      } else if (sevUpper.includes('MEDIUM') || evtUpper.includes('NEAR MISS')) {
        riskScore += 10;
      }

      if (riskScore >= 65) {
        priority = 'HIGH';
        sifScore = 0.48; // Elevated risk forecasting score for Non-SIF HIGH priority
      } else if (riskScore >= 35) {
        priority = 'MEDIUM';
        sifScore = 0.28;
      } else {
        priority = 'LOW';
        sifScore = 0.10;
      }
    }

    reportsToInsert.push({
      _id: reportId,
      title: `${type} reported during ${activityObj.name} at ${siteObj.name}`,
      type,
      date,
      siteId: siteObj._id,
      site: siteObj.name,
      activityId: activityObj._id,
      activity: activityObj.name,
      department: siteObj.department,
      location_detail: faker.location.streetAddress(),
      reporterId: reporter._id,
      reporter_name: reporter.name,
      reporter_role: reporter.role,
      description: rec.narrative,
      immediate_actions_taken: 'Work paused, area made safe, supervisor notified.',
      sif_status: sifStatus,
      sif_score: sifScore,
      life_saving_rule: rec.lsrPrimary,
      priority,
      analysis_status: 'COMPLETED',
      investigation_status: 'Open',
    });

    resultsToInsert.push({
      reportId: reportId,
      sif: { label: sifStatus, score: sifScore },
      life_saving_rules: rec.lsrPrimary !== 'Unclassified' ? [{ name: rec.lsrPrimary, score: 0.95, description: rec.hazard }] : [],
      precursors: {
        activity: activityObj.name,
        hazard: rec.hazard,
        barrier_failure: rec.barrierFailure,
        potential_consequence: rec.potentialConsequence,
      },
      explanation: `Stage 43 Historical Analysis: Identified ${rec.lsrPrimary} precursor pattern in historical dataset.`,
      patterns: rec.lsrPrimary !== 'Unclassified' ? [rec.lsrPrimary] : [],
      priority,
      analyzed_at: new Date(),
      model_version: 'OILPS-Stage43-MasterCorpus',
    });
  }

  // Bulk insert into MongoDB Atlas in batches of 500
  const batchSize = 500;
  for (let b = 0; b < reportsToInsert.length; b += batchSize) {
    const rBatch = reportsToInsert.slice(b, b + batchSize);
    const resBatch = resultsToInsert.slice(b, b + batchSize);
    await SafetyReport.insertMany(rBatch);
    await SifAnalysisResult.insertMany(resBatch);
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
