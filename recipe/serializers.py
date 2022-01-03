from rest_framework import serializers
from main_app.models import Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag model objects"""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


