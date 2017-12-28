from django.db import models

# Create your models here.

class ModelBase(models.Model):
    """
        This is a abstract model class to add is_deleted, created_at and modified at fields in any model
    """
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        """ Soft delete """
        self.is_deleted = True
        self.save()


class User(ModelBase):
    """
    It is for Use Model
    """
    user_id = models.IntegerField()
    location = models.CharField(max_length=254, null=True, blank=True)


class Book(ModelBase):
    """
    It is for Use Model
    """
    isbn = models.CharField(max_length=254, null=True, blank=True)
    book_title = models.CharField(max_length=254, null=True, blank=True)
    book_author = models.CharField(max_length=254, null=True, blank=True)
    publisher = models.CharField(max_length=254, null=True, blank=True)
    year_of_publication = models.CharField(max_length=254, null=True, blank=True)
    image_url_s = models.CharField(max_length=254, null=True, blank=True)
    image_url_m = models.CharField(max_length=254, null=True, blank=True)
    image_url_l = models.CharField(max_length=254, null=True, blank=True)

class UserBookRating(ModelBase):
    """
    User Book Rating
    """
    isbn = models.CharField(max_length=254, null=True, blank=True)
    user_id = models.IntegerField()
    book_title = models.CharField(max_length=254, null=True, blank=True)
    book_author = models.CharField(max_length=254, null=True, blank=True)
    book_rating = models.IntegerField(default=0)
    location = models.CharField(max_length=254, null=True, blank=True)