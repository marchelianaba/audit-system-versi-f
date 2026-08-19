'use client';

/**
 * TopBar — INTEGRAL AI Workspace
 *
 * Mirror style SIMWAS v2:
 * - Judul: "Sistem Informasi Manajemen Pengawasan" + "Kementerian Komunikasi Dan Digital RI"
 * - Right: avatar + role (dropdown logout)
 */
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { api, getSession, clearToken, Session } from '@/lib/api';

const ROLE_LABEL: Record<string, string> = {
  AT: 'Anggota Tim',
  KT: 'Ketua Tim',
  PT: 'Pengendali Teknis',
  PM: 'Pengendali Mutu',
  TU: 'Tata Usaha',
  ADMIN: 'Administrator',
};

const ROLE_COLOR: Record<string, string> = {
  AT: 'bg-at',
  KT: 'bg-kt',
  PT: 'bg-pt',
  PM: 'bg-pm',
  TU: 'bg-amber-600',
  ADMIN: 'bg-slate-700',
};

export function TopBar() {
  const router = useRouter();
  const [session, setSession] = useState<Session | null>(null);
  const [showMenu, setShowMenu] = useState(false);
  const [mounted, setMounted] = useState(false);

  // Modal ganti password (B4)
  const [showPw, setShowPw] = useState(false);
  const [oldPw, setOldPw] = useState('');
  const [newPw, setNewPw] = useState('');
  const [confirmPw, setConfirmPw] = useState('');
  const [busyPw, setBusyPw] = useState(false);

  useEffect(() => {
    setMounted(true);
    setSession(getSession());
  }, []);

  const onLogout = () => {
    clearToken();
    router.push('/login');
  };

  const openChangePw = () => {
    setShowMenu(false);
    setOldPw('');
    setNewPw('');
    setConfirmPw('');
    setShowPw(true);
  };

  const submitChangePw = async () => {
    if (newPw.length < 8) {
      toast.error('Password baru minimal 8 karakter.');
      return;
    }
    if (newPw !== confirmPw) {
      toast.error('Konfirmasi password tidak cocok.');
      return;
    }
    setBusyPw(true);
    try {
      await api.changePassword(oldPw, newPw);
      toast.success('Password berhasil diganti.');
      setShowPw(false);
    } catch (e) {
      const msg = e instanceof Error ? e.message.replace(/^\d+:\s*/, '') : 'Gagal mengganti password.';
      toast.error(msg || 'Gagal mengganti password.');
    } finally {
      setBusyPw(false);
    }
  };

  return (
    <header className="bg-white border-b border-gray-200 h-16 flex items-center justify-between px-6 sticky top-0 z-20">
      <div>
        <h1 className="text-sm font-bold text-ink">Sistem Informasi Manajemen Pengawasan</h1>
        <p className="text-xs text-gray-500 -mt-0.5">Kementerian Komunikasi Dan Digital RI</p>
      </div>

      <div className="flex items-center gap-3">
        {/* Avatar + role */}
        <div className="relative">
          <button
            onClick={() => setShowMenu((s) => !s)}
            className="flex items-center gap-2 hover:bg-gray-50 rounded-lg p-1 pr-3"
          >
            <div className="relative">
              <div className={`w-9 h-9 rounded-full ${session ? ROLE_COLOR[session.role_aktif] || 'bg-gray-400' : 'bg-gray-400'} flex items-center justify-center text-white font-semibold text-sm`}>
                {mounted && session ? session.user.nama_lengkap.charAt(0).toUpperCase() : '?'}
              </div>
              {/* Online indicator */}
              <span className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-green-500 rounded-full border-2 border-white"></span>
            </div>
            {mounted && session && (
              <div className="text-left leading-tight">
                <div className="text-xs font-semibold text-ink">{session.user.nama_lengkap}</div>
                <div className="text-[10px] text-gray-500">{ROLE_LABEL[session.role_aktif] || session.role_aktif}</div>
              </div>
            )}
          </button>

          {/* Dropdown */}
          {showMenu && mounted && session && (
            <div className="absolute right-0 top-full mt-2 w-56 bg-white border border-gray-200 rounded-lg shadow-card overflow-hidden">
              <div className="p-3 border-b border-gray-100">
                <div className="text-sm font-medium text-ink">{session.user.nama_lengkap}</div>
                <div className="text-xs text-gray-500">{session.user.email}</div>
                <div className="mt-1 inline-block px-2 py-0.5 rounded-full bg-primary-50 text-primary text-[10px] font-semibold">
                  {ROLE_LABEL[session.role_aktif] || session.role_aktif}
                </div>
              </div>
              <button
                onClick={openChangePw}
                className="w-full text-left px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 border-b border-gray-100"
              >
                Ganti password
              </button>
              <button
                onClick={onLogout}
                className="w-full text-left px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50"
              >
                Keluar
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Modal ganti password (B4) */}
      {showPw && (
        <div
          className="fixed inset-0 z-[100] flex items-center justify-center bg-black/40 backdrop-blur-[1px] px-4"
          onClick={() => !busyPw && setShowPw(false)}
        >
          <div
            className="bg-white rounded-2xl shadow-2xl max-w-sm w-full p-5 border border-gray-100"
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
          >
            <h3 className="font-semibold text-gray-800 mb-3">Ganti password</h3>
            <div className="space-y-2.5">
              <input
                type="password"
                autoFocus
                placeholder="Password lama"
                value={oldPw}
                onChange={(e) => setOldPw(e.target.value)}
                className="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 focus:border-primary focus:ring-1 focus:ring-primary outline-none"
              />
              <input
                type="password"
                placeholder="Password baru (min. 8 karakter)"
                value={newPw}
                onChange={(e) => setNewPw(e.target.value)}
                className="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 focus:border-primary focus:ring-1 focus:ring-primary outline-none"
              />
              <input
                type="password"
                placeholder="Ulangi password baru"
                value={confirmPw}
                onChange={(e) => setConfirmPw(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && !busyPw && submitChangePw()}
                className="w-full px-3 py-2 text-sm rounded-lg border border-gray-300 focus:border-primary focus:ring-1 focus:ring-primary outline-none"
              />
            </div>
            <div className="flex justify-end gap-2 mt-5">
              <button
                onClick={() => setShowPw(false)}
                disabled={busyPw}
                className="px-3 py-1.5 text-sm rounded-lg border border-gray-300 text-gray-600 hover:bg-gray-50 transition disabled:opacity-50"
              >
                Batal
              </button>
              <button
                onClick={submitChangePw}
                disabled={busyPw || !oldPw || !newPw || !confirmPw}
                className="px-4 py-1.5 text-sm rounded-lg text-white font-semibold bg-primary hover:bg-primary-dark transition disabled:opacity-50"
              >
                {busyPw ? 'Menyimpan…' : 'Simpan'}
              </button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
