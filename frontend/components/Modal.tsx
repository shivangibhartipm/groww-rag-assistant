"use client";

import { useEffect } from "react";
import { CloseIcon } from "./icons";

interface ModalProps {
  title: string;
  subtitle?: string;
  size?: "sm" | "md";
  onClose: () => void;
  children: React.ReactNode;
}

export function Modal({
  title,
  subtitle,
  size = "md",
  onClose,
  children,
}: ModalProps) {
  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-black/25 p-0 sm:items-center sm:p-6"
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-label={title}
        onClick={(event) => event.stopPropagation()}
        className={`flex max-h-[90vh] w-full flex-col overflow-hidden rounded-t-2xl bg-white shadow-[0_20px_60px_rgba(16,24,40,0.18)] sm:max-h-[80vh] sm:rounded-2xl ${
          size === "sm" ? "sm:max-w-md" : "sm:max-w-2xl"
        }`}
      >
        <header className="flex items-start gap-3 border-b border-line-soft px-5 py-4">
          <div className="min-w-0 flex-1">
            <h2 className="text-[16px] font-bold text-ink">{title}</h2>
            {subtitle && (
              <p className="mt-0.5 text-[12.5px] text-ink-muted">{subtitle}</p>
            )}
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close"
            className="flex size-8 shrink-0 items-center justify-center rounded-full text-ink-muted transition hover:bg-mint-50 hover:text-groww"
          >
            <CloseIcon className="size-4" />
          </button>
        </header>

        <div className="overflow-y-auto px-5 py-4">{children}</div>
      </div>
    </div>
  );
}
