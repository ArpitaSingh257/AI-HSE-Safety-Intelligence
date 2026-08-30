import mongoose, { Schema, Document, Types } from 'mongoose';
import { PriorityLevel, PRIORITY_LEVELS } from '../types';

export interface ILifeSavingRuleScore {
  name: string;
  score: number;
  description?: string;
}

export interface IPrecursors {
  activity: string;
  hazard: string;
  barrier_failure: string;
  potential_consequence: string;
}

export interface ISifAnalysisResult extends Document {
  reportId: Types.ObjectId;
  sif: { label: string; score: number };
  life_saving_rules: ILifeSavingRuleScore[];
  precursors: IPrecursors;
  explanation: string;
  patterns: string[];
  priority: PriorityLevel;
  analyzed_at?: Date | null;
  model_version?: string | null;
}

const LifeSavingRuleScoreSchema = new Schema<ILifeSavingRuleScore>(
  {
    name: { type: String, required: true },
    score: { type: Number, required: true },
    description: { type: String },
  },
  { _id: false }
);

const PrecursorsSchema = new Schema<IPrecursors>(
  {
    activity: { type: String, required: true },
    hazard: { type: String, required: true },
    barrier_failure: { type: String, required: true },
    potential_consequence: { type: String, required: true },
  },
  { _id: false }
);

const SifAnalysisResultSchema = new Schema<ISifAnalysisResult>(
  {
    reportId: { type: Schema.Types.ObjectId, ref: 'SafetyReport', required: true, unique: true, index: true },
    sif: {
      label: { type: String, required: true },
      score: { type: Number, required: true },
    },
    life_saving_rules: { type: [LifeSavingRuleScoreSchema], default: [] },
    precursors: { type: PrecursorsSchema, required: true },
    explanation: { type: String, required: true },
    patterns: { type: [String], default: [] },
    priority: { type: String, enum: PRIORITY_LEVELS, required: true },
    analyzed_at: { type: Date, default: null },
    model_version: { type: String, default: null },
  },
  { timestamps: true }
);

SifAnalysisResultSchema.set('toJSON', {
  transform: (_doc, ret: any) => {
    ret.report_id = ret.reportId?.toString();
    delete ret._id;
    delete ret.__v;
    delete ret.reportId;
    delete ret.createdAt;
    delete ret.updatedAt;
    return ret;
  },
});

export const SifAnalysisResult = mongoose.model<ISifAnalysisResult>('SifAnalysisResult', SifAnalysisResultSchema);