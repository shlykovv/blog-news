from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.postgres.search import (SearchVector, SearchQuery,
                                            SearchRank, TrigramSimilarity)
from django.db.models import Count
from taggit.models import Tag

from blog.models import Post
from blog.forms import CommentForm, EmailPostForm, SearchForm
from common.views import CommandMixin


# class PostListView(CommandMixin, ListView):
#     queryset = Post.published.all()
#     context_object_name = 'posts'
#     template_name = 'blog/post/list.html'
#     paginate_by = 3
#     title = 'My blog'
def post_share(request, post_id):
    # Извлечь пост по идентификатору id
    post = get_object_or_404(Post,
                             id=post_id,
                             status=Post.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f'{cd["name"]} recommends you read {post.title}'
            message = f'Read {post.title} at {post_url}\n\n{cd["name"]} \'s comments: {cd["comments"]}'
            send_mail(subject=subject, message=message, from_email=settings.EMAIL_HOST_USER, recipient_list=[cd['to']])
            sent = True
    else:
        form = CommentForm()
    context = {
        'post': post,
        'form': form,
        'sent': sent,
        'title': 'Send e-mail'
    }
    return render(request, 'blog/post/share.html', context)


def post_detail(request, year, month, day, post_slug):
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post_slug,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day
        )
    # Список комментариев к данному посту
    comments = post.comments.filter(active=True)
    # Форма для комментирования пользователями
    form = CommentForm()
    # Список схожих постов
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_post = Post.published.filter(
        tags__in=post_tags_ids).exclude(id=post.id)
    similar_post = similar_post.annotate(
        same_tags=Count('tags')).order_by(
            '-same_tags', '-publish')[:4]
    context = {
        'title': post.title,
        'post': post,
        'comments': comments,
        'form': form,
        'similar_posts': similar_post
    }
    return render(request, 'blog/post/detail.html', context)


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    context = {
        'title': 'Add a comment',
        'post': post,
        'form': form,
        'comment': comment
    }
    return render(request, 'blog/post/comment.html', context)


def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    context = {
        'posts': posts,
        'tag': tag
    }
    return render(request, 'blog/post/list.html', context)


def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', weight='A') + \
                            SearchVector('body', weight='B')
            search_query = SearchQuery(query, config='spanish')
            # results = Post.published.annotate(
            #     search=search_vector,
            #     rank=SearchRank(search_vector, search_query)
            # ).filter(rank__gte=0.3).order_by('-rank')
            # Триграммный метод поиска
            results = Post.published.annotate(
                similarity=TrigramSimilarity('title', query),
            ).filter(similarity__gt=0.1).order_by('similarity')
    context = {
        'title': 'Search',
        'form': form,
        'query': query,
        'results': results
    }
    return render(request, 'blog/post/search.html', context)
