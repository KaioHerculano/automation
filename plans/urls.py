from django.urls import path
from . import views

urlpatterns = [
    path('upgrade/', views.UpgradePageView.as_view(), name='upgrade_page'),
    path('terms/', views.TermsView.as_view(), name='terms'),
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
]