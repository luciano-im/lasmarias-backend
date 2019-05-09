from rest_framework import permissions

class SellerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        is_seller = request.user.userinfo.user_type
        return True if is_seller == 'VEN' else False


class HasPermissionOrSeller(permissions.BasePermission):
    def has_permission(self, request, view):
        # If seller return True
        is_seller = request.user.userinfo.user_type
        if is_seller == 'VEN':
            return True
        else:
            # If customer received by params matches with customer selected on User profile return True
            try:
                customer_url = view.kwargs['customer_id']
            except:
                return False
            customer_id = request.user.userinfo.customer_id_id
            if customer_url == customer_id:
                return True
            else:
                return False