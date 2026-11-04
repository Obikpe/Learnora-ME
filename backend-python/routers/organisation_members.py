"""Organisation membership API with lifecycle and hard capacity enforcement."""
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone
import re
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from .auth import supabase
from .permissions import PermissionContext, require_permission
from services.capacity import ensure_org_capacity
from services.audit import audit

router=APIRouter(prefix="/api/organisations",tags=["Organisation Members"])
ALLOWED_ROLES={"owner","admin","instructor","learner"}
ALLOWED_STATUS={"active","invited","suspended"}

class AddOrganisationMember(BaseModel):
    user_id: Optional[UUID] = None
    email: Optional[str] = Field(default=None, min_length=3, max_length=320)
    role: str = Field(default="learner", min_length=1, max_length=50)

class UpdateOrganisationMember(BaseModel):
    role: Optional[str]=None
    status: Optional[str]=None

def _role(v):
    v=v.strip().lower()
    if v not in ALLOWED_ROLES: raise HTTPException(400,"Invalid organisation role.")
    return v

def _status(v):
    v=v.strip().lower()
    if v not in ALLOWED_STATUS: raise HTTPException(400,"Invalid membership status.")
    return v

def _scope(context,org_id):
    target=str(org_id)
    if context.is_platform_admin:return target
    if not context.organisation_id or str(context.organisation_id)!=target:
        raise HTTPException(403,"You do not have access to this organisation.")
    return target

def _org(org_id):
    r=supabase.table("organisations").select("*").eq("id",org_id).limit(1).execute()
    if not r.data: raise HTTPException(404,"Organisation not found.")
    return r.data[0]

def _require_active_org(org):
    if not org.get("is_active"):
        raise HTTPException(409,"This organisation workspace is inactive.")

def _member(org_id,member_id):
    r=supabase.table("organisation_members").select("id,organisation_id,user_id,role,status,joined_at").eq("id",member_id).eq("organisation_id",org_id).limit(1).execute()
    return r.data[0] if r.data else None

def _user(uid):
    r=supabase.table("users").select("id,email,name,role").eq("id",uid).limit(1).execute()
    return r.data[0] if r.data else None

def _user_by_email(value):
    email = (value or "").strip().lower()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise HTTPException(400, "Enter a valid email address.")
    r = supabase.table("users").select("id,email,name,role").eq("email", email).limit(2).execute()
    rows = r.data or []
    if len(rows) > 1:
        raise HTTPException(409, "More than one account matches this email. Use the account ID to resolve the duplicate.")
    return rows[0] if rows else None

def _format(m,u):
    return {"membership_id":m["id"],"organisation_id":m["organisation_id"],"user_id":m["user_id"],"role":m["role"],"status":m["status"],"joined_at":m["joined_at"],"user":u}


def _sync_assigned_course_enrolments(org_id: str, user_id: str) -> int:
    """Materialise active organisation-wide assigned courses for a learner.

    This keeps the learner dashboard/progress APIs in step when a learner is
    added after the organisation assigned its courses.
    """
    grants = (
        supabase.table("course_access")
        .select("course_id")
        .eq("organisation_id", str(org_id))
        .eq("status", "active")
        .eq("access_type", "assigned")
        .execute()
    ).data or []
    created = 0
    now = datetime.now(timezone.utc).isoformat()
    for grant in grants:
        course_id = str(grant.get("course_id") or "")
        if not course_id:
            continue
        existing = (
            supabase.table("learnora_enrolments")
            .select("id")
            .eq("user_id", str(user_id))
            .eq("course_id", course_id)
            .eq("organisation_id", str(org_id))
            .in_("status", ["active", "completed"])
            .limit(1)
            .execute()
        ).data or []
        if existing:
            continue
        result = supabase.table("learnora_enrolments").insert({
            "user_id": str(user_id),
            "course_id": course_id,
            "organisation_id": str(org_id),
            "status": "active",
            "enrolled_at": now,
            "source_type": "organisation_assignment",
        }).execute()
        if result.data:
            created += 1
    return created

@router.get("/{organisation_id}/members")
def list_members(organisation_id:UUID,status:Optional[str]=Query(None),role:Optional[str]=Query(None),context:PermissionContext=Depends(require_permission("organisations.members"))):
    oid=_scope(context,organisation_id); _org(oid)
    if status: status=_status(status)
    if role: role=_role(role)
    q=supabase.table("organisation_members").select("id,organisation_id,user_id,role,status,joined_at").eq("organisation_id",oid)
    if status:q=q.eq("status",status)
    if role:q=q.eq("role",role)
    rows=q.order("joined_at",desc=False).execute().data or []
    return {"success":True,"organisation_id":oid,"count":len(rows),"members":[_format(m,_user(str(m["user_id"]))) for m in rows]}

@router.get("/{organisation_id}/members/{member_id}")
def get_member(organisation_id:UUID,member_id:UUID,context:PermissionContext=Depends(require_permission("organisations.members"))):
    oid=_scope(context,organisation_id); _org(oid); m=_member(oid,str(member_id))
    if not m:raise HTTPException(404,"Organisation member not found.")
    return {"success":True,"member":_format(m,_user(str(m["user_id"])))}

@router.post("/{organisation_id}/members")
def add_member(organisation_id:UUID,payload:AddOrganisationMember,context:PermissionContext=Depends(require_permission("organisations.members"))):
    oid = _scope(context, organisation_id)
    org = _org(oid)
    _require_active_org(org)
    role = _role(payload.role)
    if bool(payload.user_id) == bool(payload.email):
        raise HTTPException(400, "Provide exactly one of user_id or email.")
    u = _user(str(payload.user_id)) if payload.user_id else _user_by_email(payload.email or "")
    if not u:
        raise HTTPException(404, "No existing Learnora account uses that email or ID. Invitations for new accounts are not available yet.")
    uid = str(u["id"])
    existing=supabase.table("organisation_members").select("id,organisation_id,user_id,role,status,joined_at").eq("organisation_id",oid).eq("user_id",uid).limit(1).execute()
    if existing.data:
        m=existing.data[0]
        if m["status"]=="active":raise HTTPException(409,"User is already an active member.")
        if role in {"learner","instructor"}:
            ensure_org_capacity(oid,"learners" if role=="learner" else "instructors",1)
        r=supabase.table("organisation_members").update({"role":role,"status":"active"}).eq("id",m["id"]).execute()
    else:
        if role in {"learner","instructor"}:
            ensure_org_capacity(oid,"learners" if role=="learner" else "instructors",1)
        r=supabase.table("organisation_members").insert({"organisation_id":oid,"user_id":uid,"role":role,"status":"active"}).execute()
    if not r.data:raise HTTPException(500,"Failed to save organisation membership.")
    m=r.data[0]
    if role in {"learner", "member"} and m.get("status") == "active":
        try:
            _sync_assigned_course_enrolments(oid, uid)
        except Exception as exc:
            print(f"Assigned course enrolment sync failed after member add: {type(exc).__name__}")
            raise HTTPException(503, "Membership was saved, but assigned course access could not be synchronised. Retry the membership update.") from None
    audit(actor_user_id=context.user_id,action="organisation_member_added",resource_type="organisation_member",resource_id=m["id"],organisation_id=oid,metadata={"role":role})
    return {"success":True,"member":_format(m,u)}

@router.patch("/{organisation_id}/members/{member_id}")
def update_member(organisation_id:UUID,member_id:UUID,payload:UpdateOrganisationMember,context:PermissionContext=Depends(require_permission("organisations.members"))):
    oid=_scope(context,organisation_id); org=_org(oid); m=_member(oid,str(member_id))
    if not m:raise HTTPException(404,"Organisation member not found.")
    updates={}
    if payload.role is not None:updates["role"]=_role(payload.role)
    if payload.status is not None:updates["status"]=_status(payload.status)
    if not updates:raise HTTPException(400,"No membership changes supplied.")
    if m["role"]=="owner" and (updates.get("role") not in (None,"owner") or updates.get("status") in {"suspended"}):
        owners=supabase.table("organisation_members").select("id").eq("organisation_id",oid).eq("role","owner").eq("status","active").execute().data or []
        if len(owners)<=1:raise HTTPException(400,"The organisation must retain at least one active owner.")
    target_role=updates.get("role",m["role"])
    target_status=updates.get("status",m["status"])
    if not org.get("is_active") and (
        target_status == "active"
        or (m["status"] == "active" and target_role != m["role"])
    ):
        raise HTTPException(409,"An inactive organisation cannot grant or change active memberships.")
    if target_status == "active" and target_role in {"learner","instructor"} and (
        m["status"] != "active" or target_role != m["role"]
    ):
        ensure_org_capacity(oid,"learners" if target_role=="learner" else "instructors",1)
    r=supabase.table("organisation_members").update(updates).eq("id",str(member_id)).eq("organisation_id",oid).execute()
    if not r.data:raise HTTPException(500,"Failed to update organisation membership.")
    updated=r.data[0]
    if target_role in {"learner", "member"} and target_status == "active":
        try:
            _sync_assigned_course_enrolments(oid, str(updated["user_id"]))
        except Exception as exc:
            print(f"Assigned course enrolment sync failed after member update: {type(exc).__name__}")
            raise HTTPException(503, "Membership was updated, but assigned course access could not be synchronised. Retry the membership update.") from None
    audit(actor_user_id=context.user_id,action="organisation_member_updated",resource_type="organisation_member",resource_id=member_id,organisation_id=oid,metadata={"changes":updates})
    return {"success":True,"member":_format(updated,_user(str(updated["user_id"])))}

@router.delete("/{organisation_id}/members/{member_id}")
def remove_member(organisation_id:UUID,member_id:UUID,context:PermissionContext=Depends(require_permission("organisations.members"))):
    oid=_scope(context,organisation_id); _org(oid); m=_member(oid,str(member_id))
    if not m:raise HTTPException(404,"Organisation member not found.")
    if m["role"]=="owner" and m["status"]=="active":
        owners=supabase.table("organisation_members").select("id").eq("organisation_id",oid).eq("role","owner").eq("status","active").execute().data or []
        if len(owners)<=1:raise HTTPException(400,"The final active owner cannot be removed.")
    r=supabase.table("organisation_members").update({"status":"suspended"}).eq("id",str(member_id)).eq("organisation_id",oid).execute()
    if not r.data:raise HTTPException(500,"Failed to suspend organisation membership.")
    audit(actor_user_id=context.user_id,action="organisation_member_suspended",resource_type="organisation_member",resource_id=member_id,organisation_id=oid)
    return {"success":True,"membership_id":str(member_id),"status":"suspended"}

@router.get("/{organisation_id}/members/summary")
def summary(organisation_id:UUID,context:PermissionContext=Depends(require_permission("organisations.members"))):
    oid=_scope(context,organisation_id); _org(oid)
    rows=supabase.table("organisation_members").select("role,status").eq("organisation_id",oid).execute().data or []
    out={"total":len(rows),"active":0,"invited":0,"suspended":0,"owners":0,"admins":0,"instructors":0,"learners":0}
    for r in rows:
        if r["status"] in out:out[r["status"]]+=1
        if r["role"]+"s" in out:out[r["role"]+"s"]+=1
        elif r["role"]=="owner":out["owners"]+=1
    return {"success":True,"organisation_id":oid,"summary":out}
