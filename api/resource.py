from tastypie.resources import ModelResource, ALL
from tastypie.authorization import Authorization
from tastypie.authentication import Authentication, BasicAuthentication, MultiAuthentication, ApiKeyAuthentication
from tastypie.exceptions import BadRequest
from tastypie import fields
from django.contrib.auth.models import User
from django.db import IntegrityError
from api.models import Profile


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        fields = ['username', 'first_name', 'last_name']
        excludes = ['email', 'password', 'is_superuser']
        resource_name = 'auth/users'
        # filtering = {
        #     "slug": ('exact', 'startswith',),
        #     "username": ALL,
        # }
        include_resource_uri = False
        authentication = ApiKeyAuthentication()
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


class UserSignInResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        excludes = ['password', 'is_superuser']
        resource_name = 'auth/users'
        filtering = {
            "slug": ('exact', 'startswith',),
            "username": ALL,
        }
        authentication = ApiKeyAuthentication()
        authorization = Authorization()

    def dehydrate(self, bundle):
        bundle.data['key'] = bundle.obj.api_key.key
        return bundle


class ProfileResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user', full=True)

    class Meta:
        queryset = Profile.objects.all()
        resource_name = 'profiles'
        # allowed_methods = ['post','put','patch']
        authentication = Authentication()
        authorization = Authorization()
        fields = ['other_name', 'birthday', 'address', 'phone_number',
                  'photo_url', 'user']
        always_return_data = True
        include_resource_uri = False
