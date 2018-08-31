from django.conf.urls import url
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from tastypie.resources import ModelResource
from tastypie.http import HttpUnauthorized, HttpForbidden
from tastypie.authorization import Authorization
from tastypie.authentication import Authentication, BasicAuthentication, ApiKeyAuthentication
from tastypie.exceptions import BadRequest
from tastypie.utils import trailing_slash
from tastypie import fields
from api.models import Profile


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        fields = ['username', 'first_name', 'last_name']
        excludes = ['email', 'password', 'is_superuser']
        resource_name = 'auth/users'
        include_resource_uri = False
        authentication = BasicAuthentication()
        authorization = Authorization()


class UserSignUpResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user', full=True)

    class Meta:
        queryset = Profile.objects.all()
        object_class = Profile
        resource_name = 'registers'
        allowed_methods = ['post']
        authentication = Authentication()
        authorization = Authorization()
        always_return_data = True

    def obj_create(self, bundle, **kwargs):
        try:
            bundle = super(UserSignUpResource, self).obj_create(bundle)
            bundle.obj.user.set_password(bundle.data['user']['password'])
            bundle.obj.user.save()
        except IntegrityError:
            raise BadRequest('Username already exists')
        return bundle


class AuthenticationResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        excludes = ['password', 'is_superuser']
        allowed_methods = ['get', 'post']
        resource_name = 'authen'
        authentication = Authentication()
        authorization = Authorization()
        always_return_data = True

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/sign_in%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('sign_in'), name="api_sign_in"),
            url(r"^(?P<resource_name>%s)/sign_out%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('sign_out'), name="api_sign_out"),
        ]

    def sign_in(self, request, **kwargs): 
        self.method_check(request, allowed=['post'])
        data = self.deserialize(request, request.body,
                                format=request.META.get('CONTENT_TYPE', 'application/json'))

        username = data.get('username', '')
        password = data.get('password', '')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return self.create_response(request, {
                    'success': True,
                    'api_key': user.api_key.key
                })
            else:
                return self.create_response(request, {
                    'success': False,
                    'reason': 'disabled',
                }, HttpForbidden)
        else:
            return self.create_response(request, {
                'success': False,
                'reason': 'incorrect',
            }, HttpUnauthorized)

    def sign_out(self, request, **kwargs):
        self.is_authenticated(request)
        self.method_check(request, allowed=['get'])
        if request.user and request.user.is_authenticated:
            logout(request)
            return self.create_response(request, {'success': True})
        else:
            return self.create_response(request, {'success': False,
                                                  'error_message': 'You are not authenticated, %s' % request.user.is_authenticated})


class UserProfileResource(ModelResource):
    user = fields.ForeignKey(UserResource, attribute='user', full=True)

    class Meta:
        queryset = Profile.objects.all()
        resource_name = 'userprofile'
        allowed_methods = ['post', 'put', 'patch', 'get']
        authentication = ApiKeyAuthentication()
        authorization = Authorization()
        fields = ['other_name', 'birthday', 'address', 'phone_number',
                  'photo_url', 'user']
        always_return_data = True
        include_resource_uri = False

    def authorized_read_list(self, object_list, bundle):
        return object_list.filter(user=bundle.request.user.id).select_related()
