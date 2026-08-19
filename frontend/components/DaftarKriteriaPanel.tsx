'use client';

/**
 * DaftarKriteriaPanel — Daftar Kriteria penugasan (khusus skill *-umum).
 *
 * LATAR. Skill "umum" (audit/reviu/evaluasi/pemantauan) bersifat criteria-driven:
 * tak punya kriteria baku bawaan seperti reviu-rka-kl (PMK 107/2024) atau
 * reviu-pengadaan (Perpres 16/2018). Kriterianya datang dari auditor.
 *
 * Dulu kriteria hanya salah satu pilihan di dropdown jenis dokumen — mudah
 * terlewat, dan tak ada jaminan kriterianya benar-benar ada sebelum analisis.
 * Panel ini menjadikannya eksplisit, dengan DUA cara mengisi yang setara:
 *
 *   • Unggah berkas + sebutkan pasal yang dipakai → agen membaca BAGIAN ITU saja,
 *     bukan menyapu seluruh dokumen (hemat, dan kutipannya lebih tepat karena
 *     diarahkan auditor yang paham konteksnya).
 *   • Ketik langsung → untuk ketentuan tanpa berkas digital (SE, kebijakan
 *     internal). Tak ada auditor yang terkunci hanya karena kriterianya tak
 *     berbentuk berkas.
 *
 * Panel TIDAK tampil pada mode manual penuh: di sana auditor menulis unsur
 * Kriteria langsung di formulir KKSA.
 */
import { useCallback, useEffect, useState } from 'react';
import { api, KriteriaEntri, Role } from '@/lib/api';

type Berkas = {
  dokumen_id: number;
  nama_file: string;
  status: string;
  terbaca: boolean | null;
  pindai: boolean;
  catatan_baca: string;
  halaman_total: number;
};

const BISA_SUNTING: Role[] = ['AT', 'KT', 'PT'];

export function DaftarKriteriaPanel({
  penugasanId,
  role,
  onStatus,
}: {
  penugasanId: number;
  role: Role;
  /** Lapor ke induk: kriteria sudah ada atau belum (untuk mengunci tombol AI). */
  onStatus?: (s: { berlaku: boolean; adaKriteria: boolean; jumlah: number }) => void;
}) {
  const [berlaku, setBerlaku] = useState(false);
  const [entri, setEntri] = useState<KriteriaEntri[]>([]);
  const [berkas, setBerkas] = useState<Berkas[]>([]);
  const [memuat, setMemuat] = useState(true);
  const [menyimpan, setMenyimpan] = useState(false);
  const [mengunggah, setMengunggah] = useState(false);
  const [galat, setGalat] = useState<string | null>(null);
  const [pesan, setPesan] = useState<string | null>(null);

  const bisaSunting = BISA_SUNTING.includes(role);

  const muat = useCallback(async () => {
    try {
      const d = await api.getDaftarKriteria(penugasanId);
      setBerlaku(d.berlaku);
      setEntri(d.entri || []);
      setBerkas(d.berkas_tersedia || []);
      onStatus?.({ berlaku: d.berlaku, adaKriteria: d.ada_kriteria, jumlah: d.jumlah });
    } catch (e: any) {
      setGalat(e.message);
    } finally {
      setMemuat(false);
    }
    // onStatus sengaja tidak jadi dependensi: induk melewatkan fungsi baru tiap
    // render, dan memasukkannya akan memicu pemuatan berulang tanpa henti.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [penugasanId]);

  useEffect(() => {
    muat();
  }, [muat]);

  if (!memuat && !berlaku) return null;

  const statusBerkas = (nama: string): Berkas | undefined =>
    berkas.find((b) => b.nama_file === nama || b.nama_file === nama.split('/').pop());

  const unggah = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files?.length) return;
    setMengunggah(true);
    setGalat(null);
    try {
      for (const f of Array.from(files)) {
        await api.uploadDokumen(penugasanId, f, 'KRITERIA');
        setEntri((prev) => [
          ...prev,
          {
            tipe: 'UNGGAHAN',
            file: f.name,
            nama_file: f.name,
            rujukan: [{ pasal: '', halaman: '' }],
          },
        ]);
      }
      setPesan('Berkas terunggah. Sebutkan pasal yang dipakai, lalu simpan.');
      // Muat ulang status keterbacaan — digest jalan di latar, jadi status
      // "hasil pindai" baru diketahui beberapa saat setelah unggah.
      setTimeout(() => {
        api
          .getDaftarKriteria(penugasanId)
          .then((d) => setBerkas(d.berkas_tersedia || []))
          .catch(() => {});
      }, 2500);
    } catch (err: any) {
      setGalat(err.message);
    } finally {
      setMengunggah(false);
      e.target.value = '';
    }
  };

  const tambahKetik = () =>
    setEntri((p) => [...p, { tipe: 'KETIK', sumber: '', teks: '' }]);

  const ubah = (i: number, patch: Partial<KriteriaEntri>) =>
    setEntri((p) => p.map((e, idx) => (idx === i ? { ...e, ...patch } : e)));

  const hapus = (i: number) => setEntri((p) => p.filter((_, idx) => idx !== i));

  const ubahRujukan = (i: number, j: number, patch: { pasal?: string; halaman?: string }) =>
    setEntri((p) =>
      p.map((e, idx) =>
        idx === i
          ? { ...e, rujukan: (e.rujukan || []).map((r, rj) => (rj === j ? { ...r, ...patch } : r)) }
          : e
      )
    );

  const tambahRujukan = (i: number) =>
    setEntri((p) =>
      p.map((e, idx) =>
        idx === i ? { ...e, rujukan: [...(e.rujukan || []), { pasal: '', halaman: '' }] } : e
      )
    );

  const hapusRujukan = (i: number, j: number) =>
    setEntri((p) =>
      p.map((e, idx) =>
        idx === i ? { ...e, rujukan: (e.rujukan || []).filter((_, rj) => rj !== j) } : e
      )
    );

  const simpan = async () => {
    setMenyimpan(true);
    setGalat(null);
    setPesan(null);
    try {
      const res = await api.saveDaftarKriteria(penugasanId, entri);
      setEntri(res.entri || []);
      setPesan(`Tersimpan — ${res.jumlah} kriteria.`);
      onStatus?.({ berlaku: true, adaKriteria: res.ada_kriteria, jumlah: res.jumlah });
    } catch (e: any) {
      setGalat(e.message);
    } finally {
      setMenyimpan(false);
    }
  };

  const terisi = entri.filter(
    (e) => (e.tipe === 'KETIK' && (e.teks || '').trim()) || (e.tipe === 'UNGGAHAN' && e.file)
  ).length;

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-5">
      <div className="flex items-start justify-between gap-3 mb-1">
        <h2 className="text-lg font-bold text-primary-dark">Kriteria pengawasan</h2>
        <span
          className={`text-xs px-2.5 py-1 rounded-full whitespace-nowrap ${
            terisi > 0
              ? 'bg-green-50 text-green-800 border border-green-200'
              : 'bg-amber-50 text-amber-800 border border-amber-200'
          }`}
        >
          {terisi > 0 ? `${terisi} kriteria — siap dianalisis` : 'Wajib — belum ada kriteria'}
        </span>
      </div>
      <p className="text-sm text-gray-600 mb-4">
        Tolok ukur penilaian. Skill ini tidak membawa kriteria baku, jadi kriterianya Anda yang
        tentukan — <strong>unggah berkasnya</strong> lalu sebutkan pasal yang dipakai, atau{' '}
        <strong>ketik langsung</strong> bila tidak ada berkas digitalnya. Agen hanya membaca
        bagian yang Anda sebut, bukan seluruh dokumen.
      </p>

      {galat && (
        <div className="mb-3 p-3 rounded bg-red-50 border border-red-200 text-red-800 text-sm">
          {galat}
        </div>
      )}
      {pesan && !galat && (
        <div className="mb-3 p-3 rounded bg-green-50 border border-green-200 text-green-800 text-sm">
          {pesan}
        </div>
      )}

      {memuat ? (
        <p className="text-sm text-gray-500">Memuat…</p>
      ) : (
        <>
          {entri.length === 0 && (
            <div className="border border-dashed border-amber-300 bg-amber-50 rounded-lg p-6 text-center text-sm text-amber-900 mb-3">
              Belum ada kriteria. Tahapan analisis AI terkunci sampai minimal satu kriteria diisi.
            </div>
          )}

          <div className="space-y-3">
            {entri.map((e, i) =>
              e.tipe === 'KETIK' ? (
                <div key={`k-${i}`} className="border border-gray-200 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-semibold text-gray-800">✍ Diketik auditor</span>
                    {bisaSunting && (
                      <button
                        type="button"
                        onClick={() => hapus(i)}
                        className="text-xs text-red-600 hover:underline"
                      >
                        Hapus
                      </button>
                    )}
                  </div>
                  <input
                    value={e.sumber || ''}
                    onChange={(ev) => ubah(i, { sumber: ev.target.value })}
                    disabled={!bisaSunting}
                    placeholder="Sumber — mis. SE Sekjen 12/2025"
                    className="w-full mb-2 border border-gray-300 rounded-md px-3 py-2 text-sm disabled:bg-gray-50"
                  />
                  <textarea
                    value={e.teks || ''}
                    onChange={(ev) => ubah(i, { teks: ev.target.value })}
                    disabled={!bisaSunting}
                    rows={2}
                    placeholder="Bunyi ketentuannya — mis. Angka 4 huruf b: usulan wajib disertai lembar pengesahan pejabat eselon II."
                    className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm disabled:bg-gray-50"
                  />
                </div>
              ) : (
                <div key={`u-${i}`} className="border border-gray-200 rounded-lg p-3">
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <div className="flex items-center gap-2 min-w-0">
                      <span className="text-sm font-semibold text-gray-800 truncate">
                        📄 {e.nama_file || e.file}
                      </span>
                      {statusBerkas(e.nama_file || e.file || '')?.pindai ? (
                        <span className="text-[11px] px-2 py-0.5 rounded bg-amber-100 text-amber-800 whitespace-nowrap">
                          hasil pindai
                        </span>
                      ) : statusBerkas(e.nama_file || e.file || '')?.terbaca ? (
                        <span className="text-[11px] px-2 py-0.5 rounded bg-green-100 text-green-800 whitespace-nowrap">
                          teks digital
                        </span>
                      ) : null}
                    </div>
                    {bisaSunting && (
                      <button
                        type="button"
                        onClick={() => hapus(i)}
                        className="text-xs text-red-600 hover:underline whitespace-nowrap"
                      >
                        Hapus
                      </button>
                    )}
                  </div>

                  <p className="text-xs text-gray-500 mb-2">
                    Bagian yang dipakai — agen membaca ini saja
                    {statusBerkas(e.nama_file || e.file || '')?.halaman_total
                      ? `, bukan seluruh ${statusBerkas(e.nama_file || e.file || '')?.halaman_total} halaman`
                      : ''}
                    .
                  </p>

                  {(e.rujukan || []).map((r, j) => (
                    <div key={`r-${i}-${j}`} className="flex gap-2 mb-2">
                      <input
                        value={r.pasal}
                        onChange={(ev) => ubahRujukan(i, j, { pasal: ev.target.value })}
                        disabled={!bisaSunting}
                        placeholder="Pasal 26 ayat (5) — wajib"
                        className="flex-1 border border-gray-300 rounded-md px-3 py-2 text-sm disabled:bg-gray-50"
                      />
                      <input
                        value={r.halaman}
                        onChange={(ev) => ubahRujukan(i, j, { halaman: ev.target.value })}
                        disabled={!bisaSunting}
                        placeholder={
                          statusBerkas(e.nama_file || e.file || '')?.pindai
                            ? 'hal. — wajib'
                            : 'hal. (opsional)'
                        }
                        className={`w-32 border rounded-md px-3 py-2 text-sm disabled:bg-gray-50 ${
                          statusBerkas(e.nama_file || e.file || '')?.pindai
                            ? 'border-amber-400'
                            : 'border-gray-300'
                        }`}
                      />
                      {bisaSunting && (e.rujukan || []).length > 1 && (
                        <button
                          type="button"
                          onClick={() => hapusRujukan(i, j)}
                          className="px-2 text-gray-400 hover:text-red-600"
                          aria-label="Hapus rujukan"
                        >
                          ×
                        </button>
                      )}
                    </div>
                  ))}

                  {statusBerkas(e.nama_file || e.file || '')?.pindai && (
                    <p className="text-xs text-amber-700 mb-2">
                      Berkas hasil pindai — nomor halaman wajib diisi agar bisa dibaca sistem.
                      Tulisan pada gambar tidak bisa dicari tanpa halamannya disebut lebih dulu.
                    </p>
                  )}

                  {bisaSunting && (
                    <button
                      type="button"
                      onClick={() => tambahRujukan(i)}
                      className="text-xs text-primary hover:underline"
                    >
                      + Tambah rujukan
                    </button>
                  )}
                </div>
              )
            )}
          </div>

          {bisaSunting && (
            <div className="flex flex-wrap gap-2 mt-4">
              <label
                className={`px-4 py-2 rounded text-sm font-semibold cursor-pointer ${
                  mengunggah
                    ? 'bg-gray-200 text-gray-500'
                    : 'bg-white border border-gray-300 text-gray-800 hover:border-primary'
                }`}
              >
                {mengunggah ? 'Mengunggah…' : '⬆ Unggah berkas kriteria'}
                <input
                  type="file"
                  multiple
                  onChange={unggah}
                  disabled={mengunggah}
                  className="hidden"
                />
              </label>
              <button
                type="button"
                onClick={tambahKetik}
                className="px-4 py-2 rounded text-sm font-semibold bg-white border border-gray-300 text-gray-800 hover:border-primary"
              >
                ✍ Ketik kriteria
              </button>
              <button
                type="button"
                onClick={simpan}
                disabled={menyimpan}
                className="px-4 py-2 rounded bg-primary text-white text-sm font-semibold disabled:opacity-60"
              >
                {menyimpan ? 'Menyimpan…' : 'Simpan kriteria'}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
