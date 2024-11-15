from rest_framework.routers import DefaultRouter
from articles.views import ArticleViewSet, CategoryViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='categories')
router.register('articles', ArticleViewSet, basename='articles')

urlpatterns = router.urls
