from django.shortcuts import render
from .models import Post
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Post
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
            pattern = request_params.get('search_pattern')
            by_title, by_author = request_params.get('search_title'), request_params.get('search_author')
            if pattern:
                query_set = Post.objects.none()
                if not by_author and not by_author:
                    by_title = True
                if by_title:
                    query_set = query_set | Post.objects.filter(title__icontains=pattern)
                if by_author:
                    query_set = query_set | Post.objects.filter(author__username__icontains=pattern)
        if not query_set:
            messages.info(self.request, 'No posts found')
        return query_set.order_by(self.ordering[0])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        return context


class PostDetailView(DetailView):
    model = Post


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
