import { Request, Response, NextFunction, RequestHandler } from 'express';

/**
 * Express 4 does not automatically forward rejected promises from async
 * route handlers to the error middleware. Wrap every async
 * controller/middleware function with this so thrown errors (bad ObjectId,
 * DB errors, etc.) are caught and handled centrally instead of crashing
 * the process or hanging the request.
 */
export function asyncHandler(fn: (req: Request, res: Response, next: NextFunction) => Promise<any>): RequestHandler {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
}
