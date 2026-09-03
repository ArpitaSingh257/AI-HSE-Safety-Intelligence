export interface TextNormalizeRequest {
  text: string;
}

export interface MultilingualNormalizationResult {
  original_text: string;
  normalized_text: string;
  language_code: string;
  language_confidence: number;
  detected_languages: string[];
  is_code_mixed: boolean;
  normalization_method: 'NEURAL' | 'RULE_BASED_FALLBACK' | 'UNCHANGED';
  corrections_applied: string[];
  abbreviations_expanded: string[];
  processing_status: 'SUCCESS' | 'PARTIAL' | 'LIMITED_SUPPORT' | 'FAILED';
}
