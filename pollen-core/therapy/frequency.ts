/**
 * Frequency Therapy — Pillar 6: Forbidden Frameworks
 * 
 * Schumann resonance and personalized frequency therapy
 * Integration with Harmonic-Balance for environmental resonance
 */

export interface FrequencyProfile {
  fundamental: number;    // Hz
  harmonics: number[];    // Hz array
  duration: number;       // seconds
  waveform: 'sine' | 'square' | 'triangle' | 'binaural';
}

export class FrequencyTherapy {
  private userId: string;
  
  // Schumann resonance frequencies (Earth's natural frequencies)
  static SCHUMANN_RESONANCE = {
    fundamental: 7.83,
    harmonics: [14.3, 20.8, 27.3, 33.8]
  };

  constructor(userId: string) {
    this.userId = userId;
  }

  /**
   * Generate personalized frequency profile
   * Pillar 6: Transformation through frequency
   */
  generateProfile(
    target: 'relaxation' | 'focus' | 'recovery' | 'sleep',
    hrvBaseline: number
  ): FrequencyProfile {
    switch (target) {
      case 'relaxation':
        return {
          fundamental: 7.83,  // Schumann
          harmonics: [14.3],
          duration: 600,  // 10 minutes
          waveform: 'sine'
        };
      
      case 'focus':
        return {
          fundamental: 40,  // Gamma wave
          harmonics: [80],
          duration: 1200,  // 20 minutes
          waveform: 'binaural'
        };
      
      case 'recovery':
        return {
          fundamental: 0.1,  // Vagal tone
          harmonics: [0.2, 0.3],
          duration: 300,  // 5 minutes
          waveform: 'sine'
        };
      
      case 'sleep':
        return {
          fundamental: 2,  // Delta wave
          harmonics: [4],
          duration: 1800,  // 30 minutes
          waveform: 'binaural'
        };
      
      default:
        return {
          fundamental: FrequencyTherapy.SCHUMANN_RESONANCE.fundamental,
          harmonics: FrequencyTherapy.SCHUMANN_RESONANCE.harmonics.slice(0, 2),
          duration: 600,
          waveform: 'sine'
        };
    }
  }

  /**
   * Calculate room resonance for Harmonic-Balance integration
   * Pillar 3: Reverse Engineering — acoustic analysis
   */
  calculateRoomResonance(
    dimensions: { length: number; width: number; height: number }
  ): number[] {
    const { length, width, height } = dimensions;
    const speedOfSound = 343; // m/s at 20°C

    // Calculate room modes (simplified)
    const modes: number[] = [];
    for (let n = 1; n <= 3; n++) {
      modes.push((speedOfSound / 2) * (n / length));
      modes.push((speedOfSound / 2) * (n / width));
      modes.push((speedOfSound / 2) * (n / height));
    }

    return modes.sort((a, b) => a - b);
  }

  /**
   * Check if room resonates with Schumann frequency
   */
  isSchumannAligned(roomModes: number[]): boolean {
    const schumann = FrequencyTherapy.SCHUMANN_RESONANCE.fundamental;
    const tolerance = 0.5; // Hz

    return roomModes.some(mode => Math.abs(mode - schumann) < tolerance);
  }

  /**
   * Generate binaural beat frequencies
   * For brainwave entrainment
   */
  generateBinauralBeat(
    carrier: number,
    beat: number
  ): { left: number; right: number } {
    return {
      left: carrier,
      right: carrier + beat
    };
  }
}
