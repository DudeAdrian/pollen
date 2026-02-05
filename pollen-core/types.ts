/**
 * Pollen Core Type Definitions
 */

export interface BiometricData {
  timestamp: Date;
  hrv: {
    rmssd: number;  // Root mean square of successive differences
    sdnn: number;   // Standard deviation of NN intervals
    pnn50: number;  // Percentage of successive RR intervals > 50ms
  };
  sleep: {
    duration: number;
    quality: number;
    deep: number;
    rem: number;
  };
  activity: {
    steps: number;
    activeMinutes: number;
    calories: number;
  };
  mood: number;  // 1-10 self-reported
  location?: {
    latitude: number;
    longitude: number;
  };
}

export interface PredictionResult {
  timestamp: Date;
  target: 'wellness' | 'sleep' | 'stress' | 'recovery';
  forecast: number[];  // Next 7 days
  confidence: number;  // 0-1
  factors: string[];   // Contributing factors
  recommendation: string;
}

export interface PatternMatch {
  pattern: string;
  confidence: number;
  source: 'biometric' | 'behavioral' | 'environmental';
  timestamp: Date;
  metadata?: Record<string, unknown>;
}

export interface TherapySession {
  id: string;
  type: 'frequency' | 'breathing' | 'meditation';
  frequency?: number;  // Hz
  duration: number;    // seconds
  startedAt: Date;
  completedAt?: Date;
  outcome?: {
    hrvChange: number;
    moodChange: number;
    userRating: number;
  };
}

export interface UserProfile {
  userId: string;
  instanceId: string;
  createdAt: Date;
  biometrics: BiometricData[];
  baseline: {
    hrv: number;
    sleep: number;
    mood: number;
  };
  preferences: {
    therapyTypes: string[];
    notificationFrequency: string;
    autonomyLevel: 'assisted' | 'semi' | 'full';
  };
}
