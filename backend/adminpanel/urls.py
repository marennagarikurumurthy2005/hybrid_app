from django.urls import path
from adminpanel import views

urlpatterns = [
    path("admin/overview/", views.AdminOverviewView.as_view(), name="admin-overview"),
    path("admin/users/", views.AdminUsersView.as_view(), name="admin-users"),
    path("admin/captains/", views.AdminCaptainsView.as_view(), name="admin-captains"),
    path("admin/captain/<str:captain_id>/verify/", views.AdminCaptainVerifyView.as_view(), name="admin-captain-verify"),
]
