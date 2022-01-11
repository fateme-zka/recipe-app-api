from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TagViewSet, IngredientViewSet

# Default router is a feature of DRF that will automatically generate urls for our ViewSet.
# so when you have ViewSet you may have multiple urls associated with that One ViewSet.
router = DefaultRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls))
]
