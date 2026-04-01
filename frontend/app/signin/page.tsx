import Link from "next/link";

import { SignInForm } from "@/components/auth/signin-form";

export default function SignInPage() {
  return (
    <main className="noise-overlay min-h-screen bg-[radial-gradient(circle_at_top_left,rgba(24,24,24,0.05),transparent_30%),linear-gradient(180deg,rgba(255,255,255,0.96),rgba(247,244,238,0.96))]">
      <div className="mx-auto flex min-h-screen w-full max-w-7xl flex-col px-5 py-8 sm:px-8 lg:px-12">
        <div className="mb-10 flex items-center justify-between border-b border-border/60 pb-6">
          <Link
            className="font-display text-2xl tracking-tight transition-colors hover:text-foreground/70"
            href="/"
          >
            SentinelChain
          </Link>
          <Link
            className="text-xs uppercase tracking-[0.24em] text-muted-foreground hover:text-foreground"
            href="/"
          >
            Back to site
          </Link>
        </div>

        <div className="grid flex-1 items-center gap-10 lg:grid-cols-[1.15fr_0.85fr]">
          <section className="space-y-6">
            <div className="inline-flex items-center gap-2 border border-border/60 px-3 py-1 text-[10px] uppercase tracking-[0.3em] text-muted-foreground">
              SentinelChain Access
            </div>
            <h1 className="max-w-4xl font-display text-5xl leading-none tracking-tight sm:text-6xl">
              Surveillance operations, verification, and export for active responders.
            </h1>
            <p className="max-w-2xl text-base leading-7 text-muted-foreground">
              This temporary sign-in flow is open for internal testing. Use any valid 10-digit
              phone number or any email address, then enter the shared OTP to access the operator dashboard.
            </p>
            <div className="grid gap-3 sm:grid-cols-3">
              <div className="border-sketch bg-card/70 p-4">
                <div className="mb-2 text-xs uppercase tracking-[0.22em] text-muted-foreground">Operator Mode</div>
                <div className="text-sm">Review event logs, verification status, and exportable evidence bundles.</div>
              </div>
              <div className="border-sketch bg-card/70 p-4">
                <div className="mb-2 text-xs uppercase tracking-[0.22em] text-muted-foreground">Shared OTP</div>
                <div className="font-mono text-lg">123456</div>
              </div>
              <div className="border-sketch bg-card/70 p-4">
                <div className="mb-2 text-xs uppercase tracking-[0.22em] text-muted-foreground">Open Access</div>
                <div className="text-sm">Designed for demos until real auth is added.</div>
              </div>
            </div>
          </section>

          <SignInForm />
        </div>
      </div>
    </main>
  );
}
