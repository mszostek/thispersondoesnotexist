import hashlib
import requests as re
from django.core.files.base import ContentFile
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from thispersondoesnotexist_catalogue.settings import THISPERSONDOESNTEXISTS_URL
from tpde.models import Image
from tpde.serializers import ImageSerializer


class ImageView(APIView):
    # permission_classes = [IsAuthenticated]
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

    def get(self, request, *args, **kwargs):
        try:
            queryset = Image.objects.get(id=self.kwargs['id'])
            serializer = ImageSerializer(queryset, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Image.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class ImagePreviewView(generics.RetrieveAPIView):
    # permission_classes = [IsAuthenticated]
    serializer_class = ImageSerializer

    def get(self, request, *args, **kwargs):
        picture = self.get_image()
        if isinstance(picture, Response):
            return picture
        data = {'title': picture.name, 'image': picture}

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        new_image = serializer.save()

        queryset = Image.objects.get(id=new_image.id)
        saved = ImageSerializer(queryset, many=False)
        return Response(saved.data, status=status.HTTP_201_CREATED)

    def get_image(self):
        url = THISPERSONDOESNTEXISTS_URL
        try:
            response = re.get(url, stream=True)
            if response.status_code != 200:
                return Response({"detail": f"Error image download: status {response.status_code}"}, status=status.HTTP_400_BAD_REQUEST)

            content_hash = hashlib.md5(response.content).hexdigest()
            image_file = ContentFile(response.content, name=f"{content_hash}.jpg")
            return image_file
        except re.RequestException as e:
                return Response({"detail": f"Error image save: status {e}"}, status=status.HTTP_400_BAD_REQUEST)

