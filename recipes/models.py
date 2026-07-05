from django.conf import settings
from django.db import models


class SearchHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='search_history',
    )
    query = models.CharField(max_length=255)
    searched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-searched_at']
        verbose_name_plural = 'search history'

    def __str__(self):
        return f'{self.user} searched "{self.query}"'


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
    )
    recipe_uri = models.CharField(max_length=500)
    label = models.CharField(max_length=255)
    image = models.TextField(blank=True)
    source = models.CharField(max_length=255, blank=True)
    url = models.TextField(blank=True)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-saved_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe_uri'], name='unique_user_favorite_recipe'),
        ]

    def __str__(self):
        return f'{self.user} favorited {self.label}'
