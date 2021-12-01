from django.urls import path
from guanlian import views

urlpatterns = [
    path('', views.FinishFillStatistics),
    path('detail/',views.FinishFillShow)
]