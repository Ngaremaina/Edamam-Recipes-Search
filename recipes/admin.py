from django.contrib import admin

from .models import FavoriteRecipe, SearchHistory


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'query', 'searched_at')
    list_filter = ('searched_at',)
    search_fields = ('query', 'user__username')


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'label', 'saved_at')
    list_filter = ('saved_at',)
    search_fields = ('label', 'user__username')
