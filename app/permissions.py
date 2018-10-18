from rest_framework import permissions

class SellerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        is_seller = request.user.userinfo.user_type
        return True if is_seller == 'VEN' else False


class HasPermissionOrSeller(permissions.BasePermission):
    def has_permission(self, request, view):
        user_id = view.kwargs['user_id']
        customer_id = request.user.userinfo.customer_id_id
        is_seller = request.user.userinfo.user_type
        # If request is Create or Update check that received customer_id
        # matches with the URL's customer_id
        # If the previous condition it's ok then check that URL's customer_id
        # matches with the customer_id of logged user, or user type is a seller
        if request.method == 'POST' or request.method == 'PUT':
            if request.data['customer_id'] == user_id:
                if user_id == customer_id or is_seller == 'VEN':
                    return True
                else:
                    return False
            else:
                return False
        # If request is GET check that URL's customer_id matches with the customer_id
        # of logged user, or user type is a seller
        else:
            if user_id == customer_id or is_seller == 'VEN':
                return True
            else:
                return False
