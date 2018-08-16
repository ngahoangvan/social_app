from tastypie.resources import ModelResource, ALL
from tastypie.authorization import Authorization
from tastypie.authentication import Authentication
from tastypie.exceptions import BadRequest
from tastypie import fields
from django.contrib.auth.models import User
from django.db import IntegrityError
from api.models import Profile
import tastypie

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        # resource_name = 'user'
        allowed_methods = ('get', 'post', 'put', 'delete', 'patch')
        # filtering = {"id": ALL}
        authentication = Authentication()
        authorization = Authorization()

    # def dehydrate(self, bundle):
    #     return super(UserResource, self).dehydrate(bundle=bundle)

class UserSignUpResource(ModelResource):
    user = tastypie.fields.ForeignKey(UserResource, 'user', full=True)

    class Meta:
        queryset = Profile.objects.all()
        object_class = Profile
        resource_name = 'register'
        fields = ['user', 'address', 'birthday']
        allowed_methods = ['post']
        # include_resource_uri = False
        authentication = Authentication()
        authorization = Authorization()
        always_return_data = True

    def obj_create(self, bundle, request=None, **kwargs):
        try:
            bundle = super(UserSignUpResource, self).obj_create(bundle)
            bundle.obj.set_password(bundle.data.get('password'))
            bundle.obj.save()
        except IntegrityError:
            raise BadRequest('Username already exists')

        return bundle

# class ProfileResource(ModelResource):
#     user = fields.ForeignKey(UserResource, 'user')

#     class Meta:
#         queryset = Profile.objects.all()
#         resource_name = 'profile'
