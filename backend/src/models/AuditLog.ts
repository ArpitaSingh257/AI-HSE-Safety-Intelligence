import mongoose, { Schema, Document } from 'mongoose';
import { AuditActionType, AuditEntityType, AuditStatus } from '../types';

export interface IAuditLog extends Document {
  timestamp: Date;
  userId: string;
  userName: string;
  userRole: string;
  action: AuditActionType;
  entityType: AuditEntityType;
  entityId?: string;
  ipAddress: string;
  status: AuditStatus;
  details: string;
  changesSummary?: { before?: string; after?: string };
}

const AuditLogSchema = new Schema<IAuditLog>(
  {
    timestamp: { type: Date, required: true, default: Date.now },
    userId: { type: String, required: true },
    userName: { type: String, required: true },
    userRole: { type: String, required: true },
    action: { type: String, required: true },
    entityType: { type: String, required: true },
    entityId: { type: String },
    ipAddress: { type: String, required: true },
    status: { type: String, enum: ['SUCCESS', 'WARNING', 'FAILURE'], required: true, default: 'SUCCESS' },
    details: { type: String, required: true },
    changesSummary: {
      before: { type: String },
      after: { type: String },
    },
  },
  { timestamps: false } // we track our own `timestamp` field explicitly
);

AuditLogSchema.index({ timestamp: -1 });
AuditLogSchema.index({ userId: 1 });
AuditLogSchema.index({ action: 1 });

AuditLogSchema.set('toJSON', {
  transform: (_doc, ret: any) => {
    ret.id = ret._id.toString();
    delete ret._id;
    delete ret.__v;
    return ret;
  },
});

export const AuditLog = mongoose.model<IAuditLog>('AuditLog', AuditLogSchema);