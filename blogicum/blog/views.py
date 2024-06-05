from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.db.models import Count
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (ListView,
                                  CreateView,
                                  UpdateView,
                                  DeleteView,
                                  DetailView)

from .forms import PostForm, UserForm, CommentForm
from .mixins import CommentViewMixin, PostUpdateDeleteMixin
from .models import Post, Category, User, Comment
from .constants import PUBLIC_POSTS_NUM
from .utils import get_filtered_queryset, annotate


class PostListView(ListView):
    template_name = 'blog/index.html'
    model = Post
    paginate_by = PUBLIC_POSTS_NUM
    queryset = get_filtered_queryset(Post.objects.all())


class PostDetailView(DetailView):
    model = Post
    form_class = PostForm
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self):
        post_queryset = Post.objects.filter(pk=self.kwargs['post_id'])
        post_obj = get_object_or_404(
            post_queryset,
            pk=self.kwargs['post_id']
        )
        if post_obj.author != self.request.user:
            return get_object_or_404(
                get_filtered_queryset(post_queryset),
                pk=self.kwargs['post_id']
            )
        return post_obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={
                'username': self.request.user
            }
        )


class PostUpdateView(LoginRequiredMixin, PostUpdateDeleteMixin, UpdateView):
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class PostDeleteView(LoginRequiredMixin, PostUpdateDeleteMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user})


class CategoryListView(ListView): 
    model = Post 
    template_name = 'blog/category.html' 
    paginate_by = PUBLIC_POSTS_NUM
    category = None

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return get_filtered_queryset(self.category.posts)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class ProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = PUBLIC_POSTS_NUM
    author = None

    def get_queryset(self):
        self.author = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        queryset = self.author.posts
        if self.author != self.request.user:
            return get_filtered_queryset(queryset)
        return annotate(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:index')


class CommentCreateView(CommentViewMixin, LoginRequiredMixin, CreateView):
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.post = get_object_or_404(
            Post,
            pk=self.kwargs['post_id'],
            is_published=True
        )
        form.instance.author = self.request.user
        return super().form_valid(form)


class CommentDeleteView(CommentViewMixin, LoginRequiredMixin, DeleteView):
    def get_object(self, **kwargs):
        return get_object_or_404(Comment,
                                 pk=self.kwargs.get('comment_id'),
                                 post=self.kwargs.get('post_id'),
                                 author=self.request.user)


class CommentUpdateView(CommentViewMixin, LoginRequiredMixin, UpdateView):
    form_class = CommentForm
    pk_field = 'comment_id'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        comment_obj = self.get_object()
        if comment_obj.author != self.request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)
