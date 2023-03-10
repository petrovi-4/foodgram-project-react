from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()

router.register('ingredients', views.IngredientViewSet, basename='ingredients')
router.register('recipes', views.RecipeViewSet)
router.register('tags', views.TagViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
