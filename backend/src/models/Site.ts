import mongoose, { Schema, Document } from 'mongoose';
import { SiteName, SITE_NAMES } from '../types';

export interface ISite extends Document {
  name: SiteName;
  locationDetail?: string;
  department: string;
}

const SiteSchema = new Schema<ISite>(
  {
    name: { type: String, enum: SITE_NAMES, required: true, unique: true },
    locationDetail: { type: String },
    department: { type: String, required: true },
  },
  { timestamps: true }
);

SiteSchema.set('toJSON', {
  transform: (_doc, ret: any) => {
    ret.id = ret._id.toString();
    delete ret._id;
    delete ret.__v;
    return ret;
  },
});

export const Site = mongoose.model<ISite>('Site', SiteSchema);