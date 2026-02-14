from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.organization import Organization
from models.user_organization import UserOrganization
from models.user import User
from apis.dependencies import get_current_user
from apis.schemas.organization import OrganizationCreate, OrganizationOut

router = APIRouter()

@router.post("/", response_model=OrganizationOut)
def create_organization(
    org_in: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new organization.
    The creator becomes the 'owner' and an 'Admin' member.
    """
    # 1. Create Org
    new_org = Organization(
        name=org_in.name,
        domain=org_in.domain,
        owner_id=current_user.id
    )
    db.add(new_org)
    db.commit()
    db.refresh(new_org)

    # 3. Add creator as Admin
    member = UserOrganization(
        user_id=current_user.id,
        organization_id=new_org.id,
        role="Admin"
    )
    db.add(member)
    db.commit()

    return new_org

@router.get("/", response_model=List[OrganizationOut])
def list_my_organizations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List organizations the current user receives.
    """
    # Using the relationship helper we added to User model
    return current_user.organizations

@router.get("/{org_id}", response_model=OrganizationOut)
def get_organization(
    org_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get details of an organization if the user is a member.
    """
    # 1. Check membership
    membership = db.query(UserOrganization).filter(
        UserOrganization.user_id == current_user.id,
        UserOrganization.organization_id == org_id
    ).first()

    if not membership:
        raise HTTPException(status_code=404, detail="Organization not found or access denied")

    org = db.query(Organization).filter(Organization.id == org_id).first()
    return org
