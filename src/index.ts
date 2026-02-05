/**
 * Pollen — Personal AI Agent
 * 
 * Seven Pillar Architecture Implementation
 * One codebase, infinite instances
 * 
 * Flower → Pollen → Hive → Honey → Hum
 */

import { BiometricAnalyzer } from '../pollen-core/biometrics/analyzer';
import { PredictionEngine } from '../pollen-core/prediction/engine';
import { FrequencyTherapy } from '../pollen-core/therapy/frequency';
import { HiveClient } from '../pollen-consensus/hive/client';
import { TokenEconomics } from '../pollen-economics/tokens/economics';

export interface PollenConfig {
  userId: string;
  terracareRpc: string;
  sofieSystemsUrl: string;
  sofieBackendUrl: string;
  sandIronRatioUrl: string;
  heartwareUrl: string;
  harmonicBalanceUrl: string;
}

export class Pollen {
  public userId: string;
  
  // Core (Pillars 1-3)
  public biometrics: BiometricAnalyzer;
  public predictions: PredictionEngine;
  public therapy: FrequencyTherapy;
  
  // Consensus (Pillar 4)
  public hive: HiveClient | null = null;
  
  // Economics (Pillar 7)
  public economics: TokenEconomics;
  
  constructor(config: PollenConfig) {
    this.userId = config.userId;
    
    // Initialize core components
    this.biometrics = new BiometricAnalyzer(config.userId);
    this.predictions = new PredictionEngine(config.userId);
    this.therapy = new FrequencyTherapy(config.userId);
    this.economics = new TokenEconomics(config.userId);
    
    console.log(`[Pollen] Instance spawned for ${config.userId}`);
  }

  /**
   * Activate hive connection (Pillar 4)
   */
  async activateHive(config: {
    wsUrl: string;
    stakedMINE: number;
  }): Promise<void> {
    this.hive = new HiveClient(this.userId, {
      apiUrl: '',
      wsUrl: config.wsUrl,
      stakedMINE: config.stakedMINE,
      autoAssign: true
    });
    
    await this.hive.activate();
    console.log(`[Pollen] Hive activated`);
  }

  /**
   * Listen to the Hum (Sofie connection)
   */
  async listenToHum(wsUrl: string): Promise<void> {
    console.log(`[Pollen] Listening to Hum at ${wsUrl}`);
  }

  /**
   * Get wellness forecast
   */
  async getForecast(): Promise<{
    score: number;
    forecast: number[];
    recommendation: string;
  }> {
    const forecast = await this.predictions.forecast([]);
    
    return {
      score: this.biometrics.getWellnessScore(),
      forecast: forecast.forecast,
      recommendation: forecast.recommendation
    };
  }

  /**
   * Start therapy session
   */
  async startTherapy(type: 'relaxation' | 'focus' | 'recovery' | 'sleep'): Promise<{
    frequency: number;
    duration: number;
  }> {
    const profile = this.therapy.generateProfile(type, 40);
    
    // Earn MINE for therapy (P7)
    await this.economics.earnMINE({
      type: 'therapy_completion',
      valuePoints: 20
    });

    return {
      frequency: profile.fundamental,
      duration: profile.duration
    };
  }

  /**
   * Get token balance
   */
  getBalance(): {
    mine: string;
    well: string;
    staked: string;
  } {
    const balance = this.economics.getBalance();
    return {
      mine: balance.mine,
      well: balance.well,
      staked: balance.staked
    };
  }
}

// Export factory function
export async function spawnInstance(config: PollenConfig): Promise<Pollen> {
  const pollen = new Pollen(config);
  return pollen;
}

export default Pollen;
