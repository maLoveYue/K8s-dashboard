from django.urls import path, re_path, include
from apps.k8s import views

urlpatterns = [

    re_path('^test/$', views.test, name='test')

]