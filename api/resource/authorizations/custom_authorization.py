from __future__ import absolute_import
from tastypie.authorization import Authorization
from tastypie.exceptions import Unauthorized


class PostObjectsOnlyAuthorization(Authorization):

    def update_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no update by bundle.")

    def update_detail(self, object_list, bundle):
        return bundle.obj.author == bundle.request.user or bundle.request.user.is_superuser

    def delete_detail(self, object_list, bundle):
        return bundle.obj.author == bundle.request.user or bundle.request.user.is_superuser

    def delete_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes by bundle")
