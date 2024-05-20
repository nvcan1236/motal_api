from django.db.models import Count, F, Sum, Avg
from django.db.models.functions import TruncMonth
from django.utils import timezone

from post.models import PostForLease, PostForRent, Post


def get_post_stats():
    today = timezone.now()
    start_of_month = today.replace(day=1)
    end_of_month = start_of_month.replace(month=start_of_month.month % 12 + 1, day=1) - timezone.timedelta(days=1)

    post_for_lease_count = PostForLease.objects.count()
    post_for_rent_count = PostForRent.objects.filter(is_active=True).count()

    new_post_for_lease_count = PostForLease.objects.filter(
        created_date__lte=end_of_month,
        created_date__gte=start_of_month).count()
    new_post_for_rent_count = PostForRent.objects.filter(
        created_date__lte=end_of_month,
        created_date__gte=start_of_month).count()

    post_for_lease_stats = (PostForLease.objects
                            .annotate(month=TruncMonth('created_date')).values('month')
                            .annotate(count=Count('id'))).order_by('month')

    post_for_rent_stats = (PostForRent.objects
                           .annotate(month=TruncMonth('created_date')).values('month')
                           .annotate(count=Count('id'))).order_by('month')

    interaction_stats = (Post.objects
                         .annotate(month=TruncMonth('created_date')).values('month')
                         .annotate(post_count=Count('id', distinct=True),
                                   comment_count=Count('comments', distinct=True),
                                   like_count=Count('likes', distinct=True))
                         .order_by('month')
                         )

    # Format month
    for item in post_for_lease_stats:
        item['month'] = f"{item['month'].month}-{item['month'].year}"

    for item in post_for_rent_stats:
        item['month'] = f"{item['month'].month}-{item['month'].year}"

    for item in interaction_stats:
        item['month'] = f"{item['month'].month}-{item['month'].year}"

    #
    formatted_post_stats = list(post_for_lease_stats)
    for item in formatted_post_stats:
        item['count_pfr'] = 0

    for prent in post_for_rent_stats:
        f = False
        for please in formatted_post_stats:
            if please['month'] == prent['month']:
                please['count_pfr'] = prent['count']
                f = True
        if not f:
            formatted_post_stats.append({
                'month': prent['month'],
                'count': 0,
                'count_pfr': prent['count']
            })
    formatted_post_stats = sorted(formatted_post_stats,
                                  key=lambda x: (int(x['month'].split('-')[1]), int(x['month'].split('-')[0])))

    return {
        'post_for_lease_count': post_for_lease_count,
        'post_for_rent_count': post_for_rent_count,
        'new_post_for_lease_count': new_post_for_lease_count,
        'new_post_for_rent_count': new_post_for_rent_count,
        'post_for_lease_stats': formatted_post_stats,
        'post_for_rent_stats': post_for_rent_stats,
        'interaction_stats': interaction_stats,
    }
