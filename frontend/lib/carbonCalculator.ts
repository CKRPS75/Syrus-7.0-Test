// lib/carbonCalculator.ts
import { JourneyLeg, CarbonMetrics } from '../types';

const EMISSION_FACTORS_G_PER_KM: Record<string, number> = {
  WALK: 0,
  METRO: 25,
  SUBWAY: 25,
  TRAIN: 25,
  RAIL: 25,
  BUS: 45,
};

const CAB_BASELINE_FACTOR_G_PER_KM = 160;

export function computeCarbonMetrics(legs: JourneyLeg[], transitFare: number): CarbonMetrics {
  let totalMeters = 0;
  let transitCO2 = 0;

  for (const leg of legs) {
    totalMeters += leg.distanceMeters;
    const factor = EMISSION_FACTORS_G_PER_KM[leg.mode] ?? 40;
    transitCO2 += (leg.distanceMeters / 1000) * factor;
  }

  const totalKm = totalMeters / 1000;
  const cabCO2 = totalKm * CAB_BASELINE_FACTOR_G_PER_KM;
  const co2SavedGrams = Math.max(0, Math.round(cabCO2 - transitCO2));

  // Mumbai Ola/Uber baseline: ₹50 base + ₹18/km
  const cabFare = Math.round(50 + totalKm * 18);
  const moneySaved = Math.max(0, cabFare - transitFare);

  return {
    co2EmittedGrams: Math.round(transitCO2),
    co2SavedGrams,
    cabComparisonFare: cabFare,
    moneySaved,
  };
}