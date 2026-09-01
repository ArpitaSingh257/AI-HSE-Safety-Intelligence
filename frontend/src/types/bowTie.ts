export interface BowTieNode {
  id: string;
  type: 'HAZARD' | 'THREAT' | 'FAILED_BARRIER' | 'PREVENTIVE_BARRIER' | 'MITIGATING_BARRIER' | 'TOP_EVENT' | 'CONSEQUENCE';
  label: string;
  provenance: 'OBSERVED' | 'INFERRED' | 'UNKNOWN';
  canonical_barrier?: string;
  barrier_role?: 'PREVENTIVE' | 'MITIGATING';
  raw_evidence?: string;
}

export interface BowTieEdge {
  source: string;
  target: string;
  provenance: 'OBSERVED' | 'INFERRED' | 'UNKNOWN';
}

export interface BowTieProfile {
  bow_tie_id: string;
  report_id: string;
  hazards: string[];
  threats: string[];
  failed_barriers: string[];
  preventive_barriers: string[];
  mitigating_barriers: string[];
  top_events: string[];
  consequences: string[];
  nodes: BowTieNode[];
  edges: BowTieEdge[];
  sif_information: {
    sif_potential: boolean;
    sif_probability: number;
  };
  lsr_information: {
    primary_life_saving_rule: string;
  };
  pattern_ids: string[];
  barrier_pattern_ids: string[];
  evidence: Record<string, any>;
  provenance: string;
  mapping_confidence: 'HIGH' | 'MEDIUM' | 'LOW';
}
