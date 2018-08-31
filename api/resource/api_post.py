from django.conf.urls import url
from django.contrib.auth.models import User
# from django.db import IntegrityError
from tastypie.resources import ModelResource
# from tastypie.http import HttpUnauthorized
from tastypie.authorization import Authorization
from tastypie.authentication import Authentication, ApiKeyAuthentication
# from tastypie.exceptions import BadRequest
from tastypie import fields
# from tastypie.models import ApiKey
from .authorizations.custom_authorization import PostObjectsOnlyAuthorization
from .api_authentication import UserResource
from api.models import Post


class PostResource(ModelResource):
    author = fields.ForeignKey(UserResource, 'author', full=True)

    class Meta:
        queryset = Post.objects.all()
        resource_name = 'posts'
        allowed_methods = ['get']
        include_resource_uri = False
        authentication = Authentication()
        authorization = Authorization()
        always_return_data = True


class MyPostResource(ModelResource):
    author = fields.ForeignKey(UserResource, 'author', full=True)

    class Meta:
        queryset = Post.objects.all()
        resource_name = 'my-posts'
        allowed_methods = ['get', 'post', 'put', 'delete']
        include_resource_uri = False
        authentication = ApiKeyAuthentication()
        authorization = PostObjectsOnlyAuthorization()
        always_return_data = True

    def authorized_read_list(self, object_list, bundle):
        return object_list.filter(author=bundle.request.user).select_related()


class UserPostResource(ModelResource):
    author = fields.ForeignKey(UserResource, 'author', full=True)

    class Meta:
        queryset = Post.objects.all()
        resource_name = 'user-posts'
        allowed_methods = ['get']
        include_resource_uri = False
        authentication = Authentication()
        authorization = Authorization()
        always_return_data = True

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<name>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('dispatch_list'), name="api_dispatch_list"),
        ]

    def dispatch_list(self, request, **kwargs):
        return self.get_list(request, **kwargs)

    def authorized_read_list(self, object_list, bundle):
        name = bundle.request.resolver_match.kwargs["name"]
        user = User.objects.get(username=name)
        return object_list.filter(author=user).select_related()
