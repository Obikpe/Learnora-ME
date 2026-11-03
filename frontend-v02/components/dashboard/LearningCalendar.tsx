"use client";

import { useMemo, useState } from "react";
import { CalendarDays, ChevronLeft, ChevronRight } from "lucide-react";

function localDateKey(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return [date.getFullYear(), String(date.getMonth() + 1).padStart(2, "0"), String(date.getDate()).padStart(2, "0")].join("-");
}

export default function LearningCalendar({ courses }: { courses: any[] }) {
  const [month, setMonth] = useState(() => new Date(new Date().getFullYear(), new Date().getMonth(), 1));
  const activityDays = useMemo(() => {
    const keys = new Set<string>();
    for (const row of courses) {
      for (const value of [row.enrolment?.enrolled_at, row.last_activity_at, row.enrolment?.completed_at]) {
        if (value) keys.add(localDateKey(value));
      }
    }
    return keys;
  }, [courses]);
  const year = month.getFullYear();
  const monthIndex = month.getMonth();
  const firstWeekday = (new Date(year, monthIndex, 1).getDay() + 6) % 7;
  const daysInMonth = new Date(year, monthIndex + 1, 0).getDate();
  const cellCount = Math.ceil((firstWeekday + daysInMonth) / 7) * 7;
  const cells = Array.from({ length: cellCount }, (_, index) => {
    const day = index - firstWeekday + 1;
    return day > 0 && day <= daysInMonth ? day : null;
  });
  const today = new Date();
  const monthActivityCount = Array.from(activityDays).filter(key => key.startsWith(`${year}-${String(monthIndex + 1).padStart(2, "0")}-`)).length;

  return <section className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-5">
    <div className="flex items-center justify-between gap-3">
      <div className="flex items-center gap-2"><CalendarDays size={17} className="text-[var(--primary)]"/><h2 className="text-sm font-bold text-[var(--text-heading)]">Learning calendar</h2></div>
      <div className="flex items-center gap-1">
        <button type="button" aria-label="Previous month" onClick={() => setMonth(new Date(year, monthIndex - 1, 1))} className="grid size-8 place-items-center rounded-md hover:bg-[var(--bg-soft)]"><ChevronLeft size={16}/></button>
        <button type="button" aria-label="Next month" onClick={() => setMonth(new Date(year, monthIndex + 1, 1))} className="grid size-8 place-items-center rounded-md hover:bg-[var(--bg-soft)]"><ChevronRight size={16}/></button>
      </div>
    </div>
    <div className="mt-4 flex items-center justify-between">
      <h3 className="text-sm font-semibold text-[var(--text-heading)]">{month.toLocaleDateString("en-GB", { month: "long", year: "numeric" })}</h3>
      <span className="text-[11px] text-[var(--text-muted)]">{monthActivityCount} active {monthActivityCount === 1 ? "day" : "days"}</span>
    </div>
    <div className="mt-4 grid grid-cols-7 gap-y-2 text-center">
      {["M","T","W","T","F","S","S"].map((label, index) => <span key={label + index} className="pb-1 text-[10px] font-semibold text-[var(--text-muted)]">{label}</span>)}
      {cells.map((day, index) => {
        if (!day) return <span key={index} className="h-9"/>;
        const key = `${year}-${String(monthIndex + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
        const active = activityDays.has(key);
        const isToday = today.getFullYear() === year && today.getMonth() === monthIndex && today.getDate() === day;
        return <span key={key} className="relative grid h-9 place-items-center">
          <span className={"grid size-8 place-items-center rounded-full text-xs " + (isToday ? "bg-[var(--primary)] font-bold text-[var(--on-primary)]" : active ? "bg-[var(--primary-tint)] font-semibold text-[var(--primary)]" : "text-[var(--text-body)]")}>{day}</span>
          {active && !isToday && <span className="absolute bottom-0.5 size-1 rounded-full bg-[var(--primary)]"/>}
        </span>;
      })}
    </div>
  </section>;
}
