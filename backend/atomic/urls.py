# atomic/urls.py

from django.urls import path
from .views import start_full_workflow

urlpatterns = [
    path("get_asin_list/", start_full_workflow, name="get_asin_list"),
]