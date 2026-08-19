import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'INTEGRAL — Workspace Pengawasan Inspektorat II Komdigi',
  description:
    'INTEGRAL — workspace pengawasan Inspektorat II Komdigi: Reviu RKA-K/L, Reviu/Audit/Pemantauan Pengadaan, Audit Kinerja, Evaluasi SAKIP/SPIP/RB/MR, Konsultansi & Pendampingan. Terintegrasi dengan SIMWAS v2.',
};

import { ConfirmHost } from '@/components/ConfirmHost';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="id">
      <body>
        {children}
        <ConfirmHost />
      </body>
    </html>
  );
}
