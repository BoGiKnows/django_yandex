from django.utils import timezone

from django.db.models import Count


def annotate(notannotate_queryset):
    return notannotate_queryset.annotate(comment_count=Count('comments')).order_by('-pub_date')


def get_filtered_queryset(filtered_queryset):
    nq = filtered_queryset.filter(
         pub_date__date__lte=timezone.now(),
         is_published=True,
         category__is_published=True
         ).select_related(
            'location',
            'category',
            'author',
            )
    return annotate(nq)
