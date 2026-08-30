import { z } from 'zod';
import {
  INTERVENTION_CATEGORIES,
  INTERVENTION_TRIGGER_SOURCES,
  PRIORITY_LEVELS,
  INTERVENTION_STATUSES,
  EFFECTIVENESS_RATINGS,
} from '../types';

export const createInterventionSchema = z.object({
  title: z.string().min(3, 'Title must be at least 3 characters').max(300),
  category: z.enum(INTERVENTION_CATEGORIES as [string, ...string[]]),
  description: z.string().min(5).max(3000),
  triggerSource: z.enum(INTERVENTION_TRIGGER_SOURCES as [string, ...string[]]),
  targetSite: z.string().min(1),
  targetActivity: z.string().min(1),
  associatedRule: z.string().min(1),
  priority: z.enum(PRIORITY_LEVELS as [string, ...string[]]),
  status: z.enum(INTERVENTION_STATUSES as [string, ...string[]]).default('OPEN'),
  assignedOfficer: z.string().min(1),
  assignedOfficerRole: z.string().min(1),
  dueDate: z.string().min(1, 'Due date is required'),
  relatedReportIds: z.array(z.string()).default([]),
  patternId: z.string().nullable().optional(),
  actionsTaken: z.array(z.string()).default([]),
  verificationNotes: z.string().optional(),
  effectivenessRating: z.enum(EFFECTIVENESS_RATINGS as [string, ...string[]]).nullable().optional(),
});

export const updateInterventionSchema = z.object({
  title: z.string().min(3).max(300).optional(),
  description: z.string().min(5).max(3000).optional(),
  status: z.enum(INTERVENTION_STATUSES as [string, ...string[]]).optional(),
  priority: z.enum(PRIORITY_LEVELS as [string, ...string[]]).optional(),
  assignedOfficer: z.string().optional(),
  assignedOfficerRole: z.string().optional(),
  dueDate: z.string().optional(),
  completionDate: z.string().nullable().optional(),
  actionsTaken: z.array(z.string()).optional(),
  verificationNotes: z.string().optional(),
  effectivenessRating: z.enum(EFFECTIVENESS_RATINGS as [string, ...string[]]).nullable().optional(),
});

export type CreateInterventionInput = z.infer<typeof createInterventionSchema>;
export type UpdateInterventionInput = z.infer<typeof updateInterventionSchema>;
