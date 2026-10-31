"""Authoritative access endpoints used by future learner clients."""
from fastapi import APIRouter,Depends
from .auth import CurrentUser,get_current_user
from services.access import resolve_course_access
from services.free_access import is_individual_learner

router=APIRouter(prefix="/api/access",tags=["Access"])

@router.get("/courses/{course_id}")
def course_access(course_id:str,user:CurrentUser=Depends(get_current_user)):
    organisation_id=getattr(user,"organisation_id",None)
    result=resolve_course_access(
        user.id,
        course_id,
        organisation_id,
        allow_free_access=is_individual_learner(user.role, user.account_type),
    )
    return {"success":True,"allowed":bool(result),"access":result}
