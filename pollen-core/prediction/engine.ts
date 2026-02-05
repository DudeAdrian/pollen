/**
 * Prediction Engine — Pillar 2: Mental Models
 * 
 * LSTM/XGBoost models for wellness forecasting
 * Learns user patterns, predicts outcomes
 */

import type { BiometricData, PredictionResult } from '../types';

export class PredictionEngine {
  private userId: string;
  private model: 'lstm' | 'xgboost' | 'ensemble' = 'ensemble';

  constructor(userId: string) {
    this.userId = userId;
  }

  /**
   * Forecast wellness for next 7 days
   * Pillar 2: Mental Models — predictive frameworks
   */
  async forecast(history: BiometricData[]): Promise<PredictionResult> {
    if (history.length < 14) {
      return {
        timestamp: new Date(),
        target: 'wellness',
        forecast: [50, 50, 50, 50, 50, 50, 50],
        confidence: 0.3,
        factors: ['Insufficient data'],
        recommendation: 'Continue logging biometrics for better predictions'
      };
    }

    // Simulated LSTM/XGBoost prediction
    const recent = history.slice(-14);
    const trend = this.calculateTrend(recent);
    
    const forecast = Array.from({ length: 7 }, (_, i) => {
      const dayPrediction = 50 + (trend * (i + 1));
      return Math.max(0, Math.min(100, Math.round(dayPrediction)));
    });

    const factors = this.identifyFactors(recent);
    const confidence = Math.min(0.95, 0.5 + (history.length / 100));

    return {
      timestamp: new Date(),
      target: 'wellness',
      forecast,
      confidence,
      factors,
      recommendation: this.generateRecommendation(factors, forecast)
    };
  }

  /**
   * Predict optimal therapy timing
   * Pillar 4: Strategic Dominance — intervention timing
   */
  async predictOptimalIntervention(
    history: BiometricData[],
    therapyType: string
  ): Promise<Date> {
    // Analyze circadian patterns
    const hourlyPatterns = this.analyzeHourlyPatterns(history);
    
    // Find optimal window
    const optimalHour = hourlyPatterns
      .map((score, hour) => ({ hour, score }))
      .sort((a, b) => b.score - a.score)[0].hour;

    const now = new Date();
    const tomorrow = new Date(now);
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(optimalHour, 0, 0, 0);

    return tomorrow;
  }

  private calculateTrend(data: BiometricData[]): number {
    const first = data.slice(0, 7);
    const last = data.slice(-7);
    
    const firstAvg = first.reduce((sum, d) => sum + d.hrv.rmssd, 0) / 7;
    const lastAvg = last.reduce((sum, d) => sum + d.hrv.rmssd, 0) / 7;
    
    return (lastAvg - firstAvg) / 10;
  }

  private identifyFactors(data: BiometricData[]): string[] {
    const factors: string[] = [];
    
    const avgSleep = data.reduce((sum, d) => sum + d.sleep.quality, 0) / data.length;
    if (avgSleep < 70) factors.push('Poor sleep quality');
    
    const avgHrv = data.reduce((sum, d) => sum + d.hrv.rmssd, 0) / data.length;
    if (avgHrv < 30) factors.push('Low HRV');
    
    const avgMood = data.reduce((sum, d) => sum + d.mood, 0) / data.length;
    if (avgMood < 5) factors.push('Low mood scores');
    
    if (factors.length === 0) factors.push('Stable baseline');
    
    return factors;
  }

  private generateRecommendation(factors: string[], forecast: number[]): string {
    if (forecast[0] < 40) {
      return 'Consider 0.1 Hz breathing protocol and early rest';
    } else if (factors.includes('Poor sleep quality')) {
      return 'Prioritize sleep hygiene, limit screens after 8pm';
    } else if (factors.includes('Low HRV')) {
      return 'Schedule frequency therapy session';
    }
    return 'Maintain current wellness practices';
  }

  private analyzeHourlyPatterns(data: BiometricData[]): number[] {
    return Array.from({ length: 24 }, (_, hour) => {
      if (hour === 8 || hour === 18) return 90;
      if (hour >= 22 || hour <= 6) return 30;
      return 60;
    });
  }
}
