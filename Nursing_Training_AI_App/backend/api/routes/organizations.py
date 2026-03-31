"""
Organization Management API Routes
CRUD for organizations, teams, memberships.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List, Dict, Any

from core.database import get_db
from core.rbac import Permission
from models.user import User
from models.organization import Organization, Team, OrgMembership, MemberRole, OrgSubscription
from api.dependencies import get_current_active_user, require_permission

router = APIRouter(tags=["organizations"])


# --- Request models ---

class CreateOrgRequest(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    contact_email: Optional[str] = None
    nhs_trust_name: Optional[str] = None
    subscription: str = "free"
    max_members: int = 5

class CreateTeamRequest(BaseModel):
    name: str
    specialty: Optional[str] = None
    nhs_band_focus: Optional[str] = None
    description: Optional[str] = None

class AddMemberRequest(BaseModel):
    user_id: int
    role: str = "member"
    team_id: Optional[int] = None


# --- Organization CRUD ---

@router.post("/")
async def create_organization(
    data: CreateOrgRequest,
    admin: User = Depends(require_permission(Permission.ADMIN_USERS)),
    db: Session = Depends(get_db),
):
    """Creeaza o organizatie noua"""
    existing = db.query(Organization).filter(Organization.slug == data.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Organization slug already exists")

    try:
        sub = OrgSubscription(data.subscription)
    except ValueError:
        sub = OrgSubscription.FREE

    org = Organization(
        name=data.name,
        slug=data.slug,
        description=data.description,
        contact_email=data.contact_email,
        nhs_trust_name=data.nhs_trust_name,
        subscription=sub,
        max_members=data.max_members,
    )
    db.add(org)
    db.commit()
    db.refresh(org)

    # Adauga admin-ul ca owner
    membership = OrgMembership(
        user_id=admin.id,
        organization_id=org.id,
        role=MemberRole.OWNER,
    )
    db.add(membership)
    db.commit()

    return {"success": True, "organization_id": org.id, "slug": org.slug}


@router.get("/")
async def list_organizations(
    admin: User = Depends(require_permission(Permission.ADMIN_USERS)),
    db: Session = Depends(get_db),
):
    """Lista toate organizatiile"""
    orgs = db.query(Organization).filter(Organization.is_active == True).all()
    return {
        "success": True,
        "organizations": [
            {
                "id": o.id,
                "name": o.name,
                "slug": o.slug,
                "subscription": o.subscription.value if o.subscription else "free",
                "nhs_trust_name": o.nhs_trust_name,
                "max_members": o.max_members,
                "member_count": db.query(func.count(OrgMembership.id)).filter(
                    OrgMembership.organization_id == o.id, OrgMembership.is_active == True
                ).scalar() or 0,
                "team_count": db.query(func.count(Team.id)).filter(
                    Team.organization_id == o.id, Team.is_active == True
                ).scalar() or 0,
                "created_at": o.created_at.isoformat() if o.created_at else None,
            }
            for o in orgs
        ],
    }


@router.get("/{org_id}")
async def get_organization(
    org_id: int,
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Detalii organizatie cu echipe si membri"""
    org = db.query(Organization).filter(Organization.id == org_id, Organization.is_active == True).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    teams = db.query(Team).filter(Team.organization_id == org_id, Team.is_active == True).all()
    members = db.query(OrgMembership).filter(
        OrgMembership.organization_id == org_id, OrgMembership.is_active == True
    ).all()

    # User details for members
    user_ids = [m.user_id for m in members]
    users = db.query(User).filter(User.id.in_(user_ids)).all() if user_ids else []
    user_map = {u.id: u for u in users}

    return {
        "success": True,
        "organization": {
            "id": org.id,
            "name": org.name,
            "slug": org.slug,
            "description": org.description,
            "subscription": org.subscription.value if org.subscription else "free",
            "nhs_trust_name": org.nhs_trust_name,
            "max_members": org.max_members,
            "contact_email": org.contact_email,
        },
        "teams": [
            {
                "id": t.id, "name": t.name, "specialty": t.specialty,
                "nhs_band_focus": t.nhs_band_focus,
                "member_count": len([m for m in members if m.team_id == t.id]),
            }
            for t in teams
        ],
        "members": [
            {
                "user_id": m.user_id,
                "email": user_map[m.user_id].email if m.user_id in user_map else None,
                "name": f"{user_map[m.user_id].first_name} {user_map[m.user_id].last_name}" if m.user_id in user_map else None,
                "role": m.role.value if m.role else "member",
                "team_id": m.team_id,
                "joined_at": m.joined_at.isoformat() if m.joined_at else None,
            }
            for m in members
        ],
    }


# --- Team CRUD ---

@router.post("/{org_id}/teams")
async def create_team(
    org_id: int,
    data: CreateTeamRequest,
    admin: User = Depends(require_permission(Permission.ADMIN_USERS)),
    db: Session = Depends(get_db),
):
    """Creeaza o echipa in organizatie"""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    team = Team(
        organization_id=org_id,
        name=data.name,
        specialty=data.specialty,
        nhs_band_focus=data.nhs_band_focus,
        description=data.description,
    )
    db.add(team)
    db.commit()
    db.refresh(team)

    return {"success": True, "team_id": team.id, "name": team.name}


# --- Membership management ---

@router.post("/{org_id}/members")
async def add_member(
    org_id: int,
    data: AddMemberRequest,
    admin: User = Depends(require_permission(Permission.ADMIN_USERS)),
    db: Session = Depends(get_db),
):
    """Adauga un user la organizatie"""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Verifica limita de membri
    current_count = db.query(func.count(OrgMembership.id)).filter(
        OrgMembership.organization_id == org_id, OrgMembership.is_active == True
    ).scalar() or 0
    if current_count >= org.max_members:
        raise HTTPException(status_code=400, detail=f"Organization member limit reached ({org.max_members})")

    # Verifica ca user-ul exista
    target_user = db.query(User).filter(User.id == data.user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verifica daca e deja membru
    existing = db.query(OrgMembership).filter(
        OrgMembership.user_id == data.user_id,
        OrgMembership.organization_id == org_id,
    ).first()
    if existing:
        if existing.is_active:
            raise HTTPException(status_code=400, detail="User is already a member")
        existing.is_active = True
        existing.role = MemberRole(data.role) if data.role in [r.value for r in MemberRole] else MemberRole.MEMBER
        existing.team_id = data.team_id
    else:
        try:
            role = MemberRole(data.role)
        except ValueError:
            role = MemberRole.MEMBER
        membership = OrgMembership(
            user_id=data.user_id,
            organization_id=org_id,
            team_id=data.team_id,
            role=role,
        )
        db.add(membership)

    db.commit()
    return {"success": True, "message": f"User {data.user_id} added to organization"}


@router.delete("/{org_id}/members/{user_id}")
async def remove_member(
    org_id: int,
    user_id: int,
    admin: User = Depends(require_permission(Permission.ADMIN_USERS)),
    db: Session = Depends(get_db),
):
    """Elimina un user din organizatie"""
    membership = db.query(OrgMembership).filter(
        OrgMembership.user_id == user_id,
        OrgMembership.organization_id == org_id,
    ).first()
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")

    membership.is_active = False
    db.commit()
    return {"success": True, "message": f"User {user_id} removed from organization"}


# --- Team Analytics (manager view) ---

@router.get("/{org_id}/analytics")
async def get_org_analytics(
    org_id: int,
    user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Analytics pentru organizatie - performanta echipelor"""
    from models.training import UserAnswer, TrainingSession, Question
    from models.learning_profile import UserLearningProfile
    from datetime import datetime, timedelta, timezone
    from sqlalchemy import case

    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Membri
    members = db.query(OrgMembership).filter(
        OrgMembership.organization_id == org_id, OrgMembership.is_active == True
    ).all()
    member_ids = [m.user_id for m in members]

    if not member_ids:
        return {"success": True, "organization": org.name, "members": 0, "analytics": {}}

    # Performanta in ultimele 30 zile
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)

    total_answers = db.query(func.count(UserAnswer.id)).filter(
        UserAnswer.user_id.in_(member_ids),
        UserAnswer.answered_at >= cutoff,
    ).scalar() or 0

    correct_answers = db.query(func.count(UserAnswer.id)).filter(
        UserAnswer.user_id.in_(member_ids),
        UserAnswer.answered_at >= cutoff,
        UserAnswer.is_correct == True,
    ).scalar() or 0

    active_learners = db.query(func.count(func.distinct(UserAnswer.user_id))).filter(
        UserAnswer.user_id.in_(member_ids),
        UserAnswer.answered_at >= cutoff,
    ).scalar() or 0

    # Learning profiles
    profiles = db.query(UserLearningProfile).filter(
        UserLearningProfile.user_id.in_(member_ids)
    ).all()

    improving = sum(1 for p in profiles if p.trend == "improving")
    declining = sum(1 for p in profiles if p.trend == "declining")

    # Per team stats
    teams = db.query(Team).filter(Team.organization_id == org_id, Team.is_active == True).all()
    team_stats = []
    for team in teams:
        team_member_ids = [m.user_id for m in members if m.team_id == team.id]
        if not team_member_ids:
            team_stats.append({"team": team.name, "members": 0, "answers": 0, "accuracy": 0})
            continue
        t_answers = db.query(func.count(UserAnswer.id)).filter(
            UserAnswer.user_id.in_(team_member_ids), UserAnswer.answered_at >= cutoff
        ).scalar() or 0
        t_correct = db.query(func.count(UserAnswer.id)).filter(
            UserAnswer.user_id.in_(team_member_ids), UserAnswer.answered_at >= cutoff,
            UserAnswer.is_correct == True
        ).scalar() or 0
        team_stats.append({
            "team": team.name,
            "specialty": team.specialty,
            "members": len(team_member_ids),
            "answers": t_answers,
            "accuracy": round(t_correct / max(t_answers, 1) * 100, 1),
        })

    return {
        "success": True,
        "organization": org.name,
        "period_days": 30,
        "total_members": len(member_ids),
        "active_learners": active_learners,
        "total_answers": total_answers,
        "accuracy_pct": round(correct_answers / max(total_answers, 1) * 100, 1),
        "improving_members": improving,
        "declining_members": declining,
        "team_performance": team_stats,
    }
