import enum

from django.db import models
from motel.models import BaseModel, Motel, User, Image


class Post(BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')


class PostForLease(Post):
    motel = models.ForeignKey(Motel, on_delete=models.CASCADE, related_name='posts')


class PostImage(Image):
    post = models.ForeignKey(Post, related_name='images', on_delete=models.CASCADE)


class Interaction(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class Like(Interaction):
    class Meta:
        unique_together = ('user', 'post')


class Comment(Interaction):
    content = models.TextField()
    reply_for = models.ForeignKey('self', related_name='replies', on_delete=models.CASCADE)
