"use client";

import { CheckCircle2, ShieldAlert } from "lucide-react";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";

import type { VerifyResult } from "@/components/dashboard/types";
import { shortHash } from "@/components/dashboard/utils";

type VerifyModalProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  result: VerifyResult | null;
};

export function VerifyModal({ open, onOpenChange, result }: VerifyModalProps) {
  const intact = result?.match ?? false;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="rounded-none border-foreground/10 bg-background/95 p-0 shadow-2xl backdrop-blur">
        <DialogHeader className="border-b border-border/60 px-6 py-5 text-left">
          <DialogTitle className="font-display text-3xl">
            Evidence Verification
          </DialogTitle>
          <DialogDescription className="text-sm text-muted-foreground">
            Re-hashed locally and compared against the recorded blockchain proof.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-6 px-6 py-6">
          <div className="flex items-center gap-3">
            {intact ? (
              <CheckCircle2 className="size-6 text-emerald-600" />
            ) : (
              <ShieldAlert className="size-6 text-amber-600" />
            )}
            <Badge className="rounded-none px-3 py-1 text-xs uppercase tracking-[0.24em]" variant={intact ? "default" : "outline"}>
              {intact ? "Evidence is intact" : "WARNING: Evidence may be compromised"}
            </Badge>
          </div>
          <div className="grid gap-4 text-sm">
            <div className="border-sketch bg-card/80 p-4">
              <div className="mb-2 text-xs uppercase tracking-[0.24em] text-muted-foreground">
                Local Hash
              </div>
              <div className="font-mono text-xs break-all">{shortHash(result?.local_hash, 18, 18)}</div>
            </div>
            <div className="border-sketch bg-card/80 p-4">
              <div className="mb-2 text-xs uppercase tracking-[0.24em] text-muted-foreground">
                On-chain Hash
              </div>
              <div className="font-mono text-xs break-all">{shortHash(result?.on_chain_hash, 18, 18)}</div>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
