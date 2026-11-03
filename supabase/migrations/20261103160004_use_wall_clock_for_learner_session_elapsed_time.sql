-- Use wall-clock timestamps for elapsed learning time, including when the
-- functions are exercised inside a longer-lived transaction.

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
    v_previous timestamptz;
    v_now timestamptz := clock_timestamp();
    v_counted integer := 0;
begin
    select last_heartbeat_at into v_previous
      from public.learning_sessions
     where id = p_session_id
       and learner_id = p_learner_id
       and account_type = p_account_type
       and status = 'active'
     for update;

    if not found then
        return -1;
    end if;

    if p_active then
        v_counted := least(60, greatest(0, floor(extract(epoch from (v_now - v_previous)))::integer));
    end if;

    update public.learning_sessions
       set active_seconds = active_seconds + v_counted,
           last_heartbeat_at = v_now
     where id = p_session_id
       and learner_id = p_learner_id
       and account_type = p_account_type
       and status = 'active';

    return v_counted;
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
    v_previous timestamptz;
    v_now timestamptz := clock_timestamp();
    v_counted integer := 0;
begin
    select last_heartbeat_at into v_previous
      from public.learning_sessions
     where id = p_session_id
       and learner_id = p_learner_id
       and account_type = p_account_type
       and status = 'active'
     for update;

    if not found then
        return 0;
    end if;

    if p_active then
        v_counted := least(60, greatest(0, floor(extract(epoch from (v_now - v_previous)))::integer));
    end if;

    update public.learning_sessions
       set active_seconds = active_seconds + v_counted,
           last_heartbeat_at = v_now,
           ended_at = v_now,
           status = 'ended'
     where id = p_session_id
       and learner_id = p_learner_id
       and account_type = p_account_type
       and status = 'active';

    return v_counted;
end;
$$;

revoke all on function public.heartbeat_learner_learning_session(uuid, uuid, text, boolean) from public, anon, authenticated;
revoke all on function public.end_learner_learning_session(uuid, uuid, text, boolean) from public, anon, authenticated;
grant execute on function public.heartbeat_learner_learning_session(uuid, uuid, text, boolean) to service_role;
grant execute on function public.end_learner_learning_session(uuid, uuid, text, boolean) to service_role;
