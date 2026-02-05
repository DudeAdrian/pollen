/**
 * Biometric Analyzer — Pillar 1: Underground Knowledge
 * 
 * Processes incoming biometric data from Heartware/wearables
 * Stores encrypted history, calculates baselines
 */

import type { BiometricData, UserProfile } from '../types';

export class BiometricAnalyzer {
  private userId: string;
  private history: BiometricData[] = [];
  private baseline: UserProfile['baseline'] | null = null;

  constructor(userId: string) {
    this.userId = userId;
  }

  /**
   * Process new biometric reading
   * Pillar 1: Underground Knowledge — accumulating personal health data
   */
  async processReading(data: BiometricData): Promise<void> {
    // Encrypt and store
    await this.storeEncrypted(data);
    
    // Add to history
    this.history.push(data);
    
    // Update baseline if needed
    if (this.history.length % 30 === 0) {
      await this.recalculateBaseline();
    }
  }

  /**
   * Get current wellness score
   * Composite metric from all biometrics
   */
  getWellnessScore(): number {
    if (this.history.length === 0) return 50;
    
    const latest = this.history[this.history.length - 1];
    const baseline = this.baseline;
    
    if (!baseline) return 50;

    // HRV score (higher is better)
    const hrvScore = Math.min(100, (latest.hrv.rmssd / baseline.hrv) * 50);
    
    // Sleep score
    const sleepScore = (latest.sleep.quality / baseline.sleep) * 50;
    
    // Mood score
    const moodScore = (latest.mood / baseline.mood) * 50;
    
    return Math.round((hrvScore + sleepScore + moodScore) / 3);
  }

  /**
   * Detect anomalies from baseline
   * Pillar 3: Reverse Engineering — pattern detection
   */
  detectAnomalies(): string[] {
    if (!this.baseline || this.history.length < 7) {
      return [];
    }

    const anomalies: string[] = [];
    const recent = this.history.slice(-7);
    const avgHrv = recent.reduce((sum, d) => sum + d.hrv.rmssd, 0) / 7;

    if (avgHrv < this.baseline.hrv * 0.8) {
      anomalies.push('HRV significantly below baseline');
    }

    const avgSleep = recent.reduce((sum, d) => sum + d.sleep.quality, 0) / 7;
    if (avgSleep < this.baseline.sleep * 0.7) {
      anomalies.push('Sleep quality degraded');
    }

    return anomalies;
  }

  private async storeEncrypted(data: BiometricData): Promise<void> {
    // Would encrypt and store to PostgreSQL
    console.log(`[P1-Biometrics] Storing reading for ${this.userId}`);
  }

  private async recalculateBaseline(): Promise<void> {
    if (this.history.length < 30) return;

    const recent = this.history.slice(-30);
    
    this.baseline = {
      hrv: recent.reduce((sum, d) => sum + d.hrv.rmssd, 0) / 30,
      sleep: recent.reduce((sum, d) => sum + d.sleep.quality, 0) / 30,
      mood: recent.reduce((sum, d) => sum + d.mood, 0) / 30
    };

    console.log(`[P1-Biometrics] Baseline recalculated for ${this.userId}`);
  }
}
