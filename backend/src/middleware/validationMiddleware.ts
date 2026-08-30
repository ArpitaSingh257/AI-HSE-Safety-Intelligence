import { Request, Response, NextFunction } from 'express';
import { ZodSchema } from 'zod';

/**
 * Validates req.body against the given Zod schema.
 * On success, replaces req.body with the parsed (typed, defaulted) value.
 * On failure, responds 400 with a field-level error map.
 */
export function validateBody(schema: ZodSchema<any>) {
  return (req: Request, res: Response, next: NextFunction) => {
    const result = schema.safeParse(req.body);
    if (!result.success) {
      return res.status(400).json({ message: 'Validation failed', errors: result.error.flatten() });
    }
    req.body = result.data;
    next();
  };
}