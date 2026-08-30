import mongoose, { Schema, Document } from 'mongoose';
import { ActivityName, ACTIVITY_NAMES } from '../types';

export interface IActivity extends Document {
  name: ActivityName;
  description?: string;
}

const ActivitySchema = new Schema<IActivity>(
  {
    name: { type: String, enum: ACTIVITY_NAMES, required: true, unique: true },
    description: { type: String },
  },
  { timestamps: true }
);

ActivitySchema.set('toJSON', {
  transform: (_doc, ret: any) => {
    ret.id = ret._id.toString();
    delete ret._id;
    delete ret.__v;
    return ret;
  },
});

export const Activity = mongoose.model<IActivity>('Activity', ActivitySchema);