from django.urls import path
from payouts import views

urlpatterns = [
    path("captain/earnings", views.CaptainEarningsView.as_view(), name="captain-earnings"),
    path("captain/payout/request", views.CaptainPayoutRequestView.as_view(), name="captain-payout-request"),
    path("captain/payout/history", views.CaptainPayoutHistoryView.as_view(), name="captain-payout-history"),
    path("captain/bank/link", views.CaptainBankLinkView.as_view(), name="captain-bank-link"),
]
