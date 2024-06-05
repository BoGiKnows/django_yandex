from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy

from blog.models import Comment


class CommentViewMixin:
    model = Comment
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.kwargs.get('post_id')})


class PostUpdateDeleteMixin:

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author == request.user:
            return super().dispatch(request, *args, **kwargs)
        return redirect(
            reverse_lazy(
                'blog:post_detail',
                kwargs={'post_id': self.kwargs['post_id']}
            )
        )