"""
run_inference_demo.py - Interactive Demonstration of the Packaged OILPS AI Safety Intelligence Pipeline.

Accepts sample oilfield incident narratives and generates full structured SIF + LSR predictions.
"""

import sys
import json
from pathlib import Path

# Ensure ai-service is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.safety_pipeline import SafetyPipeline

SAMPLE_INCIDENTS = [
    {
        "title": "High-Pressure Hydrotest Manifold Bleed Failure",
        "narrative": "During hydrostatic testing of the 6-inch high pressure discharge line at 4,500 psi, an operator attempted to tighten a leaking fitting while the line remained pressurized. The bleeder plug ruptured and struck the worker in the chest."
    },
    {
        "title": "Crane Lifting Tubular Handling in Line of Fire",
        "narrative": "A crawler crane was lifting a 2-ton casing bundle across the rig floor when the nylon sling parted due to sharp edge contact. The casing bundle swung downward, striking the floor near the rotary table."
    },
    {
        "title": "Confined Space Vessel Entry with H2S Accumulation",
        "narrative": "An employee entered an enclosed crude oil storage separator without continuous gas monitoring or ventilation. Lethal levels of hydrogen sulfide (H2S) gas overcame the worker inside the vessel."
    },
    {
        "title": "Minor Slip on Ice in Maintenance Yard (Negative Control)",
        "narrative": "While walking across the paved maintenance yard after a shift change, an operator slipped on a patch of ice and bruised their knee. First aid applied; worker returned to full duty immediately."
    }
]

def run_demo():
    print("=" * 75)
    print("OILPS PRECURSOR SAFETY INTELLIGENCE — PRODUCTION INFERENCE DEMO")
    print("=" * 75)
    
    pipeline = SafetyPipeline()
    
    for idx, inc in enumerate(SAMPLE_INCIDENTS, start=1):
        print(f"\n[INCIDENT {idx}]: {inc['title']}")
        print("-" * 75)
        print(f"Narrative:\n\"{inc['narrative']}\"")
        
        result = pipeline.analyze_incident(inc["narrative"])
        sif = result["sif"]
        lsr = result["life_saving_rules"]
        
        print("\n--- SIF PRECURSOR ANALYSIS ---")
        print(f"  Risk Tier:         {result['risk_tier']}")
        print(f"  SIF Probability:   {sif['probability']*100:.2f}% (Threshold: {sif['threshold']:.2f})")
        print(f"  SIF Alert Label:   {'[ALERT] SIF POTENTIAL DETECTED (1)' if sif['label'] == 1 else '[OK] NON-SIF (0)'}")
        if sif["salient_tokens"]:
            token_str = ", ".join([f"{t['token']} ({t['weight']:.3f})" for t in sif["salient_tokens"]])
            print(f"  Salient Tokens:    {token_str}")
            
        print("\n--- IOGP LIFE-SAVING RULES (LSR) DETECTED ---")
        if lsr["predicted_rules"]:
            for r_name in lsr["predicted_rules"]:
                prob = lsr["probabilities"][r_name]
                thresh = lsr["thresholds"][r_name]
                print(f"  * [TRIGGERED] {r_name:<32} (Prob: {prob*100:.1f}%, Thresh: {thresh*100:.0f}%)")
        else:
            print("  * None (No Life-Saving Rules triggered)")
            
        print("=" * 75)

if __name__ == "__main__":
    run_demo()
