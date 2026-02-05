/**
 * Pollen Consensus — Hive Integration (Pillar 4)
 * 
 * Connects to SandIronRatio hexagonal matrix
 * Participates in swarm consensus, voting, pheromone trails
 */

export { HiveClient } from './hive/client';
export { HexCell } from './hive/hexcell';
export { PheromoneTrail } from './hive/pheromone';
export type { HiveConfig, Vote, Neighbor } from './types';
