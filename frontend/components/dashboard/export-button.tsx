"use client";

import { Download } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";

type ExportButtonProps = {
  eventId: number;
  apiBaseUrl: string;
};

export function ExportButton({ eventId, apiBaseUrl }: ExportButtonProps) {
  const [exporting, setExporting] = useState(false);

  async function handleExport() {
    setExporting(true);
    try {
      const response = await fetch(`${apiBaseUrl}/api/events/${eventId}/export`, {
        method: "POST",
      });
      if (!response.ok) {
        throw new Error("Failed to export evidence package.");
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `event-${eventId}.zip`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } finally {
      setExporting(false);
    }
  }

  return (
    <Button className="rounded-none" disabled={exporting} size="sm" variant="outline" onClick={() => void handleExport()}>
      <Download className="size-4" />
      {exporting ? "Exporting..." : "Export"}
    </Button>
  );
}
