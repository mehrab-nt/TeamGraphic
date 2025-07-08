from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model

User = get_user_model()

class EnrichUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        """
        MEH: Replace request.user with an enriched version with select_related fields.
        """
        if request.user.is_authenticated:
            request.user = (
                User.objects
                .select_related(
                    'employee_profile__level',  # nested
                    'role',                     # for customer roles
                    'introducer',               # if needed
                    'introduce_from'            # if needed
                )
                .get(pk=request.user.pk)
            )