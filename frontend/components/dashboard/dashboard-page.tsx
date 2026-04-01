"use client";

import { useEffect, useState, startTransition } from "react";
import { ArrowLeft, LogOut, RefreshCcw, Shield } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { AUTH_STORAGE_KEY } from "@/components/auth/auth";
import { EventDetail } from "@/components/dashboard/event-detail";
import { EventLog } from "@/components/dashboard/event-log";
import { StatsBar } from "@/components/dashboard/stats-bar";
import type { EventRecord, EventStats, VerifyResult } from "@/components/dashboard/types";
import { VerifyModal } from "@/components/dashboard/verify-modal";
import { Button } from "@/components/ui/button";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

const EMPTY_STATS: EventStats = {
  total_events: 0,
  events_today: 0,
  integrity_rate: 0,
};

export function DashboardPage() {
  const router = useRouter();
  const [events, setEvents] = useState<EventRecord[]>([]);
  const [stats, setStats] = useState<EventStats>(EMPTY_STATS);
  const [selectedEvent, setSelectedEvent] = useState<EventRecord | null>(null);
  const [verifyResult, setVerifyResult] = useState<VerifyResult | null>(null);
  const [verifyOpen, setVerifyOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [authorized, setAuthorized] = useState(false);

  async function refresh() {
    const [eventsResponse, statsResponse] = await Promise.all([
      fetch(`${API_BASE_URL}/api/events?limit=50&offset=0`, { cache: "no-store" }),
      fetch(`${API_BASE_URL}/api/stats`, { cache: "no-store" }),
    ]);

    if (!eventsResponse.ok || !statsResponse.ok) {
      throw new Error("Failed to load dashboard data.");
    }

    const [eventsJson, statsJson] = await Promise.all([
      eventsResponse.json() as Promise<EventRecord[]>,
      statsResponse.json() as Promise<EventStats>,
    ]);

    startTransition(() => {
      setEvents(eventsJson);
      setStats(statsJson);
      setSelectedEvent((current) => {
        if (!eventsJson.length) {
          return null;
        }
        if (current) {
          return eventsJson.find((event) => event.id === current.id) ?? eventsJson[0];
        }
        return eventsJson[0];
      });
    });
  }

  async function handleVerify(event: EventRecord) {
    const response = await fetch(`${API_BASE_URL}/api/events/${event.id}/verify`, {
      cache: "no-store",
    });
    if (!response.ok) {
      throw new Error("Failed to verify event.");
    }
    const result = (await response.json()) as VerifyResult;
    setVerifyResult(result);
    setVerifyOpen(true);
  }

  useEffect(() => {
    const session = localStorage.getItem(AUTH_STORAGE_KEY);
    if (!session) {
      router.replace("/signin");
      return;
    }
    setAuthorized(true);
  }, [router]);

  useEffect(() => {
    if (!authorized) {
      return;
    }

    let cancelled = false;

    async function load() {
      try {
        await refresh();
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void load();
    const interval = window.setInterval(() => {
      void refresh();
    }, 10000);

    return () => {
      cancelled = true;
      window.clearInterval(interval);
    };
  }, [authorized]);

  function handleLogout() {
    localStorage.removeItem(AUTH_STORAGE_KEY);
    router.push("/signin");
  }

  if (!authorized) {
    return (
      <main className="min-h-screen bg-background">
        <div className="mx-auto flex min-h-screen max-w-7xl items-center justify-center px-5 py-8 sm:px-8 lg:px-12">
          <div className="border-sketch bg-card/80 p-5 text-sm text-muted-foreground">
            Checking access...
          </div>
        </div>
      </main>
    );
  }

  return (
    <>
      <main className="noise-overlay min-h-screen bg-[radial-gradient(circle_at_top_left,rgba(24,24,24,0.05),transparent_30%),linear-gradient(180deg,rgba(255,255,255,0.96),rgba(247,244,238,0.96))]">
        <div className="mx-auto flex w-full max-w-7xl flex-col gap-8 px-5 py-8 sm:px-8 lg:px-12">
          <header className="border-b border-border/60 pb-6">
            <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
              <div className="space-y-4">
                <Link
                  className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.24em] text-muted-foreground hover:text-foreground"
                  href="/"
                >
                  <ArrowLeft className="size-4" />
                  Back to Landing Page
                </Link>
                <div className="space-y-3">
                  <div className="inline-flex items-center gap-2 border border-border/60 px-3 py-1 text-[10px] uppercase tracking-[0.3em] text-muted-foreground">
                    <Shield className="size-3.5" />
                    SentinelChain Dashboard
                  </div>
                  <h1 className="max-w-4xl font-display text-5xl leading-none tracking-tight sm:text-6xl">
                    Evidence operations, chain verification, and export in one console.
                  </h1>
                  <p className="max-w-2xl text-sm leading-6 text-muted-foreground sm:text-base">
                    Review recorded surveillance events, validate clip integrity against the chain,
                    and export evidence packages without disturbing the public landing experience.
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Button className="rounded-none self-start lg:self-auto" variant="outline" onClick={() => void refresh()}>
                  <RefreshCcw className="size-4" />
                  Refresh
                </Button>
                <Button className="rounded-none self-start lg:self-auto" variant="outline" onClick={handleLogout}>
                  <LogOut className="size-4" />
                  Sign out
                </Button>
              </div>
            </div>
          </header>

          <StatsBar stats={stats} />

          <section className="grid gap-6 xl:grid-cols-[1.55fr_0.95fr]">
            <EventLog
              apiBaseUrl={API_BASE_URL}
              events={events}
              onSelectEvent={setSelectedEvent}
              onVerify={(event) => void handleVerify(event)}
              selectedEventId={selectedEvent?.id ?? null}
            />
            <EventDetail event={selectedEvent} />
          </section>

          {loading ? (
            <div className="border-sketch bg-card/80 p-5 text-sm text-muted-foreground">
              Loading event ledger...
            </div>
          ) : null}
        </div>
      </main>

      <VerifyModal onOpenChange={setVerifyOpen} open={verifyOpen} result={verifyResult} />
    </>
  );
}
