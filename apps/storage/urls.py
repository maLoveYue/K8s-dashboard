from django.urls import path, re_path, include
from apps.storage import views

urlpatterns = [

    re_path('^pvc/$', views.pvc, name='pvc'),
    re_path('^pvc_api/$', views.pvc_api, name='pvc_api'),
    re_path('^cm/$', views.cm, name='cm'),
    re_path('^cm_api/$', views.cm_api, name='cm_api'),
    re_path('^secret/$', views.secret, name='secret'),
    re_path('^secret_api/$', views.secret_api, name='secret_api'),



]