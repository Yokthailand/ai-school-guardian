import type { Metadata } from "next";
import { IBM_Plex_Sans, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";
import AppShell from "@/components/AppShell";

const display = IBM_Plex_Sans({
  subsets: ["latin"],
  weight: ["500", "600", "700"],
  variable: "--font-display",
});
const body = IBM_Plex_Sans({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-body",
});
const osd = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-osd",
});

export const metadata: Metadata = {
  title: "AI School Guardian — Recorded Video Analysis",
  description: "AI-assisted CCTV monitoring for school safety",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="th">
      <body className={`${display.variable} ${body.variable} ${osd.variable} font-body`}>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
