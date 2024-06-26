from motel_app.admin import admin_site
from django.contrib import admin
from django import forms
from post.models import PostForRent, PostForLease, Post
from ckeditor_uploader.widgets import CKEditorUploadingWidget


class PostForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = Post
        fields = '__all__'


class PostForRentAdmin(admin.ModelAdmin):
    list_display = ['user', 'ward', 'district', 'city', 'other_address', 'is_active', ]
    form = PostForm


class PostForLeaseAdmin(admin.ModelAdmin):
    list_display = ['user', 'motel', 'is_active', ]
    form = PostForm


# Register your models here.
admin_site.register(PostForRent, PostForRentAdmin)
admin_site.register(PostForLease, PostForLeaseAdmin)
