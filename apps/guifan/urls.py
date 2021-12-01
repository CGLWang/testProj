from django.urls import path
from . import views

urlpatterns = [
    path('',views.FinishFillNormalPro),
    path('confirm/',views.guifan_confirm),
    path('export/',views.guifan_exprot),
    path('nextstep/',views.luru_confirm),
    path('finalstep/',views.final)
]