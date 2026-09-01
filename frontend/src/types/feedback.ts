export interface FeedbackSubmission {
  report_id: string;
  field_name: string;
  ai_value: any;
  human_value: any;
  action: 'ACCEPT' | 'CORRECT' | 'REJECT' | 'NEEDS_REVIEW';
  comment?: string;
  reviewer_id?: string;
}

export interface FeedbackRecord {
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
  created_at: string;
  updated_at: string;
}

export interface FeedbackStats {
  total_feedback: number;
  accepted_count: number;
  corrected_count: number;
  rejected_count: number;
  accept_rate: number;
  correction_rate: number;
  reject_rate: number;
  field_breakdown?: Record<string, any>;
}
