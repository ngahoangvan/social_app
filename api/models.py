from enum import Enum
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    other_name = models.CharField(max_length=255, blank=True)
    birthday = models.DateField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=255, blank=True)
    photo_url = models.CharField(max_length=255, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    @property
    def full_name(self):
        "Full name of user"
        return '%s %s' % (self.user.first_name, self.user.last_name)

    def __str__(self):
        return self.full_name

class Relationship(models.Model):
    # class STATUS_IN_RELATIONSHIP(Enum):
    #     pending = 0
    #     accepted = 1
    #     declined = 2
    #     blocked = 3

    STATUS_IN_RELATIONSHIP = (
        (0, 'pending'),
        (1, 'accepted'),
        (2, 'declined'),
        (3, 'blocked'),
    )
    user_one = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_one')
    user_two = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_two')
    # status = models.IntegerField(choices=[(rela, rela.value) for rela in STATUS_IN_RELATIONSHIP],
    #                              default=STATUS_IN_RELATIONSHIP.pending)
    status = models.IntegerField(choices=STATUS_IN_RELATIONSHIP, default=0)
    action_user_id = models.IntegerField()

class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    image_path = models.CharField(max_length=255)
    image_title = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    comments_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    watchers_count = models.IntegerField(default=0)

    def __str__(self):
        return str(self.title) + ' -Post of ' + str(self.author.last_name)

class Like(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_liked')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_liked')

    def __str__(self):
        return str(self.author.last_name) + ' liked ' + str(self.post.title)

class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_commented')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_commented')
