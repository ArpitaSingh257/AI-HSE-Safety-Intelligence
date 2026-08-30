import mongoose, { Schema, Document } from 'mongoose';
import { UserRole, USER_ROLES } from '../types';

export interface IUser extends Document {
  name: string;
  email: string;
  passwordHash: string;
  role: UserRole;
  department: string;
  site?: string;
  avatar?: string;
  createdAt: Date;
  updatedAt: Date;
}

const UserSchema = new Schema<IUser>(
  {
    name: { type: String, required: true, trim: true },
    email: { type: String, required: true, unique: true, lowercase: true, trim: true },
    passwordHash: { type: String, required: true },
    role: { type: String, enum: USER_ROLES, required: true, default: 'Viewer' },
    department: { type: String, required: true },
    site: { type: String },
    avatar: { type: String },
  },
  { timestamps: true }
);

// Never expose passwordHash in API responses.
UserSchema.set('toJSON', {
  transform: (_doc, ret: any) => {
    ret.id = ret._id.toString();
    delete ret._id;
    delete ret.__v;
    delete ret.passwordHash;
    return ret;
  },
});

export const User = mongoose.model<IUser>('User', UserSchema);