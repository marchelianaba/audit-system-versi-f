'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  SortingState,
  useReactTable,
} from '@tanstack/react-table';
import { api, getSession, Penugasan, Session, Skill, SkillInfo } from '@/lib/api';
import { confirmDialog } from '@/lib/confirm';
import { AppShell } from '@/components/AppShell';

// Status penugasan (di-derive backend dari artefak) → label + warna yang ramah.
const STATUS_META: Record<string, { label: string; cls: string }> = {
  DRAFT: { label: 'Draft — belum analisis', cls: 'bg-gray-100 text-gray-700' },
  INGESTING: { label: '⟳ Ekstraksi dokumen', cls: 'bg-amber-50 text-amber-700' },
  KKP_IN_PROGRESS: { label: 'KKP berjalan', cls: 'bg-blue-50 text-blue-700' },
  KKP_QC: { label: 'KKP — QC', cls: 'bg-blue-50 text-blue-700' },
  KKP_DONE: { label: 'KKP disetujui KT', cls: 'bg-indigo-50 text-indigo-700' },
  LHP_IN_PROGRESS: { label: 'LHP berjalan', cls: 'bg-violet-50 text-violet-700' },
  LHP_QC: { label: 'LHP — QC', cls: 'bg-violet-50 text-violet-700' },
  LHP_DONE: { label: '✓ LHP selesai', cls: 'bg-emerald-50 text-emerald-700' },
};

function statusMeta(status: string) {
  return STATUS_META[status] || { label: status, cls: 'bg-gray-100 text-gray-700' };
}

// 7 tahapan workflow INTEGRAL (selain Survey tahapan 0). Berapa tahapan "done"
// untuk satu status — dipakai indikator titik per-tahapan di tabel.
type StageState = 'done' | 'in_progress' | 'pending';
const STAGE_LABELS = ['KP', 'PKP', 'KKP', 'LRS KK', 'Konsep', 'LRS LHP', 'Laporan'];
function stageStates(status: string): StageState[] {
  // index 0..6 = tahapan 1..7. `done` = jumlah tahapan selesai; `ip` = indeks
  // tahapan yang sedang berjalan (opsional).
  const build = (done: number, ip?: number): StageState[] =>
    Array.from({ length: 7 }, (_, i): StageState =>
      i < done ? 'done' : i === ip ? 'in_progress' : 'pending'
    );
  switch (status) {
    case 'DRAFT':
      return build(0);
    case 'INGESTING':
    case 'KKP_IN_PROGRESS':
    case 'KKP_QC':
      return build(2, 2); // KP + PKP selesai, KKP berjalan
    case 'KKP_DONE':
      return build(4);
    case 'LHP_IN_PROGRESS':
    case 'LHP_QC':
      return build(4, 4); // sampai LRS KK selesai, Konsep berjalan
    case 'LHP_DONE':
      return build(6); // tahapan 7 (Laporan final) pending sampai disetujui PT/PM
    default:
      return build(0);
  }
}

const MONTHS = [
  'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
  'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember',
];

/** Tanggal acuan penugasan: tanggal_st (string bebas) → fallback created_at. */
function refDate(p: Penugasan): Date {
  // tanggal_st bisa berformat bebas ("10.03.2026" / "10 Maret 2026"); coba parse,
  // kalau gagal pakai created_at yang selalu ISO.
  if (p.tanggal_st) {
    const t = Date.parse(p.tanggal_st);
    if (!Number.isNaN(t)) return new Date(t);
  }
  return new Date(p.created_at);
}

function tanggalDisplay(p: Penugasan): string {
  if (p.tanggal_st) return p.tanggal_st;
  return refDate(p).toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' });
}

export default function DashboardPage() {
  const router = useRouter();
  const [penugasan, setPenugasan] = useState<Penugasan[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [obyek, setObyek] = useState('');
  const [skill, setSkill] = useState<Skill>('reviu-rka-kl');
  const [skills, setSkills] = useState<SkillInfo[]>([]);
  const [nomorSt, setNomorSt] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  // Hydration-safe: session di-baca dari localStorage HANYA setelah mount.
  const [session, setSessionState] = useState<Session | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const s = getSession();
    setSessionState(s);
    if (!s) {
      router.push('/login');
      return;
    }
    api
      .listPenugasan()
      .then(setPenugasan)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
    api
      .getSkills()
      .then((rows) => {
        setSkills(rows);
        if (rows.length && !rows.some((r) => r.slug === skill)) setSkill(rows[0].slug);
      })
      .catch(() => {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router]);

  // slug skill → label ramah (dari registry; fallback ke slug).
  const skillLabel = useMemo(() => {
    const m = new Map(skills.map((s) => [s.slug, s.jenis || s.name]));
    return (slug: string) => m.get(slug) || slug;
  }, [skills]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!obyek.trim()) {
      setError('Obyek penugasan wajib diisi.');
      return;
    }
    if (!nomorSt.trim()) {
      const lanjut = await confirmDialog({
        message:
          'Nomor ST belum diisi.\n\nContext.md akan memuat placeholder dan QC SAIPI akan KRITIS (REN-003) ' +
          'sampai Nomor ST + tanggal dilengkapi (via tab Konteks/Setup).\n\nTetap buat penugasan?',
        confirmText: 'Tetap buat',
      });
      if (!lanjut) return;
    }
    try {
      const p = await api.createPenugasan({
        obyek,
        skill,
        nomor_st: nomorSt || undefined,
      });
      setPenugasan([p, ...penugasan]);
      setShowForm(false);
      setObyek('');
      setNomorSt('');
    } catch (err: any) {
      setError(err.message);
    }
  };

  const [deleting, setDeleting] = useState<number | null>(null);
  const handleDelete = async (p: Penugasan) => {
    if (
      !(await confirmDialog({
        message: `Hapus penugasan "${p.obyek}"?\n\nSeluruh dokumen, hasil ingest, KKP, dan LHP akan DIHAPUS PERMANEN dari disk. Tindakan ini tidak bisa dibatalkan.`,
        danger: true,
        confirmText: 'Hapus permanen',
      }))
    )
      return;
    setDeleting(p.id);
    try {
      await api.deletePenugasan(p.id);
      setPenugasan((prev) => prev.filter((x) => x.id !== p.id));
    } catch (err: any) {
      setError(err.message);
    } finally {
      setDeleting(null);
    }
  };

  if (!mounted) {
    return <main className="min-h-screen" />;
  }
  if (!session) return null;

  return (
    <AppShell>
      <div className="max-w-6xl mx-auto">
        <div className="text-sm text-gray-500 mb-1">INTEGRAL / Penugasan</div>
        <div className="flex justify-between items-center mb-5">
          <h1 className="text-2xl font-bold text-primary-dark">Daftar Penugasan</h1>
          <div className="flex items-center gap-3">
            {/* Feedback Agen → dipindah ke sidebar (hindari tombol duplikat, Prinsip UX). */}
            {session?.role_aktif === 'PT' ? (
              <button
                onClick={() => setShowForm(!showForm)}
                className="px-4 py-2 rounded bg-primary text-white text-sm font-semibold hover:bg-primary-dark"
              >
                {showForm ? '× Batal' : '+ Penugasan Baru'}
              </button>
            ) : (
              <span className="text-xs text-gray-400 italic">
                🔒 Hanya Pengendali Teknis yang dapat membuat penugasan
              </span>
            )}
          </div>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded bg-red-50 border border-red-200 text-red-700 text-sm">
            {error}
          </div>
        )}

        {showForm && session?.role_aktif === 'PT' && (
          <form
            onSubmit={handleCreate}
            className="bg-white border border-gray-200 rounded-lg p-5 mb-5 grid gap-3"
          >
            <h3 className="font-semibold text-primary-dark">Penugasan Baru</h3>
            <label className="block">
              <span className="text-sm text-gray-700">Obyek penugasan</span>
              <input
                value={obyek}
                onChange={(e) => setObyek(e.target.value)}
                required
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                placeholder="Contoh: RKA-K/L Dit. Pengendalian 2027"
              />
            </label>
            <label className="block">
              <span className="text-sm text-gray-700">Skill</span>
              <select
                value={skill}
                onChange={(e) => setSkill(e.target.value as Skill)}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm bg-white"
              >
                {skills.length === 0 ? (
                  <>
                    <option value="reviu-rka-kl">Reviu RKA-K/L</option>
                    <option value="reviu-pengadaan">Reviu Pengadaan</option>
                  </>
                ) : (
                  skills.map((s) => (
                    <option key={s.slug} value={s.slug}>
                      {s.jenis || s.name}
                      {s.has_pipeline ? '' : ' · criteria-driven'}
                    </option>
                  ))
                )}
              </select>
            </label>
            <label className="block">
              <span className="text-sm text-gray-700">Nomor ST (opsional)</span>
              <input
                value={nomorSt}
                onChange={(e) => setNomorSt(e.target.value)}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                placeholder="51 IJ.3 KP.01.06 10.03.2026"
              />
            </label>
            <button
              type="submit"
              className="px-4 py-2 rounded bg-primary text-white font-semibold text-sm"
            >
              Buat
            </button>
          </form>
        )}

        {loading ? (
          <div className="text-gray-500 text-sm">Memuat…</div>
        ) : penugasan.length === 0 ? (
          <div className="bg-white border border-gray-200 rounded-lg p-8 text-center text-gray-500">
            {session?.role_aktif === 'PT'
              ? <>Belum ada penugasan. Klik <strong>+ Penugasan Baru</strong>.</>
              : <>Belum ada penugasan. Tunggu Pengendali Teknis membuat penugasan terlebih dahulu.</>}
          </div>
        ) : (
          <PenugasanTable
            rows={penugasan}
            skillLabel={skillLabel}
            canDelete={session?.role_aktif === 'PT'}
            onDelete={handleDelete}
            deleting={deleting}
          />
        )}
      </div>
    </AppShell>
  );
}

// ============================================================
// PenugasanTable — DataTable SIMWAS-style (S3.3)
//   Filter: Tahun + Bulan + pencarian global + Export CSV.
//   Kolom: NO | JUDUL | JENIS | TANGGAL | STATUS (per-tahapan) | AKSI.
//   Fitur tanstack: sort kolom + pagination ("Show N entries").
// ============================================================
type Row = Penugasan;

function PenugasanTable({
  rows,
  skillLabel,
  canDelete,
  onDelete,
  deleting,
}: {
  rows: Row[];
  skillLabel: (slug: string) => string;
  canDelete: boolean;
  onDelete: (p: Row) => void;
  deleting: number | null;
}) {
  const [tahun, setTahun] = useState<string>('');
  const [bulan, setBulan] = useState<string>('');
  const [globalFilter, setGlobalFilter] = useState('');
  const [sorting, setSorting] = useState<SortingState>([]);

  // SIMWAS-style judul. Catatan: unit pelaksana + rentang tanggal mulai-selesai
  // belum tersedia dari data v7 (akan terisi saat sinkron ST dari SIMWAS, S4.1) —
  // di sini dibangun dari field yang ada.
  const simwasJudul = (p: Row) =>
    `Melakukan ${skillLabel(p.skill)} atas ${p.obyek} TA ${refDate(p).getFullYear()}`;

  const yearsAvailable = useMemo(() => {
    const set = new Set(rows.map((p) => String(refDate(p).getFullYear())));
    return Array.from(set).sort((a, b) => Number(b) - Number(a));
  }, [rows]);

  // Pre-filter Tahun + Bulan sebelum diserahkan ke tanstack (search/sort/paginate).
  const data = useMemo(() => {
    return rows.filter((p) => {
      const d = refDate(p);
      if (tahun && String(d.getFullYear()) !== tahun) return false;
      if (bulan && String(d.getMonth() + 1) !== bulan) return false;
      return true;
    });
  }, [rows, tahun, bulan]);

  const columns = useMemo<ColumnDef<Row>[]>(
    () => [
      {
        id: 'no',
        header: 'NO',
        cell: ({ row, table }) =>
          table.getState().pagination.pageIndex * table.getState().pagination.pageSize +
          row.index +
          1,
        enableSorting: false,
        size: 50,
      },
      {
        id: 'judul',
        header: 'JUDUL',
        accessorFn: (p) => simwasJudul(p),
        cell: ({ row }) => {
          const p = row.original;
          return (
            <Link href={`/penugasan/${p.id}`} className="group block">
              <span className="font-medium text-gray-800 group-hover:text-primary group-hover:underline">
                {simwasJudul(p)}
              </span>
              {p.nomor_st && (
                <span className="block text-[11px] text-gray-400 font-mono mt-0.5">
                  ST: {p.nomor_st}
                </span>
              )}
            </Link>
          );
        },
      },
      {
        id: 'jenis',
        header: 'JENIS',
        accessorFn: (p) => skillLabel(p.skill),
        cell: ({ getValue }) => (
          <span className="px-2 py-0.5 text-xs rounded bg-blue-50 text-blue-700 whitespace-nowrap">
            {getValue<string>()}
          </span>
        ),
      },
      {
        id: 'tanggal',
        header: 'TANGGAL',
        accessorFn: (p) => refDate(p).getTime(),
        cell: ({ row }) => (
          <span className="text-xs text-gray-600 whitespace-nowrap">
            {tanggalDisplay(row.original)}
          </span>
        ),
        sortingFn: 'basic',
      },
      {
        id: 'status',
        header: 'STATUS / TAHAPAN',
        accessorFn: (p) => p.status,
        enableSorting: false,
        cell: ({ row }) => {
          const p = row.original;
          const states = stageStates(p.status);
          return (
            <div>
              <span className={`px-2 py-0.5 text-xs rounded ${statusMeta(p.status).cls}`}>
                {statusMeta(p.status).label}
              </span>
              <div className="flex items-center gap-1 mt-1.5" title="Tahapan 1–7">
                {states.map((st, i) => (
                  <span
                    key={i}
                    title={STAGE_LABELS[i]}
                    className={`w-3.5 h-3.5 rounded-full text-[8px] flex items-center justify-center font-bold ${
                      st === 'done'
                        ? 'bg-emerald-500 text-white'
                        : st === 'in_progress'
                        ? 'bg-amber-400 text-white'
                        : 'bg-gray-200 text-gray-400'
                    }`}
                  >
                    {st === 'done' ? '✓' : i + 1}
                  </span>
                ))}
              </div>
            </div>
          );
        },
      },
      {
        id: 'aksi',
        header: 'AKSI',
        enableSorting: false,
        cell: ({ row }) => {
          const p = row.original;
          return (
            <div className="flex items-center gap-3 whitespace-nowrap">
              <Link href={`/penugasan/${p.id}`} className="text-primary hover:underline">
                Buka →
              </Link>
              {canDelete && (
                <button
                  onClick={() => onDelete(p)}
                  disabled={deleting === p.id}
                  className="text-red-600 hover:text-red-800 hover:underline disabled:opacity-50"
                  title="Hapus penugasan (permanen)"
                >
                  {deleting === p.id ? 'Menghapus…' : 'Hapus'}
                </button>
              )}
            </div>
          );
        },
      },
    ],
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [skillLabel, canDelete, deleting]
  );

  const table = useReactTable({
    data,
    columns,
    state: { sorting, globalFilter },
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: { pagination: { pageSize: 10 } },
  });

  const exportCsv = () => {
    const header = ['NO', 'JUDUL', 'JENIS', 'TANGGAL', 'STATUS', 'NOMOR_ST', 'KODE'];
    const sorted = table.getSortedRowModel().rows; // hasil filter + sort terkini
    const lines = sorted.map((r, i) => {
      const p = r.original;
      const cells = [
        String(i + 1),
        simwasJudul(p),
        skillLabel(p.skill),
        tanggalDisplay(p),
        statusMeta(p.status).label.replace(/[✓⟳🔔]/g, '').trim(),
        p.nomor_st || '',
        p.kode,
      ];
      // Escape CSV: bungkus dengan quote, double-quote internal.
      return cells.map((c) => `"${String(c).replace(/"/g, '""')}"`).join(',');
    });
    const csv = '﻿' + [header.join(','), ...lines].join('\r\n'); // BOM agar Excel baca UTF-8
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `daftar-penugasan-${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const reset = () => {
    setTahun('');
    setBulan('');
    setGlobalFilter('');
  };

  const totalFiltered = table.getFilteredRowModel().rows.length;

  return (
    <div>
      {/* Filter bar */}
      <div className="bg-white border border-gray-200 rounded-lg p-3 mb-3 flex flex-wrap items-center gap-2">
        <select
          value={tahun}
          onChange={(e) => setTahun(e.target.value)}
          className="border border-gray-300 rounded-md px-2 py-2 text-sm bg-white"
          title="Filter tahun"
        >
          <option value="">Semua Tahun</option>
          {yearsAvailable.map((y) => (
            <option key={y} value={y}>{y}</option>
          ))}
        </select>
        <select
          value={bulan}
          onChange={(e) => setBulan(e.target.value)}
          className="border border-gray-300 rounded-md px-2 py-2 text-sm bg-white"
          title="Filter bulan"
        >
          <option value="">Semua Bulan</option>
          {MONTHS.map((m, i) => (
            <option key={m} value={String(i + 1)}>{m}</option>
          ))}
        </select>
        <input
          value={globalFilter}
          onChange={(e) => setGlobalFilter(e.target.value)}
          placeholder="🔍 Cari judul / jenis…"
          className="flex-1 min-w-[180px] border border-gray-300 rounded-md px-3 py-2 text-sm"
        />
        {(tahun || bulan || globalFilter) && (
          <button
            onClick={reset}
            className="px-3 py-2 text-sm text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
          >
            × Reset
          </button>
        )}
        <button
          onClick={exportCsv}
          className="px-3 py-2 text-sm border border-primary text-primary rounded-md hover:bg-primary-50 font-medium"
          title="Export hasil filter ke CSV"
        >
          ⬇ Export CSV
        </button>
      </div>

      {/* Tabel */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50">
            {table.getHeaderGroups().map((hg) => (
              <tr key={hg.id}>
                {hg.headers.map((h) => {
                  const sortable = h.column.getCanSort();
                  const sorted = h.column.getIsSorted();
                  return (
                    <th
                      key={h.id}
                      onClick={sortable ? h.column.getToggleSortingHandler() : undefined}
                      className={`text-left p-3 font-semibold text-gray-600 uppercase text-xs ${
                        sortable ? 'cursor-pointer select-none hover:text-primary' : ''
                      }`}
                    >
                      {flexRender(h.column.columnDef.header, h.getContext())}
                      {sortable && (
                        <span className="ml-1 text-gray-400">
                          {sorted === 'asc' ? '▲' : sorted === 'desc' ? '▼' : '↕'}
                        </span>
                      )}
                    </th>
                  );
                })}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="p-6 text-center text-gray-400">
                  Tidak ada penugasan yang cocok dengan filter.
                </td>
              </tr>
            ) : (
              table.getRowModel().rows.map((r) => (
                <tr key={r.id} className="border-t border-gray-100 hover:bg-gray-50 align-top">
                  {r.getVisibleCells().map((c) => (
                    <td key={c.id} className="p-3">
                      {flexRender(c.column.columnDef.cell, c.getContext())}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Footer: jumlah entri + pagination */}
      <div className="flex flex-wrap items-center justify-between gap-3 mt-3 text-sm text-gray-600">
        <div className="flex items-center gap-2">
          <span>Tampilkan</span>
          <select
            value={table.getState().pagination.pageSize}
            onChange={(e) => table.setPageSize(Number(e.target.value))}
            className="border border-gray-300 rounded px-2 py-1 bg-white"
          >
            {[10, 25, 50, 100].map((n) => (
              <option key={n} value={n}>{n}</option>
            ))}
          </select>
          <span>entri · {totalFiltered} penugasan</span>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
            className="px-3 py-1 border border-gray-300 rounded disabled:opacity-40 hover:bg-gray-50"
          >
            ‹ Sebelumnya
          </button>
          <span className="px-2">
            Hal {table.getState().pagination.pageIndex + 1} / {table.getPageCount() || 1}
          </span>
          <button
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
            className="px-3 py-1 border border-gray-300 rounded disabled:opacity-40 hover:bg-gray-50"
          >
            Berikutnya ›
          </button>
        </div>
      </div>
    </div>
  );
}
