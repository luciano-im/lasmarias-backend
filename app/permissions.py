from rest_framework import permissions

class SellerPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        is_seller = request.user.UserInfo.user_type
        return True if is_seller == 'VEN' else False
