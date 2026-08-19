/**
 * Confirm dialog global (pengganti window.confirm) — bergaya INTEGRAL.
 * Pakai: `if (!(await confirmDialog('Hapus item ini?'))) return;`
 * Host (<ConfirmHost/>) dipasang sekali di app/layout.tsx.
 */
export type ConfirmOpts = {
  message: string;
  title?: string;
  confirmText?: string;
  cancelText?: string;
  danger?: boolean;
};

type State = (ConfirmOpts & { resolve: (v: boolean) => void }) | null;

let listener: ((s: State) => void) | null = null;
let current: State = null;

export function _subscribeConfirm(fn: (s: State) => void): () => void {
  listener = fn;
  return () => {
    if (listener === fn) listener = null;
  };
}

export function confirmDialog(opts: ConfirmOpts | string): Promise<boolean> {
  const o: ConfirmOpts = typeof opts === 'string' ? { message: opts } : opts;
  return new Promise<boolean>((resolve) => {
    current = { ...o, resolve };
    listener?.(current);
  });
}

export function _resolveConfirm(v: boolean): void {
  current?.resolve(v);
  current = null;
  listener?.(null);
}
