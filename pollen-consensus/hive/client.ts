/**
 * Hive Client — Pillar 4: Strategic Dominance
 * 
 * Connects to SandIronRatio hexagonal matrix
 * Manages hexcell registration, voting, neighbor connections
 */

import { HexCell } from './hexcell';
import type { HiveConfig, Vote, Neighbor } from '../types';

export class HiveClient {
  private userId: string;
  private config: HiveConfig;
  private hexCell: HexCell | null = null;
  private neighbors: Neighbor[] = [];
  private ws: WebSocket | null = null;

  constructor(userId: string, config: HiveConfig) {
    this.userId = userId;
    this.config = config;
  }

  /**
   * Activate hive connection
   * Register in hexagonal matrix
   */
  async activate(): Promise<HexCell> {
    console.log(`[P4-Hive] Activating hive connection for ${this.userId}`);

    // Connect to SandIronRatio WebSocket
    this.ws = new WebSocket(this.config.wsUrl);
    
    // Register hexcell
    this.hexCell = new HexCell({
      userId: this.userId,
      position: await this.claimPosition(),
      votingPower: this.config.stakedMINE
    });

    // Discover six neighbors
    this.neighbors = await this.discoverNeighbors();

    console.log(`[P4-Hive] Activated at position (${this.hexCell.position.x}, ${this.hexCell.position.y})`);
    console.log(`[P4-Hive] Connected to ${this.neighbors.length} neighbors`);

    return this.hexCell;
  }

  /**
   * Submit vote to queen consensus
   * Participate in swarm decisions
   */
  async submitVote(vote: Vote): Promise<void> {
    if (!this.hexCell) {
      throw new Error('Hive not activated');
    }

    console.log(`[P4-Hive] Submitting vote: ${vote.topic}`);

    // Send to SandIronRatio consensus
    this.ws?.send(JSON.stringify({
      type: 'VOTE',
      userId: this.userId,
      hexCell: this.hexCell.id,
      vote
    }));
  }

  /**
   * Share pheromone trail
   * Anonymized biometric state marker
   */
  async sharePheromone(state: {
    wellnessScore: number;
    activityLevel: string;
    moodTrend: string;
  }): Promise<void> {
    // Hash for anonymity
    const pheromone = {
      id: this.hashState(state),
      hexCell: this.hexCell?.id,
      timestamp: new Date(),
      signature: 'anonymous', // Real implementation would use ZK proofs
      data: {
        wellnessRange: this.rangeBucket(state.wellnessScore),
        activity: state.activityLevel,
        mood: state.moodTrend
      }
    };

    this.ws?.send(JSON.stringify({
      type: 'PHEROMONE',
      pheromone
    }));
  }

  /**
   * Pathfind to similar users
   * Data flows along hex edges
   */
  async pathfindSimilar(targetPattern: string): Promise<Neighbor[]> {
    // Find neighbors with similar patterns
    return this.neighbors.filter(n => 
      n.lastPheromone?.data.wellnessRange === targetPattern
    );
  }

  private async claimPosition(): Promise<{ x: number; y: number }> {
    // Request position from SandIronRatio
    // Simplified: return random hex coordinates
    return {
      x: Math.floor(Math.random() * 100),
      y: Math.floor(Math.random() * 100)
    };
  }

  private async discoverNeighbors(): Promise<Neighbor[]> {
    // SandIronRatio assigns 6 neighbors based on similarity
    return Array.from({ length: 6 }, (_, i) => ({
      id: `neighbor-${i}`,
      userId: `0x${i}`,
      hexCellId: `hex-${i}`,
      distance: Math.random() * 10,
      lastPheromone: null
    }));
  }

  private hashState(state: unknown): string {
    // Simplified hash
    return Buffer.from(JSON.stringify(state)).toString('base64').slice(0, 16);
  }

  private rangeBucket(score: number): string {
    if (score >= 80) return 'high';
    if (score >= 50) return 'medium';
    return 'low';
  }
}
