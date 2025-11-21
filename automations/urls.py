from django.urls import path
from . import views

urlpatterns = [
    path('automations/', views.AutomationListView.as_view(), name='automation_list'),
    path('automations/new/', views.AutomationCreateView.as_view(), name='automation_create'),
    path('automations/<int:pk>/edit/', views.AutomationUpdateView.as_view(), name='automation_update'),
    path('automations/<int:pk>/delete/', views.AutomationDeleteView.as_view(), name='automation_delete'),
]