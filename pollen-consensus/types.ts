/**
 * Pollen Consensus Type Definitions
 */

export interface HiveConfig {
  apiUrl: string;
  wsUrl: string;
  stakedMINE: number;
  autoAssign: boolean;
}

export interface HexCellData {
  id: string;
  userId: string;
  position: { x: number; y: number };
  votingPower: number;
  neighbors?: string[];
}

export interface Neighbor {
  id: string;
  userId: string;
  hexCellId: string;
  distance: number;
  lastPheromone?: PheromoneTrail | null;
}

export interface PheromoneTrail {
  id: string;
  hexCell: string;
  timestamp: Date;
  signature: string;
  data: {
    wellnessRange: string;
    activity: string;
    mood: string;
  };
}

export interface Vote {
  topic: string;
  proposal: string;
  choice: 'for' | 'against' | 'abstain';
  weight: number;  // Based on staked MINE
}

export interface ConsensusResult {
  topic: string;
  totalVotes: number;
  for: number;
  against: number;
  abstain: number;
  passed: boolean;
  executedAt?: Date;
}
