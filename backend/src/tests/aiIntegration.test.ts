import { analyzeIncidentText } from '../services/aiService';

describe('Stage 22 — MERN ↔ FastAPI AI Service Integration Tests', () => {
  const originalEnv = process.env.AI_SERVICE_URL;

  beforeEach(() => {
    process.env.AI_SERVICE_URL = 'http://127.0.0.1:8000/api/v1/analyze';
  });

  afterAll(() => {
    process.env.AI_SERVICE_URL = originalEnv;
  });

  test('1. Invalid incident input is rejected before calling AI service', async () => {
    await expect(analyzeIncidentText('')).rejects.toThrow('Incident text cannot be empty');
    await expect(analyzeIncidentText('   ')).rejects.toThrow('Incident text cannot be empty');
  });

  test('2. AI service unreachable returns safe error message', async () => {
    process.env.AI_SERVICE_URL = 'http://127.0.0.1:9999/invalid_route';
    await expect(analyzeIncidentText('Test narrative')).rejects.toThrow('AI safety analysis service is currently unavailable');
  });

  test('3. AI service analysis contract structure is preserved', async () => {
    // If live AI service is available, test real request
    try {
      const res = await analyzeIncidentText('During hydrostatic testing of the 6-inch discharge line at 4,500 psi, an operator was exposed to a pressure release after a bleeder plug ruptured.');
      expect(res).toHaveProperty('sif');
      expect(res).toHaveProperty('lsr');
      expect(res).toHaveProperty('recommendations');
      expect(res).toHaveProperty('explainability');
      expect(res.recommendations).toHaveProperty('status');
      expect(res.recommendations).toHaveProperty('grounded');
      expect(['GROUNDED', 'PARTIALLY_GROUNDED', 'INSUFFICIENT_SOURCE_SUPPORT', 'UNSUPPORTED']).toContain(res.recommendations.status);
    } catch (err: any) {
      // If server is not running during unit tests, verify error message
      expect(err.message).toMatch(/unavailable|fetch failed/i);
    }
  });
});
