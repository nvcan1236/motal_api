import enum

from cloudinary.models import CloudinaryField
from django.db import models
from motel.models import BaseModel, Motel, User
from ckeditor.fields import RichTextField


class Post(BaseModel):
    content = RichTextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')


class PostForLease(Post):
    motel = models.ForeignKey(Motel, on_delete=models.CASCADE, related_name='posts')


class PostForRent(Post):
    ward = models.CharField(max_length=255)
    district = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    other_address = models.CharField(max_length=255)
    image = CloudinaryField()


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
