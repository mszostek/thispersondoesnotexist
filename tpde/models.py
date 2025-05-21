from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

class Image(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/tpde/')
    thumb =  ImageSpecField(source='image',
                            processors=[ResizeToFill(200, 200)],
                            format='JPEG')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        app_label = 'tpde'