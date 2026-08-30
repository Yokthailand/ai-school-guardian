"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect } from "react";

const links = [
  { href: "/", label: "ภาพรวม", sub: "Overview", icon: "grid" },
  { href: "/videos", label: "คลังวิดีโอ", sub: "MP4 Library", icon: "video" },
  { href: "/image-analysis", label: "ตรวจสอบรูปภาพ", sub: "Image Analysis", icon: "image" },
  { href: "/zones", label: "กำหนดพื้นที่", sub: "Zone Editor", icon: "zone" },
  { href: "/events", label: "เหตุการณ์", sub: "Event Log", icon: "event" },
  { href: "/analytics", label: "สถิติ", sub: "Analytics", icon: "chart" },
  { href: "/evaluation", label: "ประเมินระบบ", sub: "Evaluation", icon: "check" },
  { href: "/settings", label: "การตั้งค่า", sub: "Settings", icon: "settings" },
] as const;

function LineIcon({ name }: { name: (typeof links)[number]["icon"] }) {
  const paths = {
    grid: <><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></>,
    video: <><rect x="3" y="5" width="14" height="14" rx="2"/><path d="m17 10 4-2v8l-4-2"/></>,
    image: <><rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="9" cy="10" r="2"/><path d="m4 17 5-4 3 3 3-2 5 4"/></>,
    zone: <><path d="m5 6 7-3 7 4-2 11-9 3-4-8Z"/><circle cx="5" cy="6" r="1"/><circle cx="19" cy="7" r="1"/><circle cx="8" cy="21" r="1"/></>,
    event: <><path d="M12 3 2.8 19h18.4Z"/><path d="M12 9v4"/><path d="M12 17h.01"/></>,
    chart: <><path d="M4 20V10"/><path d="M10 20V4"/><path d="M16 20v-7"/><path d="M22 20H2"/></>,
    check: <><circle cx="12" cy="12" r="9"/><path d="m8 12 2.5 2.5L16 9"/></>,
    settings: <><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-2.8 2.8-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6v.2h-4V21a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1L4.2 17l.1-.1a1.7 1.7 0 0 0 .3-1.9A1.7 1.7 0 0 0 3 14H2.8v-4H3a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9L4.2 7 7 4.2l.1.1a1.7 1.7 0 0 0 1.9.3A1.7 1.7 0 0 0 10 3v-.2h4V3a1.7 1.7 0 0 0 1 1.6 1.7 1.7 0 0 0 1.9-.3l.1-.1L19.8 7l-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.6 1h.2v4H21a1.7 1.7 0 0 0-1.6 1Z"/></>,
  };
  return <svg viewBox="0 0 24 24" aria-hidden="true" className="h-[18px] w-[18px] shrink-0" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">{paths[name]}</svg>;
}

export default function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const activeLink = links.find(({ href }) => href === "/" ? pathname === "/" : pathname.startsWith(href));

  useEffect(() => {
    document.title = `${activeLink?.label ?? "AI School Guardian"} — AI School Guardian`;
  }, [activeLink]);

  return (
    <div className="app-shell min-h-screen bg-base/70 text-ink lg:grid lg:grid-cols-[264px_minmax(0,1fr)]">
      <aside className="app-sidebar z-30 border-b border-panelborder bg-[#081522]/95 backdrop-blur-xl lg:sticky lg:top-0 lg:h-screen lg:border-b-0 lg:border-r">
        <div className="p-3 lg:p-4">
          <div className="brand-mark flex items-center gap-3 rounded-xl px-3 py-3 lg:block lg:px-4 lg:py-4">
            <div className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-osd text-base shadow-[0_0_28px_rgba(57,213,195,.2)]">
              <svg viewBox="0 0 32 32" className="h-6 w-6" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="2"><path d="M16 3 5 8v7c0 7 4.7 11.7 11 14 6.3-2.3 11-7 11-14V8Z"/><path d="m10 16 4 4 8-9"/></svg>
            </div>
            <div className="min-w-0 lg:mt-3">
              <div className="truncate font-display text-[16px] font-semibold tracking-tight text-ink lg:text-[17px]">AI School Guardian</div>
              <div className="mt-0.5 font-osd text-[9px] uppercase tracking-[.2em] text-osd">Evidence review console</div>
            </div>
          </div>
        </div>
        <nav aria-label="เมนูหลัก" className="flex gap-1 overflow-x-auto px-3 pb-3 lg:flex-col lg:overflow-visible lg:px-4 lg:pb-0">
          {links.map(({ href, label, sub, icon }) => {
            const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
            return <Link key={href} href={href} aria-current={active ? "page" : undefined} className={`group relative flex min-h-11 shrink-0 items-center gap-3 rounded-lg px-3 py-2.5 text-sm ${active ? "bg-osd/[.12] text-ink shadow-[inset_3px_0_0_#39D5C3]" : "text-muted hover:bg-panelraised hover:text-ink"}`}>
              <span className={active ? "text-osd" : "text-muted group-hover:text-osd"}><LineIcon name={icon}/></span>
              <span className="leading-tight"><span className="block whitespace-nowrap font-medium">{label}</span><span className="hidden font-osd text-[9px] uppercase tracking-wider text-muted lg:block">{sub}</span></span>
            </Link>;
          })}
        </nav>
        <div className="absolute inset-x-4 bottom-4 hidden lg:block">
          <div className="rounded-xl border border-watch/25 bg-watch/[.07] p-3.5">
            <div className="flex items-center gap-2 font-osd text-[9px] uppercase tracking-[.16em] text-watch"><span className="h-1.5 w-1.5 rounded-full bg-watch"/> Human review required</div>
            <p className="mt-2 text-[11px] leading-relaxed text-muted">AI ช่วยคัดกรองเหตุการณ์เท่านั้น เจ้าหน้าที่ต้องตรวจสอบหลักฐานทุกครั้ง</p>
          </div>
          <div className="mt-3 flex items-center justify-between px-1 font-osd text-[9px] uppercase tracking-wider text-muted"><span>MP4 mode</span><span className="flex items-center gap-1.5 text-osd"><span className="status-beacon h-1.5 w-1.5 rounded-full bg-osd"/> Online</span></div>
        </div>
      </aside>
      <div className="min-w-0">{children}</div>
    </div>
  );
}
