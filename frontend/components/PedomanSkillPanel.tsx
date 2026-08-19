'use client';

/**
 * PedomanSkillPanel — intisari SKILL.md, ditampilkan di sebelah formulir KKSA manual.
 *
 * LATAR. Isi pedoman skill (checklist yang perlu ditelusuri, format unsur, bahasa
 * simpulan baku, batasan) selama ini hanya dibaca AGEN lewat `load_skill`. Pada
 * mode manual penuh tidak ada sesi agen sama sekali — sehingga justru di jalur
 * itulah doktrin skill tak hadir di layar, dan auditor menulis di ruang kosong.
 *
 * Panel ini murni PANDUAN BACA: tidak memvalidasi, tidak mengunci, tidak mengubah
 * apa pun yang diketik. Isinya ditarik dari `GET /skills/{slug}` (SKILL.md yang
 * sama dengan yang dibaca agen), jadi tidak ada teks kedua yang harus dirawat
 * terpisah dan tidak mungkin melenceng dari doktrin yang dipakai agen.
 */
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

/** Ambil isi satu bagian markdown berdasarkan judulnya (##/###). */
function bagian(md: string, ...judul: string[]): string {
  for (const j of judul) {
    const re = new RegExp(`^#{2,3}\\s*[^\\n]*${j}[^\\n]*$`, 'im');
    const m = re.exec(md);
    if (!m) continue;
    const mulai = m.index + m[0].length;
    const sisa = md.slice(mulai);
    const berikut = /^#{2,3}\s/m.exec(sisa);
    return sisa.slice(0, berikut ? berikut.index : undefined).trim();
  }
  return '';
}

/** Ringkas jadi beberapa butir pendek — panel ini pendamping, bukan dokumen. */
function butir(teks: string, maks = 4): string[] {
  return teks
    .split('\n')
    .map((b) => b.replace(/^[\s>*-]+/, '').trim())
    .filter((b) => b.length > 25 && !b.startsWith('|') && !b.startsWith('#'))
    .slice(0, maks)
    .map((b) => (b.length > 190 ? b.slice(0, 190) + '…' : b));
}

export function PedomanSkillPanel({ skill }: { skill: string }) {
  const [md, setMd] = useState<string | null>(null);
  const [gagal, setGagal] = useState(false);
  const [buka, setBuka] = useState(true);

  useEffect(() => {
    let batal = false;
    api
      .getSkillDetail(skill)
      .then((d) => !batal && setMd(d.content || ''))
      .catch(() => !batal && setGagal(true));
    return () => {
      batal = true;
    };
  }, [skill]);

  if (gagal || md === null) return null;

  const lingkup = butir(bagian(md, 'Lingkup', 'Paradigma'), 3);
  const penilaian = butir(bagian(md, 'Penutupan Penilaian', 'Paradigma Penilaian'), 3);
  const unsur = butir(bagian(md, 'Format Unsur'), 3);
  const batasan = butir(bagian(md, 'Batasan'), 4);
  const simpulan = butir(bagian(md, 'Bahasa Simpulan', 'Simpulan'), 2);

  const seksi: Array<[string, string[]]> = [
    ['Lingkup & paradigma', lingkup],
    ['Cara menilai', penilaian],
    ['Unsur temuan', unsur],
    ['Kalimat simpulan', simpulan],
  ];

  return (
    <div className="mb-3 border border-gray-200 rounded bg-white p-3">
      <button
        type="button"
        onClick={() => setBuka((b) => !b)}
        className="w-full flex items-center justify-between text-left"
      >
        <span className="text-xs font-semibold text-gray-700">
          📖 Pedoman skill — {skill}
          <span className="ml-2 font-normal text-gray-400">panduan baca, tidak mengikat</span>
        </span>
        <span className="text-gray-400 text-xs">{buka ? '▾' : '▸'}</span>
      </button>

      {buka && (
        <div className="mt-2 space-y-2 text-[11px] text-gray-600">
          {seksi
            .filter(([, isi]) => isi.length > 0)
            .map(([judul, isi]) => (
              <div key={judul}>
                <div className="font-semibold text-gray-700 mb-0.5">{judul}</div>
                <ul className="list-disc pl-4 space-y-0.5">
                  {isi.map((b, i) => (
                    <li key={i}>{b}</li>
                  ))}
                </ul>
              </div>
            ))}
          {batasan.length > 0 && (
            <div className="pt-2 border-t border-gray-100">
              <div className="font-semibold text-red-700 mb-0.5">Jangan</div>
              <ul className="list-disc pl-4 space-y-0.5">
                {batasan.map((b, i) => (
                  <li key={i}>{b}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
