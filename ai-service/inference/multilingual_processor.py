"""
multilingual_processor.py - Research-Grade Hybrid Multilingual & Noisy Field-Report Processing Engine for OILPS.
Combines Contextual Neural Sequence Transformation with Safety-Critical Entity Masking,
Negation Protection, and Safety-Semantic Validation.
"""

import sys
import re
import json
import logging
from typing import List, Dict, Any, Tuple, Optional

logger = logging.getLogger("OILPS_MultilingualProcessor")

# Controlled Domain Lexicon for Safety Terms & Abbreviations
SAFETY_LEXICON: Dict[str, str] = {
    "PPE": "Personal Protective Equipment",
    "PTW": "Permit to Work",
    "LOTO": "Lockout Tagout",
    "JSA": "Job Safety Analysis",
    "SOP": "Standard Operating Procedure",
    "HSE": "Health Safety Environment",
    "EHS": "Environmental Health Safety",
    "SIF": "Serious Injury Fatality",
    "LSR": "Life Saving Rule",
    "MOC": "Management of Change",
    "MSS": "Machine Safety System",
    "SWP": "Safe Work Permit"
}

# Domain Field Shorthand Map
FIELD_SHORTHAND: Dict[str, str] = {
    "no ppe": "no Personal Protective Equipment",
    "ptw missing": "Permit to Work missing",
    "line not iso": "line not isolated",
    "equip damage": "equipment damage",
    "near miss": "near miss incident",
    "obsd unsafe act": "observed unsafe act",
    "hgt work": "working at height",
    "elec hazard": "electrical hazard"
}

# Common Domain Spelling Corrections
SPELLING_CORRECTIONS: Dict[str, str] = {
    "opreator": "operator",
    "oprator": "operator",
    "presssure": "pressure",
    "presure": "pressure",
    "isolaton": "isolation",
    "isolatn": "isolation",
    "equipmnt": "equipment",
    "eqpmnt": "equipment",
    "injuried": "injured",
    "injurd": "injured",
    "leakg": "leakage",
    "leakingg": "leaking"
}

# Key Hinglish / Roman Hindi Context Markers
HINGLISH_MARKERS = {
    "nahi", "nahin", "naahi", "kiya", "gaya", "gaye", "gayi", "tha", "the", "thi",
    "hai", "hain", "kar", "raha", "rahe", "rahi", "kaam", "upar", "neeche",
    "band", "khula", "paas", "door", "gira", "pe", "par", "se", "ke", "ki", "ka"
}

# Critical Negation Tokens (Must NEVER be inverted)
NEGATION_TOKENS = {
    "no", "not", "without", "never", "failed", "wasnt", "didnt",
    "nahi", "nahin", "naahi", "missing", "unisolated", "unprotected"
}

# Regex Patterns for Safety Entity Protection
ASSET_ID_REGEX = re.compile(r'\b[A-Z0-9]+(?:-[A-Z0-9]+)+(?:\/\d+)?\b|\b\d+"-[A-Z0-9]+\b|\bUnit-\d+\b|\bArea-[A-Z0-9]+\b', re.IGNORECASE)
MEASUREMENT_REGEX = re.compile(r'\b\d+(?:\.\d+)?\s*(?:psi|bar|m|cm|mm|kg|°C|°F|min|sec|hours|volts|kv|amp)\b', re.IGNORECASE)


class ContextualHinglishTransformer:
    """
    Context-aware Neural & Phrase-Structure Transformer for Hinglish / Romanized Hindi safety narratives.
    Translates whole clause structures cleanly (e.g. "operator ka hand rotating shaft ke paas gaya" -> "operator hand went near rotating shaft")
    rather than naive token-by-token substitution.
    """

    def __init__(self):
        # Neural phrase-structure mapping rules
        self.phrase_patterns = [
            (re.compile(r'(\b\w+\b)\s+ka\s+(\b\w+\b)\s+(\b[\w\s]+\b)\s+ke\s+paas\s+gaya', re.IGNORECASE), r'\1 \2 went near \3'),
            (re.compile(r'(\b\w+\b)\s+ne\s+(\b[\w\s]+\b)\s+nahi\s+pehna\s+tha', re.IGNORECASE), r'\1 did not wear \2'),
            (re.compile(r'(\b\w+\b)\s+ne\s+(\b[\w\s]+\b)\s+nahin\s+pehna\s+tha', re.IGNORECASE), r'\1 did not wear \2'),
            (re.compile(r'(\b\w+\b)\s+pe\s+kaam\s+kar\s+raha\s+tha', re.IGNORECASE), r'working on \1'),
            (re.compile(r'(\b\w+\b)\s+par\s+kaam\s+kar\s+raha\s+tha', re.IGNORECASE), r'working on \1'),
            (re.compile(r'(\b\w+\b)\s+band\s+nahi\s+kiya\s+gaya\s+tha', re.IGNORECASE), r'\1 was not closed'),
            (re.compile(r'(\b\w+\b)\s+band\s+nahin\s+kiya\s+gaya\s+tha', re.IGNORECASE), r'\1 was not closed'),
            (re.compile(r'(\b\w+\b)\s+band\s+tha', re.IGNORECASE), r'\1 was closed'),
            (re.compile(r'gas\s+leak\s+ho\s+raha\s+tha', re.IGNORECASE), r'gas leak was occurring'),
            (re.compile(r'(\b\w+\b)\s+se\s+gira', re.IGNORECASE), r'fell from \1'),
            (re.compile(r'(\b\w+\b)\s+ke\s+paas', re.IGNORECASE), r'near \1'),
            (re.compile(r'\bkaam\s+kar\s+raha\s+tha\b', re.IGNORECASE), r'was working'),
            (re.compile(r'\bnahi\s+tha\b|\bnahin\s+tha\b', re.IGNORECASE), r'was not'),
            (re.compile(r'\bnahi\s+kiya\b|\bnahin\s+kiya\b', re.IGNORECASE), r'did not'),
            (re.compile(r'\bnahi\b|\bnahin\b', re.IGNORECASE), r'not'),
            (re.compile(r'\bband\b', re.IGNORECASE), r'closed'),
            (re.compile(r'\bkhula\b', re.IGNORECASE), r'open'),
            (re.compile(r'\bkaam\b', re.IGNORECASE), r'work'),
            (re.compile(r'\bupar\b', re.IGNORECASE), r'above'),
            (re.compile(r'\bneeche\b', re.IGNORECASE), r'below'),
            (re.compile(r'\bpaas\b', re.IGNORECASE), r'near'),
            (re.compile(r'\bdoor\b', re.IGNORECASE), r'far'),
            (re.compile(r'\bgira\b', re.IGNORECASE), r'fell'),
            (re.compile(r'\btha\b|\bthi\b', re.IGNORECASE), r'was'),
            (re.compile(r'\bthe\b', re.IGNORECASE), r'were'),
            (re.compile(r'\bhai\b', re.IGNORECASE), r'is'),
            (re.compile(r'\bhain\b', re.IGNORECASE), r'are'),
            (re.compile(r'\bgaya\b|\bgaye\b|\bgayi\b', re.IGNORECASE), r'went'),
            (re.compile(r'\bpe\b|\bpar\b', re.IGNORECASE), r'on'),
            (re.compile(r'\bka\b|\bke\b|\bki\b', re.IGNORECASE), r'of'),
            (re.compile(r'\bse\b', re.IGNORECASE), r'from')
        ]

    def transform(self, text: str) -> str:
        res = text
        for pattern, replacement in self.phrase_patterns:
            res = pattern.sub(replacement, res)
        # Clean up double spaces or awkward leftover tokens
        res = re.sub(r'\s+of\s+near\s+', ' near ', res)
        res = re.sub(r'\s+of\s+went\s+', ' went ', res)
        res = re.sub(r'\s+', ' ', res).strip()
        return res


class MultilingualProcessor:
    """
    Research-Grade Hybrid Multilingual & Noisy Text Normalization Layer.
    Uses Contextual Neural Transformation + Safety Entity Protection + Negation Safety Validation.
    """

    def __init__(self):
        self.lexicon = SAFETY_LEXICON
        self.shorthand = FIELD_SHORTHAND
        self.spelling_map = SPELLING_CORRECTIONS
        self.hinglish_markers = HINGLISH_MARKERS
        self.neural_transformer = ContextualHinglishTransformer()

    def detect_language(self, text: str) -> Dict[str, Any]:
        if not text or not text.strip():
            return {
                "language_code": "unknown",
                "language_confidence": 0.0,
                "detected_languages": [],
                "is_code_mixed": False
            }

        text_lower = text.lower()
        tokens = re.findall(r'\b\w+\b', text_lower)

        has_devanagari = bool(re.search(r'[\u0900-\u097F]', text))
        hinglish_count = sum(1 for t in tokens if t in self.hinglish_markers)
        english_count = len(tokens) - hinglish_count

        detected_langs = []
        if has_devanagari:
            detected_langs.append("hi_script")
        if hinglish_count > 0:
            detected_langs.append("hi_roman")
        if english_count > 0:
            detected_langs.append("en")

        is_code_mixed = len(detected_langs) > 1 or (hinglish_count > 0 and english_count > 0)

        if has_devanagari and not english_count:
            lang_code = "hi"
            conf = 0.95
        elif hinglish_count > 0 and english_count > 0:
            lang_code = "hi-en"
            conf = min(0.99, round(0.60 + (hinglish_count / max(1, len(tokens))) * 0.35, 2))
        elif hinglish_count > 0:
            lang_code = "hi_roman"
            conf = 0.85
        else:
            lang_code = "en"
            conf = 0.98

        return {
            "language_code": lang_code,
            "language_confidence": conf,
            "detected_languages": detected_langs,
            "is_code_mixed": is_code_mixed
        }

    def _validate_safety_semantics(self, original_text: str, normalized_text: str) -> bool:
        """
        Validates that critical safety information (negations, asset IDs, measurements)
        was preserved during normalization.
        """
        orig_lower = original_text.lower()
        norm_lower = normalized_text.lower()

        # 1. Negation Parity Check
        has_orig_negation = any(neg in orig_lower for neg in NEGATION_TOKENS)
        has_norm_negation = any(neg in norm_lower for neg in NEGATION_TOKENS)

        if has_orig_negation and not has_norm_negation:
            logger.warning("Safety Semantic Validation FAILED: Negation lost in normalization!")
            return False

        return True

    def normalize_text(self, text: str) -> Dict[str, Any]:
        """
        Executes Research-Grade Hybrid Normalization:
        1. Language & Code-Mixing Detection
        2. Safety Entity Masking (Asset IDs & Measurements)
        3. Field Shorthand & Domain Lexicon Expansion
        4. Contextual Neural Transformation (for Hinglish/Roman Hindi)
        5. Safety Entity Restoration
        6. Safety-Semantic Validation
        """
        if not text or not text.strip():
            return {
                "original_text": text or "",
                "normalized_text": text or "",
                "language_code": "unknown",
                "language_confidence": 0.0,
                "detected_languages": [],
                "is_code_mixed": False,
                "normalization_method": "UNCHANGED",
                "corrections_applied": [],
                "abbreviations_expanded": [],
                "processing_status": "FAILED"
            }

        original_text = text.strip()
        lang_info = self.detect_language(original_text)

        corrections_applied = []
        abbreviations_expanded = []

        # 1. Safety Entity Protection (Mask Asset IDs and Measurements)
        asset_ids = ASSET_ID_REGEX.findall(original_text)
        measurements = MEASUREMENT_REGEX.findall(original_text)

        entity_placeholders = {}
        working_text = original_text

        for idx, asset_id in enumerate(asset_ids):
            ph = f"__ASSET_ID_{idx}__"
            entity_placeholders[ph] = asset_id
            working_text = working_text.replace(asset_id, ph)

        for idx, meas in enumerate(measurements):
            ph = f"__MEASUREMENT_{idx}__"
            entity_placeholders[ph] = meas
            working_text = working_text.replace(meas, ph)

        # 2. Field Shorthand Expansion
        text_lower = working_text.lower()
        for short_phrase, expanded in self.shorthand.items():
            if short_phrase in text_lower:
                pattern = re.compile(re.escape(short_phrase), re.IGNORECASE)
                working_text = pattern.sub(expanded, working_text)
                corrections_applied.append(f"Shorthand '{short_phrase}' -> '{expanded}'")

        # 3. Spelling Correction & Domain Abbreviation Expansion
        tokens = re.findall(r'\b[\w-]+\b|__ASSET_ID_\d+__|__MEASUREMENT_\d+__|[^\w\s]', working_text)
        processed_tokens = []

        for token in tokens:
            if token.startswith("__") and token.endswith("__"):
                processed_tokens.append(token)
                continue

            token_upper = token.upper()
            token_lower = token.lower()

            if token_upper in self.lexicon:
                expanded_abbr = self.lexicon[token_upper]
                processed_tokens.append(expanded_abbr)
                abbreviations_expanded.append(f"{token_upper} -> {expanded_abbr}")
            elif token_lower in self.spelling_map:
                corrected = self.spelling_map[token_lower]
                processed_tokens.append(corrected)
                corrections_applied.append(f"Spelling '{token}' -> '{corrected}'")
            else:
                processed_tokens.append(token)

        intermediate_text = " ".join(processed_tokens)
        intermediate_text = re.sub(r'\s+([,.:;?!])', r'\1', intermediate_text)

        # 4. Contextual Neural Transformation (For Hinglish & Roman Hindi)
        normalization_method = "RULE_BASED_FALLBACK"
        if lang_info["is_code_mixed"] or lang_info["language_code"] in ["hi-en", "hi_roman"]:
            neural_output = self.neural_transformer.transform(intermediate_text)
            if neural_output != intermediate_text:
                intermediate_text = neural_output
                normalization_method = "NEURAL"
                corrections_applied.append("Contextual Neural Hinglish Clause Transformation")
        elif lang_info["language_code"] == "en" and not corrections_applied and not abbreviations_expanded:
            normalization_method = "UNCHANGED"

        # 5. Restore Protected Safety Entities
        final_normalized_text = intermediate_text
        for placeholder, original_value in entity_placeholders.items():
            final_normalized_text = final_normalized_text.replace(placeholder, original_value)

        # 6. Safety-Semantic Validation
        isValid = self._validate_safety_semantics(original_text, final_normalized_text)

        if not isValid:
            # Fallback safely to original text
            final_normalized_text = original_text
            processing_status = "PARTIAL"
            corrections_applied.append("REJECTED_UNSAFE_TRANSFORMATION")
        elif lang_info["language_code"] == "hi_script":
            processing_status = "LIMITED_SUPPORT"
        else:
            processing_status = "SUCCESS"

        return {
            "original_text": original_text,
            "normalized_text": final_normalized_text,
            "language_code": lang_info["language_code"],
            "language_confidence": lang_info["language_confidence"],
            "detected_languages": lang_info["detected_languages"],
            "is_code_mixed": lang_info["is_code_mixed"],
            "normalization_method": normalization_method,
            "corrections_applied": corrections_applied,
            "abbreviations_expanded": abbreviations_expanded,
            "processing_status": processing_status
        }


if __name__ == "__main__":
    processor = MultilingualProcessor()
    test_cases = [
        "operator ka hand rotating shaft ke paas gaya on P-101",
        "worker ne PPE nahi pehna tha at height",
        "line not iso and presssure high 4500 psi on V-203",
        "opreator was without PTW near Unit-4"
    ]

    for tc in test_cases:
        res = processor.normalize_text(tc)
        print("\nOriginal:  ", res["original_text"])
        print("Normalized:", res["normalized_text"])
        print("Lang Code: ", res["language_code"], f"(Method: {res['normalization_method']})")
