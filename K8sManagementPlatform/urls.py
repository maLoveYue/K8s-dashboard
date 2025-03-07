"""K8sManagementPlatform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
import sys

from django.contrib import admin
from django.urls import path, re_path, include
from dashboard import views


urlpatterns = [
    path('admin/', admin.site.urls),
    re_path('^$', views.index, name='index'),
    re_path('^login/$', views.login, name='login'),
    re_path('^logout/$', views.logout, name='logout'),
    re_path('^ace_editor/$', views.ace_editor, name='ace_editor'),
    re_path('^export_resource_api/$', views.export_resource_api, name='export_resource_api'),
    path('k8s/', include('k8s.urls')),
    path('workload/', include('workload.urls')),
    path('loadbalancer/', include('loadbalancer.urls')),
    path('storage/', include('storage.urls'))
]
