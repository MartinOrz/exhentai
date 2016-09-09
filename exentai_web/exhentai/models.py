from django.db import models


class ExGallery(models.Model):
    """
    用于存储的画集实体类
    """
    id = models.IntegerField(primary_key=True)
    root_path = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    name_n = models.CharField(max_length=255)
    name_j = models.CharField(max_length=255)
    type = models.IntegerField()
    language = models.IntegerField()
    translator = models.CharField(max_length=255)
    pages = models.IntegerField()
    length = models.IntegerField()
    posted = models.DateTimeField()
    is_anthology = models.IntegerField()
    rating = models.IntegerField()
    status = models.IntegerField()
    last_view = models.DateTimeField()

