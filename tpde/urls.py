from django.urls import path

from tpde.views import ImageView, ImagePreviewView

urlpatterns = [
    # path('images/', ImageView.as_view(), name='image-upload'),
    path('gallery/<int:id>/', ImageView.as_view(), name='image-view'),
    path('gallery/preview/', ImagePreviewView.as_view(), name='image-save'),
]