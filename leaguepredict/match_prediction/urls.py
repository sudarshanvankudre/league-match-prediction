from django.urls import path
from . import views

app_name = 'match_prediction'
urlpatterns = [
    path('', views.index, name='index'),
    path('display/<slug:sname>', views.display_sname, name="display_name"),
]