from rest_framework.viewsets import ModelViewSet
from .models import Article, Category
from .serializers import ArticleSerializer, CategorySerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer



class ArticleViewSet(ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    filterset_fields = ['category']
    search_fields = ['title', 'content']
