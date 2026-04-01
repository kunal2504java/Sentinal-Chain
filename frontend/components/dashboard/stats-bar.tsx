import { Activity, DatabaseZap, ShieldCheck } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

import type { EventStats } from "@/components/dashboard/types";

type StatsBarProps = {
  stats: EventStats;
};

export function StatsBar({ stats }: StatsBarProps) {
  const cards = [
    {
      label: "Total Events",
      value: stats.total_events,
      icon: DatabaseZap,
      tone: "text-foreground",
    },
    {
      label: "Events Today",
      value: stats.events_today,
      icon: Activity,
      tone: "text-foreground/70",
    },
    {
      label: "Integrity Rate",
      value: `${stats.integrity_rate}%`,
      icon: ShieldCheck,
      tone: "text-emerald-700",
    },
  ];

  return (
    <section className="grid gap-4 lg:grid-cols-[1fr_1fr_1.2fr]">
      {cards.map(({ label, value, icon: Icon, tone }) => (
        <Card key={label} className="rounded-none border-border/70 bg-card/70 shadow-none backdrop-blur">
          <CardHeader className="flex flex-row items-center justify-between gap-4 pb-2">
            <CardTitle className="text-xs uppercase tracking-[0.24em] text-muted-foreground">
              {label}
            </CardTitle>
            <Icon className={`size-4 ${tone}`} />
          </CardHeader>
          <CardContent className="pt-0">
            <div className="font-display text-4xl leading-none">{value}</div>
            {label === "Integrity Rate" ? (
              <div className="mt-4 space-y-2">
                <Progress className="h-1.5 rounded-none" value={stats.integrity_rate} />
                <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">
                  Verified against the chain record
                </p>
              </div>
            ) : null}
          </CardContent>
        </Card>
      ))}
    </section>
  );
}
