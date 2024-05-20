from django.db.models.functions import TruncMonth, Floor
from django.template.loader import render_to_string
from django.utils import timezone

from django.db.models import Q, Count, F, IntegerField

from motel.models import User, UserRole, Motel, Follow
from django.core.mail import send_mail


def get_motel_stats():
    today = timezone.now()
    start_of_month = today.replace(day=1)
    end_of_month = start_of_month.replace(month=start_of_month.month % 12 + 1, day=1) - timezone.timedelta(days=1)
    PRICE_RANGE = 2000000
    AREA_RANGE = 5

    motel_count = Motel.objects.filter(is_active=True).count()
    approved_count = Motel.objects.filter(is_active=True, approved=True).count()
    new_motel_count = Motel.objects.filter(is_active=True, created_date__gte=start_of_month,
                                           created_date__lte=end_of_month).count()
    new_approved_motel_count = Motel.objects.filter(is_active=True, approved=True,
                                                    created_date__gte=start_of_month,
                                                    created_date__lte=end_of_month).count()

    stats = (Motel.objects.filter(is_active=True)
             .annotate(month=TruncMonth('created_date')).values('month')
             .annotate(count=Count('id'))
             .annotate(approved_count=Count('id', filter=Q(approved=True)))
             .order_by('month')
             )

    price_stats = (Motel.objects.filter(is_active=True, approved=True)
                   .annotate(price_range=Floor(F('price') / PRICE_RANGE)).values('price_range')
                   .annotate(count=Count('id'))
                   ).order_by('price_range').all()

    area_stats = (Motel.objects.filter(is_active=True, approved=True)
                  .annotate(area_range=Floor(F('area') / AREA_RANGE)).values('area_range')
                  .annotate(count=Count('id'))
                  ).order_by('area_range').all()

    for item in stats:
        item['month'] = f"{item['month'].month}-{item['month'].year}"

    for item in price_stats:
        item['price_range'] = f"{item['price_range'] * PRICE_RANGE} - {item['price_range'] * PRICE_RANGE + PRICE_RANGE}"

    for item in area_stats:
        item['area_range'] = f"{item['area_range'] * AREA_RANGE} - {item['area_range'] * AREA_RANGE + AREA_RANGE}"

    return {
        'motel_count': motel_count,
        'approved_count': approved_count,
        'new_motel_count': new_motel_count,
        'new_approved_motel_count': new_approved_motel_count,
        'price_stats': price_stats,
        'area_stats': area_stats,
        'stats': stats,
    }


def get_user_stats():
    user_count = User.objects.filter(is_active=True).count()
    owner = User.objects.filter(is_active=True, user_role=UserRole.MOTEL_OWNER).count()
    tenant = User.objects.filter(is_active=True, user_role=UserRole.TENANT).count()

    today = timezone.now()
    start_of_month = today.replace(day=1)
    end_of_month = start_of_month.replace(month=start_of_month.month % 12 + 1, day=1) - timezone.timedelta(days=1)
    new_user = User.objects.filter(is_active=True,
                                   date_joined__gte=start_of_month,
                                   date_joined__lte=end_of_month,
                                   ).count()
    new_owner = User.objects.filter(is_active=True,
                                    user_role=UserRole.MOTEL_OWNER,
                                    date_joined__gte=start_of_month,
                                    date_joined__lte=end_of_month).count()
    new_tenant = User.objects.filter(is_active=True,
                                     user_role=UserRole.TENANT,
                                     date_joined__gte=start_of_month,
                                     date_joined__lte=end_of_month).count()

    stats = (User.objects
             .annotate(month=TruncMonth('date_joined'))
             .values('month', 'user_role')
             .annotate(count=Count('id'))
             .order_by('month', 'user_role'))

    formated_stats = {}
    for s in stats:
        month = s['month'].strftime('%m-%Y')
        role = s['user_role'] = 'owner' if s['user_role'] == UserRole.MOTEL_OWNER else 'tenant'
        count = s['count']
        if month not in formated_stats:
            formated_stats[month] = {role: count}
        else:
            formated_stats[month][role] = count

    stats = {
        'user_count': user_count,
        'owner_count': owner,
        'tenant_count': tenant,
        'new_user_count': new_user,
        'new_owner_count': new_owner,
        'new_tenant_count': new_tenant,
        'stats': formated_stats,
    }
    return stats


def send_motel_news_email(context):
    html_context = {
        'address': f"{context.get('motel').get('other_address')} - {context.get('motel').get('ward')} - {context.get('motel').get('district')} - {context.get('motel').get('city')}",
        'area': context.get('motel').get('area'),
        'price': context.get('motel').get('price'),
        'description': context.get('motel').get('description'),
        'furniture': context.get('motel').get('furniture'),
        'owner': context.get('user')
    }
    template_html = render_to_string('motel_email_template.html', html_context)
    # danh sách follower
    # get_follower_emails(context['user'].id)
    receivers = ['ngcanh1236@gmail.com', 'nganbui.23112003@gmail.com']

    send_mail('New activity from your follower', None,
              "NACA motel",
              receivers,
              fail_silently=False,
              html_message=template_html,
              )


def get_follower_emails(user_id):
    follower = Follow.objects.filter(following=user_id, is_active=True).all()
    emails = [u.follower.email for u in follower]
    return emails
