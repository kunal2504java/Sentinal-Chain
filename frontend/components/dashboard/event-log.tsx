"use client";

import { ExternalLink, ShieldCheck } from "lucide-react";

import { ExportButton } from "@/components/dashboard/export-button";
import type { EventRecord } from "@/components/dashboard/types";
import { formatPercent, formatTimestamp, shortHash } from "@/components/dashboard/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

type EventLogProps = {
  events: EventRecord[];
  selectedEventId: number | null;
  onSelectEvent: (event: EventRecord) => void;
  onVerify: (event: EventRecord) => void;
  apiBaseUrl: string;
};

export function EventLog({
  events,
  selectedEventId,
  onSelectEvent,
  onVerify,
  apiBaseUrl,
}: EventLogProps) {
  return (
    <Card className="rounded-none border-border/70 bg-card/70 shadow-none">
      <CardHeader className="border-b border-border/60">
        <CardTitle className="font-display text-3xl">Event Log</CardTitle>
      </CardHeader>
      <CardContent className="pt-0">
        <Table>
          <TableHeader>
            <TableRow className="border-border/60">
              <TableHead className="h-14 px-4 text-xs uppercase tracking-[0.22em] text-muted-foreground">Timestamp</TableHead>
              <TableHead className="text-xs uppercase tracking-[0.22em] text-muted-foreground">Type</TableHead>
              <TableHead className="text-xs uppercase tracking-[0.22em] text-muted-foreground">Camera</TableHead>
              <TableHead className="text-xs uppercase tracking-[0.22em] text-muted-foreground">Confidence</TableHead>
              <TableHead className="text-xs uppercase tracking-[0.22em] text-muted-foreground">IPFS</TableHead>
              <TableHead className="text-xs uppercase tracking-[0.22em] text-muted-foreground">Avalanche TX</TableHead>
              <TableHead className="text-right text-xs uppercase tracking-[0.22em] text-muted-foreground">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {events.map((event) => {
              const isSelected = selectedEventId === event.id;
              const txHref =
                event.tx_hash && !event.tx_hash.startsWith("queued:") && event.tx_hash !== "not-submitted"
                  ? `https://testnet.snowtrace.io/tx/${event.tx_hash}`
                  : null;

              return (
                <TableRow
                  key={event.id}
                  className={isSelected ? "bg-accent/40" : ""}
                  onClick={() => onSelectEvent(event)}
                >
                  <TableCell className="px-4 py-4">{formatTimestamp(event.timestamp)}</TableCell>
                  <TableCell>
                    <Badge className="rounded-none px-2.5 py-1 text-[10px] uppercase tracking-[0.2em]" variant="outline">
                      {event.event_type}
                    </Badge>
                  </TableCell>
                  <TableCell>{event.camera_id}</TableCell>
                  <TableCell>{formatPercent(event.confidence)}</TableCell>
                  <TableCell className="font-mono text-xs">{shortHash(event.ipfs_cid)}</TableCell>
                  <TableCell className="font-mono text-xs">
                    {txHref ? (
                      <a
                        className="inline-flex items-center gap-1 hover:underline"
                        href={txHref}
                        rel="noreferrer"
                        target="_blank"
                        onClick={(eventClick) => eventClick.stopPropagation()}
                      >
                        {shortHash(event.tx_hash)}
                        <ExternalLink className="size-3" />
                      </a>
                    ) : (
                      shortHash(event.tx_hash)
                    )}
                  </TableCell>
                  <TableCell className="py-4 text-right">
                    <div className="flex justify-end gap-2" onClick={(eventClick) => eventClick.stopPropagation()}>
                      <Button className="rounded-none" size="sm" variant="outline" onClick={() => onVerify(event)}>
                        <ShieldCheck className="size-4" />
                        Verify
                      </Button>
                      <ExportButton apiBaseUrl={apiBaseUrl} eventId={event.id} />
                    </div>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
        {events.length === 0 ? (
          <div className="px-4 py-10 text-sm text-muted-foreground">
            No events recorded yet. Run the detection pipeline to populate the dashboard.
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}
