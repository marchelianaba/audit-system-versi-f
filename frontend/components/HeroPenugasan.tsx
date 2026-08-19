'use client';

/**
 * HeroPenugasan — header detail penugasan ala SIMWAS v2.
 *
 * Layout: 2 kolom
 *   Left (col-span-1, fixed width-ish): Info penugasan (logo unit, nomor ST,
 *     tanggal mulai/selesai, participants, days, jenis pengawasan, judul, progress)
 *   Right (col-span-2): StageGrid 7 tahapan
 */
import { StageGrid, StageInfo, StageStatus } from './StageGrid';
import { Penugasan } from '@/lib/api';

const SKILL_LABEL: Record<string, string> = {
  'reviu-rka-kl': 'Reviu RKA-K/L',
  'reviu-pengadaan': 'Reviu Pengadaan',
  'reviu-umum': 'Reviu Umum',
  'audit-umum': 'Audit Umum',
  'evaluasi-umum': 'Evaluasi Umum',
  'pemantauan-umum': 'Pemantauan Umum',
};

const SKILL_GROUP: Record<string, 'audit' | 'reviu' | 'evaluasi' | 'pemantauan'> = {
  'audit-umum': 'audit',
  'reviu-rka-kl': 'reviu',
  'reviu-pengadaan': 'reviu',
  'reviu-umum': 'reviu',
  'evaluasi-umum': 'evaluasi',
  'pemantauan-umum': 'pemantauan',
};

// Map status penugasan v7 → status tahapan workflow INTEGRAL.
// Heuristic: bila penugasan ada di status KKP_*, tahapan 3 in_progress; LHP_* tahapan 5 dst.
function deriveStageStatus(
  penugasan: Penugasan,
  stageNum: number,
  lhpReviewStatus?: 'APPROVED' | 'NEEDS_REVISION' | null,
): StageStatus {
  const status = penugasan.status as string;
  // v10.1 (transplant tahapan v8): rantai status GRANULAR KP→PKP→KKP.
  // Stage 4 (persetujuan KKP per-sasaran) & stage 6-8 tetap logika v10.
  const statusOrder = [
    'DRAFT',           // 0
    'KP_DONE',         // 1 — PT simpan KP
    'PKP_KT_DONE',     // 2 — KT simpan sasaran
    'PKP_DONE',        // 3 — PT setujui PKP
    'INGESTING',       // 4 — dokumen sedang diproses
    'KKP_IN_PROGRESS', // 5 — AT mengerjakan KKP
    'KKP_QC',          // 6 — legacy
    'KKP_AT_DONE',     // 7 — semua AT submit temuan
    'KKP_DONE',        // 8 — semua sasaran DISETUJUI_KT
    'LHP_IN_PROGRESS', // 9 — Konsep Laporan sedang dibuat
    'LHP_QC',          // 10 — legacy
    'LHP_DONE',        // 11 — Konsep Laporan tersedia
  ];
  const idx = statusOrder.indexOf(status);

  // Stage 0 (Survey) — hanya audit-*
  if (stageNum === 0) {
    return SKILL_GROUP[penugasan.skill] === 'audit' ? 'pending' : 'locked';
  }

  // Stage 1 — Kartu Penugasan: in_progress saat DRAFT, done setelah PT simpan
  if (stageNum === 1) {
    return status === 'DRAFT' ? 'in_progress' : (idx >= 1 ? 'done' : 'in_progress');
  }

  // Stage 2 — PKP: locked sampai KP_DONE; in_progress saat KT simpan; done saat PT setujui
  if (stageNum === 2) {
    if (idx < 1) return 'locked';
    if (idx >= 3) return 'done';
    if (status === 'PKP_KT_DONE') return 'in_progress';
    return 'pending';
  }

  // Stage 3 — KKP: locked sampai PKP_DONE; done saat semua AT submit (KKP_AT_DONE)
  if (stageNum === 3) {
    if (idx < 3) return 'locked';
    if (idx >= 7) return 'done';
    if (idx >= 4) return 'in_progress';
    return 'pending';
  }

  // Stage 4 — Persetujuan KKP oleh KT per-sasaran (v10, DIPERTAHANKAN): KT bisa
  // setujui/kembalikan per-AT secara bertahap; done saat SEMUA sasaran DISETUJUI_KT.
  if (stageNum === 4) {
    if (status === 'KKP_DONE' || status === 'LHP_IN_PROGRESS' || status === 'LHP_QC' || status === 'LHP_DONE') return 'done';
    return idx >= 5 ? 'in_progress' : 'pending';
  }

  // Stage 5 — Konsep Laporan: locked sampai KKP_DONE; revert ke in_progress bila LRS LHP ditolak
  if (stageNum === 5) {
    if (idx < 8) return 'locked';
    if (status === 'LHP_DONE') {
      return lhpReviewStatus === 'NEEDS_REVISION' ? 'in_progress' : 'done';
    }
    if (idx >= 9) return 'in_progress';
    return 'pending';
  }

  // Stage 6 LRS LHP — reviu PT/PM atas konsep LHP.
  //   APPROVED → done; NEEDS_REVISION → in_progress (revisi diminta);
  //   belum direviu tapi LHP_DONE → in_progress (menunggu reviu); else locked.
  if (stageNum === 6) {
    if (lhpReviewStatus === 'APPROVED') return 'done';
    if (lhpReviewStatus === 'NEEDS_REVISION') return 'in_progress';
    return status === 'LHP_DONE' ? 'in_progress' : 'locked';
  }

  // Stage 7 Laporan Hasil — siap (pending) hanya setelah konsep LHP disetujui PT/PM.
  if (stageNum === 7) {
    return lhpReviewStatus === 'APPROVED' ? 'pending' : 'locked';
  }

  // Stage 8 Administrasi (TU) — terbuka hanya setelah laporan disetujui (garis serah).
  if (stageNum === 8) {
    return lhpReviewStatus === 'APPROVED' ? 'pending' : 'locked';
  }

  return 'pending';
}

export function HeroPenugasan({
  penugasan,
  lhpReviewStatus,
  onStageSelect,
  activeStage,
}: {
  penugasan: Penugasan;
  lhpReviewStatus?: 'APPROVED' | 'NEEDS_REVISION' | null;
  /** Kartu tahapan = navigasi (ala SIMWAS): klik → buka workspace tahapan tsb. */
  onStageSelect?: (stageNum: number) => void;
  /** Tahapan yang sedang dibuka — di-highlight di grid. */
  activeStage?: number;
}) {
  const skillGroup = SKILL_GROUP[penugasan.skill];
  const showSurvey = skillGroup === 'audit';
  const skillLabel = SKILL_LABEL[penugasan.skill] || penugasan.skill;
  const st = (n: number) => deriveStageStatus(penugasan, n, lhpReviewStatus);

  // Progress % berbasis tahapan done
  const totalStages = showSurvey ? 9 : 8;
  const stages: StageInfo[] = [
    { num: 0, label: 'Survey Pendahuluan', hint: 'Hanya audit-*', status: st(0) },
    { num: 1, label: 'Kartu Penugasan', hint: 'PT · template wiki', status: st(1) },
    { num: 2, label: 'PKP', hint: 'KT · detail dari KP', status: st(2) },
    { num: 3, label: 'KKP', hint: 'AT · AI + HITL', status: st(3) },
    { num: 4, label: 'LRS KK', hint: 'auto dari approval', status: st(4) },
    { num: 5, label: 'Konsep Laporan', hint: 'KT · LHP draft', status: st(5) },
    { num: 6, label: 'LRS LHP', hint: 'PT/PM review', status: st(6) },
    { num: 7, label: 'Laporan Hasil', hint: 'Inspektur', status: st(7) },
    { num: 8, label: 'Administrasi', hint: 'TU · pasca-persetujuan', status: st(8) },
  ];

  const doneCount = stages.filter((s, i) => (i > 0 || showSurvey) && s.status === 'done').length;
  const progress = Math.round((doneCount / totalStages) * 100);

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      {/* Left panel — info penugasan */}
      <div className="md:col-span-1 integral-card p-4">
        <div className="flex items-center gap-3 mb-3 pb-3 border-b border-gray-100">
          <div className="w-10 h-10 rounded-lg bg-primary-100 text-primary-dark flex items-center justify-center text-lg">🏛</div>
          <div>
            <div className="font-semibold text-sm">Inspektorat II</div>
            <div className="text-xs text-gray-500 font-mono">{penugasan.nomor_st || '[Nomor ST belum diisi]'}</div>
          </div>
        </div>
        <div className="space-y-2 text-xs">
          <div>
            <div className="text-gray-400 uppercase text-[10px] mb-0.5">Tanggal ST</div>
            <div>{penugasan.tanggal_st || <span className="text-gray-400">—</span>}</div>
          </div>
          <div>
            <div className="text-gray-400 uppercase text-[10px] mb-0.5">Jenis Penugasan</div>
            <div className="font-medium text-primary-dark">
              {penugasan.jenis_penugasan || <span className="text-gray-400">—</span>}
              {penugasan.sub_penugasan && (
                <span className="font-normal text-gray-600"> · {penugasan.sub_penugasan}</span>
              )}
            </div>
          </div>
          <div>
            <div className="text-gray-400 uppercase text-[10px] mb-0.5">Skill</div>
            <div className="font-medium text-primary-dark">
              {skillLabel}
              {penugasan.jenis_penugasan && penugasan.sub_penugasan && (
                <span className="ml-1 text-[10px] font-normal text-green-700">
                  ditentukan otomatis
                </span>
              )}
            </div>
          </div>
          <div>
            <div className="text-gray-400 uppercase text-[10px] mb-0.5">Obyek</div>
            <div>{penugasan.obyek}</div>
          </div>
          <div>
            <div className="text-gray-400 uppercase text-[10px] mb-0.5">Status</div>
            <div className="inline-block px-2 py-0.5 rounded-full bg-primary-50 text-primary text-[11px] font-semibold">
              {penugasan.status}
            </div>
          </div>
        </div>

        {/* Progress bar */}
        <div className="mt-4 pt-3 border-t border-gray-100">
          <div className="flex justify-between text-xs mb-1.5">
            <span className="text-gray-500">Progres Tahapan</span>
            <span className="font-semibold text-primary">{doneCount}/{totalStages} • {progress}%</span>
          </div>
          <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
            <div className="h-full integral-gradient rounded-full transition-all" style={{ width: `${progress}%` }}></div>
          </div>
        </div>
      </div>

      {/* Right panel — 7/8 tahapan grid */}
      <div className="md:col-span-2 integral-card p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-sm text-primary-dark">Detail Pelaksanaan Penugasan</h3>
          <span className="text-[10px] text-gray-400 uppercase tracking-wider">
            klik tahapan untuk membuka · {totalStages} tahap
          </span>
        </div>
        <StageGrid
          stages={stages}
          showSurvey={showSurvey}
          activeNum={activeStage}
          onSelect={onStageSelect ? (s) => onStageSelect(Number(s.num)) : undefined}
        />
      </div>
    </div>
  );
}
