"""
test_recommendation_demo.py - Stage 15: Safety Recommendation Engine Interactive Demo.

Sends realistic scenarios to /api/v1/analyze and displays complete SIF, LSR, and actionable safety recommendations.
"""

import sys
import json
from pathlib import Path
from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.main import app

client = TestClient(app)

DEMO_SCENARIOS = [
    {
        "id": "DEMO-001",
        "title": "A. Hydrotest Pressurized Fitting Failure",
        "text": "During hydrostatic testing of the 6-inch high pressure discharge line at 4,500 psi, an operator attempted to tighten a leaking fitting while the line remained pressurized. The bleeder plug ruptured and struck the worker in the chest."
    },
    {
        "id": "DEMO-002",
        "title": "B. Crane Lifting / Sling Failure",
        "text": "A crawler crane was lifting a 2-ton casing bundle across the rig floor when the nylon sling parted due to sharp edge contact. The casing bundle swung downward, striking the floor near the rotary table."
    },
    {
        "id": "DEMO-003",
        "title": "C. Confined-Space H2S Incident",
        "text": "An employee entered an enclosed crude oil storage separator without continuous gas monitoring or ventilation. Lethal levels of hydrogen sulfide (H2S) gas overcame the worker inside the vessel."
    },
    {
        "id": "DEMO-004",
        "title": "D. Minor Slip on Ice in Yard (Negative Control)",
        "text": "While walking across the paved maintenance yard after a shift change, an operator slipped on a patch of ice and bruised their knee. First aid applied; worker returned to full duty immediately."
    }
]

def run_recommendation_demo():
    print("=" * 80)
    print("OILPS AI SAFETY RECOMMENDATION ENGINE — PRODUCTION DEMO")
    print("=" * 80)
    
    for item in DEMO_SCENARIOS:
        payload = {
            "incident_id": item["id"],
            "incident_text": item["text"]
        }
        resp = client.post("/api/v1/analyze", json=payload)
        assert resp.status_code == 200, f"Error: {resp.text}"
        data = resp.json()
        
        sif = data["sif"]
        lsr = data["lsr"]
        rec = data["recommendations"]
        
        print("\n" + "=" * 80)
        print(f"SCENARIO: {item['title']} (ID: {item['id']})")
        print(f"Narrative:\n\"{item['text']}\"")
        print("-" * 80)
        print("1. MODEL DETECTIONS:")
        print(f"   * SIF Potential:    {'[ALERT] SIF (1)' if sif['is_sif'] else '[OK] NON-SIF (0)'} (Probability: {sif['probability']*100:.2f}%)")
        print(f"   * Risk Tier:        {sif['risk_tier']}")
        print(f"   * Triggered LSRs:   {lsr['triggered_rules'] if lsr['triggered_rules'] else 'None'}")
        
        print("\n2. SAFETY RECOMMENDATIONS (Decision-Support Layer):")
        print(f"   * Priority Level:   [{rec['priority']}]")
        print(f"   * Summary:          {rec['summary']}")
        
        if rec["immediate_actions"]:
            print("   * Immediate Actions:")
            for act in rec["immediate_actions"]:
                print(f"       -> {act}")
                
        if rec["control_verification"]:
            print("   * Barrier / Control Verification:")
            for chk in rec["control_verification"]:
                print(f"       [ ] {chk}")
                
        if rec["escalation"]:
            print("   * Escalation Protocol:")
            for esc in rec["escalation"]:
                print(f"       [!] {esc}")
                
    print("\n" + "=" * 80)
    print("DEMONSTRATION COMPLETED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    run_recommendation_demo()
