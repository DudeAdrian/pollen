/**
 * Token Economics — Pillar 7: Billionaire Mindset
 * 
 * MINE earning through activity
 * WELL conversion for utility
 * Staking for governance
 */

import type { TokenBalance, EarningRecord } from '../types';

export class TokenEconomics {
  private userId: string;
  private balance: TokenBalance;

  // Conversion ratio: 100 MINE = 1 WELL
  static CONVERSION_RATIO = 100;

  constructor(userId: string) {
    this.userId = userId;
    this.balance = {
      mine: '0',
      well: '0',
      staked: '0',
      votingPower: '0'
    };
  }

  /**
   * Earn MINE through activity
   * Pillar 7: Economic participation
   */
  async earnMINE(activity: {
    type: string;
    valuePoints: number;
    metadata?: Record<string, unknown>;
  }): Promise<EarningRecord> {
    // Calculate MINE (10 MINE per value point)
    const mineAmount = activity.valuePoints * 10;
    
    const record: EarningRecord = {
      id: `earn-${Date.now()}`,
      userId: this.userId,
      activity: activity.type,
      valuePoints: activity.valuePoints,
      mineEarned: mineAmount.toString(),
      timestamp: new Date(),
      txHash: null // Will be set after blockchain confirmation
    };

    // Update balance
    this.balance.mine = (BigInt(this.balance.mine) + BigInt(mineAmount)).toString();

    console.log(`[P7-Economics] Earned ${mineAmount} MINE for ${activity.type}`);

    return record;
  }

  /**
   * Convert MINE to WELL
   * Burns MINE, mints WELL
   */
  async convertMineToWell(mineAmount: bigint): Promise<{
    mineBurned: string;
    wellReceived: string;
    txHash: string;
  }> {
    const minConversion = BigInt(100); // Minimum 100 MINE
    
    if (mineAmount < minConversion) {
      throw new Error(`Minimum ${minConversion} MINE required for conversion`);
    }

    if (BigInt(this.balance.mine) < mineAmount) {
      throw new Error('Insufficient MINE balance');
    }

    const wellAmount = mineAmount / BigInt(TokenEconomics.CONVERSION_RATIO);

    // Update balances
    this.balance.mine = (BigInt(this.balance.mine) - mineAmount).toString();
    this.balance.well = (BigInt(this.balance.well) + wellAmount).toString();

    console.log(`[P7-Economics] Converted ${mineAmount} MINE → ${wellAmount} WELL`);

    return {
      mineBurned: mineAmount.toString(),
      wellReceived: wellAmount.toString(),
      txHash: `0x${Date.now().toString(16)}` // Simulated
    };
  }

  /**
   * Stake MINE for governance
   */
  async stakeMINE(amount: bigint, lockPeriodDays: number): Promise<void> {
    if (BigInt(this.balance.mine) < amount) {
      throw new Error('Insufficient MINE balance');
    }

    // Move from available to staked
    this.balance.mine = (BigInt(this.balance.mine) - amount).toString();
    this.balance.staked = (BigInt(this.balance.staked) + amount).toString();
    
    // Voting power = staked amount (if locked > 30 days)
    if (lockPeriodDays >= 30) {
      this.balance.votingPower = this.balance.staked;
    }

    console.log(`[P7-Economics] Staked ${amount} MINE for ${lockPeriodDays} days`);
  }

  /**
   * Get current balances
   */
  getBalance(): TokenBalance {
    return { ...this.balance };
  }

  /**
   * Check if user is cooperative member
   * Requires 1000+ MINE
   */
  isCooperativeMember(): boolean {
    const total = BigInt(this.balance.mine) + BigInt(this.balance.staked);
    return total >= BigInt(1000);
  }
}
