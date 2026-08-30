export default function StatCard({
  label,
  value,
  accent = "ink",
}: {
  label: string;
  value: string | number;
  accent?: "ink" | "watch" | "alert" | "osd";
}) {
  const accentClass = {
    ink: "text-ink",
    watch: "text-watch",
    alert: "text-alert",
    osd: "text-osd",
  }[accent];

  const railClass = {
    ink: "from-info/70",
    watch: "from-watch",
    alert: "from-alert",
    osd: "from-osd",
  }[accent];

  return (
    <div className="relative min-h-[112px] overflow-hidden rounded-xl border border-panelborder bg-panel/90 px-4 py-4 shadow-[inset_0_1px_0_rgba(255,255,255,.025)]">
      <div className={`absolute inset-x-0 top-0 h-px bg-gradient-to-r ${railClass} to-transparent`} />
      <div className="flex items-start justify-between gap-3">
        <div className="font-osd text-[10px] uppercase leading-relaxed tracking-[.16em] text-muted">{label}</div>
        <span className={`mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-current ${accentClass}`} aria-hidden="true" />
      </div>
      <div className={`mt-3 font-osd text-[28px] font-medium leading-none tracking-tight ${accentClass}`}>{value}</div>
    </div>
  );
}
