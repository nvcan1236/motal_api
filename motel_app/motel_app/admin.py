from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse


class MyAdminSite(admin.AdminSite):
    site_header = 'QUẢN LÝ HỆ THỐNG TÌM KIẾM TRỌ NACA'
    site_title = 'Hệ thống tìm kiếm trọ'
    index_title = 'Trang chủ'

    def get_urls(self):
        return [
            path('motel-stats/', self.motel_stats_view),
            path('post-stats/', self.post_stats_view),
        ] + super().get_urls()

    def motel_stats_view(self, request):
        return TemplateResponse(request, 'admin/motel-stats.html', {})

    def post_stats_view(self, request):
        return TemplateResponse(request, 'admin/post-stats.html', {})

    def get_app_list(self, request, app_label=None):
        return super().get_app_list(request) + [
            {
                'name': 'BÁO CÁO THỐNG KÊ',
                'models': [
                    {
                        'name': 'Motel Stats',
                        'admin_url': '/admin/motel-stats/'
                    },
                    {
                        'name': 'Post Stats',
                        'admin_url': '/admin/post-stats/'
                    },
                ]
            }
        ]


admin_site = MyAdminSite(name='myadminsite')
