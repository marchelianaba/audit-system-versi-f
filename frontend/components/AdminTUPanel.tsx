'use client';

/**
 * AdminTUPanel — Tahapan 8: Administrasi / Pasca-Persetujuan (peran TU).
 * Lingkup "handoff + register ringkas": paket ekspor (LHP final + Daftar Temuan &
 * Rekomendasi) + draft Surat Penyampaian. Penomoran resmi/TTE/distribusi/arsip = SIMWAS.
 */
import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import { api, Role } from '@/lib/api';

type FileRef = { name: string; path: string };

export function AdminTUPanel({ penugasanId, role }: { penugasanId: number; role: Role }) {
  const [data, setData] = useState<any>(null);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [form, setForm] = useState({ nomor: '', tanggal: '', tujuan: '', perihal: '' });
  const canEdit = ['TU', 'PT', 'PM', 'ADMIN'].includes(role);

  const load = () => api.getAdministrasi(penugasanId).then(setData).catch((e: any) => setErr(e.message));
  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [penugasanId]);

  const download = async (f: FileRef) => {
    try {
      const blob = await api.downloadFile(penugasanId, f.path);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = f.name;
      document.body.appendChild(a); a.click(); document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (e: any) { toast.error(e.message); }
  };

  const generateSurat = async () => {
    setBusy(true);
    try {
      await api.buatSuratPenyampaian(penugasanId, form);
      toast.success('Draft Surat Penyampaian dibuat. Lengkapi nomor/tanggal lalu serahkan ke SIMWAS.');
      await load();
    } catch (e: any) { toast.error(e.message); } finally { setBusy(false); }
  };

  const [uploading, setUploading] = useState<string | null>(null);
  const uploadFor = async (kode: string, file: File) => {
    setUploading(kode);
    try {
      await api.uploadKelengkapan(penugasanId, kode, file);
      toast.success('Dokumen kelengkapan terunggah.');
      await load();
    } catch (e: any) { toast.error(e.message); } finally { setUploading(null); }
  };
  const hapus = async (path: string) => {
    try { await api.hapusKelengkapan(penugasanId, path); await load(); }
    catch (e: any) { toast.error(e.message); }
  };

  if (err) return <div className="p-3 rounded bg-red-50 border border-red-200 text-red-700 text-sm">{err}</div>;
  if (!data) return <p className="text-sm text-gray-400 italic">Memuat administrasi…</p>;
  if (!data.approved) {
    return (
      <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
        Administrasi terbuka <strong>setelah konsep laporan disetujui</strong> (Tahapan 6 — LRS LHP).
      </div>
    );
  }

  const lhp: FileRef[] = data.paket_ekspor?.lhp || [];
  const daftar: FileRef[] = data.paket_ekspor?.daftar_temuan || [];
  const surat: FileRef[] = data.surat_penyampaian || [];
  const kelengkapan: Array<{ kode: string; nama: string; wajib: boolean; files: FileRef[] }> = data.kelengkapan || [];

  const fileRow = (f: FileRef) => (
    <div key={f.path} className="flex items-center justify-between border border-gray-200 rounded px-3 py-2">
      <span className="text-sm text-gray-700 truncate">📄 {f.name}</span>
      <button onClick={() => download(f)} className="text-xs px-2 py-1 rounded border border-primary text-primary hover:bg-primary hover:text-white transition">
        Unduh
      </button>
    </div>
  );

  return (
    <div className="space-y-5">
      {/* Kelengkapan administrasi (unggah sesuai pedoman) */}
      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <h3 className="font-semibold text-primary-dark mb-1">🗂 Kelengkapan Administrasi (Pedoman)</h3>
        <p className="text-xs text-gray-500 mb-3">Unggah dokumen administrasi yang sudah ditandatangani/diproses sesuai pedoman. Wajib bertanda <span className="text-rose-600 font-semibold">*</span>.</p>
        <div className="space-y-2">
          {kelengkapan.map((item) => {
            const ada = item.files.length > 0;
            return (
              <div key={item.kode} className="border border-gray-200 rounded px-3 py-2">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-sm text-gray-800">
                    {ada ? '✅' : (item.wajib ? '⛔' : '⬜')} {item.nama}
                    {item.wajib && <span className="text-rose-600 font-semibold"> *</span>}
                  </span>
                  {canEdit && (
                    <label className="text-xs px-2 py-1 rounded border border-primary text-primary hover:bg-primary hover:text-white transition cursor-pointer whitespace-nowrap">
                      {uploading === item.kode ? 'Mengunggah…' : '+ Unggah'}
                      <input type="file" className="hidden" disabled={uploading !== null}
                        onChange={(e) => { const f = e.target.files?.[0]; if (f) uploadFor(item.kode, f); e.currentTarget.value = ''; }} />
                    </label>
                  )}
                </div>
                {ada && (
                  <div className="mt-1.5 space-y-1">
                    {item.files.map((f) => (
                      <div key={f.path} className="flex items-center justify-between text-xs text-gray-600 pl-5">
                        <button onClick={() => download(f)} className="hover:underline text-primary truncate">📎 {f.name}</button>
                        {canEdit && <button onClick={() => hapus(f.path)} className="text-rose-500 hover:text-rose-700 ml-2">hapus</button>}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Paket ekspor */}
      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <h3 className="font-semibold text-primary-dark mb-1">📦 Paket Ekspor (Garis Serah)</h3>
        <p className="text-xs text-gray-500 mb-3">Dihasilkan otomatis saat laporan disetujui — diserahkan ke administrasi/SIMWAS.</p>
        <div className="space-y-2">
          {lhp.length ? lhp.map(fileRow) : <p className="text-xs text-gray-400">Belum ada file LHP final.</p>}
          {daftar.length ? daftar.map(fileRow) : (
            <p className="text-xs text-gray-400">Daftar Temuan &amp; Rekomendasi belum ada (otomatis dibuat saat approval).</p>
          )}
        </div>
      </div>

      {/* Surat penyampaian */}
      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <h3 className="font-semibold text-primary-dark mb-1">✉️ Surat Penyampaian (Draft)</h3>
        <p className="text-xs text-gray-500 mb-3">Draft surat pengantar penyampaian LHP ke auditi. Penomoran resmi &amp; TTE di SIMWAS.</p>
        {canEdit && (
          <div className="grid md:grid-cols-2 gap-2 mb-3">
            <input value={form.nomor} onChange={(e) => setForm({ ...form, nomor: e.target.value })}
              placeholder="Nomor agenda (opsional)" className="border border-gray-300 rounded px-3 py-2 text-sm" />
            <input value={form.tanggal} onChange={(e) => setForm({ ...form, tanggal: e.target.value })}
              placeholder="Tanggal (opsional)" className="border border-gray-300 rounded px-3 py-2 text-sm" />
            <input value={form.tujuan} onChange={(e) => setForm({ ...form, tujuan: e.target.value })}
              placeholder="Ditujukan kepada (opsional)" className="border border-gray-300 rounded px-3 py-2 text-sm" />
            <input value={form.perihal} onChange={(e) => setForm({ ...form, perihal: e.target.value })}
              placeholder="Perihal (opsional)" className="border border-gray-300 rounded px-3 py-2 text-sm" />
          </div>
        )}
        {canEdit && (
          <button onClick={generateSurat} disabled={busy}
            className="px-4 py-1.5 text-sm rounded bg-primary text-white font-semibold hover:bg-primary-dark disabled:opacity-50">
            {busy ? 'Membuat…' : '✍ Buat / Perbarui Draft Surat'}
          </button>
        )}
        <div className="space-y-2 mt-3">
          {surat.length ? surat.map(fileRow) : <p className="text-xs text-gray-400">Belum ada draft surat.</p>}
        </div>
      </div>

      {/* Catatan SIMWAS */}
      <div className="rounded-lg border border-gray-200 bg-gray-50 p-4 text-xs text-gray-600">
        {data.catatan_simwas}
      </div>
    </div>
  );
}
