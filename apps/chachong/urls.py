from chachong import views
from django.urls import path


urlpatterns = [
    path('', views.CC),
    path('detail/',views.detail),
    path('export/',views.export),
    path('confirm/',views.chachong_confirm)

]