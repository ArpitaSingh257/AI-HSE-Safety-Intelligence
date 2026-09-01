import mongoose, { Schema, Document } from 'mongoose';

export interface IFeedback extends Document {
  feedback_id: string;
  report_id: string;
  field_name: string;
  ai_value: any;
  human_value: any;
  action: 'ACCEPT' | 'CORRECT' | 'REJECT' | 'NEEDS_REVIEW';
  comment: string;
  reviewer_id: string;
  review_timestamp: string;
  model_version: string;
  pipeline_version: string;
  schema_version: string;
  status: 'SUBMITTED' | 'REVIEWED' | 'ACCEPTED_FOR_EVALUATION';
  revision: number;
  created_at: Date;
  updated_at: Date;
}

const FeedbackSchema: Schema = new Schema(
  {
    feedback_id: { type: String, required: true, unique: true, index: true },
    report_id: { type: String, required: true, index: true },
    field_name: { type: String, required: true, index: true },
    ai_value: { type: Schema.Types.Mixed, required: true },
    human_value: { type: Schema.Types.Mixed, required: true },
    action: {
      type: String,
      enum: ['ACCEPT', 'CORRECT', 'REJECT', 'NEEDS_REVIEW'],
      required: true,
      index: true
    },
    comment: { type: String, default: '' },
    reviewer_id: { type: String, required: true, index: true },
    review_timestamp: { type: String, required: true },
    model_version: { type: String, default: 'OILPS_v2.0.0' },
    pipeline_version: { type: String, default: '2.0.0' },
    schema_version: { type: String, default: '1.0.0' },
    status: {
      type: String,
      enum: ['SUBMITTED', 'REVIEWED', 'ACCEPTED_FOR_EVALUATION'],
      default: 'SUBMITTED',
      index: true
    },
    revision: { type: Number, default: 1 }
  },
  { timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' } }
);

export const FeedbackModel = mongoose.model<IFeedback>('Feedback', FeedbackSchema);
