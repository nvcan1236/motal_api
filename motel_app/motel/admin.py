from django.contrib import admin

from motel_app.admin import admin_site
from django.utils.html import mark_safe


from motel.models import Motel, User, MotelImage
from cloudinary.models import CloudinaryResource


@admin.action(description="Approve motel")
def approve_motel(modeladmin, request, queryset):
    queryset.update(approved=True)


@admin.action(description="Soft delete")
def soft_delete(modeladmin, request, queryset):
    queryset.update(is_active=False)


@admin.action(description="Activate")
def active(modeladmin, request, queryset):
    queryset.update(is_active=True)


class UserAdmin(admin.ModelAdmin):
    exclude = ('password',)
    readonly_fields = ['avatar_image']
    list_filter = ['is_active', 'user_role', 'gender']
    search_fields = ['email', 'phone', 'first_name', 'last_name']
    actions = [active, soft_delete]

    def avatar_image(self, obj):
        if obj.avatar:
            if type(obj.avatar) is CloudinaryResource:
                return mark_safe(
                    f'<img src="{obj.avatar.url}" height="200" alt="avatar" />'
                )
            return mark_safe(
                f'<img src="{obj.avatar.name}" height="200" alt="avatar" />'
            )


class ImageInline(admin.TabularInline):
    model = MotelImage
    readonly_fields = ['url']
    extra = 1  # Số lượng form trống hiển th


class MotelAdmin(admin.ModelAdmin):
    list_filter = ['approved', 'is_active']
    search_fields = ["ward", "district", "city", 'other_address', 'description', 'price']
    actions = [approve_motel, active, soft_delete]
    # inlines = [ImageInline]
    readonly_fields = ['display_images']

    def display_images(self, obj):
        images = ''.join(
            f'<img src="{image.url.url}" style="width:200px; max-height:120px;">' for image in obj.images.all())
        return mark_safe(f'<div style="width: 100%; display:flex; flex-wrap:wrap;">{images} </div>')


admin_site.register(User, UserAdmin)
admin_site.register(Motel, MotelAdmin)
