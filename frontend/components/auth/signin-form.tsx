"use client";

import { startTransition, useState } from "react";
import { ArrowRight, ShieldCheck } from "lucide-react";
import { useRouter } from "next/navigation";

import { AUTH_STORAGE_KEY, createSession, isValidOtp, isValidPhoneOrEmail } from "@/components/auth/auth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export function SignInForm() {
  const router = useRouter();
  const [identifier, setIdentifier] = useState("");
  const [otp, setOtp] = useState("");
  const [error, setError] = useState("");

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const normalizedIdentifier = identifier.trim();

    if (!isValidPhoneOrEmail(normalizedIdentifier)) {
      setError("Enter a valid 10-digit phone number or email address.");
      return;
    }

    if (!isValidOtp(otp)) {
      setError("Use 123456 as the OTP for now.");
      return;
    }

    localStorage.setItem(AUTH_STORAGE_KEY, createSession(normalizedIdentifier));
    setError("");
    startTransition(() => {
      router.push("/dashboard");
    });
  }

  return (
    <Card className="rounded-none border-border/70 bg-card/80 shadow-none backdrop-blur">
      <CardHeader className="border-b border-border/60">
        <div className="inline-flex items-center gap-2 border border-border/60 px-3 py-1 text-[10px] uppercase tracking-[0.3em] text-muted-foreground">
          <ShieldCheck className="size-3.5" />
          Operator Sign In
        </div>
        <CardTitle className="font-display text-4xl leading-none">
          Access the evidence dashboard.
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-6">
        <form className="space-y-5" onSubmit={handleSubmit}>
          <div className="space-y-2">
            <Label className="text-xs uppercase tracking-[0.24em] text-muted-foreground" htmlFor="identifier">
              Phone / Mail
            </Label>
            <Input
              id="identifier"
              autoComplete="username"
              className="h-12 rounded-none border-border/70 bg-background/70"
              onChange={(event) => setIdentifier(event.target.value)}
              placeholder="9876543210 or ops@sentinelchain.ai"
              value={identifier}
            />
          </div>

          <div className="space-y-2">
            <Label className="text-xs uppercase tracking-[0.24em] text-muted-foreground" htmlFor="otp">
              Password / OTP
            </Label>
            <Input
              id="otp"
              autoComplete="one-time-code"
              className="h-12 rounded-none border-border/70 bg-background/70"
              inputMode="numeric"
              maxLength={6}
              onChange={(event) => setOtp(event.target.value)}
              placeholder="123456"
              type="password"
              value={otp}
            />
          </div>

          <div className="border-sketch bg-background/70 p-4 text-sm text-muted-foreground">
            Temporary access rule: any valid 10-digit phone number or any email address works,
            and the OTP is <span className="font-mono text-foreground">123456</span>.
          </div>

          {error ? <p className="text-sm text-destructive">{error}</p> : null}

          <Button className="h-12 w-full rounded-none" type="submit">
            Continue to Dashboard
            <ArrowRight className="size-4" />
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
