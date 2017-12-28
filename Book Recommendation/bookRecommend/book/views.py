from django.shortcuts import render

import json
from django.shortcuts import render
from django.views.generic import View
from django.db import transaction
from django.http import HttpResponse, HttpResponseNotFound
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django import forms
from django.db.models import Prefetch, Q, Max
import uuid
import copy
import datetime

from requests import Response
from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.exceptions import APIException
from django.contrib.auth import authenticate, login
from book import models as book_model
from book import serializers as book_serializers
from book import utils as book_utils
from rest_framework.views import APIView

# Create your views here.


class Login(View):
    """
    """
    template_name = "login.html"

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            # import pdb;pdb.set_trace()
            login(request, user)
            if user.is_staff:
                return render(request, 'admin/books.html', {"access_token": settings.TEMP_TOKEN})
            else:
                return render(request, 'admin/books.html', {"access_token": settings.TEMP_TOKEN})
        else:
            message = 'Email/Password is incorrect.'
            return render(request, self.template_name, {'message': message})

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name,context={'BASE_URL': request.get_host()})


class Books(View):
    template_name = "admin/books.html"

    def get(self, request, *args, **kwargs):
        book_objects = book_model.Book.objects.filter(is_deleted=False)
        book_serializer_data = book_serializers.BookSerializer(book_objects, many=True).data
        return render(request, self.template_name, context={"book_objects": book_serializer_data})


class SearchBook(APIView):
    template_name = "admin/book_details.html"
    def get(self, request, *args, **kwargs):
        # import pdb;pdb.set_trace()
        book_title = request.GET.get('book_title')
        user_id = int(request.user.username)
        # user_id = request.GET.get('user_id',None)
        book_object = book_model.Book.objects.filter(is_deleted=False, book_title=book_title).first()
        current_book_information = book_serializers.BookSerializer(book_object).data
        recommended_books = book_utils.get_recommendations_to_book(current_book_information['book_title'])
        current_book_information['book_rating'] = 0
        if user_id:
            user_book_recommend = book_model.UserBookRating.objects.filter(book_title=book_title,
                                                                           user_id=int(user_id)).first()
            if user_book_recommend:
                current_book_information['book_rating'] = user_book_recommend.book_rating
        # return book_utils.response(
        #     {'current_book': current_book_information, 'recommended_books': recommended_books})
        return render(request, self.template_name, context={'current_book': current_book_information, 'recommended_books': recommended_books})

class UserRecommend(APIView):
    template_name = "admin/books.html"

    def get(self, request, *args, **kwargs):
        # import pdb;pdb.set_trace()
        user_id = int(request.user.username)
        # user_id = int(request.GET['user_id'])
        user_object = book_model.User.objects.filter(is_deleted=False,user_id = user_id).first()
        recommended_books = book_utils.get_recommendations_for_user(user_id)
        # import pdb;pdb.set_trace()
        # return book_utils.response({'recommended_books':recommended_books})
        return render(request, self.template_name, context={"book_objects": recommended_books})

class UpdateRating(APIView):

    def post(self, request):
        # import pdb;pdb.set_trace()

        # user_id = int(request.POST.get('user_id'))
        user_id = int(request.user.username)
        book_title = request.POST.get('book_title')
        rating = request.POST.get('book_rating')
        user_object = book_model.User.objects.filter(is_deleted=False, user_id=user_id).first()
        book_object = book_model.Book.objects.filter(is_deleted=False, book_title=book_title).first()
        user_information = book_serializers.UserSerializer(user_object).data
        current_book_information = book_serializers.BookSerializer(book_object).data
        params = {
            'user_id':user_id,
            'book_title':current_book_information['book_title'],
            'book_rating':rating,
            'isbn':current_book_information['isbn'],
            'book_author':current_book_information['book_author'],
            'location': user_information['location']
        }
        user_book_recommend = book_model.UserBookRating.objects.filter(book_title=book_title,
                                                                       user_id=int(user_id)).first()
        if user_book_recommend:
            rating_serializer = book_serializers.UserBookRatingSerializer(user_book_recommend,data=params,partial=True)
        else:
            rating_serializer = book_serializers.UserBookRatingSerializer(data=params)
        if rating_serializer.is_valid():
            rating_serializer.save()
        return book_utils.response({'message':'added successfully'})



class Logout(View):
    def post(self, request):
        """
        This API logs the user out.
        """
        user = getattr(request, 'user', None)
        request.session.flush()
        if hasattr(request, 'user'):
            from django.contrib.auth.models import AnonymousUser
            request.user = AnonymousUser()
        return render(request, 'login.html')