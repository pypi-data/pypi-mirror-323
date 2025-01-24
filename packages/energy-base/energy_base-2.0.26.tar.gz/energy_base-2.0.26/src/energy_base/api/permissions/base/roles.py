from rest_framework.permissions import IsAuthenticated


class BaseRolePermissions(IsAuthenticated):
    required_role = None

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        if hasattr(request.user, 'roles'):
            return self.required_role in request.user.roles

        return False