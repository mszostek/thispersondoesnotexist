from rest_framework import serializers

from tpde.models import Image


class ImageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    thumb = serializers.ImageField(read_only=True)

    @staticmethod
    def validate_image(value):
        if not value.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            raise serializers.ValidationError("Required PNG, JPG, JPEG or GIF file.")
        return value

    class Meta:
        model = Image
        # fields = ['id', 'title', 'image', 'thumb',  'uploaded_at']
        fields = '__all__'