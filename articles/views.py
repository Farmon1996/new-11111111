from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect

from articles import forms
from articles.models import Article, Comment


@login_required(login_url='/users/sign_up')
def articles(request):
    search = request.GET.get('search')
    articles = Article.objects.all().order_by('date')
    articles = articles.filter(Q(title__icontains=search) | Q(text__icontains=search)) if search else articles
    return render(request, 'articles.html', {'articles': articles, })


def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug)
    form = forms.CommentForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        instance.article = article
        instance.save()
        return redirect('articles:article_detail', slug=article.slug)

    return render(request, 'article_detail.html', {
        'form': form,
        'article': article
    })


@login_required(login_url='/users/sign_in')
def article_create(request):
    form = forms.ArticleForm(request.POST or None, request.FILES)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('articles:articles')
    return render(request, 'article_create.html', {
        'form': form
    })


def edit_article(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if request.user != article.author:
        return render(request, 'error.html', {'article': article})
    form = forms.ArticleForm(request.POST or None, request.FILES or None, instance=article)
    if form.is_valid():
        form.save()
        return redirect('articles:article_detail', slug=slug)
    return render(request, 'edit_article.html', {
        'form': form,
        'article': article
    })


def delete_article(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if request.user != article.author:
        return render(request, 'error.html', {'article': article})
    if request.method == 'POST':
        article.delete()
        return redirect('articles:articles')
    return render(request, 'delete_article.html', {'article': article})


def like(request, slug):
    article = Article.objects.get(slug=slug)

    if request.user not in article.likes.all():
        article.likes.add(request.user)
        article.dislikes.remove(request.user)
    elif request.user in article.likes.all():
        article.likes.remove(request.user)
    return redirect('articles:article_detail', slug=slug)


def dislike(request, slug):
    article = Article.objects.get(slug=slug)

    if request.user not in article.dislikes.all():
        article.dislikes.add(request.user)
        article.likes.remove(request.user)
    elif request.user in article.dislikes.all():
        article.dislikes.remove(request.user)
    return redirect('articles:article_detail', slug=slug)


def delete_comment(request, pk):
    comment = Comment.objects.get(pk=pk)
    if request.user != comment.user:
        return render(request, 'error.html', {'article': comment})
    form = forms.ArticleForm(request.POST or None, request.FILES or None, instance=comment)

    if request.method == 'POST':
        comment.delete()
        return redirect('articles:article_detail', slug=comment.article.slug)
    return render(request, 'delete_comment.html', {
        'article': comment.article,
        'form':form
    })


def edit_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    form = forms.CommentForm(request.POST or None, instance=comment)
    if request.user != comment.user:
        return render(request, 'error.html', {'article': comment})
    if form.is_valid():
        form.save()
        return redirect('articles:article_detail', slug=comment.article.slug)
    return render(request, 'comment_edit.html', {
        'form': form,
        'article': comment.article
    })
