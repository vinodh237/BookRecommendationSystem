import csv
from book import models as book_model
from django.contrib.auth.models import User
import operator
import sqlite3
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from book import serializers as book_serializers
import math
from rest_framework import status
from rest_framework.response import Response


def response(data, code=status.HTTP_200_OK, error=""):
    """Overrides rest_framework response

        :param data: data to be send in response
        :param code: response status code(default has been set to 200)
        :param error: error message(if any, not compulsory)
    """
    res = {"error": error, "response": data}
    return Response(data=res, status=code)

def populate_book():
    with open(r'C:\Users\Vinodh\CS512\bookRecommend\book\filt_books') as f:
        reader = csv.reader(f, delimiter=',')
        header = next(reader)
        book_model.Book.objects.bulk_create([book_model.Book(isbn=row[0], book_title=row[1],book_author=row[2],year_of_publication=row[3],publisher = row[4],image_url_s=row[5],image_url_m=row[6],image_url_l=row[7]) for row in reader])


def populate_user():
    with open(r'C:\Users\Vinodh\CS512\bookRecommend\book\filt_users') as f:
        reader = csv.reader(f, delimiter=',')
        header = next(reader)
        book_model.User.objects.bulk_create([book_model.User(user_id=row[0], location=row[1]) for row in reader])

def populate_user_book():
    with open(r'C:\Users\Vinodh\CS512\bookRecommend\book\user_books') as f:
        reader = csv.reader(f, delimiter=',')
        header = next(reader)
        book_model.UserBookRating.objects.bulk_create([book_model.UserBookRating(isbn=row[0], book_title=row[1],book_author=row[2],user_id=row[3],book_rating=row[4],location=row[5]) for row in reader])

def create_users():
    users = book_model.User.objects.all()
    for user in users:
        user = User.objects.create_user(username=user.user_id,
                                        email=str(user.user_id)+'@book.com',
                                        password='book')

def cosine_similarity(popular_books_ratings_with_user_data_pivot,indexes,book_1,book_2):
    den1 = 0
    den2 = 0
    numerator = 0
    import math
    means = popular_books_ratings_with_user_data_pivot.loc['mean']
    sim = []
    index = []
    for index in indexes:
        user_mean = means.values[means.index.get_loc(index)]
        user_book_1_rating = book_1.values[book_1.index.get_loc(index)]
        user_book_2_rating = book_2.values[book_2.index.get_loc(index)]
        numerator+= (user_book_1_rating - user_mean)*(user_book_2_rating - user_mean)
        den1+=(user_book_1_rating - user_mean)**2
        den2+=(user_book_2_rating - user_mean)**2
    if den1 == 0 or den2 == 0:
        return 0
    return numerator/math.sqrt(den1*den2)


def get_similar_books_book(popular_books_ratings_with_user_data_pivot,book_name_input):
    """

    :return:
    """
    # book_name_input = input('Input the Book Name for Recommendation System')
    # Pride and Prejudice
    index_book_similar = popular_books_ratings_with_user_data_pivot.index.get_loc(book_name_input)
    book_1 = popular_books_ratings_with_user_data_pivot.iloc[index_book_similar]
    book_1 = book_1[book_1 != 0]
    dict = {}
    for i in range(0, popular_books_ratings_with_user_data_pivot.index.size):
        if i != index_book_similar:
            book_2 = popular_books_ratings_with_user_data_pivot.iloc[i]
            book_2 = book_2[book_2 != 0]
            indexes = book_1.index.intersection(book_2.index)
            dict[popular_books_ratings_with_user_data_pivot.index[i]] = cosine_similarity(popular_books_ratings_with_user_data_pivot,indexes, book_1, book_2)
    sorted_d = sorted(dict.items(), key=operator.itemgetter(1), reverse=True)
    return sorted_d[:100]

def get_user_book_rating():
    """

    :return:
    """
    popular_books_ratings = pd.DataFrame(list(book_model.UserBookRating.objects.all().values('book_title','book_author','isbn','user_id','book_rating','location')))
    popular_books_ratings_with_user_data = popular_books_ratings
    popular_books_ratings_with_user_data = popular_books_ratings_with_user_data.drop_duplicates(
        subset=['user_id', 'book_title'], keep="last")
    popular_books_ratings_with_user_data_pivot = popular_books_ratings_with_user_data.pivot(index='book_title',
                                                                                            columns='user_id',
                                                                                            values='book_rating').fillna(
        0)
    popular_books_ratings_with_user_data_sparse = csr_matrix(popular_books_ratings_with_user_data_pivot.values)
    popular_books_ratings_with_user_data_pivot = popular_books_ratings_with_user_data_pivot.replace(0, np.NaN)
    popular_books_ratings_with_user_data_pivot.loc['mean'] = popular_books_ratings_with_user_data_pivot.replace(0,
                                                                                                                np.NaN).mean()
    popular_books_ratings_with_user_data_pivot = popular_books_ratings_with_user_data_pivot.replace(np.NaN, 0)

    # print(popular_books_ratings_with_user_data_pivot)
    return popular_books_ratings_with_user_data_pivot


def get_recommendations_to_book(book_name):
    """

    :return:
    """
    books_pivot = get_user_book_rating()
    recommendation_list = get_similar_books_book(books_pivot,book_name)
    serialized_recommendation_list = []
    # import pdb;pdb.set_trace()
    for recommendation in recommendation_list:
        book = book_model.Book.objects.filter(is_deleted=False,book_title=recommendation[0]).first()
        if book:
            serialized_data = book_serializers.BookSerializer(book).data
            serialized_recommendation_list.append(serialized_data)
    return serialized_recommendation_list


def pearson_similarity(indexes,user_1,user_2,user_1_mean,user_2_mean):
    den1 = 0
    den2 = 0
    numerator = 0
    sim = []
    index = []
    for index in indexes:
        user_book_1_rating = user_1.get(index)
        user_book_2_rating = user_2.get(index)
        numerator+= (user_book_1_rating - user_1_mean)*(user_book_2_rating - user_2_mean)
        den1+=(user_book_1_rating - user_1_mean)**2
        den2+=(user_book_2_rating - user_2_mean)**2
    if den1 == 0 or den2 == 0:
        return 0
    return numerator/math.sqrt(den1*den2)


def get_user_data():
    """

    :return:
    """

    popular_books_ratings = pd.DataFrame(list(
        book_model.UserBookRating.objects.all().values('book_title', 'book_author', 'isbn', 'user_id', 'book_rating',
                                                       'location')))
    popular_books_ratings_with_user_data = popular_books_ratings
    popular_books_ratings_with_user_data = popular_books_ratings_with_user_data.drop_duplicates(
        subset=['user_id', 'book_title'], keep="last")

    popular_books_ratings_with_user_data_pivot_users = popular_books_ratings_with_user_data.pivot(index='user_id',
                                                                                                  columns='book_title',
                                                                                                  values='book_rating').fillna(
        0)
    popular_books_ratings_with_user_data_pivot_users = popular_books_ratings_with_user_data_pivot_users.replace(0,
                                                                                                                np.NaN)
    popular_books_ratings_with_user_data_pivot_users['mean'] = popular_books_ratings_with_user_data_pivot_users.replace(
        0, np.NaN).mean(axis=1)
    popular_books_ratings_with_user_data_pivot_users = popular_books_ratings_with_user_data_pivot_users.replace(np.NaN,
                                                                                                                0)

    popular_books_ratings_with_user_data_pivot_users_new = popular_books_ratings_with_user_data_pivot_users

    popular_books_ratings_with_user_data_pivot_users = popular_books_ratings_with_user_data_pivot_users.drop(['mean'],
                                                                                                             axis=1)

    means = popular_books_ratings_with_user_data_pivot_users_new['mean']

    return (popular_books_ratings_with_user_data_pivot_users,means)


def get_similar_users_to_user(user_id,means,popular_books_ratings_with_user_data_pivot_users):
    """

    :param user_id:
    :return:
    """

    user_index_to_query = int(user_id)
    index_user_similar = popular_books_ratings_with_user_data_pivot_users.index.get_loc(user_index_to_query)
    user_1 = popular_books_ratings_with_user_data_pivot_users.iloc[index_user_similar]
    user_1 = user_1[user_1 != 0]
    user_1_mean = means.values[means.index.get_loc(user_index_to_query)]

    dict = {}
    for i in range(0, popular_books_ratings_with_user_data_pivot_users.index.size):
        if i != index_user_similar:
            user_2 = popular_books_ratings_with_user_data_pivot_users.iloc[i]
            user_2 = user_2[user_2 != 0]
            user_2_mean = means.values[means.index.get_loc(popular_books_ratings_with_user_data_pivot_users.index[i])]
            indexes = user_1.index.intersection(user_2.index)
            dict[popular_books_ratings_with_user_data_pivot_users.index[i]] = pearson_similarity(indexes, user_1,
                                                                                                 user_2, user_1_mean,
                                                                                                 user_2_mean)
    sorted_d = sorted(dict.items(), key=operator.itemgetter(1), reverse=True)
    # sorted_d
    return (sorted_d,user_1_mean)


def predict_rating(sorted_list,book_name,means,popular_books_ratings_with_user_data_pivot_users,user_1_mean):
    total_sim=0
    numerator = 0
    k = 0
    for i in sorted_list:
        user_index = popular_books_ratings_with_user_data_pivot_users.index.get_loc(i[0])
        rating = popular_books_ratings_with_user_data_pivot_users.iloc[user_index].get(book_name)
        mean_rating = means.values[means.index.get_loc(i[0])]
        if rating !=0:
            numerator += i[1]*(rating-mean_rating)
            total_sim+=i[1]
            k+=1
        if k>=10:
            break
    if total_sim==0:
#         print("reee")
        return user_1_mean
    else:
        predict_rating = user_1_mean + (numerator/total_sim)
        if predict_rating > 10:
            predict_rating = 10
        elif predict_rating < 1:
            predict_rating = 1
        return predict_rating



def get_recommendations_for_user(user_id):
    """

    :return:
    """
    popular_books_ratings_with_user_data_pivot = get_user_book_rating()
    user_data = get_user_data()
    popular_books_ratings_with_user_data_pivot_users = user_data[0]
    means = user_data[1]
    similar_users = get_similar_users_to_user(user_id,means,popular_books_ratings_with_user_data_pivot_users)
    sorted_d = similar_users[0]
    user_1_mean = similar_users[1]
    book_titles = list(popular_books_ratings_with_user_data_pivot.index.values)
    recommended_books = {}
    k = 0
    for book in book_titles:
        current_user_index = popular_books_ratings_with_user_data_pivot_users.index.get_loc(user_id)
        current_user_rating = popular_books_ratings_with_user_data_pivot_users.iloc[current_user_index].get(book)
        if current_user_rating == 0:
            predict_rat = predict_rating(sorted_d, book, means, popular_books_ratings_with_user_data_pivot_users,user_1_mean)
            recommended_books[book] = predict_rat
            k += 1
        if k >= 40:
            break
    recommended_books_sorted = sorted(recommended_books.items(), key=operator.itemgetter(1), reverse=True)

    serialized_recommendation_list = []
    # import pdb;
    # pdb.set_trace()
    for recommendation in recommended_books_sorted:
        book = book_model.Book.objects.filter(is_deleted=False, book_title=recommendation[0]).first()
        if book:
            serialized_data = book_serializers.BookSerializer(book).data
            serialized_recommendation_list.append(serialized_data)
    return serialized_recommendation_list