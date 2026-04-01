import { ExternalLink, FileVideo, MapPin, Shield } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

import type { EventRecord } from "@/components/dashboard/types";
import { formatPercent, formatTimestamp, shortHash } from "@/components/dashboard/utils";

type EventDetailProps = {
  event: EventRecord | null;
};

export function EventDetail({ event }: EventDetailProps) {
  if (!event) {
    return (
      <Card className="rounded-none border-border/70 bg-card/70 shadow-none">
        <CardHeader>
          <CardTitle className="font-display text-3xl">Event Detail</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          Select an event from the log to inspect its evidence trail.
        </CardContent>
      </Card>
    );
  }

  const rows = [
    { label: "Timestamp", value: formatTimestamp(event.timestamp) },
    { label: "Camera", value: event.camera_id },
    { label: "Confidence", value: formatPercent(event.confidence) },
    { label: "IPFS CID", value: shortHash(event.ipfs_cid, 16, 10) },
    { label: "Transaction", value: shortHash(event.tx_hash, 16, 10) },
    { label: "Clip Hash", value: shortHash(event.clip_hash, 16, 12) },
  ];

  return (
    <Card className="rounded-none border-border/70 bg-card/70 shadow-none">
      <CardHeader className="border-b border-border/60">
        <div className="flex items-start justify-between gap-4">
          <div>
            <CardTitle className="font-display text-3xl">{event.event_type}</CardTitle>
            <p className="mt-2 text-sm text-muted-foreground">
              Full record for the selected evidence package.
            </p>
          </div>
          <Badge className="rounded-none px-3 py-1 text-xs uppercase tracking-[0.24em]" variant="outline">
            Event #{event.id}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-5 pt-6">
        <div className="grid gap-3 sm:grid-cols-2">
          {rows.map((row) => (
            <div key={row.label} className="border-sketch bg-background/70 p-4">
              <div className="mb-2 text-xs uppercase tracking-[0.22em] text-muted-foreground">
                {row.label}
              </div>
              <div className="text-sm">{row.value}</div>
            </div>
          ))}
        </div>
        <div className="grid gap-3 text-sm text-muted-foreground">
          <div className="flex items-start gap-3">
            <MapPin className="mt-0.5 size-4 shrink-0" />
            <span>Evidence stored from the recorded camera source and written into the SentinelChain event store.</span>
          </div>
          <div className="flex items-start gap-3">
            <FileVideo className="mt-0.5 size-4 shrink-0" />
            <span className="break-all">{event.clip_path}</span>
          </div>
          <div className="flex items-start gap-3">
            <Shield className="mt-0.5 size-4 shrink-0" />
            <span>Use verify to compare the stored clip against the blockchain proof.</span>
          </div>
          {event.tx_hash && event.tx_hash !== "not-submitted" && !event.tx_hash.startsWith("queued:") ? (
            <div className="flex items-start gap-3">
              <ExternalLink className="mt-0.5 size-4 shrink-0" />
              <span className="break-all">{event.tx_hash}</span>
            </div>
          ) : null}
        </div>
      </CardContent>
    </Card>
  );
}
