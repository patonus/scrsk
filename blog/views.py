from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, F
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Post, Comment
from .forms import SearchOptionsForm


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']

    def get(self, request, *args, **kwargs):
        self.form = SearchOptionsForm(request.GET)
        if self.form.is_valid() and self.form.cleaned_data.get('ascending_order') == 'true':
            self.ordering = ['date_posted']
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        query_set = Post.objects.all()
        if self.form.is_valid():
            request_params = self.form.cleaned_data
            title_pattern = request_params.get('title')
            if title_pattern:
                query_set = query_set.filter(title__icontains=title_pattern)
            author = request_params.get('author')
            if author:
                query_set = query_set.filter(author__username=author)
        if not query_set:
            messages.info(self.request, 'No posts found')
        return query_set.order_by(self.ordering[0])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        return context


class PostDetailView(DetailView):
    model = Post

    def get(self, request, *args, **kwargs):
        post = Post.objects.get(pk=kwargs['pk'])
        post.visits = F('visits') + 1
        post.save()
        return super().get(request, *args, **kwargs)


class PostCreateView(LoginRequiredMixin, CreateView):
    login_url = '/login/'
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    login_url = '/login/'

    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    login_url = '/login/'

    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class SidebarView(ListView):
    context_object_name = 'object_list'

    def get(self, request, *args, **kwargs):
        self.query = request.GET.get('query')
        if self.query:
            if self.query in ('most_popular_list', 'most_commented_list'):
                self.model = Post
                self.template_name = 'blog/sidebar_posts_view.html'
            elif self.query in ('top_users_list',):
                self.model = User
                self.template_name = 'blog/sidebar_users_view.html'
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if self.query == 'most_popular_list':
            return Post.objects.order_by('-visits')[:5]
        if self.query == 'most_commented_list':
            return Post.objects.all().annotate(num_comments=Count('comment')).order_by('-num_comments')[:5]
        if self.query == 'top_users_list':
            return User.objects.all().annotate(num_posts=Count('post')).order_by('-num_posts')[:5]


@login_required(login_url='/login/')
def comment_post_view(request, pk):
    if request.method == 'POST':
        comment_content = request.POST.get('comment')
        if not comment_content.strip():
            messages.warning(request, 'Cannot add empty comment')
        else:
            comment = Comment(content=comment_content,
                              author=request.user, post=Post.objects.get(pk=pk))
            comment.save()
    return HttpResponseRedirect(reverse('post-detail', args=(pk,)))
