from django.urls import path
from . import views

urlpatterns = [
    path('automations/', views.AutomationListView.as_view(), name='automation_list'),
    path('automations/new/', views.AutomationCreateView.as_view(), name='automation_create'),
    path('automations/<int:pk>/edit/', views.AutomationUpdateView.as_view(), name='automation_update'),
    path('automations/<int:pk>/delete/', views.AutomationDeleteView.as_view(), name='automation_delete'),
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('upgrade/', views.UpgradePageView.as_view(), name='upgrade_page'),
    path('terms/', views.TermsView.as_view(), name='terms'),
    path('privacy', views.PrivacyView.as_view(), name='privacy'),
    path('', views.DashboardView.as_view(), name='dashboard'),
]