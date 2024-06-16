from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import path
from django.template.response import TemplateResponse
from allauth.socialaccount.models import SocialApp
from vnpay.models import Billing

import motel.utils
import post.utils


class MyAdminSite(admin.AdminSite):
    site_header = 'QUẢN LÝ HỆ THỐNG TÌM KIẾM TRỌ NACA'
    site_title = 'Hệ thống tìm kiếm trọ'
    index_title = 'Trang chủ'

    def get_urls(self):
        return [
            path('motel-stats/', self.motel_stats_view),
            path('post-stats/', self.post_stats_view),
            path('user-stats/', self.user_stats_view),
        ] + super().get_urls()

    def motel_stats_view(self, request):
        if not request.user.is_authenticated:
            messages.error(request, "Bạn cần phải đăng nhập để xem thống kê.")
            return redirect('/admin/login/')
        stats = motel.utils.get_motel_stats()

        return TemplateResponse(request, 'admin/motel-stats.html', {**stats})

    def post_stats_view(self, request):
        if not request.user.is_authenticated:
            messages.error(request, "Bạn cần phải đăng nhập để xem thống kê.")
            return redirect('/admin/login/')
        stats = post.utils.get_post_stats()
        return TemplateResponse(request, 'admin/post-stats.html', {**stats})

    def user_stats_view(self, request):
        if not request.user.is_authenticated:
            messages.error(request, "Bạn cần phải đăng nhập để xem thống kê.")
            return redirect('/admin/login/')
        stats = motel.utils.get_user_stats()
        return TemplateResponse(request, 'admin/user-stats.html',
                                {**stats})

    def get_app_list(self, request, app_label=None):
        return super().get_app_list(request) + [
            {
                'name': 'BÁO CÁO THỐNG KÊ',
                'models': [
                    {
                        'name': 'Motel Stats',
                        'admin_url': '/admin/motel-stats/',
                        "view_only": True,
                    },
                    {
                        'name': 'Post Stats',
                        'admin_url': '/admin/post-stats/',
                        "view_only": True,
                    },
                    {
                        'name': 'User Stats',
                        'admin_url': '/admin/user-stats/',
                        "view_only": True,
                    },
                ]
            }
        ]


admin_site = MyAdminSite(name='myadminsite')
# admin_site.register(SocialApp)
admin_site.register(Billing)
