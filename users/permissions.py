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
        # Handle different object types
        if hasattr(obj, 'company'):
            # For Job objects
            company = obj.company
        elif hasattr(obj, 'job') and hasattr(obj.job, 'company'):
            # For Application objects
            company = obj.job.company
        else:
            # For Company objects
            company = obj
            
        return (
            request.user.is_authenticated and (
                getattr(company, 'created_by', None) == request.user or 
                company.managers.filter(id=request.user.id).exists() or
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
        # Require authentication
        if not request.user or not request.user.is_authenticated:
            return False

        # Admins always allowed
        if request.user.is_admin_user():
            return True

        # For JobApplicationsView - check if user owns the job or manages the company
        if hasattr(view, 'kwargs') and 'job_id' in view.kwargs:
            from jobs.models import Job
            try:
                job = Job.objects.get(id=view.kwargs['job_id'])
                return (job.posted_by == request.user or 
                        job.company.managers.filter(id=request.user.id).exists())
            except Job.DoesNotExist:
                return False

        # For CompanyApplicationsView - check if user manages the company
        if hasattr(view, 'kwargs') and 'company_id' in view.kwargs:
            from companies.models import Company
            try:
                company = Company.objects.get(id=view.kwargs['company_id'])
                return (company.created_by == request.user or 
                        company.managers.filter(id=request.user.id).exists())
            except Company.DoesNotExist:
                return False

        return True


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

