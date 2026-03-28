"""
Advanced Role-Based Access Control (RBAC)
Enterprise-grade permissions system with fine-grained access control
"""

from typing import List, Dict, Optional, Set
from enum import Enum
from datetime import datetime
from fastapi import Depends, HTTPException

class Permission(str, Enum):
    # User Permissions
    USER_READ = "user:read"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"
    
    # Question Permissions
    QUESTION_READ = "question:read"
    QUESTION_WRITE = "question:write"
    QUESTION_DELETE = "question:delete"
    QUESTION_APPROVE = "question:approve"
    
    # Analytics Permissions
    ANALYTICS_VIEW_OWN = "analytics:view:own"
    ANALYTICS_VIEW_TEAM = "analytics:view:team"
    ANALYTICS_VIEW_ORG = "analytics:view:org"
    ANALYTICS_VIEW_PLATFORM = "analytics:view:platform"
    ANALYTICS_EXPORT = "analytics:export"
    
    # Subscription Permissions
    SUBSCRIPTION_VIEW = "subscription:view"
    SUBSCRIPTION_MANAGE = "subscription:manage"
    SUBSCRIPTION_CANCEL = "subscription:cancel"
    
    # Organization Permissions
    ORG_READ = "org:read"
    ORG_WRITE = "org:write"
    ORG_DELETE = "org:delete"
    ORG_SETTINGS = "org:settings"
    ORG_SSO_CONFIG = "org:sso:config"
    ORG_BILLING = "org:billing"
    
    # Content Permissions
    CONTENT_CREATE = "content:create"
    CONTENT_EDIT = "content:edit"
    CONTENT_DELETE = "content:delete"
    CONTENT_PUBLISH = "content:publish"
    
    # Admin Permissions
    ADMIN_USERS = "admin:users"
    ADMIN_CONTENT = "admin:content"
    ADMIN_BILLING = "admin:billing"
    ADMIN_ANALYTICS = "admin:analytics"
    ADMIN_SYSTEM = "admin:system"
    ADMIN_AUDIT = "admin:audit"
    
    # Super Admin
    SUPER_ADMIN = "super:admin"

class Role(str, Enum):
    # Standard User Roles
    USER = "user"                        # Regular user
    PREMIUM_USER = "premium_user"        # Paid user
    
    # Organization Roles
    ORG_MEMBER = "org_member"            # Organization member
    ORG_ADMIN = "org_admin"              # Can manage organization
    ORG_OWNER = "org_owner"              # Organization owner
    
    # Team Roles
    TEAM_MEMBER = "team_member"          # Team member
    TEAM_LEADER = "team_leader"          # Can manage team
    DEPARTMENT_HEAD = "department_head"  # Can manage department
    
    # Content Roles
    CONTENT_CREATOR = "content_creator"  # Can create content
    CONTENT_REVIEWER = "content_reviewer" # Can review content
    CONTENT_ADMIN = "content_admin"      # Can manage all content
    
    # Platform Roles
    SUPPORT_AGENT = "support_agent"      # Customer support
    ANALYST = "analyst"                  # Can view analytics
    BILLING_ADMIN = "billing_admin"      # Can manage billing
    
    # Admin Roles
    ADMIN = "admin"                      # Platform admin
    SUPER_ADMIN = "super_admin"          # Full platform access

# Role-Permission Mappings
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.USER: {
        Permission.USER_READ,
        Permission.QUESTION_READ,
        Permission.ANALYTICS_VIEW_OWN,
        Permission.SUBSCRIPTION_VIEW
    },
    
    Role.PREMIUM_USER: {
        Permission.USER_READ,
        Permission.USER_WRITE,
        Permission.QUESTION_READ,
        Permission.ANALYTICS_VIEW_OWN,
        Permission.ANALYTICS_EXPORT,
        Permission.SUBSCRIPTION_VIEW,
        Permission.SUBSCRIPTION_MANAGE
    },
    
    Role.ORG_MEMBER: {
        Permission.USER_READ,
        Permission.QUESTION_READ,
        Permission.ANALYTICS_VIEW_OWN,
        Permission.ANALYTICS_VIEW_TEAM,
        Permission.ORG_READ
    },
    
    Role.TEAM_LEADER: {
        Permission.USER_READ,
        Permission.USER_WRITE,
        Permission.QUESTION_READ,
        Permission.ANALYTICS_VIEW_OWN,
        Permission.ANALYTICS_VIEW_TEAM,
        Permission.ANALYTICS_EXPORT,
        Permission.ORG_READ
    },
    
    Role.ORG_ADMIN: {
        Permission.USER_READ,
        Permission.USER_WRITE,
        Permission.USER_DELETE,
        Permission.QUESTION_READ,
        Permission.ANALYTICS_VIEW_OWN,
        Permission.ANALYTICS_VIEW_TEAM,
        Permission.ANALYTICS_VIEW_ORG,
        Permission.ANALYTICS_EXPORT,
        Permission.ORG_READ,
        Permission.ORG_WRITE,
        Permission.ORG_SETTINGS,
        Permission.ORG_BILLING,
        Permission.SUBSCRIPTION_VIEW,
        Permission.SUBSCRIPTION_MANAGE
    },
    
    Role.ORG_OWNER: {
        Permission.USER_READ,
        Permission.USER_WRITE,
        Permission.USER_DELETE,
        Permission.QUESTION_READ,
        Permission.QUESTION_WRITE,
        Permission.ANALYTICS_VIEW_OWN,
        Permission.ANALYTICS_VIEW_TEAM,
        Permission.ANALYTICS_VIEW_ORG,
        Permission.ANALYTICS_EXPORT,
        Permission.ORG_READ,
        Permission.ORG_WRITE,
        Permission.ORG_DELETE,
        Permission.ORG_SETTINGS,
        Permission.ORG_SSO_CONFIG,
        Permission.ORG_BILLING,
        Permission.SUBSCRIPTION_VIEW,
        Permission.SUBSCRIPTION_MANAGE,
        Permission.SUBSCRIPTION_CANCEL
    },
    
    Role.CONTENT_ADMIN: {
        Permission.QUESTION_READ,
        Permission.QUESTION_WRITE,
        Permission.QUESTION_DELETE,
        Permission.QUESTION_APPROVE,
        Permission.CONTENT_CREATE,
        Permission.CONTENT_EDIT,
        Permission.CONTENT_DELETE,
        Permission.CONTENT_PUBLISH,
        Permission.ANALYTICS_VIEW_PLATFORM
    },
    
    Role.ADMIN: {
        Permission.ADMIN_USERS,
        Permission.ADMIN_CONTENT,
        Permission.ADMIN_BILLING,
        Permission.ADMIN_ANALYTICS,
        Permission.ADMIN_AUDIT,
        Permission.USER_READ,
        Permission.USER_WRITE,
        Permission.USER_DELETE,
        Permission.QUESTION_READ,
        Permission.QUESTION_WRITE,
        Permission.QUESTION_DELETE,
        Permission.ANALYTICS_VIEW_PLATFORM,
        Permission.ORG_READ,
        Permission.ORG_WRITE
    },
    
    Role.SUPER_ADMIN: {
        Permission.SUPER_ADMIN,  # This grants ALL permissions
    }
}

class RBACService:
    """Service for Role-Based Access Control"""
    
    def has_permission(
        self,
        user_roles: List[Role],
        required_permission: Permission
    ) -> bool:
        """Check if user has required permission"""
        try:
            # Super admin has all permissions
            if Role.SUPER_ADMIN in user_roles:
                return True
            
            # Check if any of user's roles has the required permission
            for role in user_roles:
                role_permissions = ROLE_PERMISSIONS.get(role, set())
                
                # Super admin permission grants all
                if Permission.SUPER_ADMIN in role_permissions:
                    return True
                
                if required_permission in role_permissions:
                    return True
            
            return False
        except Exception as e:
            print(f"Error checking permission: {e}")
            return False
    
    def has_any_permission(
        self,
        user_roles: List[Role],
        required_permissions: List[Permission]
    ) -> bool:
        """Check if user has ANY of the required permissions"""
        return any(
            self.has_permission(user_roles, perm) 
            for perm in required_permissions
        )
    
    def has_all_permissions(
        self,
        user_roles: List[Role],
        required_permissions: List[Permission]
    ) -> bool:
        """Check if user has ALL required permissions"""
        return all(
            self.has_permission(user_roles, perm) 
            for perm in required_permissions
        )
    
    def get_user_permissions(self, user_roles: List[Role]) -> Set[Permission]:
        """Get all permissions for user based on their roles"""
        try:
            all_permissions = set()
            
            for role in user_roles:
                role_permissions = ROLE_PERMISSIONS.get(role, set())
                
                # If super admin, return all permissions
                if Permission.SUPER_ADMIN in role_permissions:
                    return set(Permission)
                
                all_permissions.update(role_permissions)
            
            return all_permissions
        except Exception as e:
            print(f"Error getting permissions: {e}")
            return set()
    
    def can_access_resource(
        self,
        user_id: str,
        user_roles: List[Role],
        resource_type: str,
        resource_id: str,
        action: str
    ) -> bool:
        """Check if user can access specific resource"""
        try:
            # Map action to permission
            permission_map = {
                "read": f"{resource_type}:read",
                "write": f"{resource_type}:write",
                "delete": f"{resource_type}:delete"
            }
            
            required_permission = Permission(permission_map.get(action))
            
            # Check basic permission
            if not self.has_permission(user_roles, required_permission):
                return False
            
            # TODO: Additional checks
            # - Check if resource belongs to user's organization
            # - Check if resource is in user's accessible scope
            # - Check resource-specific rules
            
            return True
        except Exception as e:
            print(f"Error checking resource access: {e}")
            return False
    
    # ========================================
    # ORGANIZATION-LEVEL PERMISSIONS
    # ========================================
    
    def assign_role_to_user(
        self,
        user_id: str,
        role: Role,
        organization_id: Optional[str] = None,
        scope: Optional[Dict] = None
    ) -> Dict:
        """Assign role to user"""
        try:
            role_assignment = {
                "user_id": user_id,
                "role": role,
                "organization_id": organization_id,
                "scope": scope or {},  # Department, team, etc.
                "assigned_at": datetime.now().isoformat(),
                "assigned_by": "system"  # TODO: Track who assigned
            }
            
            # TODO: Save to database
            
            return role_assignment
        except Exception as e:
            print(f"Error assigning role: {e}")
            raise
    
    def revoke_role_from_user(
        self,
        user_id: str,
        role: Role,
        organization_id: Optional[str] = None
    ) -> bool:
        """Revoke role from user"""
        try:
            # TODO: Remove from database
            return True
        except Exception as e:
            print(f"Error revoking role: {e}")
            raise

# Singleton instance
rbac_service = RBACService()


# ========================================
# PRAGMATIC MAPPING: UserRole -> RBAC Permissions
# Mapeaza cele 4 roluri existente la permisiuni RBAC
# fara a schimba schema DB
# ========================================

# Mapping UserRole string values -> RBAC Role
USER_ROLE_MAPPING: Dict[str, Role] = {
    "demo": Role.USER,
    "student": Role.USER,
    "trainer": Role.CONTENT_ADMIN,
    "admin": Role.ADMIN,
}

# Permisiuni suplimentare per UserRole (peste cele din ROLE_PERMISSIONS)
USER_ROLE_EXTRA_PERMISSIONS: Dict[str, Set[Permission]] = {
    "demo": {
        Permission.QUESTION_READ,
        Permission.ANALYTICS_VIEW_OWN,
    },
    "student": {
        Permission.USER_READ,
        Permission.QUESTION_READ,
        Permission.ANALYTICS_VIEW_OWN,
        Permission.SUBSCRIPTION_VIEW,
    },
    "trainer": {
        Permission.USER_READ,
        Permission.USER_WRITE,
        Permission.QUESTION_READ,
        Permission.QUESTION_WRITE,
        Permission.ANALYTICS_VIEW_OWN,
        Permission.ANALYTICS_VIEW_TEAM,
        Permission.ANALYTICS_EXPORT,
        Permission.CONTENT_CREATE,
        Permission.CONTENT_EDIT,
    },
    "admin": set(Permission),  # toate permisiunile
}


def get_permissions_for_user_role(role_value: str) -> Set[Permission]:
    """Returneaza toate permisiunile pentru un UserRole (string value)"""
    # Admin are toate permisiunile
    if role_value == "admin":
        return set(Permission)

    permissions = set()

    # Permisiuni din RBAC Role mapping
    rbac_role = USER_ROLE_MAPPING.get(role_value)
    if rbac_role:
        permissions.update(ROLE_PERMISSIONS.get(rbac_role, set()))

    # Permisiuni extra per UserRole
    extras = USER_ROLE_EXTRA_PERMISSIONS.get(role_value, set())
    permissions.update(extras)

    return permissions


def check_user_permission(user_role_value: str, required_permission: Permission) -> bool:
    """Verifica daca un user cu rolul dat are permisiunea ceruta"""
    if user_role_value == "admin":
        return True
    permissions = get_permissions_for_user_role(user_role_value)
    return required_permission in permissions

