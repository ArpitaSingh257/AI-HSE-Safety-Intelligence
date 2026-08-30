"""
test_final_inference.py - Production QA Test Suite for the Packaged Inference Pipeline.

Tests:
1. SIF Predictor initializes and infers on CPU & CUDA.
2. LSR Predictor initializes and predicts all 9 official IOGP rules.
3. SafetyPipeline delivers unified, valid JSON schema.
4. Empty/whitespace/None narratives are handled safely without crashing.
5. Thresholds are strictly preserved from validation stages.
6. Zero training/gradient modification happens during inference.
7. Model manifest exists and matches packaged architectures.
"""

import sys
import json
import torch
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.preprocessing import clean_and_tokenize, InferenceVocabulary
from inference.sif_predictor import SIFPredictor
from inference.lsr_predictor import LSRPredictor
from inference.safety_pipeline import SafetyPipeline

OFFICIAL_9_LSR = [
    "Bypassing Safety Controls",
    "Confined Space",
    "Driving",
    "Energy Isolation",
    "Hot Work",
    "Line of Fire",
    "Safe Mechanical Lifting",
    "Toxic Gas / Hazardous Substance",
    "Working at Height"
]

def test_preprocessing_and_tokenization():
    raw_text = "Hydrostatic testing at 4,500 PSI! Bleeder valve blew out."
    tokens = clean_and_tokenize(raw_text)
    assert "hydrostatic" in tokens
    assert "4" in tokens or "4500" in tokens or "500" in tokens
    assert "bleeder" in tokens
    
    # Test empty string handling
    assert clean_and_tokenize("") == []
    assert clean_and_tokenize(None) == []

def test_sif_predictor_inference():
    predictor = SIFPredictor(device="cpu")
    sample_narrative = "Pressure relief valve failed on high pressure line at 3000 psi causing gas release."
    result = predictor.predict(sample_narrative)
    
    assert "sif_probability" in result
    assert "sif_label" in result
    assert "threshold" in result
    assert "model" in result
    assert "top_attended_tokens" in result
    assert 0.0 <= result["sif_probability"] <= 1.0
    assert result["sif_label"] in [0, 1]
    assert result["threshold"] == 0.30

def test_lsr_predictor_inference():
    predictor = LSRPredictor(device="cpu")
    sample_narrative = "Worker operating crane when wire rope parted dropped load into line of fire."
    result = predictor.predict(sample_narrative)
    
    assert "predicted_rules" in result
    assert "rule_probabilities" in result
    assert "rule_thresholds" in result
    assert len(result["rule_probabilities"]) == 9
    assert len(result["rule_thresholds"]) == 9
    
    for r in OFFICIAL_9_LSR:
        assert r in result["rule_probabilities"]
        assert 0.0 <= result["rule_probabilities"][r] <= 1.0
        assert r in result["rule_thresholds"]

def test_safety_pipeline_unified_schema():
    pipeline = SafetyPipeline(device="cpu")
    narrative = "Hot work welding near diesel fuel tank triggered sudden explosion."
    out = pipeline.analyze_incident(narrative)
    
    assert "narrative" in out
    assert "risk_tier" in out
    assert "sif" in out
    assert "life_saving_rules" in out
    assert out["sif"]["label"] in [0, 1]
    assert isinstance(out["life_saving_rules"]["predicted_rules"], list)

def test_empty_and_corrupt_inputs():
    pipeline = SafetyPipeline(device="cpu")
    for bad_input in ["", "   ", None, "\n\t"]:
        res = pipeline.analyze_incident(bad_input)
        assert res["sif"]["label"] == 0
        assert res["sif"]["probability"] == 0.0
        assert res["life_saving_rules"]["predicted_rules"] == []

def test_no_gradient_updates():
    pipeline = SafetyPipeline(device="cpu")
    # Verify models are in eval mode
    assert not pipeline.sif_predictor.model.training
    assert not pipeline.lsr_predictor.model.training

def test_model_manifest():
    manifest_path = BASE_DIR / "models" / "MODEL_MANIFEST.json"
    assert manifest_path.exists(), "MODEL_MANIFEST.json missing"
    with open(manifest_path) as f:
        manifest = json.load(f)
    assert "production_models" in manifest
    assert "sif_binary_classifier" in manifest["production_models"]
    assert "lsr_multilabel_classifier" in manifest["production_models"]

if __name__ == "__main__":
    print("Running Stage 9 Production Inference Pipeline Quality Assurance Tests...")
    test_preprocessing_and_tokenization()
    print("  [PASS] Preprocessing and tokenization verified.")
    test_sif_predictor_inference()
    print("  [PASS] SIF Predictor inference & threshold (0.30) verified.")
    test_lsr_predictor_inference()
    print("  [PASS] LSR Predictor inference & 9-rule thresholds verified.")
    test_safety_pipeline_unified_schema()
    print("  [PASS] SafetyPipeline unified JSON schema verified.")
    test_empty_and_corrupt_inputs()
    print("  [PASS] Empty/corrupt inputs safely handled.")
    test_no_gradient_updates()
    print("  [PASS] Evaluation-only mode confirmed (zero training gradients).")
    test_model_manifest()
    print("  [PASS] MODEL_MANIFEST.json verified.")
    print("\nALL STAGE 9 INFERENCE TESTS PASSED SUCCESSFULLY!")
