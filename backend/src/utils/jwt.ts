import jwt from 'jsonwebtoken';
import { JwtPayload } from '../types';

const JWT_SECRET: string = process.env.JWT_SECRET || 'dev_only_insecure_default_secret';

export function signToken(payload: JwtPayload, expiresIn: string = '1d'): string {
  return jwt.sign(payload, JWT_SECRET, { expiresIn } as jwt.SignOptions);
}

export function verifyToken(token: string): JwtPayload {
  return jwt.verify(token, JWT_SECRET) as JwtPayload;
}