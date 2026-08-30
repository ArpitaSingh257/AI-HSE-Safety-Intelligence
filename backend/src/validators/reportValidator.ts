import { z } from 'zod';
import { REPORT_TYPES, PRIORITY_LEVELS } from '../types';

// NOTE: `site` and `activity` are validated as free-text here (not the strict
// backend enum) because the frontend's CreateReportPayload sends rich display
// strings (e.g. "Duliajan Central Complex"). The controller normalizes these
// down to the canonical Site/Activity enum values before saving - see
// src/controllers/reportsController.ts -> normalizeSiteName/normalizeActivityName.
export const createReportSchema = z.object({
  title: z.string().min(3, 'Title must be at least 3 characters').max(300),
  type: z.enum(REPORT_TYPES as [string, ...string[]]),
  date: z.string().datetime().or(z.string().min(1)).optional(),
  site: z.string().min(1, 'Site is required'),
  department: z.string().min(1, 'Department is required'),
  location_detail: z.string().optional(),
  activity: z.string().min(1, 'Activity is required'),
  reporter_name: z.string().min(1, 'Reporter name is required'),
  description: z.string().min(10, 'Description must be at least 10 characters').max(5000),
  immediate_actions_taken: z.string().max(5000).optional(),
  priority: z.enum(PRIORITY_LEVELS as [string, ...string[]]).optional(),
});

export const updateReportSchema = z.object({
  title: z.string().min(3).max(300).optional(),
  description: z.string().min(10).max(5000).optional(),
  immediate_actions_taken: z.string().max(5000).optional(),
  location_detail: z.string().optional(),
  priority: z.enum(PRIORITY_LEVELS as [string, ...string[]]).optional(),
  investigation_status: z
    .enum(['Open', 'Under Review', 'Intervention Scheduled', 'Closed'])
    .optional(),
});

export type CreateReportInput = z.infer<typeof createReportSchema>;
export type UpdateReportInput = z.infer<typeof updateReportSchema>;
