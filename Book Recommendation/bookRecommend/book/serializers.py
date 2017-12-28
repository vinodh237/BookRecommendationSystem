from rest_framework import serializers
from book import models as book_models


class UserSerializer(serializers.ModelSerializer):
    """
    User Serializer
    """

    class Meta:
        model = book_models.User


class BookSerializer(serializers.ModelSerializer):
    """
    Book Serializer
    """

    class Meta:
        model = book_models.Book

class UserBookRatingSerializer(serializers.ModelSerializer):
    """
    Book Serializer
    """

    class Meta:
        model = book_models.UserBookRating