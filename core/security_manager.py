import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import re
import logging
from passlib.context import CryptContext
from fastapi import HTTPException, status
import json

class UserRole(Enum):
    """User roles with hierarchical permissions"""
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"
    GUEST = "guest"

class Permission(Enum):
    """System permissions"""
    READ_DATA = "read_data"
    WRITE_DATA = "write_data"
    DELETE_DATA = "delete_data"
    MANAGE_USERS = "manage_users"
    MANAGE_DATABASES = "manage_databases"
    VIEW_SCHEMA = "view_schema"
    EXECUTE_QUERY = "execute_query"
    EXPORT_DATA = "export_data"
    MANAGE_SECURITY = "manage_security"

@dataclass
class User:
    """User entity"""
    id: str
    username: str
    email: str
    role: UserRole
    permissions: List[Permission]
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None

@dataclass
class SecurityPolicy:
    """Security policy configuration"""
    max_failed_attempts: int = 5
    lockout_duration_minutes: int = 30
    session_timeout_hours: int = 8
    password_min_length: int = 8
    require_special_chars: bool = True
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    allowed_origins: List[str] = None

@dataclass
class AuditLog:
    """Security audit log entry"""
    timestamp: datetime
    user_id: str
    action: str
    resource: str
    ip_address: str
    user_agent: str
    success: bool
    details: Dict[str, Any] = None

class SecurityManager:
    """Comprehensive security management system"""
    
    def __init__(self, policy: SecurityPolicy = None):
        self.policy = policy or SecurityPolicy()
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Dict] = {}
        self.audit_logs: List[AuditLog] = []
        self.logger = logging.getLogger(__name__)
        
        # Initialize default admin user
        self._initialize_default_users()
        
        # Role-based permissions mapping
        self.role_permissions = {
            UserRole.ADMIN: [
                Permission.READ_DATA, Permission.WRITE_DATA, Permission.DELETE_DATA,
                Permission.MANAGE_USERS, Permission.MANAGE_DATABASES, Permission.VIEW_SCHEMA,
                Permission.EXECUTE_QUERY, Permission.EXPORT_DATA, Permission.MANAGE_SECURITY
            ],
            UserRole.ANALYST: [
                Permission.READ_DATA, Permission.VIEW_SCHEMA, Permission.EXECUTE_QUERY, Permission.EXPORT_DATA
            ],
            UserRole.VIEWER: [
                Permission.READ_DATA, Permission.VIEW_SCHEMA
            ],
            UserRole.GUEST: [
                Permission.READ_DATA
            ]
        }
    
    def _initialize_default_users(self):
        """Initialize default admin user"""
        admin_password = self.hash_password("admin123")  # Change in production
        admin_user = User(
            id="admin",
            username="admin",
            email="admin@neurosql.com",
            role=UserRole.ADMIN,
            permissions=self.role_permissions[UserRole.ADMIN],
            created_at=datetime.now()
        )
        
        self.users["admin"] = admin_user
        self.logger.info("Default admin user initialized")
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def validate_password_strength(self, password: str) -> Tuple[bool, str]:
        """Validate password strength"""
        if len(password) < self.policy.password_min_length:
            return False, f"Password must be at least {self.policy.password_min_length} characters"
        
        if self.policy.require_special_chars:
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                return False, "Password must contain at least one special character"
            if not re.search(r'[A-Z]', password):
                return False, "Password must contain at least one uppercase letter"
            if not re.search(r'[a-z]', password):
                return False, "Password must contain at least one lowercase letter"
            if not re.search(r'\d', password):
                return False, "Password must contain at least one digit"
        
        return True, "Password is valid"
    
    def create_user(self, username: str, email: str, password: str, role: UserRole) -> Tuple[bool, str]:
        """Create new user"""
        # Validate password
        is_valid, message = self.validate_password_strength(password)
        if not is_valid:
            return False, message
        
        # Check if user already exists
        if any(u.username == username for u in self.users.values()):
            return False, "Username already exists"
        
        if any(u.email == email for u in self.users.values()):
            return False, "Email already exists"
        
        # Create user
        user_id = secrets.token_hex(8)
        hashed_password = self.hash_password(password)
        
        new_user = User(
            id=user_id,
            username=username,
            email=email,
            role=role,
            permissions=self.role_permissions[role],
            created_at=datetime.now()
        )
        
        self.users[user_id] = new_user
        self.logger.info(f"User created: {username} ({role.value})")
        
        return True, "User created successfully"
    
    def authenticate_user(self, username: str, password: str, ip_address: str = "unknown", user_agent: str = "unknown") -> Tuple[Optional[str], str]:
        """Authenticate user and return JWT token"""
        # Find user
        user = None
        for u in self.users.values():
            if u.username == username:
                user = u
                break
        
        if not user:
            self._log_audit(None, "login_failed", "authentication", ip_address, user_agent, False, {"username": username})
            return None, "Invalid credentials"
        
        # Check if user is locked
        if user.locked_until and user.locked_until > datetime.now():
            self._log_audit(user.id, "login_blocked", "authentication", ip_address, user_agent, False, {"reason": "account_locked"})
            return None, f"Account locked until {user.locked_until}"
        
        # Check if user is active
        if not user.is_active:
            self._log_audit(user.id, "login_blocked", "authentication", ip_address, user_agent, False, {"reason": "account_inactive"})
            return None, "Account is inactive"
        
        # Verify password
        if not self.verify_password(password, user.id):  # Note: In real implementation, store hashed password separately
            user.failed_login_attempts += 1
            
            # Lock account if too many failed attempts
            if user.failed_login_attempts >= self.policy.max_failed_attempts:
                user.locked_until = datetime.now() + timedelta(minutes=self.policy.lockout_duration_minutes)
                self._log_audit(user.id, "account_locked", "security", ip_address, user_agent, False, {"attempts": user.failed_login_attempts})
                return None, f"Account locked due to too many failed attempts"
            
            self._log_audit(user.id, "login_failed", "authentication", ip_address, user_agent, False, {"attempts": user.failed_login_attempts})
            return None, "Invalid credentials"
        
        # Successful login
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.now()
        
        # Generate JWT token
        token = self._generate_jwt_token(user)
        
        self._log_audit(user.id, "login_success", "authentication", ip_address, user_agent, True)
        
        return token, "Login successful"
    
    def _generate_jwt_token(self, user: User) -> str:
        """Generate JWT token for user"""
        payload = {
            "user_id": user.id,
            "username": user.username,
            "role": user.role.value,
            "permissions": [p.value for p in user.permissions],
            "exp": datetime.utcnow() + timedelta(hours=self.policy.session_timeout_hours),
            "iat": datetime.utcnow()
        }
        
        return jwt.encode(payload, self.policy.jwt_secret_key, algorithm=self.policy.jwt_algorithm)
    
    def verify_jwt_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.policy.jwt_secret_key, algorithms=[self.policy.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def check_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if user has specific permission"""
        user = self.users.get(user_id)
        if not user or not user.is_active:
            return False
        
        return permission in user.permissions
    
    def check_query_permission(self, user_id: str, query: str, database: str = "default") -> Tuple[bool, str]:
        """Check if user is allowed to execute specific query"""
        user = self.users.get(user_id)
        if not user:
            return False, "User not found"
        
        # Check basic execute permission
        if not self.check_permission(user_id, Permission.EXECUTE_QUERY):
            return False, "No permission to execute queries"
        
        # Check for dangerous operations
        query_upper = query.upper().strip()
        
        # Check for DELETE operations
        if query_upper.startswith('DELETE') and not self.check_permission(user_id, Permission.DELETE_DATA):
            return False, "No permission to delete data"
        
        # Check for DROP operations
        if 'DROP' in query_upper and not self.check_permission(user_id, Permission.MANAGE_DATABASES):
            return False, "No permission to modify database structure"
        
        # Check for INSERT/UPDATE operations
        if (query_upper.startswith('INSERT') or query_upper.startswith('UPDATE')) and not self.check_permission(user_id, Permission.WRITE_DATA):
            return False, "No permission to write data"
        
        # Additional security checks
        if self._contains_suspicious_patterns(query):
            self._log_audit(user_id, "suspicious_query_blocked", "security", "unknown", "unknown", False, {"query": query[:100]})
            return False, "Query contains suspicious patterns"
        
        return True, "Query allowed"
    
    def _contains_suspicious_patterns(self, query: str) -> bool:
        """Check for suspicious SQL patterns"""
        suspicious_patterns = [
            r';\s*(DROP|DELETE|UPDATE|INSERT)',  # Multiple statements
            r'UNION\s+SELECT',  # Potential SQL injection
            r'--',  # SQL comments
            r'/\*.*\*/',  # SQL comments
            r'EXEC\s*\(',  # Execute function
            r'xp_cmdshell',  # Command execution
            r'sp_executesql',  # Dynamic SQL
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return True
        
        return False
    
    def _log_audit(self, user_id: Optional[str], action: str, resource: str, ip_address: str, user_agent: str, success: bool, details: Dict = None):
        """Log security audit event"""
        audit_log = AuditLog(
            timestamp=datetime.now(),
            user_id=user_id or "anonymous",
            action=action,
            resource=resource,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            details=details or {}
        )
        
        self.audit_logs.append(audit_log)
        
        # Keep only last 10000 audit logs
        if len(self.audit_logs) > 10000:
            self.audit_logs = self.audit_logs[-10000:]
        
        # Log to file
        log_level = logging.INFO if success else logging.WARNING
        self.logger.log(log_level, f"AUDIT: {action} by {user_id} on {resource} - {'SUCCESS' if success else 'FAILED'}")
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        for user in self.users.values():
            if user.username == username:
                return user
        return None
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def update_user_role(self, admin_user_id: str, target_user_id: str, new_role: UserRole) -> Tuple[bool, str]:
        """Update user role (admin only)"""
        if not self.check_permission(admin_user_id, Permission.MANAGE_USERS):
            return False, "No permission to manage users"
        
        user = self.users.get(target_user_id)
        if not user:
            return False, "User not found"
        
        old_role = user.role
        user.role = new_role
        user.permissions = self.role_permissions[new_role]
        
        self._log_audit(admin_user_id, "role_updated", "user_management", "unknown", "unknown", True, {
            "target_user": target_user_id,
            "old_role": old_role.value,
            "new_role": new_role.value
        })
        
        return True, "User role updated successfully"
    
    def deactivate_user(self, admin_user_id: str, target_user_id: str) -> Tuple[bool, str]:
        """Deactivate user (admin only)"""
        if not self.check_permission(admin_user_id, Permission.MANAGE_USERS):
            return False, "No permission to manage users"
        
        user = self.users.get(target_user_id)
        if not user:
            return False, "User not found"
        
        user.is_active = False
        
        self._log_audit(admin_user_id, "user_deactivated", "user_management", "unknown", "unknown", True, {
            "target_user": target_user_id
        })
        
        return True, "User deactivated successfully"
    
    def get_audit_logs(self, admin_user_id: str, limit: int = 100) -> List[Dict]:
        """Get audit logs (admin only)"""
        if not self.check_permission(admin_user_id, Permission.MANAGE_SECURITY):
            return []
        
        recent_logs = self.audit_logs[-limit:]
        return [
            {
                "timestamp": log.timestamp.isoformat(),
                "user_id": log.user_id,
                "action": log.action,
                "resource": log.resource,
                "ip_address": log.ip_address,
                "success": log.success,
                "details": log.details
            }
            for log in recent_logs
        ]
    
    def get_security_stats(self, admin_user_id: str) -> Dict:
        """Get security statistics (admin only)"""
        if not self.check_permission(admin_user_id, Permission.MANAGE_SECURITY):
            return {}
        
        total_users = len(self.users)
        active_users = sum(1 for u in self.users.values() if u.is_active)
        locked_users = sum(1 for u in self.users.values() if u.locked_until and u.locked_until > datetime.now())
        
        # Recent failed logins
        recent_failed = sum(1 for log in self.audit_logs[-1000:] if log.action == "login_failed")
        recent_successful = sum(1 for log in self.audit_logs[-1000:] if log.action == "login_success")
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "locked_users": locked_users,
            "recent_failed_logins": recent_failed,
            "recent_successful_logins": recent_successful,
            "total_audit_logs": len(self.audit_logs)
        }

# Global security manager instance
security_manager = SecurityManager()
