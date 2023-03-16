from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('tags', views.TagsViewSet)
router.register('ingredients', views.IngredientsViewSet, basename='ingredient')
router.register('recipes', views.RecipesViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
