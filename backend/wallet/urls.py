from django.urls import path
from wallet import views

urlpatterns = [
    path("wallet/transactions/", views.WalletTransactionsView.as_view(), name="wallet-transactions"),
    path("wallet/refund/", views.WalletRefundView.as_view(), name="wallet-refund"),
]
