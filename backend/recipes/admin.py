from django.contrib import admin
from django.db.models import Count

from .models import (
    FavoriteList,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingList,
    Tag,
)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'author',
        'name',
    )
    list_filter = ('author', 'name', 'tags')
    inlines = (RecipeIngredientInline,)
    readonly_fields = ('quantity_in_favorites',)

    def quantity_in_favorites(self, obj):
        """Возвращаем общее число добавлений рецепта в избранное."""
        return obj.in_favorites

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(in_favorites=Count('favorites'))


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)


class FavoriteListAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')


class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(FavoriteList, FavoriteListAdmin)
admin.site.register(ShoppingList, ShoppingListAdmin)
