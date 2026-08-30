import mongoose, { Schema, Document } from 'mongoose';
import { PriorityLevel, PRIORITY_LEVELS, TrendStatus, TREND_STATUSES } from '../types';

export interface IPattern extends Document {
  name: string;
  description: string;
  reportCount: number;
  mainActivity: string;
  mostAffectedSite: string;
  sifPotentialRate: number;
  priority: PriorityLevel;
  primaryLifeSavingRule: string;
  keyHazards: string[];
  commonBarrierFailures: string[];
  firstDetected: Date;
  lastOccurrence: Date;
  trendStatus: TrendStatus;
  recommendedIntervention: string;
  matchedReportIds: string[];
}

const PatternSchema = new Schema<IPattern>(
  {
    name: { type: String, required: true },
    description: { type: String, required: true },
    reportCount: { type: Number, required: true, default: 0 },
    mainActivity: { type: String, required: true },
    mostAffectedSite: { type: String, required: true },
    sifPotentialRate: { type: Number, required: true, default: 0 },
    priority: { type: String, enum: PRIORITY_LEVELS, required: true },
    primaryLifeSavingRule: { type: String, required: true },
    keyHazards: { type: [String], default: [] },
    commonBarrierFailures: { type: [String], default: [] },
    firstDetected: { type: Date, required: true },
    lastOccurrence: { type: Date, required: true },
    trendStatus: { type: String, enum: TREND_STATUSES, required: true, default: 'STABLE' },
    recommendedIntervention: { type: String, required: true },
    matchedReportIds: { type: [String], default: [] },
  },
  { timestamps: true }
);

PatternSchema.set('toJSON', {
  transform: (_doc, ret: any) => {
    ret.id = ret._id.toString();
    delete ret._id;
    delete ret.__v;
    delete ret.createdAt;
    delete ret.updatedAt;
    return ret;
  },
});

export const Pattern = mongoose.model<IPattern>('Pattern', PatternSchema);