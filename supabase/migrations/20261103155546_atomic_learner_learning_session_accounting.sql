-- Prevent duplicate active learner sessions across browser tabs and provide
-- service-role-only database operations for session creation and accounting.

create unique index if not exists learning_sessions_one_active_per_learner_idx
    on public.learning_sessions (learner_id, account_type)
    where status = 'active';

create or replace function public.start_learner_learning_session(
    p_learner_id uuid,
    p_account_type text,
    p_timezone text
) returns jsonb
language plpgsql
security definer
set search_path = public, pg_temp
as $$
declare
    v_session jsonb;
    v_now timestamptz := now();
begin
    if p_account_type not in ('individual', 'cohort') then
        raise exception 'Invalid learner account type';
    end if;

    perform pg_advisory_xact_lock(
        hashtextextended(p_learner_id::text || ':' || p_account_type, 0)
    );

    update public.learning_sessions
       set status = 'interrupted',
           ended_at = last_heartbeat_at
     where learner_id = p_learner_id
       and account_type = p_account_type
       and status = 'active'
       and last_heartbeat_at < v_now - interval '3 minutes';

    select to_jsonb(s) into v_session
      from public.learning_sessions s
     where s.learner_id = p_learner_id
       and s.account_type = p_account_type
       and s.status = 'active'
     order by s.started_at desc
     limit 1;

    if v_session is not null then
        return v_session;
    end if;

    insert into public.learning_sessions (
        learner_id, account_type, started_at, last_heartbeat_at,
        timezone, status, active_seconds
    ) values (
        p_learner_id, p_account_type, v_now, v_now,
        coalesce(nullif(p_timezone, ''), 'Africa/Lagos'), 'active', 0
    )
    returning to_jsonb(learning_sessions.*) into v_session;

    return v_session;
end;
$$;

create or replace function public.heartbeat_learner_learning_session(
    p_session_id uuid,
    p_learner_id uuid,
    p_account_type text,
    p_active boolean
) returns integer
language plpgsql
security definer
set search_path = public, pg_temp
as $$
declare
    v_counted integer;
begin
    update public.learning_sessions
       set active_seconds = active_seconds + case
               when p_active then least(
                   60,
                   greatest(0, floor(extract(epoch from (now() - last_heartbeat_at)))::integer)
               )
               else 0
           end,
           last_heartbeat_at = now()
     where id = p_session_id
       and learner_id = p_learner_id
       and account_type = p_account_type
       and status = 'active'
    returning case
        when p_active then least(
            60,
            greatest(0, floor(extract(epoch from (now() - last_heartbeat_at)))::integer)
        )
        else 0
    end into v_counted;

    if not found then
        return -1;
    end if;
    return coalesce(v_counted, 0);
end;
$$;

create or replace function public.end_learner_learning_session(
    p_session_id uuid,
    p_learner_id uuid,
    p_account_type text,
    p_active boolean
) returns integer
language plpgsql
security definer
set search_path = public, pg_temp
as $$
declare
    v_counted integer;
begin
    update public.learning_sessions
       set active_seconds = active_seconds + case
               when p_active then least(
                   60,
                   greatest(0, floor(extract(epoch from (now() - last_heartbeat_at)))::integer)
               )
               else 0
           end,
           last_heartbeat_at = now(),
           ended_at = now(),
           status = 'ended'
     where id = p_session_id
       and learner_id = p_learner_id
       and account_type = p_account_type
       and status = 'active'
    returning case
        when p_active then least(
            60,
            greatest(0, floor(extract(epoch from (now() - last_heartbeat_at)))::integer)
        )
        else 0
    end into v_counted;

    if not found then
        return 0;
    end if;
    return coalesce(v_counted, 0);
end;
$$;

revoke all on function public.start_learner_learning_session(uuid, text, text) from public, anon, authenticated;
revoke all on function public.heartbeat_learner_learning_session(uuid, uuid, text, boolean) from public, anon, authenticated;
revoke all on function public.end_learner_learning_session(uuid, uuid, text, boolean) from public, anon, authenticated;
grant execute on function public.start_learner_learning_session(uuid, text, text) to service_role;
grant execute on function public.heartbeat_learner_learning_session(uuid, uuid, text, boolean) to service_role;
grant execute on function public.end_learner_learning_session(uuid, uuid, text, boolean) to service_role;
