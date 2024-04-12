from django.contrib import admin
from motel_app.admin import admin_site
from django.utils.html import mark_safe

from motel.models import Motel, User, Reservation, Follow


class UserAdmin(admin.ModelAdmin):
    exclude = ('password',)
    readonly_fields = ['avatar_image']

    def avatar_image(self, obj):
        if obj.avatar:
            return mark_safe(
                f'<img src="{obj.avatar.name}" width="200" alt="avatar" />'
            )


admin_site.register(User, UserAdmin)
admin_site.register(Motel)
