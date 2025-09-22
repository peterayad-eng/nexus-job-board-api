from rest_framework import permissions

class IsAdminUserRole(permissions.BasePermission):
    """Allows access only to admin users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin_user()

class IsEmployerUser(permissions.BasePermission):
    """Allows access only to employer users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_employer()

class IsJobSeekerUser(permissions.BasePermission):
    """Allows access only to job seeker users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_job_seeker()

class IsCompanyManager(permissions.BasePermission):
    """Allows access only to managers of a specific company."""
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated and (
                obj.created_by == request.user or 
                obj.managers.filter(id=request.user.id).exists() or
                request.user.is_admin_user()
            )
        )

class IsOwnerOrAdmin(permissions.BasePermission):
    """Allows access only to the owner of the object or admin users."""
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated and (
                getattr(obj, "user", obj) == request.user or 
                request.user.is_admin_user()
            )
        )

class IsCompanyOwnerOrAdmin(permissions.BasePermission):
    """Allows only company creator or admin users."""
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated and (
                obj.created_by == request.user or 
                request.user.is_admin_user()
            )
        )

class IsUserOwnerOrAdmin(permissions.BasePermission):
    """Allows access only to the user themselves or admin users."""
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
            
        if request.user.is_admin_user():
            return True
            
        return obj == request.user

class IsJobOwnerOrManager(permissions.BasePermission):
    """Allows access to job owners, company managers, or admin users."""

    def has_permission(self, request, view):
        # Require authentication for any job-related action
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user.is_authenticated:
            return False

        # Admins always allowed
        if user.is_admin_user():
            return True

        # Resolve job object
        job = None
        if hasattr(obj, "posted_by"):   # e.g. Job object
            job = obj
        elif hasattr(obj, "job"):       # e.g. Application object
            job = obj.job

        # Job owner check
        if job and job.posted_by == user:
            return True

        # Resolve company object
        company = None
        if hasattr(obj, "company"):     # e.g. Job.company
            company = obj.company
        elif job and hasattr(job, "company"):  # e.g. Application.job.company
            company = job.company

        # Company manager check
        if company and company.managers.filter(id=user.id).exists():
            return True

        return False

