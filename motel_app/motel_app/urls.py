from motel_app.admin import admin_site
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Course API",
        default_version='v1',
        description="APIs for Motel App - NACA",
        contact=openapi.Contact(email="2151053005canh@ou.edu.vn"),
        license=openapi.License(name="Nguyễn Văn Cảnh @ 2024"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny,],
)

urlpatterns = [
    path('admin/', admin_site.urls),
    path('motel/', include('motel.urls')),
    path('post/', include('post.urls')),
    re_path(r'^ckeditor/',
            include('ckeditor_uploader.urls')),
    path('o/', include('oauth2_provider.urls',
                       namespace='oauth2_provider')),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0),
            name='schema-json'),
    re_path(r'^swagger/$',
            schema_view.with_ui('swagger', cache_timeout=0),
            name='schema-swagger-ui'),
    re_path(r'^redoc/$',
            schema_view.with_ui('redoc', cache_timeout=0),
            name='schema-redoc'),

]
