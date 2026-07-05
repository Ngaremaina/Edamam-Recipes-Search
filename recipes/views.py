import requests
from django.conf import settings
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import RegisterForm
from .models import FavoriteRecipe, SearchHistory


def _fetch_recipes(query):
    response = requests.get(
        "https://api.edamam.com/api/recipes/v2",
        params={
            'type': 'public',
            'q': query,
            'app_id': settings.EDAMAM_APP_ID,
            'app_key': settings.EDAMAM_APP_KEY,
        },
    )
    return response.json().get('hits', [])


def _annotate_favorites(request, recipes):
    if request.user.is_authenticated:
        favorite_uris = set(
            FavoriteRecipe.objects.filter(user=request.user).values_list('recipe_uri', flat=True)
        )
        for hit in recipes:
            hit['is_favorited'] = hit.get('recipe', {}).get('uri') in favorite_uris
    return recipes


def index(request):
    # Get 'q' parameter from the request, default to "pork"
    query_set = request.GET.get('userText', 'pork')
    recipes = _annotate_favorites(request, _fetch_recipes(query_set))

    return render(request, 'recipes/index.html', {
        "recipes": recipes,
        "query": query_set,
    })


def recipe_search(request):
    if request.method == 'POST':
        user_text = request.POST.get('userText', '')
        recipes = _annotate_favorites(request, _fetch_recipes(user_text))
        if request.user.is_authenticated and user_text:
            SearchHistory.objects.create(user=request.user, query=user_text)
        return render(request, 'recipes/index.html', {
            "recipes": recipes,
            "query": user_text,
        })
    else:
        return render(request, 'recipes/index.html', {
            "recipes": [],
            "query": "",
        })


def about(request):
    return render(request, 'recipes/about.html')


def contact(request):
    return render(request, 'recipes/contact.html', {
        'flag_emoji': '🇰🇪',
    })


def register(request):
    if request.user.is_authenticated:
        return redirect('home-page')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home-page')
    else:
        form = RegisterForm()
    return render(request, 'recipes/register.html', {'form': form})


@login_required
def history(request):
    return render(request, 'recipes/history.html', {
        'history': request.user.search_history.all()[:50],
    })


@login_required
def favorites(request):
    return render(request, 'recipes/favorites.html', {
        'favorites': request.user.favorite_recipes.all(),
    })


@login_required
def toggle_favorite(request):
    if request.method == 'POST':
        recipe_uri = request.POST.get('recipe_uri')
        favorite, created = FavoriteRecipe.objects.get_or_create(
            user=request.user,
            recipe_uri=recipe_uri,
            defaults={
                'label': request.POST.get('label', ''),
                'image': request.POST.get('image', ''),
                'source': request.POST.get('source', ''),
                'url': request.POST.get('url', ''),
            },
        )
        if not created:
            favorite.delete()

    referer = request.META.get('HTTP_REFERER')
    if referer and url_has_allowed_host_and_scheme(referer, allowed_hosts={request.get_host()}):
        return redirect(referer)
    return redirect('home-page')
