"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('users.urls')),
    path('api/v1/', include('wallet.urls')),
    path('api/v1/', include('restaurants.urls')),
    path('api/v1/', include('recommendations.urls')),
    path('api/v1/', include('orders.urls')),
    path('api/v1/', include('rides.urls')),
    path('api/v1/', include('captains.urls')),
    path('api/v1/', include('payments.urls')),
    path('api/v1/', include('notifications.urls')),
    path('api/v1/', include('pricing.urls')),
    path('api/v1/', include('ratings.urls')),
    path('api/v1/', include('fraud.urls')),
    path('api/v1/', include('adminpanel.urls')),
    path('api/v1/', include('routing.urls')),
    path('api/v1/', include('analytics.urls')),
    path('api/v1/', include('maps.urls')),
    path('api/v1/', include('cancellation.urls')),
    path('api/v1/', include('chat.urls')),
    path('api/v1/', include('promotions.urls')),
    path('api/v1/', include('payouts.urls')),
    path('api/v1/', include('restaurant_ops.urls')),
    path('api/v1/', include('trust.urls')),
    path('api/v1/', include('eta.urls')),
    path('api/v1/', include('growth.urls')),
    path('api/v1/', include('vehicles.urls')),
    path('api/v1/', include('support.urls')),
    path('api/v1/', include('observability.urls')),
    path('api/', include('maps.urls')),
    path('api/', include('captains.urls')),
]
