'use client';

/** Host modal confirm global (bergaya INTEGRAL). Dipasang sekali di layout. */
import { useEffect, useState } from 'react';
import { _subscribeConfirm, _resolveConfirm, ConfirmOpts } from '@/lib/confirm';

export function ConfirmHost() {
  const [state, setState] = useState<(ConfirmOpts & { resolve: (v: boolean) => void }) | null>(null);

  useEffect(() => _subscribeConfirm(setState), []);

  // ESC = batal, Enter = konfirmasi (saat dialog terbuka).
  useEffect(() => {
    if (!state) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') _resolveConfirm(false);
      if (e.key === 'Enter') _resolveConfirm(true);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [state]);

  if (!state) return null;

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black/40 backdrop-blur-[1px] px-4"
      onClick={() => _resolveConfirm(false)}
    >
      <div
        className="bg-white rounded-2xl shadow-2xl max-w-sm w-full p-5 border border-gray-100"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
      >
        <h3 className="font-semibold text-gray-800 mb-1.5">
          {state.title || (state.danger ? 'Konfirmasi tindakan' : 'Konfirmasi')}
        </h3>
        <p className="text-sm text-gray-600 whitespace-pre-line leading-relaxed">{state.message}</p>
        <div className="flex justify-end gap-2 mt-5">
          <button
            onClick={() => _resolveConfirm(false)}
            className="px-3 py-1.5 text-sm rounded-lg border border-gray-300 text-gray-600 hover:bg-gray-50 transition"
          >
            {state.cancelText || 'Batal'}
          </button>
          <button
            onClick={() => _resolveConfirm(true)}
            autoFocus
            className={`px-4 py-1.5 text-sm rounded-lg text-white font-semibold transition ${
              state.danger ? 'bg-rose-600 hover:bg-rose-700' : 'bg-primary hover:bg-primary-dark'
            }`}
          >
            {state.confirmText || 'Ya, lanjutkan'}
          </button>
        </div>
      </div>
    </div>
  );
}
