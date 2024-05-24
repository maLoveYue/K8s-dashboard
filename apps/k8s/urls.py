from django.urls import path, re_path, include
from apps.k8s import views

urlpatterns = [

    re_path('^namespace-api/$', views.namespace_api, name='namespace-api'),
    re_path('^namespace/$', views.namespace, name='namespace'),
    re_path('^node/$', views.node, name='node'),
    re_path('^node-api/$', views.node_api, name='node-api'),
    re_path('^pv/$', views.pv, name='pv'),
    re_path('^pv_api/$', views.pv_api, name='pv_api'),
    re_path('^pv_create/$', views.pv_create, name='pv_create'),
]