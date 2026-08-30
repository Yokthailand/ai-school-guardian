"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { API, api, videoUrl, VideoSource, Zone } from "@/lib/api";

type Result = { status: string; processed_video_url: string; detector_engine: string; risk_detector_engine: string; unique_people: number; max_people_in_frame: number; restricted_zone_entries: number; loitering_events: number; risk_object_events: number; processed_frames: number; events: {id:number; event_type:string}[] };

export default function AnalyzePage({ params }: { params: { id: string } }) {
  const id = Number(params.id);
  const [video, setVideo] = useState<VideoSource | null>(null);
  const [zones, setZones] = useState<Zone[]>([]);
  const [result, setResult] = useState<Result | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => {
    Promise.all([
      api<VideoSource[]>("/api/cameras"),
      api<Zone[]>(`/api/zones?camera_id=${id}`),
      api<Result>(`/api/analysis-result?camera_id=${id}`).catch(() => null),
    ]).then(([all, z, saved]) => {
      setVideo(all.find(v => v.id === id) || null);
      setZones(z);
      if (saved) setResult(saved);
    }).catch(e => setError(e.message));
  }, [id]);
  async function analyze() { setRunning(true); setError(""); try { setResult(await api<Result>(`/api/analyze-video?camera_id=${id}`, {method:"POST"})); } catch(e){setError(e instanceof Error?e.message:"Analysis failed");} finally{setRunning(false);} }
  if (!video) return <main className="p-7 text-muted">{error || "Loading video…"}</main>;
  return <main className="p-5 lg:p-7">
    <div className="mb-5 flex flex-wrap items-end justify-between gap-3"><div><Link href="/videos" className="text-xs text-osd">← MP4 Library</Link><h1 className="mt-2 font-display text-2xl font-semibold">{video.name}</h1><p className="text-sm text-muted">{video.location} · {zones.length} monitored zone(s) · {video.environment?.replaceAll("_"," ")}</p></div><button onClick={analyze} disabled={running} className="rounded bg-osd px-5 py-2.5 text-sm font-semibold text-base disabled:opacity-50">{running ? "ANALYZING VIDEO…" : "RUN AI ANALYSIS"}</button></div>
    {!zones.length && <div className="mb-4 rounded border border-watch/40 bg-watch/10 p-3 text-sm text-watch">ยังไม่มี Zone — ระบบจะตรวจจับบุคคลได้ แต่จะไม่สร้าง Restricted/Loitering Event <Link href={`/zones?video=${id}`} className="underline">สร้าง Zone</Link></div>}
    {error && <div className="mb-4 rounded border border-alert/40 bg-alert/10 p-3 text-sm text-alert">{error}</div>}
    <div className="grid gap-5 xl:grid-cols-[1.6fr_1fr]">
      <section className="rounded-lg border border-panelborder bg-panel p-3"><div className="mb-2 font-osd text-[10px] uppercase tracking-widest text-muted">{result ? "Analyzed output" : "Original recording"}</div><video key={result?.processed_video_url || "source"} src={result ? `${API}${result.processed_video_url}` : videoUrl(video)} controls className="aspect-video w-full rounded bg-black" /></section>
      <aside className="space-y-3">
        <div className="rounded-lg border border-panelborder bg-panel p-4"><div className="font-osd text-[10px] uppercase tracking-widest text-muted">Analysis status</div><div className={`mt-2 text-lg ${result ? "text-osd" : "text-muted"}`}>{running ? "Processing frames…" : result ? "Completed" : "Ready"}</div><p className="mt-2 text-xs text-muted">ไฟล์ขนาดใหญ่ใช้เวลาประมวลผล ระบบจะวาด Bounding Box, Person ID และ Zone ลงในวิดีโอผลลัพธ์</p></div>
        {result && <><div className="grid grid-cols-2 gap-2">{[["Tracked IDs",result.unique_people],["Peak people",result.max_people_in_frame],["Restricted",result.restricted_zone_entries],["Loitering",result.loitering_events],["Potential risk",result.risk_object_events],["Events",result.events.length]].map(([l,v])=><div key={l} className="rounded border border-panelborder bg-panel p-3"><div className="text-[10px] uppercase text-muted">{l}</div><div className="mt-1 font-osd text-xl text-osd">{v}</div></div>)}</div><div className="rounded border border-panelborder bg-panel p-3 text-xs text-muted">Person: <span className="text-ink">{result.detector_engine}</span><br/>Risk: <span className="text-ink">{result.risk_detector_engine}</span><br/>ทุก Event ต้องผ่านการตรวจสอบโดยผู้รับผิดชอบ</div></>}
      </aside>
    </div>
  </main>;
}
