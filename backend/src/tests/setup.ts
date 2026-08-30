// Referenced by jest.config.js -> setupFilesAfterEnv. Kept intentionally
// minimal: just ensures a JWT_SECRET is present for tests that sign/verify
// tokens, without requiring a real .env file to exist in CI.
process.env.JWT_SECRET = process.env.JWT_SECRET || 'test_secret_for_jest';
process.env.NODE_ENV = 'test';
