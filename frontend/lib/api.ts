// API client untuk backend Audit AI v7.

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

export function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('audit_v7_token');
}

export function setToken(token: string): void {
  localStorage.setItem('audit_v7_token', token);
}

export function clearToken(): void {
  localStorage.removeItem('audit_v7_token');
  localStorage.removeItem('audit_v7_session');
}

export function getSession(): Session | null {
  if (typeof window === 'undefined') return null;
  const raw = localStorage.getItem('audit_v7_session');
  if (!raw) return null;
  try {
    return JSON.parse(raw) as Session;
  } catch {
    // Session korup/format lama — dulu throw di sini men-crash SELURUH halaman
    // (dipanggil saat render) sampai user membersihkan localStorage manual. (#F9)
    clearToken();
    return null;
  }
}

export function setSession(session: Session): void {
  localStorage.setItem('audit_v7_session', JSON.stringify(session));
}

async function request<T>(
  path: string,
  init: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    ...(init.headers as Record<string, string>),
  };
  if (!(init.body instanceof FormData)) {
    headers['Content-Type'] = headers['Content-Type'] || 'application/json';
  }
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
  });
  if (!res.ok) {
    const text = await res.text();
    // Sesi kedaluwarsa / token tak valid → bersihkan & arahkan ke login.
    // Dikecualikan: endpoint login (401 = kredensial salah, biar pesan tampil).
    if (
      res.status === 401 &&
      !path.startsWith('/auth/login') &&
      typeof window !== 'undefined' &&
      window.location.pathname !== '/login'
    ) {
      clearToken();
      window.location.href = '/login?expired=1';
    }
    throw new Error(`${res.status}: ${text}`);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

// ===== Types =====
export type Role = 'AT' | 'KT' | 'PT' | 'PM' | 'TU' | 'ADMIN';
// Skill kini folder-driven di backend (registry) — bukan enum tetap. Tetap
// alias `string` supaya komponen lama yang mereferensikan `Skill` tidak rusak.
export type Skill = string;

export interface SkillInfo {
  slug: string;
  name: string;
  jenis: string;
  output: string;
  has_pipeline: boolean;
}

export interface User {
  id: number;
  username?: string | null;
  email: string;
  nama_lengkap: string;
  nip: string;
  role_default: Role;
}

export interface Session {
  user: User;
  role_aktif: Role;
  token: string;
}

export interface Penugasan {
  id: number;
  kode: string;
  obyek: string;
  skill: Skill;
  /** Identitas ala SIMWAS. Keduanya MENENTUKAN skill lewat matriks di backend —
   *  skill bukan lagi pilihan bebas. Null pada penugasan lama. */
  jenis_penugasan?: string | null;
  sub_penugasan?: string | null;
  nomor_st: string | null;
  tanggal_st: string | null;
  status: string;
  folder_path: string;
  created_at: string;
  updated_at: string;
}

export interface Dokumen {
  id: number;
  penugasan_id: number;
  nama_file: string;
  jenis: string | null;
  sha256: string;
  size_bytes: number;
  status: 'UPLOADED' | 'INGESTING' | 'READY' | 'FAILED';
  ingested_json_path: string | null;
  error_message: string | null;
  uploaded_at: string;
  ingested_at: string | null;
}

// ===== API =====
/** Satu kriteria pengawasan. `UNGGAHAN` = berkas + rujukan pasal yang dipakai;
 *  `KETIK` = kriteria yang diketik auditor (untuk ketentuan tanpa berkas digital). */
export type KriteriaEntri = {
  id?: string;
  tipe: 'UNGGAHAN' | 'KETIK';
  file?: string;
  nama_file?: string;
  pindai?: boolean;
  rujukan?: Array<{ pasal: string; halaman: string }>;
  sumber?: string;
  teks?: string;
};

export const api = {
  /** Login (Workstream B): username + password. Jalur legacy {role,email} masih
   * didukung backend di dev (untuk transisi), tapi UI utama pakai username+password. */
  login: (body: { username?: string; password?: string; role?: Role; email?: string }) =>
    request<Session>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  /** Ganti password sendiri (B4). Perlu sesi aktif + password lama benar. */
  changePassword: (old_password: string, new_password: string) =>
    request<void>('/auth/change-password', {
      method: 'POST',
      body: JSON.stringify({ old_password, new_password }),
    }),

  /** Daftar user seed (opsional filter role). Dipakai layar login untuk
   * memilih orang saat satu role punya >1 user (mis. beberapa Anggota Tim),
   * dan oleh KT untuk dropdown assignment sasaran. Publik (prototype). */
  listUsers: (role?: Role) =>
    request<User[]>(`/auth/users${role ? `?role=${role}` : ''}`),

  /** Daftar skill pengawasan terdaftar (folder-driven) untuk dropdown. */
  getSkills: () => request<SkillInfo[]>('/skills'),

  // ===== Baca Skill (read-only — tulis dicabut di FREE) =====

  /** Detail 1 skill: isi SKILL.md + daftar reference. */
  getSkillDetail: (slug: string) =>
    request<{ slug: string; content: string; references: string[] }>(
      `/skills/${encodeURIComponent(slug)}`
    ),

  /** Baca isi 1 file reference skill (read-only). */
  getSkillReference: (slug: string, path: string) =>
    request<{ slug: string; path: string; binary: boolean; content: string }>(
      `/skills/${encodeURIComponent(slug)}/reference?path=${encodeURIComponent(path)}`
    ),

  /** Simpan perubahan SKILL.md — PT only (validasi frontmatter di backend). */
  renderSurveyPendahuluan: (penugasanId: number) =>
    request<{ ok: boolean; path: string; name: string }>(
      `/penugasan/${penugasanId}/survey-pendahuluan`,
      { method: 'POST' },
    ),

  /** Ringkasan beranda (1 panggilan, di-cache backend ~30s) — widget dashboard. */
  getDashboardSummary: () => request<any>('/dashboard/summary'),

  /** Lembar Reviu berjenjang (level KT / PT) — aspek baku + isian + paraf. */
  getLembarReviu: (penugasanId: number, level: 'KT' | 'PT' | 'PM') =>
    request<any>(`/penugasan/${penugasanId}/lembar-reviu/${level}`),
  saveLembarReviu: (penugasanId: number, level: 'KT' | 'PT' | 'PM', body: any) =>
    request<any>(`/penugasan/${penugasanId}/lembar-reviu/${level}`, {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  // ===== Administrasi (Tahapan 8 — TU, pasca-persetujuan) =====
  getAdministrasi: (penugasanId: number) =>
    request<any>(`/penugasan/${penugasanId}/administrasi`),
  buatSuratPenyampaian: (
    penugasanId: number,
    body: { nomor?: string; tanggal?: string; tujuan?: string; perihal?: string; auditi?: string },
  ) =>
    request<{ ok: boolean; path: string; name: string }>(
      `/penugasan/${penugasanId}/administrasi/surat-penyampaian`,
      { method: 'POST', body: JSON.stringify(body) },
    ),
  uploadKelengkapan: (penugasanId: number, kode: string, file: File) => {
    const fd = new FormData();
    fd.append('kode', kode);
    fd.append('file', file);
    return request<{ ok: boolean; kode: string; name: string; path: string }>(
      `/penugasan/${penugasanId}/administrasi/kelengkapan`,
      { method: 'POST', body: fd },
    );
  },
  hapusKelengkapan: (penugasanId: number, path: string) =>
    request<{ ok: boolean }>(
      `/penugasan/${penugasanId}/administrasi/kelengkapan?path=${encodeURIComponent(path)}`,
      { method: 'DELETE' },
    ),

  /** Daftar rekomendasi TLHP (ber-aging). Filter opsional satker/status. */
  listTlhp: (params?: { satker_kode?: string; status?: string }) => {
    const qs = new URLSearchParams();
    if (params?.satker_kode) qs.set('satker_kode', params.satker_kode);
    if (params?.status) qs.set('status', params.status);
    const q = qs.toString();
    return request<{ total: number; items: any[] }>(`/tlhp${q ? `?${q}` : ''}`);
  },

  listPenugasan: () => request<Penugasan[]>('/penugasan'),

  getPenugasan: (id: number) => request<Penugasan>(`/penugasan/${id}`),

  /** Hapus penugasan + seluruh file di disk (hard delete). Hanya PT. */
  deletePenugasan: (id: number) =>
    request<{ ok: boolean; deleted: string; folder_removed: string }>(
      `/penugasan/${id}`,
      { method: 'DELETE' }
    ),

  createPenugasan: (payload: {
    obyek: string;
    /** Boleh dikosongkan: backend menurunkannya dari jenis + sub penugasan. */
    skill?: Skill;
    jenis_penugasan?: string;
    sub_penugasan?: string;
    nomor_st?: string;
    tanggal_st?: string;
  }) =>
    request<Penugasan>('/penugasan', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  /** Tebak Jenis & Sub dari judul penugasan — pembantu pengisian, bukan penentu.
   *  Yang mengikat tetap Jenis + Sub yang dipilih Pengendali Teknis. */
  deteksiSkill: (judul: string) =>
    request<{
      jenis: string | null;
      sub: string | null;
      ambigu: boolean;
      skill: string | null;
      alasan: string;
      penjelasan: string;
      jenis_pilihan: string[];
      sub_pilihan: string[];
    }>(`/penugasan/deteksi-skill?judul=${encodeURIComponent(judul)}`),

  /** Koreksi Jenis/Sub (dan karenanya skill). PT saja, hanya sebelum tahap KKP. */
  ubahSkill: (
    penugasanId: number,
    payload: { jenis_penugasan?: string; sub_penugasan?: string; skill?: string; alasan?: string }
  ) =>
    request<{ ok: boolean; skill: string; skill_sebelumnya: string; penjelasan: string }>(
      `/penugasan/${penugasanId}/skill`,
      { method: 'PUT', body: JSON.stringify(payload) }
    ),

  listDokumen: (penugasanId: number) =>
    request<Dokumen[]>(`/dokumen?penugasan_id=${penugasanId}`),

  uploadDokumen: async (penugasanId: number, file: File, jenis?: string) => {
    const fd = new FormData();
    fd.append('penugasan_id', String(penugasanId));
    fd.append('file', file);
    if (jenis) fd.append('jenis', jenis);
    return request<Dokumen>('/dokumen', { method: 'POST', body: fd });
  },

  /** Hapus 1 dokumen (file + hasil ingest) lalu reset analisis turunan. Hanya AT. */
  deleteDokumen: (dokumenId: number) =>
    request<{ ok: boolean; deleted: string; reset_downstream: string[] }>(
      `/dokumen/${dokumenId}`,
      { method: 'DELETE' }
    ),

  triggerIngestion: (penugasanId: number) =>
    request<{ penugasan_id: number; reset_downstream: string[]; dokumen_diproses: any[] }>(
      `/agen/ingest/${penugasanId}`,
      { method: 'POST' }
    ),

  /** URL untuk EventSource SSE — bukan fetch(). */
  agentStreamUrl: (
    agent: 'ingestion' | 'anggota_tim' | 'ketua_tim' | 'qc_saipi',
    penugasanId: number,
    prompt: string
  ) => {
    const token = getToken() || '';
    const qs = new URLSearchParams({
      penugasan_id: String(penugasanId),
      prompt,
    });
    // Token via query param (EventSource tidak mendukung custom headers di browser
    // standar). Untuk produksi, gunakan cookie session.
    return `${API_BASE}/agen/${agent}/stream?${qs.toString()}&_token=${encodeURIComponent(token)}`;
  },

  /** URL EventSource untuk RECONNECT ke run aktif (replay buffer + tail).
   * Bila tak ada run aktif, server kirim event `idle` lalu tutup. */
  agentAttachUrl: (
    agent: 'ingestion' | 'anggota_tim' | 'ketua_tim' | 'qc_saipi',
    penugasanId: number
  ) => {
    const token = getToken() || '';
    const qs = new URLSearchParams({ penugasan_id: String(penugasanId) });
    return `${API_BASE}/agen/${agent}/attach?${qs.toString()}&_token=${encodeURIComponent(token)}`;
  },

  /** Cek cepat (non-stream) apakah ada run agen aktif di backend. */
  getActiveRun: (
    agent: 'ingestion' | 'anggota_tim' | 'ketua_tim' | 'qc_saipi',
    penugasanId: number
  ) =>
    request<{ active: boolean; run_id?: number; text_so_far?: string }>(
      `/agen/${agent}/active?penugasan_id=${penugasanId}`
    ),
  /** History semua run agen pada penugasan ini, urutan oldest → newest.
   * Dipakai untuk persist percakapan lampau saat user login ulang. */
  getAgentHistory: (
    agent: 'ingestion' | 'anggota_tim' | 'ketua_tim' | 'qc_saipi',
    penugasanId: number
  ) =>
    request<{
      agent_name: string;
      penugasan_id: number;
      total: number;
      runs: Array<{
        id: number;
        status: string;
        input_summary: string;
        output_summary: string;
        tool_calls: Array<{ tool: string; input: any }>;
        tokens_in: number;
        tokens_out: number;
        started_at: string | null;
        ended_at: string | null;
        error_message: string | null;
      }>;
    }>(`/agen/${agent}/history?penugasan_id=${penugasanId}`),

  // ===== File output access =====

  listFiles: (penugasanId: number) =>
    request<{
      penugasan_id: number;
      folder_path: string;
      categories: Array<{
        key: string;
        label: string;
        files: Array<{
          name: string;
          path: string;
          size_bytes: number;
          mtime: string;
          ext: string;
        }>;
      }>;
    }>(`/penugasan/${penugasanId}/files`),

  /** Download file sebagai Blob — pakai untuk Save As / open. */
  downloadFile: async (penugasanId: number, path: string): Promise<Blob> => {
    const token = getToken() || '';
    const url = `${API_BASE}/penugasan/${penugasanId}/files/download?path=${encodeURIComponent(path)}`;
    const res = await fetch(url, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error(`${res.status}: ${await res.text()}`);
    return res.blob();
  },

  /** Preview text-based file (.md, .json, .txt). Return content string. */
  previewFile: (penugasanId: number, path: string, maxBytes = 50_000) =>
    request<{
      path: string;
      size_bytes: number;
      ext: string;
      truncated: boolean;
      content: string;
    }>(`/penugasan/${penugasanId}/files/preview?path=${encodeURIComponent(path)}&max_bytes=${maxBytes}`),

  // ===== Setup Penugasan (Ketua Tim only — endpoint return 403 untuk AT) =====

  getSasaranAssignment: (penugasanId: number) =>
    request<{
      penugasan_id: string;
      skill: string;
      schema_version: string;
      sasaran: Array<{
        sasaran_id: string;
        deskripsi: string;
        assigned_to: string[];
        langkah_kerja: string[];
        status: string;
        waktu?: string;
        no_kkp?: string;
        mode?: 'AI' | 'CATATAN' | 'MANUAL';
      }>;
      // Meta PKP format INTEGRAL (opsional — file lama belum punya)
      nomor_pkp?: string;
      langkah_perencanaan?: Array<{ langkah: string; pelaksana: string; waktu: string }>;
      langkah_pelaporan?: Array<{ langkah: string; pelaksana: string; waktu: string }>;
    }>(`/penugasan/${penugasanId}/sasaran-assignment`),

  saveSasaranAssignment: (
    penugasanId: number,
    sasaran: Array<{
      sasaran_id: string;
      deskripsi: string;
      assigned_to: string[];
      langkah_kerja: string[];
      status: string;
      waktu?: string;
      no_kkp?: string;
    }>,
    meta?: {
      nomor_pkp?: string;
      langkah_perencanaan?: Array<{ langkah: string; pelaksana: string; waktu: string }>;
      langkah_pelaporan?: Array<{ langkah: string; pelaksana: string; waktu: string }>;
    }
  ) =>
    request<{ ok: boolean; total_sasaran: number; path: string }>(
      `/penugasan/${penugasanId}/sasaran-assignment`,
      { method: 'PUT', body: JSON.stringify({ sasaran, ...(meta || {}) }) }
    ),

  /** Daftar Kriteria — khusus skill *-umum (criteria-driven).
   *  Skill umum tak punya kriteria baku bawaan; kriterianya datang dari auditor,
   *  lewat berkas yang diunggah (dengan rujukan pasal) atau diketik langsung. */
  getDaftarKriteria: (penugasanId: number) =>
    request<{
      berlaku: boolean;
      ada_kriteria: boolean;
      jumlah: number;
      entri: KriteriaEntri[];
      berkas_tersedia: Array<{
        dokumen_id: number;
        nama_file: string;
        status: string;
        terbaca: boolean | null;
        pindai: boolean;
        catatan_baca: string;
        halaman_total: number;
      }>;
    }>(`/penugasan/${penugasanId}/daftar-kriteria`),

  saveDaftarKriteria: (penugasanId: number, entri: KriteriaEntri[]) =>
    request<{ ok: boolean; jumlah: number; ada_kriteria: boolean; entri: KriteriaEntri[] }>(
      `/penugasan/${penugasanId}/daftar-kriteria`,
      { method: 'PUT', body: JSON.stringify({ entri }) }
    ),

  /** Cara penyusunan KKSA per sasaran — DIPILIH ANGGOTA TIM di Tahapan 3
   *  (Kertas Kerja), bukan Ketua Tim di PKP. KT/PT boleh override.
   *  AI = agen menganalisis dokumen · CATATAN = agen merumuskan dari catatan
   *  auditor · MANUAL = auditor menyusun sendiri tanpa AI. */
  setSasaranMode: (
    penugasanId: number,
    sasaranId: string,
    mode: 'AI' | 'CATATAN' | 'MANUAL'
  ) =>
    request<{ ok: boolean; sasaran_id: string; mode: string; mode_sebelumnya: string }>(
      `/penugasan/${penugasanId}/sasaran/${encodeURIComponent(sasaranId)}/mode`,
      { method: 'PUT', body: JSON.stringify({ mode }) }
    ),

  /** PT menyetujui PKP setelah KT mengisi sasaran → status PKP_DONE (v10.1: transplant tahapan v8). */
  approvePkp: (penugasanId: number) =>
    request<{ ok: boolean; message: string }>(
      `/penugasan/${penugasanId}/pkp/approve`,
      { method: 'PUT' }
    ),

  // ===== Per-Temuan Review (Prioritas 2 — HITL per-temuan) =====
  /** List semua temuan + status review-nya. */
  listTemuanReview: (penugasanId: number) =>
    request<{
      total: number;
      counts: Record<string, number>;
      items: Array<{
        id_temuan: string;
        judul: string;
        sasaran_id: string;
        ro: string;
        /** Asal-usul temuan — penentu label draf-AI. */
        origin: 'AI' | 'AI_DARI_CATATAN' | 'MANUAL';
        /** Asal bunyi pasal pada unsur Kriteria — supaya kutipan dari berkas
         *  penugasan bisa dibedakan dari kutipan referensi bawaan skill. */
        sumber_kriteria?: Array<{ tipe: string; berkas: string; bagian: string }>;
        kondisi: string;
        kriteria: string;
        sebab: string;
        akibat: string;
        anggota: string;
        dokumen_sumber: Array<{ file?: string; halaman?: number | string; kutipan?: string }>;
        dokumen_sumber_count: number;
        status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'EDITED';
        note: string | null;
        reviewed_at: string | null;
        reviewed_by_user_id: number | null;
        has_edits?: boolean;
        edited_fields?: {
          judul_temuan?: string;
          kondisi?: string;
          kriteria?: string;
          sebab?: string;
          akibat?: string;
          dokumen_sumber?: Array<{ file?: string; halaman?: number | string; kutipan?: string }>;
          kode_kondisi?: string;
          kode_penyebab?: string;
          kode_rekomendasi?: string;
        } | null;
        edit_log?: Array<{
          at: string;
          by_nama?: string;
          by_role?: string;
          changes: Record<string, { from: string; to: string }>;
          note?: string | null;
        }> | null;
      }>;
    }>(`/penugasan/${penugasanId}/temuan-review`),

  /** Submit KKP ke Ketua Tim (AT) — tandai sasaran miliknya diajukan ke KT. */
  submitKkp: (penugasanId: number) =>
    request<{ ok: boolean; submitted_count: number; sasaran: string[]; message: string }>(
      `/penugasan/${penugasanId}/kkp/submit`,
      { method: 'POST' }
    ),

  /** Setujui 1 temuan (AT/KT/PT/PM). */
  approveTemuan: (penugasanId: number, temuanId: string, note?: string) =>
    request<{ ok: boolean; id_temuan: string; status: string; reviewed_at: string | null }>(
      `/penugasan/${penugasanId}/temuan-review/${encodeURIComponent(temuanId)}/approve`,
      { method: 'POST', body: JSON.stringify({ note: note ?? null }) }
    ),

  /** Tolak 1 temuan (KT/PT/PM). */
  rejectTemuan: (penugasanId: number, temuanId: string, note?: string) =>
    request<{ ok: boolean; id_temuan: string; status: string; reviewed_at: string | null }>(
      `/penugasan/${penugasanId}/temuan-review/${encodeURIComponent(temuanId)}/reject`,
      { method: 'POST', body: JSON.stringify({ note: note ?? null }) }
    ),

  /** Bulk approve semua temuan PENDING (KT/PT/PM). */
  bulkApproveTemuan: (penugasanId: number) =>
    request<{ ok: boolean; approved_count: number; total_temuan: number }>(
      `/penugasan/${penugasanId}/temuan-review/bulk-approve`,
      { method: 'POST' }
    ),

  /** Edit field temuan via overlay (KT/PT/PM). String "" eksplisit → hapus
   * overlay key (revert ke versi agen). Field undefined → tidak ubah. */
  editTemuan: (
    penugasanId: number,
    temuanId: string,
    edits: {
      judul_temuan?: string;
      kondisi?: string;
      kriteria?: string;
      /** Kosongkan ("") untuk kembali ke versi agen. */
      sebab?: string;
      akibat?: string;
      /** [] = kembali ke versi agen. */
      dokumen_sumber?: Array<{ file: string; halaman: number | string; kutipan?: string }>;
      kode_kondisi?: string;
      kode_penyebab?: string;
      kode_rekomendasi?: string;
      note?: string;
    }
  ) =>
    request<{
      ok: boolean;
      id_temuan: string;
      status: string;
      edited_fields: Record<string, string> | null;
      has_edits: boolean;
      reviewed_at: string | null;
    }>(
      `/penugasan/${penugasanId}/temuan-review/${encodeURIComponent(temuanId)}/edit`,
      { method: 'PUT', body: JSON.stringify(edits) }
    ),

  /** Hapus 1 temuan dari temuan.json (AT/KT/PT/PM). */
  /** Tulis 1 temuan KKSA MANUAL, tanpa agen (skema 3). AT only.
   *  dokumen_sumber WAJIB >=1 dan tiap entri wajib `file` + `halaman` —
   *  doktrin kutipan sumber tidak dilonggarkan di mode manual. */
  createTemuanManual: (
    penugasanId: number,
    temuan: {
      sasaran_id: string;
      judul_temuan: string;
      kondisi: string;
      kriteria: string;
      akibat: string;
      // OPSIONAL sejak 9 Agu 2026: temuan manual diperiksa sendiri oleh auditor,
      // jadi dokumen sumber (dan halamannya) tidak lagi diwajibkan. QC SAIPI
      // tetap jalan penuh — temuan manual dikecualikan dari LAK-001/LAK-003
      // dan pengecualiannya tercatat di laporan QC (backend/app/qc_exempt.py).
      dokumen_sumber?: Array<{ file: string; halaman?: number | string; kutipan?: string }>;
      sebab?: string;
      kode_kondisi?: string;
      kode_penyebab?: string;
      kode_rekomendasi?: string;
      langkah_kerja_terkait?: string;
    }
  ) =>
    request<{ ok: boolean; id_temuan: string; origin: string; total_temuan: number }>(
      `/penugasan/${penugasanId}/temuan`,
      { method: 'POST', body: JSON.stringify(temuan) }
    ),

  /** Render KKP-{nama}.docx tanpa sesi agen (dibutuhkan mode manual). AT only. */
  renderKkp: (penugasanId: number) =>
    request<{ ok: boolean; file: string; detail: string }>(
      `/penugasan/${penugasanId}/kkp/render`,
      { method: 'POST' }
    ),

  deleteTemuan: (penugasanId: number, temuanId: string) =>
    request<{ ok: boolean; deleted: string; total_remaining: number }>(
      `/penugasan/${penugasanId}/temuan/${encodeURIComponent(temuanId)}`,
      { method: 'DELETE' }
    ),

  // ===== Reviu Konsep LHP (S3.2 — tahapan 6 LRS LHP, PT/PM) =====
  /** Riwayat reviu konsep LHP. latest_status: APPROVED | NEEDS_REVISION | null. */
  listLhpReview: (penugasanId: number) =>
    request<{
      total: number;
      latest_status: 'APPROVED' | 'NEEDS_REVISION' | null;
      items: Array<{
        id: number;
        status: 'APPROVED' | 'NEEDS_REVISION';
        catatan: string | null;
        reviewer_user_id: number | null;
        reviewer_role: string | null;
        reviewer_name: string | null;
        reviewed_at: string | null;
      }>;
    }>(`/penugasan/${penugasanId}/lhp-review`),

  /** Setujui / minta revisi konsep LHP (PT/PM only). */
  createLhpReview: (
    penugasanId: number,
    status: 'APPROVED' | 'NEEDS_REVISION',
    catatan?: string
  ) =>
    request<{
      ok: boolean;
      id: number;
      status: 'APPROVED' | 'NEEDS_REVISION';
      catatan: string | null;
      reviewer_role: string | null;
      reviewer_name: string | null;
      reviewed_at: string | null;
    }>(`/penugasan/${penugasanId}/lhp-review`, {
      method: 'POST',
      body: JSON.stringify({ status, catatan: catatan ?? null }),
    }),

  /** W1.1 — sync sasaran dari payload PKP SIMWAS (manual paste/upload hari ini;
   * source='api' placeholder 501 sampai kontrak API + SSO SIMWAS resmi). PT/KT. */
  syncSasaranFromSimwas: (
    penugasanId: number,
    payload: {
      source?: 'manual' | 'api';
      strategy?: 'replace' | 'append';
      pkp_rows: Array<{
        sasaran: string;
        langkah_kerja?: string;
        dilaksanakan_oleh?: string;
        waktu?: string;
        no_kkp?: string;
        mode?: 'AI' | 'CATATAN' | 'MANUAL';
        sasaran_id?: string;
      }>;
    }
  ) =>
    request<{
      ok: boolean;
      source: string;
      strategy: string;
      total_input_rows: number;
      total_sasaran: number;
      added_sasaran: string[];
      added_count: number;
      skipped_duplicate: number;
    }>(`/penugasan/${penugasanId}/sasaran/sync-from-simwas`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  getContextMd: (penugasanId: number) =>
    request<{ content: string; exists: boolean }>(
      `/penugasan/${penugasanId}/context-md`
    ),

  // ===== Kartu Penugasan (KP) — diisi PT, format INTEGRAL =====
  /** Baca Kartu Penugasan: markdown + nilai field form INTEGRAL + daftar sasaran. */
  getKpMd: (penugasanId: number) =>
    request<{
      content: string;
      exists: boolean;
      fields: Record<string, string> | null;
      sasaran: string[] | null;
      template_slug: string | null;
    }>(`/penugasan/${penugasanId}/kp-md`),

  /** Simpan Kartu Penugasan (PT/KT only). `sasaran` otomatis di-sync ke PKP
   * (sasaran-assignment) — meniru INTEGRAL: bagian II Pelaksanaan PKP dari sasaran KP. */
  saveKpMd: (
    penugasanId: number,
    content: string,
    fields?: Record<string, string>,
    sasaran?: string[],
    templateSlug?: string | null
  ) =>
    request<{ ok: boolean; size_bytes: number; path: string; sasaran_synced_to_pkp: number }>(
      `/penugasan/${penugasanId}/kp-md`,
      {
        method: 'PUT',
        body: JSON.stringify({
          content,
          fields: fields ?? null,
          sasaran: sasaran ?? null,
          template_slug: templateSlug ?? null,
        }),
      }
    ),

  /** Prasyarat Generate Context: sasaran (KT) + dokumen ter-digest (AT). */
  getContextReadiness: (penugasanId: number) =>
    request<{ ready: boolean; has_sasaran: boolean; has_ingested: boolean; reason: string }>(
      `/penugasan/${penugasanId}/context-readiness`
    ),

  saveContextMd: (penugasanId: number, content: string) =>
    request<{ ok: boolean; size_bytes: number; path: string }>(
      `/penugasan/${penugasanId}/context-md`,
      { method: 'PUT', body: JSON.stringify({ content }) }
    ),

  /** Cari catatan di vault pengetahuan organisasi (read-only). */
  // ===== Sasaran Template Suggestions =====
  // 3-sumber paralel untuk membantu KT setup penugasan tanpa start-from-zero.

  /** Saran template setup dari penugasan historis / skeleton pattern / catatan W3 vault. */
  getSasaranTemplates: (penugasanId: number, source: 'all' | 'historis' | 'patterns' | 'writeback' = 'all') =>
    request<{
      skill: string;
      obyek: string;
      historis?: Array<{
        kode: string;
        obyek: string;
        skill: string;
        status: string;
        similarity: number;
        total_sasaran: number;
        sasaran: Array<{
          sasaran_id: string;
          deskripsi: string;
          assigned_to: string[];
          langkah_kerja: string[];
        }>;
      }>;
      patterns?: {
        skill: string;
        total_patterns: number;
        sasaran: Array<{
          sasaran_id: string;
          deskripsi: string;
          langkah_kerja: string[];
          assigned_to: string[];
          kategori: string;
          pattern_ids: string[];
        }>;
      };
      writeback?: Array<{
        nama_file: string;
        judul: string;
        skill_label: string;
        obyek: string;
        jumlah_temuan: number;
        similarity: number;
      }>;
    }>(`/penugasan/${penugasanId}/sasaran/templates?source=${source}`),

  // ===== Feedback Aggregate Dashboard (Phase 2) =====

  /** Ringkasan agregat feedback agen cross-penugasan untuk N hari ke belakang. */
  getFeedbackAggregate: (days = 30) =>
    request<{
      days: number;
      total_feedback: number;
      by_agent: Record<string, number>;
      by_confidence: Record<string, number>;
      top_workflow_issues: Array<{
        category: string;
        severity: string;
        count: number;
        examples: string[];
      }>;
      top_substansi_issues: Array<{
        category: string;
        severity: string;
        count: number;
        examples: string[];
      }>;
      top_pattern_suggestions: Array<{
        id_proposed: string;
        judul: string;
        count: number;
        rationales: string[];
      }>;
      severity_heatmap: Record<string, Record<string, number>>;
      recent_files: Array<{
        path: string;
        full_path: string;
        agent: string;
        confidence: string;
        summary: string;
        penugasan_folder: string;
        timestamp: string | null;
        workflow_count: number;
        substansi_count: number;
        pattern_count: number;
      }>;
    }>(`/feedback/aggregate?days=${days}`),

  /** List file feedback mentah untuk drill-down. */
  listFeedback: (days = 30) =>
    request<{
      days: number;
      total: number;
      items: Array<{
        file: string;
        agent: string;
        confidence: string;
        summary: string;
        workflow_count: number;
        substansi_count: number;
        pattern_count: number;
        timestamp: string | null;
        penugasan_id: number | null;
        penugasan_obyek: string;
        penugasan_folder: string;
      }>;
    }>(`/feedback/list?days=${days}`),

  // ===== Templates KP & PKP (INTEGRAL workflow tahapan 1+2) =====
  getPenilaianLke: (penugasanId: number) =>
    request<{
      is_lke: boolean;
      skill: string;
      tersedia: boolean;
      komponen: { nama: string; bobot: any; nilai_pm: any; nilai_apip: any; delta: number | null; predikat: string; catatan?: string }[];
      total_pm: any;
      total_apip: any;
      predikat_akhir: any;
    }>(`/penugasan/${penugasanId}/penilaian-lke`),

  /** Chat bebas berbasis pengetahuan wiki (RAG). Semua role. */
};
