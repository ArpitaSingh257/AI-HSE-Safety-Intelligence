import { Request, Response, NextFunction } from 'express';

export function notFoundHandler(req: Request, res: Response) {
  res.status(404).json({ message: `Route not found: ${req.method} ${req.originalUrl}` });
}

// Must have 4 args (err, req, res, next) so Express recognizes it as an
// error-handling middleware, even though `next` is unused.
export function errorHandler(err: any, _req: Request, res: Response, _next: NextFunction) {
  console.error('Unhandled error:', err);

  if (err?.name === 'CastError') {
    return res.status(400).json({ message: `Invalid identifier: ${err.value}` });
  }
  if (err?.name === 'ValidationError') {
    return res.status(400).json({ message: 'Validation failed', errors: err.errors });
  }
  if (err?.code === 11000) {
    return res.status(409).json({ message: 'Duplicate value violates a unique constraint', keyValue: err.keyValue });
  }

  const status = err?.status || 500;
  res.status(status).json({ message: err?.message || 'Internal server error' });
}
