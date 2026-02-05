/**
 * Pollen Bridge — Ecosystem Integration
 * 
 * Connects to all aligned repositories:
 * - Terracare-Ledger (Layer 1)
 * - sofie-systems (Layer 2)
 * - sofie-backend (API Layer)
 * - sandironratio-node (Layer 3)
 * - Heartware (Layer 3)
 * - Harmonic-Balance (Layer 3)
 */

export { TerracareBridge } from './adapters/terracare';
export { SofieSystemsBridge } from './adapters/sofie-systems';
export { SofieBackendBridge } from './adapters/sofie-backend';
export { SandIronRatioBridge } from './adapters/sandironratio';
export { HeartwareBridge } from './adapters/heartware';
export { HarmonicBalanceBridge } from './adapters/harmonic-balance';
