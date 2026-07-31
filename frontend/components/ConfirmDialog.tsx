"use client";

import { Modal } from "./Modal";

interface ConfirmDialogProps {
  title: string;
  message: string;
  confirmLabel: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export function ConfirmDialog({
  title,
  message,
  confirmLabel,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  return (
    <Modal title={title} size="sm" onClose={onCancel}>
      <p className="text-[13.5px] leading-relaxed text-ink-soft">{message}</p>

      <div className="mt-5 flex justify-end gap-2">
        <button
          type="button"
          onClick={onCancel}
          className="rounded-lg border border-line px-4 py-2 text-[13px] font-semibold text-ink-soft transition hover:border-groww hover:text-groww"
        >
          Cancel
        </button>
        <button
          type="button"
          onClick={onConfirm}
          className="rounded-lg bg-danger px-4 py-2 text-[13px] font-semibold text-white transition hover:bg-danger-dark"
        >
          {confirmLabel}
        </button>
      </div>
    </Modal>
  );
}
