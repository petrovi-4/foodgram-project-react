from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('', views.UserViewSet)

urlpatterns = [
    path('token/login/', views.GetTokenView.as_view()),
    path('token/logout/', views.delete_toke_view),
    path('set_password/', views.SetPasswordView.as_view()),
    path('', include(router.urls)),
]
