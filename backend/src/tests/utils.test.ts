import { signToken, verifyToken } from '../utils/jwt';
import { hashPassword, comparePassword } from '../utils/password';

describe('jwt utils', () => {
  it('signs and verifies a token round-trip', () => {
    const payload = { userId: '123', name: 'Test User', email: 't@example.com', role: 'Admin' as const };
    const token = signToken(payload, '1h');
    const decoded = verifyToken(token);
    expect(decoded.userId).toBe(payload.userId);
    expect(decoded.email).toBe(payload.email);
  });
});

describe('password utils', () => {
  it('hashes a password and verifies it correctly', async () => {
    const hash = await hashPassword('Password@123');
    expect(await comparePassword('Password@123', hash)).toBe(true);
    expect(await comparePassword('WrongPassword', hash)).toBe(false);
  });
});
