# from django.conf.urls import url
from home.views import HomeView
from django.urls import path, re_path

urlpatterns = [
    re_path(r'^$', HomeView.as_view(template_name="home/main.html")),
]
