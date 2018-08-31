from tastypie.http import HttpUnauthorized
from tastypie.authentication import ApiKeyAuthentication
from tastypie.models import ApiKey


class ApiKeyAuthenticationExt(ApiKeyAuthentication):
    def extract_credentials(self, request):
        try:
            if request.GET.get('api_key'):
                api_key = request.GET['api_key']
            elif request.META.get('HTTP_AUTHORIZATION'):
                api_key = request.META.get('HTTP_AUTHORIZATION')
            else:
                raise ValueError("Incorrect authorization header.")
        except Exception:
            raise ValueError("Incorrect authorization header.")

        return api_key

    def is_authenticated(self, request, **kwargs):
        try:
            api_key = self.extract_credentials(request)
        except ValueError:
            return self._unauthorized

        # Bypass all Get methods
        if not api_key and request.method == "GET":
            return True
        elif api_key and not request.user.is_authenticated:
            try:
                apiKey = ApiKey.objects \
                    .filter(key__iexact=api_key) \
                    .prefetch_related('user') \
                    .prefetch_related('user__userprofile') \
                    .first()

                user = apiKey.user
            except (ApiKey.DoesNotExist, ApiKey.MultipleObjectReturned):
                return self._unauthorized()

            if not self.check_active(user):
                return False

            key_auth_check = self.get_key(user, api_key)
            if key_auth_check and not isinstance(key_auth_check, HttpUnauthorized):
                request.user = user

            return key_auth_check
        elif api_key and request.user.is_authenticated:
            return True
        else:
            return self._unauthorized()

    def get_identifier(self, request):
        if request.method == "GET":
            return True

        api_key = self.extract_credentials(request)
        return api_key or 'nouser'
