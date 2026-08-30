"""
test_api_demo.py - Stage 14: Fast API Smoke Test & Contract Verification.

Runs simulated API requests against the production FastAPI app using FastAPI TestClient.
"""

import sys
import json
from pathlib import Path
from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.main import app

client = TestClient(app)

TEST_PAYLOADS = [
    {
        "id": "API-TEST-001",
        "title": "Hydrotest Pressure Fitting Failure",
        "text": "During hydrostatic testing of the 6-inch high pressure discharge line at 4,500 psi, an operator attempted to tighten a leaking fitting while the line remained pressurized. The bleeder plug ruptured and struck the worker in the chest."
    },
    {
        "id": "API-TEST-002",
        "title": "Crane Lifting Tubular Handling",
        "text": "A crawler crane was lifting a 2-ton casing bundle across the rig floor when the nylon sling parted due to sharp edge contact. The casing bundle swung downward, striking the floor near the rotary table."
    },
    {
        "id": "API-TEST-003",
        "title": "Confined Space Vessel Entry with H2S",
        "text": "An employee entered an enclosed crude oil storage separator without continuous gas monitoring or ventilation. Lethal levels of hydrogen sulfide (H2S) gas overcame the worker inside the vessel."
    },
    {
        "id": "API-TEST-004",
        "title": "Minor Slip on Ice in Maintenance Yard (Negative Control)",
        "text": "While walking across the paved maintenance yard after a shift change, an operator slipped on a patch of ice and bruised their knee. First aid applied; worker returned to full duty immediately."
    }
]

def run_smoke_test():
    print("=" * 80)
    print("OILPS AI INFERENCE API — STAGE 14 INTEGRATION SMOKE TEST")
    print("=" * 80)
    
    # 1. Health Check
    health_resp = client.get("/health")
    assert health_resp.status_code == 200, f"Health check failed: {health_resp.text}"
    health_data = health_resp.json()
    print("\n[GET /health]:")
    print(f"  Status:              {health_data['status']}")
    print(f"  SIF Champion Loaded: {health_data['sif_champion_loaded']}")
    print(f"  LSR Champion Loaded: {health_data['lsr_champion_loaded']}")
    print(f"  API Version:         {health_data['version']}")
    
    # 2. Analyze Endpoints
    print("\n[POST /api/v1/analyze]:")
    for item in TEST_PAYLOADS:
        payload = {
            "incident_id": item["id"],
            "incident_text": item["text"]
        }
        resp = client.post("/api/v1/analyze", json=payload)
        assert resp.status_code == 200, f"Inference request failed: {resp.text}"
        data = resp.json()
        
        sif = data["sif"]
        lsr = data["lsr"]
        
        print("\n" + "-" * 80)
        print(f"Incident ID: {data['incident_id']} | {item['title']}")
        print(f"Text: \"{data['incident_text'][:90]}...\"")
        print(f"SIF Potential:    {'[ALERT] SIF (1)' if sif['is_sif'] else '[OK] NON-SIF (0)'} | Probability: {sif['probability']*100:.2f}% | Risk Tier: {sif['risk_tier']}")
        if sif["salient_tokens"]:
            print(f"Salient Tokens:   " + ", ".join([f"{t['token']} ({t['weight']:.3f})" for t in sif["salient_tokens"]]))
        print(f"Triggered LSRs:   {lsr['triggered_rules'] if lsr['triggered_rules'] else 'None'}")
        print("Per-Rule Breakdown:")
        for r in lsr["rule_predictions"]:
            if r["probability"] > 0.08 or r["triggered"]:
                print(f"  - {r['rule']:<32}: {r['probability']*100:5.1f}% (Thresh: {r['threshold']*100:.0f}%) -> {'[TRIGGERED]' if r['triggered'] else '[OFF]'}")
                
    print("\n" + "=" * 80)
    print("ALL API SMOKE TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    run_smoke_test()
