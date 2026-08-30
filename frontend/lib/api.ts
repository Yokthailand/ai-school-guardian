const browserApi =
  typeof window !== "undefined"
    ? `${window.location.protocol}//${window.location.hostname}:8000`
    : "http://localhost:8000";

export const API = process.env.NEXT_PUBLIC_API_URL || browserApi;

export type VideoSource = {
  id: number;
  name: string;
  location: string | null;
  source: "mp4";
  source_uri: string | null;
  status: "online" | "offline";
  environment: "normal" | "low_light" | "partial_occlusion";
};

export type Zone = {
  id: number;
  camera_id: number;
  name: string;
  polygon: number[][];
  zone_type: "restricted" | "loitering";
  loitering_threshold: number;
};

export type EventItem = {
  id: number;
  camera_id: number;
  track_id: number | null;
  event_type: string;
  alert_level: "NORMAL" | "WATCH" | "ALERT";
  confidence: number | null;
  snapshot: string | null;
  timestamp: string;
  video_seconds: number | null;
  response_time_ms: number | null;
  review_status: "pending" | "confirmed" | "rejected";
  reviewed_by: string | null;
  reviewed_at: string | null;
};

export type Statistics = {
  alerts_today: number;
  restricted_zone_count: number;
  loitering_count: number;
  risk_object_count: number;
  cameras_online: number;
  cameras_total: number;
  watch_count: number;
  alert_count: number;
  pending_review_count: number;
};

export type GroundTruth = {
  id: number;
  camera_id: number;
  event_type: "normal" | "restricted_zone" | "loitering" | "risk_object";
  video_seconds: number;
  tolerance_seconds: number;
  description: string | null;
  created_at: string;
};

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API}${path}`, { cache: "no-store", ...init });
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      message = body.detail || message;
    } catch {}
    throw new Error(message);
  }
  return response.json();
}

export function videoUrl(source: VideoSource) {
  const filename = source.source_uri?.split(/[\\/]/).pop();
  return filename ? `${API}/media/videos/${filename}` : "";
}
