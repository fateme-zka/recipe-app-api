from rest_framework.decorators import action  # to add custom action to your viewset
from rest_framework.response import Response  # for returning a custom response
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from main_app.models import Tag, Ingredient, Recipe
from .serializers import *


class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin):
    """Base viewset for user owned recipe attributes"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Create a new objects of model"""
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipes in the database"""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    # get_queryset is a default action of django view
    def get_queryset(self):
        """Retrieve the recipe for the authenticated user"""
        return self.queryset.filter(user=self.request.user)

    # get_serializer_class is a default action of django view
    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':  # action is being used for our current request action
            return RecipeDetailSerializer
        elif self.action == 'upload_image':
            return RecipeImageSerializer

        return self.serializer_class

    # perform_create is a default action of django view
    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)

    # to create our custom action in view
    @action(methods=['POST'], detail=True, url_path='upload-image')  # the url name
    # this action only accept post method request,
    # and you're only going to be able to upload image for "a created recipe" because of detail=True
    def upload_image(self, request, pk=None):  # pk that is passed in with the url: site/recipe/3/upload-image/
        """Upload an image to a recipe"""
        recipe = self.get_object()  # get the object accessed based on the id/pk (in url detail)

        # then we'll get the serializer of view (by get_serializer()) and passing data in it
        serializer = self.get_serializer(
            recipe,
            data=request.data
        )
        if serializer.is_valid():
            # because it's a Model serializer you can use .save() to save it
            serializer.save()
            return Response(
                data=serializer.data,  # it would be id and image filed
                status=status.HTTP_200_OK
            )
        return Response(  # if serializer was not valid
            data=serializer.errors,  # it creates all the fields have error
            status=status.HTTP_400_BAD_REQUEST
        )
