-- Learner learning-time and meaningful-day tracking.
-- Backend service-role access only; browser clients must use the authenticated API.

create table if not exists public.learning_sessions (
    id uuid primary key default gen_random_uuid(),
    learner_id uuid not null,
    account_type text not null check (account_type in ('individual', 'cohort')),
    started_at timestamptz not null default now(),
    last_heartbeat_at timestamptz not null default now(),
    ended_at timestamptz,
    active_seconds integer not null default 0 check (active_seconds >= 0),
    timezone text not null default 'Africa/Lagos',
    status text not null default 'active' check (status in ('active', 'ended', 'interrupted')),
    created_at timestamptz not null default now(),
    check (ended_at is null or ended_at >= started_at)
);

create index if not exists learning_sessions_learner_started_idx
    on public.learning_sessions (learner_id, account_type, started_at desc);
create index if not exists learning_sessions_active_heartbeat_idx
    on public.learning_sessions (learner_id, account_type, last_heartbeat_at)
    where status = 'active';

create table if not exists public.learner_learning_days (
    id uuid primary key default gen_random_uuid(),
    learner_id uuid not null,
    account_type text not null check (account_type in ('individual', 'cohort')),
    activity_date date not null,
    timezone text not null default 'Africa/Lagos',
    activity_count integer not null default 1 check (activity_count > 0),
    activity_types text[] not null default '{}',
    last_activity_at timestamptz not null default now(),
    created_at timestamptz not null default now(),
    unique (learner_id, account_type, activity_date)
);

create index if not exists learner_learning_days_history_idx
    on public.learner_learning_days (learner_id, account_type, activity_date desc);

alter table public.learning_sessions enable row level security;
alter table public.learner_learning_days enable row level security;
revoke all on public.learning_sessions from anon, authenticated;
revoke all on public.learner_learning_days from anon, authenticated;
grant all on public.learning_sessions to service_role;
grant all on public.learner_learning_days to service_role;

create or replace function public.record_learner_learning_day(
    p_learner_id uuid,
    p_account_type text,
    p_activity_date date,
    p_timezone text,
    p_activity_type text,
    p_activity_at timestamptz
) returns void
language plpgsql
security definer
set search_path = public, pg_temp
as $$
begin
    if p_account_type not in ('individual', 'cohort') then
        raise exception 'Invalid learner account type';
    end if;
    if p_activity_type not in ('lesson_completed', 'quiz_passed', 'assignment_submitted') then
        raise exception 'Invalid learning activity type';
    end if;

    insert into public.learner_learning_days (
        learner_id, account_type, activity_date, timezone,
        activity_count, activity_types, last_activity_at
    ) values (
        p_learner_id, p_account_type, p_activity_date, p_timezone,
        1, array[p_activity_type], p_activity_at
    )
    on conflict (learner_id, account_type, activity_date)
    do update set
        activity_count = public.learner_learning_days.activity_count + 1,
        activity_types = (
            select array_agg(distinct activity_type order by activity_type)
            from unnest(public.learner_learning_days.activity_types || excluded.activity_types) as activity_type
        ),
        last_activity_at = greatest(public.learner_learning_days.last_activity_at, excluded.last_activity_at),
        timezone = excluded.timezone;
end;
$$;

revoke all on function public.record_learner_learning_day(uuid, text, date, text, text, timestamptz) from public, anon, authenticated;
grant execute on function public.record_learner_learning_day(uuid, text, date, text, text, timestamptz) to service_role;

create or replace function public.get_learner_learning_seconds(
    p_learner_id uuid,
    p_account_type text
) returns bigint
language sql
security definer
set search_path = public, pg_temp
as $$
    select coalesce(sum(active_seconds), 0)::bigint
    from public.learning_sessions
    where learner_id = p_learner_id
      and account_type = p_account_type;
$$;

revoke all on function public.get_learner_learning_seconds(uuid, text) from public, anon, authenticated;
grant execute on function public.get_learner_learning_seconds(uuid, text) to service_role;