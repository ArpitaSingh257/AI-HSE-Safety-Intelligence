/** @type {import('ts-jest').JestConfigWithTsJest} */
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  testMatch: ['**/src/tests/**/*.test.ts'],
  testTimeout: 30000,
  setupFilesAfterEnv: ['<rootDir>/src/tests/setup.ts'],
};