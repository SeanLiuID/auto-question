# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib import admin
from rest_framework.schemas import get_schema_view
from xg.views import ReturnJson

urlpatterns = [
    url(r'^docs/', get_schema_view()),
    url(r'^answers', ReturnJson.as_view()),
]
