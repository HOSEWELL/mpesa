from django.urls import path
from .views import lipa_na_mpesa

urlpatterns = [
    path('lipa/', lipa_na_mpesa),
]
