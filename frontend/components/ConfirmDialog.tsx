"use client";

import { useEffect, useRef } from "react";

type ConfirmDialogProps = {
  open: boolean;
  title: string;
  description: string;
  confirmLabel: string;
  busy?: boolean;
  error?: string;
  onCancel: () => void;
  onConfirm: () => void;
};

export default function ConfirmDialog({ open, title, description, confirmLabel, busy = false, error = "", onCancel, onConfirm }: ConfirmDialogProps) {
  const cancelRef = useRef<HTMLButtonElement>(null);
  const dialogRef = useRef<HTMLElement>(null);
  const previousFocus = useRef<HTMLElement | null>(null);
  const cancelHandlerRef = useRef(onCancel);

  useEffect(() => { cancelHandlerRef.current = onCancel; }, [onCancel]);

  useEffect(() => {
    if (!open) return;
    previousFocus.current = document.activeElement as HTMLElement | null;
    const timer = window.setTimeout(() => cancelRef.current?.focus(), 0);
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape" && !busy) cancelHandlerRef.current();
      if (event.key === "Tab") {
        const focusable = Array.from(dialogRef.current?.querySelectorAll<HTMLButtonElement>("button:not(:disabled)") ?? []);
        if (!focusable.length) return;
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
        if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
      }
    };
    document.addEventListener("keydown", onKeyDown);
    document.body.style.overflow = "hidden";
    return () => {
      window.clearTimeout(timer);
      document.removeEventListener("keydown", onKeyDown);
      document.body.style.overflow = "";
      previousFocus.current?.focus();
    };
  }, [open, busy]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-[#02070D]/80 p-4 backdrop-blur-sm" onMouseDown={(event) => { if (event.target === event.currentTarget && !busy) onCancel(); }}>
      <section ref={dialogRef} role="alertdialog" aria-modal="true" aria-labelledby="confirm-title" aria-describedby="confirm-description" className="w-full max-w-md overflow-hidden rounded-2xl border border-alert/30 bg-panelraised shadow-[0_30px_90px_rgba(0,0,0,.55)]">
        <div className="h-1 bg-gradient-to-r from-alert via-alert/60 to-transparent" />
        <div className="p-5 sm:p-6">
          <div className="mb-4 grid h-10 w-10 place-items-center rounded-xl border border-alert/30 bg-alert/10 text-alert" aria-hidden="true">
            <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="1.8"><path d="M4 7h16M9 7V4h6v3m3 0-1 13H7L6 7m4 4v5m4-5v5"/></svg>
          </div>
          <h2 id="confirm-title" className="font-display text-xl font-semibold">{title}</h2>
          <p id="confirm-description" className="mt-2 text-sm leading-relaxed text-muted">{description}</p>
          {error && <p role="alert" className="mt-4 rounded-lg border border-alert/30 bg-alert/10 p-3 text-sm text-alert">{error}</p>}
          <div className="mt-6 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <button ref={cancelRef} type="button" disabled={busy} onClick={onCancel} className="min-h-11 rounded-lg border border-panelborder px-4 text-sm font-medium text-ink hover:bg-panel disabled:opacity-50">ยกเลิก</button>
            <button type="button" disabled={busy} onClick={onConfirm} aria-busy={busy} className="min-h-11 min-w-32 rounded-lg bg-alert px-4 text-sm font-semibold text-base hover:bg-[#ff7b84] disabled:opacity-60">{busy ? "กำลังลบ…" : confirmLabel}</button>
          </div>
        </div>
      </section>
    </div>
  );
}
