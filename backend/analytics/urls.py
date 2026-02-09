from django.urls import path
from analytics import views

urlpatterns = [
    path("wallet/analytics/<str:user_id>/", views.WalletAnalyticsView.as_view(), name="wallet-analytics"),
]
