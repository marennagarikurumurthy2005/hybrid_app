from django.urls import path
from captains import views

urlpatterns = [
    path("captains/online/", views.CaptainOnlineView.as_view(), name="captain-online"),
    path("captains/location/", views.CaptainLocationView.as_view(), name="captain-location"),
    path("captains/accept-job/", views.CaptainAcceptJobView.as_view(), name="captain-accept"),
    path("captains/complete-job/", views.CaptainCompleteJobView.as_view(), name="captain-complete"),
    path("captain/online/", views.CaptainOnlineView.as_view(), name="captain-online-singular"),
    path("captain/location/", views.CaptainLocationView.as_view(), name="captain-location-singular"),
    path("captain/location/update", views.CaptainLocationView.as_view(), name="captain-location-update"),
    path("jobs/create/", views.JobCreateView.as_view(), name="jobs-create"),
    path("jobs/accept/", views.JobAcceptView.as_view(), name="jobs-accept"),
    path("jobs/reject/", views.JobRejectView.as_view(), name="jobs-reject"),
    path("jobs/complete/", views.JobCompleteView.as_view(), name="jobs-complete"),
]
