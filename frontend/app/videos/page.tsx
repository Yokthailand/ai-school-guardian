"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { API, api, VideoSource } from "@/lib/api";
import ConfirmDialog from "@/components/ConfirmDialog";

export default function VideosPage() {
  const [videos, setVideos] = useState<VideoSource[]>([]);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [deleteTarget, setDeleteTarget] = useState<VideoSource | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState("");
  const load = () => api<VideoSource[]>("/api/cameras").then(setVideos).catch(e => setMessage(e.message));
  useEffect(() => { load(); }, []);

  async function upload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setMessage("");
    const form = new FormData(event.currentTarget);
    try {
      await api("/api/videos", { method: "POST", body: form });
      event.currentTarget.reset(); setMessage("อัปโหลด MP4 สำเร็จ"); await load();
    } catch (e) { setMessage(e instanceof Error ? e.message : "Upload failed"); }
    finally { setBusy(false); }
  }

  async function remove() {
    if (!deleteTarget) return;
    setDeleting(true); setDeleteError("");
    try {
      await api(`/api/cameras/${deleteTarget.id}`, { method: "DELETE" });
      setDeleteTarget(null); await load();
    } catch (error) {
      setDeleteError(error instanceof Error ? error.message : "ลบวิดีโอไม่สำเร็จ");
    } finally { setDeleting(false); }
  }

  return <main className="p-5 lg:p-7">
    <div className="mb-6"><p className="font-osd text-[10px] uppercase tracking-[.25em] text-osd">Input management</p><h1 className="mt-1 font-display text-2xl font-semibold">MP4 Library</h1><p className="mt-1 text-sm text-muted">เพิ่มไฟล์บันทึกเหตุการณ์ กำหนดพื้นที่ แล้วส่งเข้ากระบวนการ AI</p></div>
    <form onSubmit={upload} noValidate className="mb-7 grid gap-4 rounded-xl border border-panelborder bg-panel/90 p-5 shadow-[inset_0_1px_0_rgba(255,255,255,.025)] md:grid-cols-2 xl:grid-cols-[1fr_1fr_1fr_1.4fr_auto]">
      <label className="text-xs text-muted">ชื่อวิดีโอ<input name="name" required placeholder="เช่น หน้าอาคารเรียน" className="mt-1 w-full rounded border border-panelborder bg-base px-3 py-2 text-sm text-ink" /></label>
      <label className="text-xs text-muted">สถานที่<input name="location" required placeholder="School entrance" className="mt-1 w-full rounded border border-panelborder bg-base px-3 py-2 text-sm text-ink" /></label>
      <label className="text-xs text-muted">สภาพแวดล้อม<select name="environment" className="mt-1 w-full rounded border border-panelborder bg-base px-3 py-2 text-sm text-ink"><option value="normal">Normal Lighting</option><option value="low_light">Low Light</option><option value="partial_occlusion">Partial Occlusion</option></select></label>
      <label className="text-xs text-muted">ไฟล์ MP4<input name="file" type="file" required accept="video/mp4,.mp4" className="mt-1 block w-full text-sm text-muted file:mr-3 file:rounded file:border-0 file:bg-osd/10 file:px-3 file:py-2 file:text-osd" /></label>
      <button disabled={busy} aria-busy={busy} className="min-h-11 self-end rounded-lg bg-osd px-5 py-2 text-sm font-semibold text-base shadow-[0_8px_22px_rgba(57,213,195,.12)] hover:bg-[#57dfcf] disabled:opacity-50">{busy ? "กำลังอัปโหลด…" : "อัปโหลด MP4"}</button>
    </form>
    {message && <div className="mb-4 text-sm text-watch">{message}</div>}
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      {videos.map(video => <article key={video.id} className="surface-hover overflow-hidden rounded-xl border border-panelborder bg-panel/95">
        <div className="camera-frame"><img src={`${API}/api/cameras/${video.id}/preview`} alt={`ภาพตัวอย่าง ${video.name}`} className="aspect-video w-full bg-black object-cover" /></div>
        <div className="p-4"><div className="flex items-start justify-between gap-2"><div><h2 className="font-medium">{video.name}</h2><p className="text-xs text-muted">{video.location}</p></div><span className="rounded bg-osd/10 px-2 py-1 font-osd text-[10px] text-osd">MP4</span></div>
          <div className="mt-2 font-osd text-[10px] uppercase text-muted">{video.environment?.replaceAll("_"," ") || "normal"}</div><div className="mt-4 flex gap-2"><Link href={`/videos/${video.id}`} className="flex-1 rounded-lg bg-osd px-3 py-2.5 text-center text-xs font-semibold text-base hover:bg-[#57dfcf]">เปิดและวิเคราะห์</Link><button type="button" onClick={() => { setDeleteError(""); setDeleteTarget(video); }} className="rounded-lg border border-alert/40 px-3 py-2 text-xs text-alert hover:bg-alert/10">ลบ</button></div>
        </div>
      </article>)}
    </div>
    <ConfirmDialog open={Boolean(deleteTarget)} title={`ลบ “${deleteTarget?.name ?? "วิดีโอ"}” หรือไม่?`} description="วิดีโอ โซน และเหตุการณ์ที่เชื่อมโยงจะถูกลบถาวรและไม่สามารถกู้คืนได้" confirmLabel="ลบวิดีโอถาวร" busy={deleting} error={deleteError} onCancel={() => { if (!deleting) setDeleteTarget(null); }} onConfirm={remove}/>
  </main>;
}
