import { Request, Response } from 'express';
import { User } from '../models/User';
import { hashPassword, comparePassword } from '../utils/password';
import { signToken } from '../utils/jwt';
import { logAudit } from '../services/auditService';
import { RegisterInput, LoginInput } from '../validators/authValidator';

export async function register(req: Request<{}, {}, RegisterInput>, res: Response) {
  const { name, email, password, role, department, site } = req.body;

  const existing = await User.findOne({ email: email.toLowerCase() });
  if (existing) {
    return res.status(409).json({ message: 'A user with this email already exists' });
  }

  const passwordHash = await hashPassword(password);
  const user = await User.create({ name, email, passwordHash, role, department, site });

  const token = signToken({
    userId: (user._id as any).toString(),
    name: user.name,
    email: user.email,
    role: user.role,
  });

  res.status(201).json({ token, user: user.toJSON() });
}

export async function login(req: Request<{}, {}, LoginInput>, res: Response) {
  const { email, password } = req.body;

  const user = await User.findOne({ email: email.toLowerCase() });
  if (!user) {
    return res.status(401).json({ message: 'Invalid email or password' });
  }

  const valid = await comparePassword(password, user.passwordHash);
  if (!valid) {
    await logAudit({
      req,
      action: 'USER_LOGIN',
      entityType: 'AUTH',
      status: 'FAILURE',
      details: `Failed login attempt for ${email}`,
      userOverride: { userId: (user._id as any).toString(), name: user.name, role: user.role },
    });
    return res.status(401).json({ message: 'Invalid email or password' });
  }

  const token = signToken({
    userId: (user._id as any).toString(),
    name: user.name,
    email: user.email,
    role: user.role,
  });

  // req.user isn't set yet at this point (this route runs before `authenticate`),
  // so we pass identity explicitly via userOverride instead of relying on req.user.
  await logAudit({
    req,
    action: 'USER_LOGIN',
    entityType: 'AUTH',
    entityId: (user._id as any).toString(),
    details: `User ${user.name} (${user.role}) authenticated via email/password`,
    userOverride: { userId: (user._id as any).toString(), name: user.name, role: user.role },
  });

  res.json({ token, user: user.toJSON() });
}

export async function getMe(req: Request, res: Response) {
  if (!req.user) {
    return res.status(401).json({ message: 'Unauthenticated' });
  }
  const user = await User.findById(req.user.userId);
  if (!user) {
    return res.status(404).json({ message: 'User not found' });
  }
  res.json(user.toJSON());
}

export async function logout(req: Request, res: Response) {
  // JWTs are stateless here (no server-side session/blacklist), so logout is
  // primarily an audit event; the client discards the token.
  await logAudit({
    req,
    action: 'USER_LOGOUT',
    entityType: 'AUTH',
    entityId: req.user?.userId,
    details: `User ${req.user?.name || 'unknown'} logged out`,
  });
  res.json({ success: true });
}