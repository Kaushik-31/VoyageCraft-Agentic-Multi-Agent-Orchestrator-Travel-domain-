"use client";

import React, { useState } from "react";
import type { TripRequest, Plan } from "@/types";
import { defaultRequest } from "@/types";
import { createPlan, ApiError } from "@/lib/api";

export default function Page() {
  const [form, setForm] = useState<TripRequest>(defaultRequest);
  const [interestsInput, setInterestsInput] = useState<string>(
    defaultRequest.profile.interests.join(", ")
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [plan, setPlan] = useState<Plan | null>(null);

  const onChange = <K extends keyof TripRequest>(key: K, value: TripRequest[K]) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const onProfileChange = <K extends keyof TripRequest["profile"]>(
    key: K,
    value: TripRequest["profile"][K]
  ) => {
    setForm((prev) => ({ ...prev, profile: { ...prev.profile, [key]: value } }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setPlan(null);

    // parse interests from text -> array
    const interests = interestsInput
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);

    const req: TripRequest = {
      ...form,
      profile: { ...form.profile, interests },
    };

    try {
      const result = await createPlan(req);
      setPlan(result);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(`Request failed (${err.status})`);
        console.error("API error:", err.body);
      } else {
        setError("Something went wrong");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-black text-white">
      <div className="mx-auto max-w-6xl px-6 py-10">
        <h1 className="text-3xl font-semibold tracking-tight">VoyageCraft – Planner</h1>
        <p className="text-zinc-400">End-to-end multi-agent orchestrator (Travel)</p>

        <div className="mt-8 grid grid-cols-1 gap-6 md:grid-cols-2">
          {/* Form */}
          <section className="rounded-2xl border border-zinc-800 p-6">
            <h2 className="mb-4 text-xl font-medium">Trip Request</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <label className="flex flex-col gap-2">
                  <span className="text-sm text-zinc-400">Origin</span>
                  <input
                    className="rounded-xl border border-zinc-800 bg-zinc-950 p-2 outline-none focus:ring-2 focus:ring-zinc-700"
                    value={form.origin}
                    onChange={(e) => onChange("origin", e.target.value)}
                    placeholder="Chicago"
                    required
                  />
                </label>

                <label className="flex flex-col gap-2">
                  <span className="text-sm text-zinc-400">Destination</span>
                  <input
                    className="rounded-xl border border-zinc-800 bg-zinc-950 p-2 outline-none focus:ring-2 focus:ring-zinc-700"
                    value={form.destination}
                    onChange={(e) => onChange("destination", e.target.value)}
                    placeholder="Paris"
                    required
                  />
                </label>
              </div>

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                <label className="flex flex-col gap-2">
                  <span className="text-sm text-zinc-400">Start date</span>
                  <input
                    type="date"
                    className="rounded-xl border border-zinc-800 bg-zinc-950 p-2 outline-none focus:ring-2 focus:ring-zinc-700"
                    value={form.start_date}
                    onChange={(e) => onChange("start_date", e.target.value)}
                    required
                  />
                </label>

                <label className="flex flex-col gap-2">
                  <span className="text-sm text-zinc-400">Days</span>
                  <input
                    type="number"
                    min={1}
                    max={30}
                    className="rounded-xl border border-zinc-800 bg-zinc-950 p-2 outline-none focus:ring-2 focus:ring-zinc-700"
                    value={form.days}
                    onChange={(e) => onChange("days", Number(e.target.value))}
                    required
                  />
                </label>

                <label className="flex flex-col gap-2">
                  <span className="text-sm text-zinc-400">People</span>
                  <input
                    type="number"
                    min={1}
                    className="rounded-xl border border-zinc-800 bg-zinc-950 p-2 outline-none focus:ring-2 focus:ring-zinc-700"
                    value={form.profile.people}
                    onChange={(e) => onProfileChange("people", Number(e.target.value))}
                    required
                  />
                </label>
              </div>

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <label className="flex flex-col gap-2">
                  <span className="text-sm text-zinc-400">Budget total (USD)</span>
                  <input
                    type="number"
                    min={0}
                    className="rounded-xl border border-zinc-800 bg-zinc-950 p-2 outline-none focus:ring-2 focus:ring-zinc-700"
                    value={form.profile.budget_total ?? ""}
                    onChange={(e) =>
                      onProfileChange(
                        "budget_total",
                        e.target.value === "" ? undefined : Number(e.target.value)
                      )
                    }
                    placeholder="1000"
                  />
                </label>

                <label className="flex flex-col gap-2">
                  <span className="text-sm text-zinc-400">Interests (comma-separated)</span>
                  <input
                    className="rounded-xl border border-zinc-800 bg-zinc-950 p-2 outline-none focus:ring-2 focus:ring-zinc-700"
                    value={interestsInput}
                    onChange={(e) => setInterestsInput(e.target.value)}
                    placeholder="art, cafes"
                  />
                </label>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="mt-2 inline-flex items-center justify-center rounded-xl bg-white px-4 py-2 font-medium text-black hover:bg-zinc-200 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loading ? "Planning…" : "Create plan"}
              </button>

              {error && <p className="text-sm text-red-400">{error}</p>}
            </form>
          </section>

          {/* Results */}
          <section className="rounded-2xl border border-zinc-800 p-6">
            <h2 className="mb-4 text-xl font-medium">Result</h2>
            {!plan && !loading && <p className="text-zinc-400">No plan yet. Submit the form.</p>}

            {plan && (
              <div className="space-y-6">
                <div className="rounded-xl border border-zinc-800 p-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold">
                      {plan.destination} — {plan.days.length} days
                    </h3>
                    <div className="text-sm text-zinc-400">
                      Est. cost: <span className="text-white">${plan.total_estimated_cost}</span>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  {plan.days.map((d) => (
                    <div key={d.day} className="rounded-xl border border-zinc-800 p-4">
                      <div className="mb-2 text-sm text-zinc-400">
                        Day {d.day} • {d.date}
                      </div>
                      <ul className="list-disc space-y-1 pl-6">
                        {d.activities.map((a, i) => (
                          <li key={i}>{a}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>

                <div className="rounded-xl border border-zinc-800 p-4">
                  <div className="mb-2 text-sm text-zinc-400">Decision trace</div>
                  <pre className="whitespace-pre-wrap text-sm text-zinc-300">
                    {plan.trace.join("\n")}
                  </pre>
                </div>
              </div>
            )}
          </section>
        </div>
      </div>
    </main>
  );
}
