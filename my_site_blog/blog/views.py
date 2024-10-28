from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_POST

from blog.models import Post
from blog.forms import CommentForm, EmailPostForm
from common.views import CommandMixin


class PostListView(CommandMixin, ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    template_name = 'blog/post/list.html'
    paginate_by = 3
    title = 'My blog'


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
    context = {
        'title': post.title,
        'post': post,
        'comments': comments,
        'form': form
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
