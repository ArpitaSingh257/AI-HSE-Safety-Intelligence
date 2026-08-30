import mongoose, { Schema, Document, Types } from 'mongoose';
import {
  ReportType, REPORT_TYPES,
  SifStatus, SIF_STATUSES,
  PriorityLevel, PRIORITY_LEVELS,
  AnalysisStatus, ANALYSIS_STATUSES,
  InvestigationStatus, INVESTIGATION_STATUSES,
} from '../types';

// Design note: we keep normalized refs (siteId/activityId/reporterId) for
// data integrity, but ALSO cache the flat display strings (site/activity/
// reporter_name) on the document itself at write time. This means the API
// response never needs a populate() step to match the frontend's flat
// SafetyReportResponse contract, and aggregations (dashboard, patterns)
// can run directly against these cached string fields without joins.

export interface ISafetyReport extends Document {
  title: string;
  type: ReportType;
  date: Date;

  siteId: Types.ObjectId;
  site: string; // cached display string

  activityId: Types.ObjectId;
  activity: string; // cached display string

  department: string;
  location_detail?: string;

  reporterId: Types.ObjectId;
  reporter_name: string; // cached display string
  reporter_role?: string;

  description: string;
  immediate_actions_taken?: string;

  sif_status: SifStatus;
  sif_score: number;
  life_saving_rule: string;
  priority: PriorityLevel;
  analysis_status: AnalysisStatus;
  investigation_status?: InvestigationStatus;

  createdAt: Date;
  updatedAt: Date;
}

const SafetyReportSchema = new Schema<ISafetyReport>(
  {
    title: { type: String, required: true, trim: true },
    type: { type: String, enum: REPORT_TYPES, required: true },
    date: { type: Date, required: true, default: Date.now },

    siteId: { type: Schema.Types.ObjectId, ref: 'Site', required: true },
    site: { type: String, required: true },

    activityId: { type: Schema.Types.ObjectId, ref: 'Activity', required: true },
    activity: { type: String, required: true },

    department: { type: String, required: true },
    location_detail: { type: String },

    reporterId: { type: Schema.Types.ObjectId, ref: 'User', required: true },
    reporter_name: { type: String, required: true },
    reporter_role: { type: String },

    description: { type: String, required: true, maxlength: 5000 },
    immediate_actions_taken: { type: String, maxlength: 5000 },

    sif_status: { type: String, enum: SIF_STATUSES, required: true, default: 'PENDING_ANALYSIS' },
    sif_score: { type: Number, required: true, default: 0, min: 0, max: 1 },
    life_saving_rule: { type: String, default: '' },
    priority: { type: String, enum: PRIORITY_LEVELS, required: true, default: 'LOW' },
    analysis_status: { type: String, enum: ANALYSIS_STATUSES, required: true, default: 'PENDING' },
    investigation_status: { type: String, enum: INVESTIGATION_STATUSES, default: 'Open' },
  },
  { timestamps: true }
);

SafetyReportSchema.index({ site: 1 });
SafetyReportSchema.index({ activity: 1 });
SafetyReportSchema.index({ sif_status: 1 });
SafetyReportSchema.index({ priority: 1 });
SafetyReportSchema.index({ date: -1 });
SafetyReportSchema.index({ title: 'text', description: 'text' });

SafetyReportSchema.set('toJSON', {
  transform: (_doc, ret: any) => {
    ret.id = ret._id.toString();
    ret.created_at = ret.createdAt;
    ret.updated_at = ret.updatedAt;
    delete ret._id;
    delete ret.__v;
    delete ret.createdAt;
    delete ret.updatedAt;
    delete ret.siteId;
    delete ret.activityId;
    delete ret.reporterId;
    return ret;
  },
});

export const SafetyReport = mongoose.model<ISafetyReport>('SafetyReport', SafetyReportSchema);