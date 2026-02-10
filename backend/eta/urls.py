from django.urls import path
from eta import views

urlpatterns = [
    path("eta/predict", views.EtaPredictView.as_view(), name="eta-predict"),
]
