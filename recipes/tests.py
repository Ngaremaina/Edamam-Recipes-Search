from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import FavoriteRecipe, SearchHistory

MOCK_EDAMAM_RESPONSE = {
    "hits": [
        {
            "recipe": {
                "uri": "http://www.edamam.com/ontologies/edamam.owl#recipe_123",
                "label": "Pork Stew",
                "image": "http://example.com/pork.jpg",
                "source": "Test Kitchen",
                "url": "http://example.com/recipe/pork-stew",
                "calories": 450.0,
                "dishType": ["main course"],
                "ingredientLines": ["1 lb pork", "2 cups broth"],
            }
        }
    ]
}


def mock_edamam_get(*args, **kwargs):
    response = Mock()
    response.json.return_value = MOCK_EDAMAM_RESPONSE
    return response


class PublicPagesTests(TestCase):
    @patch('recipes.views.requests.get', side_effect=mock_edamam_get)
    def test_home_page_lists_recipes(self, mock_get):
        response = self.client.get(reverse('home-page'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pork Stew')
        mock_get.assert_called_once()

    def test_about_page(self):
        response = self.client.get(reverse('about-page'))
        self.assertEqual(response.status_code, 200)

    def test_contact_page(self):
        response = self.client.get(reverse('contact-page'))
        self.assertEqual(response.status_code, 200)


class RecipeSearchTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='s3cret-pass')

    @patch('recipes.views.requests.get', side_effect=mock_edamam_get)
    def test_search_records_history_for_authenticated_user(self, mock_get):
        self.client.force_login(self.user)
        response = self.client.post(reverse('recipe-search'), {'userText': 'pork'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(SearchHistory.objects.filter(user=self.user, query='pork').count(), 1)

    @patch('recipes.views.requests.get', side_effect=mock_edamam_get)
    def test_search_does_not_record_history_for_anonymous_user(self, mock_get):
        self.client.post(reverse('recipe-search'), {'userText': 'pork'})
        self.assertEqual(SearchHistory.objects.count(), 0)

    def test_search_get_request_returns_empty_results(self):
        response = self.client.get(reverse('recipe-search'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['recipes'], [])


class FavoriteToggleTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='bob', password='s3cret-pass')
        self.recipe_data = {
            'recipe_uri': 'http://www.edamam.com/ontologies/edamam.owl#recipe_123',
            'label': 'Pork Stew',
            'image': 'http://example.com/pork.jpg',
            'source': 'Test Kitchen',
            'url': 'http://example.com/recipe/pork-stew',
        }

    def test_requires_login(self):
        response = self.client.post(reverse('toggle-favorite'), self.recipe_data)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_toggle_creates_then_removes_favorite(self):
        self.client.force_login(self.user)

        self.client.post(reverse('toggle-favorite'), self.recipe_data)
        self.assertEqual(FavoriteRecipe.objects.filter(user=self.user).count(), 1)

        self.client.post(reverse('toggle-favorite'), self.recipe_data)
        self.assertEqual(FavoriteRecipe.objects.filter(user=self.user).count(), 0)

    def test_toggle_accepts_long_signed_urls(self):
        # Edamam's real image/recipe URLs are signed CDN links that can run
        # well past 1000 characters; this must not overflow the DB column.
        self.client.force_login(self.user)
        long_url_data = {
            **self.recipe_data,
            'image': 'http://example.com/pork.jpg?' + 'token=' + 'x' * 1500,
            'url': 'http://example.com/recipe/pork-stew?' + 'token=' + 'y' * 1500,
        }
        response = self.client.post(reverse('toggle-favorite'), long_url_data)
        self.assertEqual(response.status_code, 302)
        favorite = FavoriteRecipe.objects.get(user=self.user)
        self.assertEqual(len(favorite.image), len(long_url_data['image']))

    def test_favorite_is_scoped_to_owning_user(self):
        other_user = User.objects.create_user(username='carol', password='s3cret-pass')
        FavoriteRecipe.objects.create(user=other_user, recipe_uri='uri-1', label='Other')

        self.client.force_login(self.user)
        response = self.client.get(reverse('favorites'))
        self.assertNotContains(response, 'Other')


class HistoryFavoritesAccessTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='dave', password='s3cret-pass')

    def test_history_requires_login(self):
        response = self.client.get(reverse('history'))
        self.assertEqual(response.status_code, 302)

    def test_favorites_requires_login(self):
        response = self.client.get(reverse('favorites'))
        self.assertEqual(response.status_code, 302)

    def test_authenticated_user_sees_own_history(self):
        SearchHistory.objects.create(user=self.user, query='beef')
        self.client.force_login(self.user)
        response = self.client.get(reverse('history'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'beef')


class AuthFlowTests(TestCase):
    def test_register_creates_user_and_logs_in(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'a-strong-passw0rd',
            'password2': 'a-strong-passw0rd',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_view_renders(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_login_with_valid_credentials(self):
        User.objects.create_user(username='erin', password='s3cret-pass')
        response = self.client.post(reverse('login'), {
            'username': 'erin',
            'password': 's3cret-pass',
        })
        self.assertEqual(response.status_code, 302)


class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='frank', password='s3cret-pass')

    def test_search_history_str(self):
        entry = SearchHistory.objects.create(user=self.user, query='fish')
        self.assertIn('fish', str(entry))

    def test_favorite_unique_per_user_and_recipe(self):
        FavoriteRecipe.objects.create(user=self.user, recipe_uri='uri-1', label='Fish Tacos')
        with self.assertRaises(Exception):
            FavoriteRecipe.objects.create(user=self.user, recipe_uri='uri-1', label='Fish Tacos Again')
