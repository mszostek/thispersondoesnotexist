import hashlib
import os
import requests as re
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from django.core.files.base import ContentFile
from rest_framework.response import Response
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from thispersondoesnotexist_catalogue.settings import BASE_DIR
from tpde.models import Image
from tpde.serializers import ImageSerializer


class ImageViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.fake_img = fake_img()
        self.image = Image.objects.create(
            title="Test Image",
            image=ContentFile(self.fake_img.read(), name="test_image.jpg")
        )
        self.url = reverse('image-view', kwargs={'id': self.image.id})

    def test_get_existing_image(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = ImageSerializer(self.image)
        self.assertEqual(response.data, serializer.data)

    def test_get_nonexistent_image(self):
        url = reverse('image-view', kwargs={'id': 2137})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def tearDown(self):
        for image in Image.objects.all():
            if image.image and os.path.exists(image.image.path):
                os.remove(image.image.path)
            if image.thumb and os.path.exists(image.thumb.path):
                os.remove(image.thumb.path)

class ImagePreviewViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('image-save')
        self.fake_image_content = fake_img()
        self.fake_image_name = f"{hashlib.md5(self.fake_image_content.read()).hexdigest()}.jpg"

    @patch('tpde.views.re.get')
    def test_get_new_image_success(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.content = self.fake_image_content.read()

        response = self.client.get(self.url)
        # TODO
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # image = Image.objects.all().first()

    @patch('tpde.views.re.get')
    def test_get_image_download_failure(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.status_code = 500

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"detail": "Error image download: status 500"})

    @patch('tpde.views.re.get')
    def test_get_image_request_exception(self, mock_get):
        mock_get.side_effect = re.RequestException("Connection error")

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"detail": "Error image save: status Connection error"})

    def test_get_image_serialization_failure(self):
        with patch('tpde.views.ImagePreviewView.get_image') as mock_get_image:
            mock_get_image.return_value = Response(
                {"detail": "Error image download: status 400"},
                status=status.HTTP_400_BAD_REQUEST
            )
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data, {"detail": "Error image download: status 400"})

    def tearDown(self):
        for image in Image.objects.all():
            if image.image and os.path.exists(image.image.path):
                os.remove(image.image.path)
            if image.thumb and os.path.exists(image.thumb.path):
                os.remove(image.thumb.path)

def fake_img():
    from io import BytesIO
    from PIL import Image as Img

    image = Img.new('RGB', size=(250, 250), color=(0, 0, 0))
    file = BytesIO(image.tobytes())
    image.save(file, 'jpeg')
    file.seek(0)
    return file