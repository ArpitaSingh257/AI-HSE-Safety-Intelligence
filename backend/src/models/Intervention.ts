import mongoose, { Schema, Document } from 'mongoose';
import {
  InterventionCategory, INTERVENTION_CATEGORIES,
  InterventionTriggerSource, INTERVENTION_TRIGGER_SOURCES,
  PriorityLevel, PRIORITY_LEVELS,
  InterventionStatus, INTERVENTION_STATUSES,
  EffectivenessRating, EFFECTIVENESS_RATINGS,
} from '../types';

export interface IIntervention extends Document {
  title: string;
  category: InterventionCategory;
  description: string;
  triggerSource: InterventionTriggerSource;
  targetSite: string;
  targetActivity: string;
  associatedRule: string;
  priority: PriorityLevel;
  status: InterventionStatus;
  assignedOfficer: string;
  assignedOfficerRole: string;
  dueDate: Date;
  createdDate: Date;
  completionDate?: Date | null;
  relatedReportIds: string[];
  patternId?: string | null;
  actionsTaken?: string[];
  verificationNotes?: string;
  effectivenessRating?: EffectivenessRating | null;
}

const InterventionSchema = new Schema<IIntervention>(
  {
    title: { type: String, required: true },
    category: { type: String, enum: INTERVENTION_CATEGORIES, required: true },
    description: { type: String, required: true },
    triggerSource: { type: String, enum: INTERVENTION_TRIGGER_SOURCES, required: true },
    targetSite: { type: String, required: true },
    targetActivity: { type: String, required: true },
    associatedRule: { type: String, required: true },
    priority: { type: String, enum: PRIORITY_LEVELS, required: true },
    status: { type: String, enum: INTERVENTION_STATUSES, required: true, default: 'OPEN' },
    assignedOfficer: { type: String, required: true },
    assignedOfficerRole: { type: String, required: true },
    dueDate: { type: Date, required: true },
    createdDate: { type: Date, required: true, default: Date.now },
    completionDate: { type: Date, default: null },
    relatedReportIds: { type: [String], default: [] },
    patternId: { type: String, default: null },
    actionsTaken: { type: [String], default: [] },
    verificationNotes: { type: String },
    effectivenessRating: { type: String, enum: EFFECTIVENESS_RATINGS, default: null },
  },
  { timestamps: true }
);

InterventionSchema.set('toJSON', {
  transform: (_doc, ret: any) => {
    ret.id = ret._id.toString();
    delete ret._id;
    delete ret.__v;
    delete ret.createdAt;
    delete ret.updatedAt;
    return ret;
  },
});

export const Intervention = mongoose.model<IIntervention>('Intervention', InterventionSchema);