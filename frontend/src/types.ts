// Frontend TypeScript types mirroring backend Pydantic models

export interface UserProfile {
  people: number;                 // >= 1
  budget_total?: number;          // optional, USD
  interests: string[];            // e.g., ["art","cafes"]
}

export interface TripRequest {
  origin: string;
  destination: string;
  start_date: string;             // YYYY-MM-DD
  days: number;                   // 1..30
  profile: UserProfile;
}

export interface DayPlan {
  day: number;
  date: string;                   // YYYY-MM-DD
  activities: string[];
  notes?: string | null;
}

export interface Plan {
  destination: string;
  total_estimated_cost: number;
  currency: string;               // "USD"
  days: DayPlan[];
  trace: string[];
  metadata: Record<string, unknown>;
}

// Small helpers for the form
export const defaultProfile: UserProfile = {
  people: 2,
  interests: ["art", "cafes"],
};

export const defaultRequest: TripRequest = {
  origin: "Chicago",
  destination: "Paris",
  start_date: "2025-09-10",
  days: 3,
  profile: defaultProfile,
};
