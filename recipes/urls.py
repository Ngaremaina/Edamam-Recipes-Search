from django.contrib.auth import views as auth_views
from django.urls import path

from recipes import views
from recipes.forms import StyledAuthenticationForm, StyledPasswordResetForm, StyledSetPasswordForm

urlpatterns = [
    path('', views.index, name="home-page"),
    path('search', views.recipe_search, name="recipe-search"),
    path('about', views.about, name="about-page"),
    path('contact', views.contact, name="contact-page"),

    path('register', views.register, name='register'),
    path('login', auth_views.LoginView.as_view(
        template_name='recipes/login.html',
        authentication_form=StyledAuthenticationForm,
    ), name='login'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),

    path('password-reset', auth_views.PasswordResetView.as_view(
        template_name='recipes/password_reset.html',
        email_template_name='recipes/password_reset_email.html',
        subject_template_name='recipes/password_reset_subject.txt',
        form_class=StyledPasswordResetForm,
    ), name='password_reset'),
    path('password-reset/done', auth_views.PasswordResetDoneView.as_view(
        template_name='recipes/password_reset_done.html',
    ), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(
        template_name='recipes/password_reset_confirm.html',
        form_class=StyledSetPasswordForm,
    ), name='password_reset_confirm'),
    path('password-reset-complete', auth_views.PasswordResetCompleteView.as_view(
        template_name='recipes/password_reset_complete.html',
    ), name='password_reset_complete'),

    path('history', views.history, name='history'),
    path('favorites', views.favorites, name='favorites'),
    path('favorites/toggle', views.toggle_favorite, name='toggle-favorite'),
]
