"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import StatCard from "@/components/StatCard";
import { API, api, EventItem, Statistics, videoUrl, VideoSource } from "@/lib/api";

export default function DashboardPage() {
  const [stats, setStats] = useState<Statistics | null>(null);
  const [videos, setVideos] = useState<VideoSource[]>([]);
  const [events, setEvents] = useState<EventItem[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([
      api<Statistics>("/api/statistics"),
      api<VideoSource[]>("/api/cameras"),
      api<EventItem[]>("/api/events?limit=6"),
    ]).then(([s, v, e]) => { setStats(s); setVideos(v); setEvents(e); }).catch(e => setError(e.message));
  }, []);

  const names = Object.fromEntries(videos.map(v => [v.id, v.name]));
  const systemLevel = !stats ? "LOADING" : stats.alert_count > 0 ? "ALERT" : stats.watch_count > 0 ? "WATCH" : "NORMAL";
  return (
    <main className="p-4 sm:p-5 lg:p-7 xl:p-8">
      <header className="mb-7 flex flex-wrap items-start justify-between gap-5 border-b border-panelborder/80 pb-6">
        <div className="max-w-2xl">
          <div className="flex items-center gap-2 font-osd text-[9px] uppercase tracking-[.24em] text-osd"><span className="h-px w-8 bg-osd"/> Command deck / 01</div>
          <h1 className="mt-3 font-display text-3xl font-semibold tracking-[-.025em] sm:text-[34px]">ศูนย์ตรวจสอบวิดีโอ</h1>
          <p className="mt-2 text-sm leading-relaxed text-muted">ติดตามวิดีโอที่วิเคราะห์แล้ว เหตุการณ์ล่าสุด และคิวที่รอเจ้าหน้าที่ตรวจสอบจากข้อมูลจริง</p>
        </div>
        <div className={`min-w-[176px] rounded-xl border bg-panel/90 px-4 py-3 ${systemLevel === "ALERT" ? "border-alert/35 text-alert" : systemLevel === "WATCH" ? "border-watch/35 text-watch" : "border-osd/35 text-osd"}`}>
          <div className="font-osd text-[9px] uppercase tracking-[.18em] text-muted">System posture</div>
          <div className="mt-2 flex items-center gap-2 font-osd text-sm"><span className="status-beacon h-2 w-2 rounded-full bg-current"/> {systemLevel}</div>
        </div>
      </header>
      {error && <div className="mb-4 rounded border border-alert/50 bg-alert/10 p-3 text-sm text-alert">{error}</div>}
      <section aria-label="สรุปสถานะ" className="mb-8 grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-6">
        <StatCard label="Video Sources" value={stats ? stats.cameras_total : "—"} />
        <StatCard label="Available" value={stats ? stats.cameras_online : "—"} />
        <StatCard label="WATCH" value={stats ? stats.watch_count : "—"} accent="watch" />
        <StatCard label="ALERT" value={stats ? stats.alert_count : "—"} accent="alert" />
        <StatCard label="Restricted / Loiter" value={stats ? `${stats.restricted_zone_count} / ${stats.loitering_count}` : "—"} />
        <StatCard label="Pending Review" value={stats ? stats.pending_review_count : "—"} accent="watch" />
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,1.65fr)_minmax(330px,1fr)]">
        <div>
          <div className="mb-3 flex items-end justify-between border-b border-panelborder/70 pb-3">
            <div><p className="font-osd text-[9px] uppercase tracking-[.2em] text-muted">Evidence feeds</p><h2 className="mt-1 font-display text-lg font-semibold">วิดีโอที่พร้อมตรวจสอบ</h2></div>
            <Link href="/videos" className="rounded-md px-2 py-1 text-xs text-osd hover:bg-osd/10">จัดการ MP4 <span aria-hidden="true">→</span></Link>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            {videos.slice(0, 4).map(video => (
              <Link href={`/videos/${video.id}`} key={video.id} className="surface-hover group overflow-hidden rounded-xl border border-panelborder bg-panel/95">
                <div className="camera-frame relative aspect-video overflow-hidden bg-black">
                  <DashboardVideo source={video}/>
                  <div className="absolute left-4 top-4 rounded-md border border-osd/25 bg-base/85 px-2 py-1 font-osd text-[9px] text-osd backdrop-blur">FEED {String(video.id).padStart(2, "0")} · LOOP</div>
                </div>
                <div className="flex items-center justify-between gap-3 p-4"><div className="min-w-0"><div className="truncate font-medium">{video.name}</div><div className="mt-1 truncate text-xs text-muted">{video.location}</div></div><span className="font-osd text-[9px] uppercase text-muted">MP4</span></div>
              </Link>
            ))}
            {!videos.length && <div className="rounded border border-dashed border-panelborder p-8 text-center text-sm text-muted">ยังไม่มีวิดีโอ</div>}
          </div>
        </div>

        <div>
          <div className="mb-3 flex items-end justify-between border-b border-panelborder/70 pb-3">
            <div><p className="font-osd text-[9px] uppercase tracking-[.2em] text-muted">Review queue</p><h2 className="mt-1 font-display text-lg font-semibold">เหตุการณ์ล่าสุด</h2></div>
            <Link href="/events" className="rounded-md px-2 py-1 text-xs text-osd hover:bg-osd/10">ดูทั้งหมด <span aria-hidden="true">→</span></Link>
          </div>
          <div className="overflow-hidden rounded-xl border border-panelborder bg-panel/95">
            {events.map(event => (
              <div key={event.id} className="flex gap-3 border-b border-panelborder/80 p-3.5 last:border-0 hover:bg-panelraised/60">
                <div className="h-14 w-20 shrink-0 overflow-hidden rounded-md border border-panelborder bg-base">
                  {event.snapshot && <img src={`${API}${event.snapshot}`} alt="Event snapshot" className="h-full w-full object-cover" />}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex justify-between gap-2"><span className="truncate text-sm font-medium capitalize">{event.event_type.replaceAll("_", " ")}</span><span className={`rounded px-1.5 py-0.5 font-osd text-[9px] ${event.alert_level === "ALERT" ? "bg-alert/10 text-alert" : "bg-watch/10 text-watch"}`}>{event.alert_level}</span></div>
                  <div className="text-xs text-muted">{names[event.camera_id] || `Video #${event.camera_id}`} · Person #{event.track_id ?? "—"}</div>
                  <div className="mt-1 font-osd text-[10px] text-muted">{new Date(event.timestamp).toLocaleString("th-TH")} · {event.review_status}</div>
                </div>
              </div>
            ))}
            {!events.length && <div className="p-8 text-center text-sm text-muted">ยังไม่มี Event — วิเคราะห์วิดีโอเพื่อเริ่มต้น</div>}
          </div>
        </div>
      </section>
    </main>
  );
}

function DashboardVideo({source}:{source:VideoSource}){
  const [analyzed,setAnalyzed]=useState(true);
  useEffect(()=>setAnalyzed(true),[source.id]);
  const processed=`${API}/media/processed/camera_${source.id}_analyzed_h264.mp4`;
  return <><video key={`${source.id}-${analyzed}`} src={analyzed?processed:videoUrl(source)} poster={`${API}/api/cameras/${source.id}/preview`} autoPlay muted loop playsInline preload="metadata" onError={()=>{if(analyzed)setAnalyzed(false)}} className="h-full w-full object-cover opacity-90 transition duration-300 group-hover:scale-[1.015] group-hover:opacity-100"/><div className={`absolute bottom-4 right-4 rounded-md border bg-base/85 px-2 py-1 font-osd text-[9px] backdrop-blur ${analyzed?"border-osd/25 text-osd":"border-watch/25 text-watch"}`}>{analyzed?"ANALYZED · BOXES":"SOURCE · ANALYZE FIRST"}</div></>;
}
