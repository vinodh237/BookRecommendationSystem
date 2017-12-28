
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix


# In[2]:


# Reading Users Data File as Pandas Dataframe
users = pd.read_csv(r'C:\Users\Vinodh\Downloads\Book\BX-Users.csv', sep=';', encoding="latin-1",error_bad_lines=False)
users.columns = ['user_id', 'location', 'age']
len(users)


# In[3]:


# Reading User Book Rating file as Pandas Data Frame
user_book_ratings = pd.read_csv(r'C:\Users\Vinodh\Downloads\Book\BX-Book-Ratings.csv', sep=';', error_bad_lines=False, encoding="latin-1")
user_book_ratings.columns = ['user_id', 'isbn', 'book_rating']
user_book_ratings.head(5)
len(user_book_ratings)


# In[4]:


# Reading books data file as Pandas Dataframe
books = pd.read_csv(r'C:\Users\Vinodh\Downloads\Book\BX-Books.csv', sep=';', encoding="latin-1", error_bad_lines=False)
books.columns = ['isbn', 'book_title', 'book_author', 'year_of_publication', 'publisher', 'image_url_s', 'image_url_m', 'image_url_l']
len(books)
books.head()


# In[5]:


unnecessary_book_columns = ['image_url_s', 'image_url_m', 'image_url_l', 'year_of_publication', 'publisher']
unnecessary_user_columns = ['age']
books = books.drop(unnecessary_book_columns, axis=1)
users = users.drop(unnecessary_user_columns, axis=1)
users.head()


# In[6]:


books.head(5)


# In[7]:


# filter out all the books that don't have titles
print(len(books))
books_with_title = books.dropna(axis = 0, subset = ['book_title'])
len(books_with_title)


# In[8]:


# Joining books with user book ratings for title based on isbn
merge_ratings_books_data = pd.merge(books_with_title, user_book_ratings, on='isbn')
merge_ratings_books_data.head()


# In[9]:


# Total number of ratings for each book # We can do that counting
# merge_ratings_books_data = merge_ratings_books_data['book_rating' != 0]
merge_ratings_books_data = merge_ratings_books_data.loc[merge_ratings_books_data['book_rating'] != 0]
merge_ratings_books_data
merge_ratings_books_data = merge_ratings_books_data.merge(users, right_on = 'user_id', left_on = 'user_id', how = 'left')
merge_ratings_books_data = merge_ratings_books_data.loc[merge_ratings_books_data['location'].str.contains("usa|canada")]
merge_ratings_books_data.head()


# In[10]:


book_rating_count = merge_ratings_books_data.groupby(by = ['book_title'])['book_rating'].count().reset_index().rename(columns = {'book_rating': 'total_book_rating_count'})
book_rating_count.head()


# In[11]:



user_book_rating_count = merge_ratings_books_data.groupby(by = ['user_id'])['book_rating'].count().reset_index().rename(columns = {'book_rating': 'total_user_rating_count'})

user_book_rating_count


# In[12]:


# Joining User Ratings with the total rating
ratings_book_total_count = merge_ratings_books_data.merge(book_rating_count, right_on = 'book_title', left_on = 'book_title', how = 'left')

ratings_book_total_count = ratings_book_total_count.merge(user_book_rating_count, right_on = 'user_id', left_on = 'user_id', how = 'left')

ratings_book_total_count.head()


# In[13]:


print(ratings_book_total_count['total_book_rating_count'].describe())


# In[14]:


print(ratings_book_total_count['total_book_rating_count'].quantile(np.arange(.9, 1, .01)))


# In[15]:


# len(ratings_book_total_count['book_title'].value_counts())


# In[24]:


total_book_rating_count_threshold = 50
total_user_rating_count_threshold = 30
popular_books_ratings = ratings_book_total_count.query('total_book_rating_count >= @total_book_rating_count_threshold and total_user_rating_count >= @total_user_rating_count_threshold ')
popular_books_ratings


# In[44]:


plist_user_ids = popular_books_ratings['user_id'].tolist()
plist_user_ids
plist_books = popular_books_ratings['book_title'].unique()
filt_books = books.loc[books['book_title'].isin(plist_books)]
filt_books_final = filt_books[filt_books.groupby(by = ['book_title'])['isbn'].transform(max)==filt_books['isbn']].reset_index()
len(books)
len(filt_books)
filt_users = users.loc[users['user_id'].isin(plist_user_ids)]
filt_users


# In[25]:


len(popular_books_ratings)


# In[26]:


popular_books_ratings_with_user_data = popular_books_ratings
len(popular_books_ratings['book_title'].value_counts())


# In[299]:


len(popular_books_ratings['user_id'].value_counts())


# In[185]:


# Joining popular books with the user data to filter on location
# Only USA users are considered because number of users would be more and to be compuationally efficienct
# popular_books_ratings_with_user_data = popular_books_ratings.merge(users, right_on = 'user_id', left_on = 'user_id', how = 'left')
# popular_books_ratings_with_user_data = popular_books_ratings_with_user_data.loc[popular_books_ratings_with_user_data['location'].str.contains("usa|canada")]
# popular_books_ratings_with_user_datat


# In[300]:


# Removing the duplicates so that it wont fail when we convert to pivot using book_title as index
popular_books_ratings_with_user_data= popular_books_ratings_with_user_data.drop_duplicates(subset=['user_id','book_title'], keep="last")
popular_books_ratings_with_user_data


# In[301]:


# Converting to pivot with book_title as index, user_id as columns and values as book ratings
popular_books_ratings_with_user_data_pivot = popular_books_ratings_with_user_data.pivot(index = 'book_title', columns = 'user_id', values = 'book_rating').fillna(0)
popular_books_ratings_with_user_data_sparse = csr_matrix(popular_books_ratings_with_user_data_pivot.values)
popular_books_ratings_with_user_data_pivot


# In[302]:


popular_books_ratings_with_user_data_pivot = popular_books_ratings_with_user_data_pivot.replace(0, np.NaN)
popular_books_ratings_with_user_data_pivot.loc['mean'] = popular_books_ratings_with_user_data_pivot.replace(0, np.NaN).mean()


# In[303]:


popular_books_ratings_with_user_data_pivot = popular_books_ratings_with_user_data_pivot.replace(np.NaN,0)
popular_books_ratings_with_user_data_pivot


# In[304]:


popular_books_ratings_with_user_data_pivot.loc['mean']
# popular_books_ratings_with_user_data_pivot.index[2]


# In[305]:


def cosine_similarity(indexes,book_1,book_2):
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


# In[306]:


book_name_input = input('Input the Book Name for Recommendation System')
# Pride and Prejudice
index_book_similar = popular_books_ratings_with_user_data_pivot.index.get_loc(book_name_input)
book_1 = popular_books_ratings_with_user_data_pivot.iloc[index_book_similar]
book_1 = book_1[book_1!=0]
dict = {}
for i in range(0,popular_books_ratings_with_user_data_pivot.index.size):
    if i != index_book_similar:
        book_2 = popular_books_ratings_with_user_data_pivot.iloc[i]
        book_2 = book_2[book_2!=0]
        indexes = book_1.index.intersection(book_2.index)
        dict[popular_books_ratings_with_user_data_pivot.index[i]] = cosine_similarity(indexes,book_1,book_2)
dict


# In[307]:


import operator
sorted_d = sorted(dict.items(), key=operator.itemgetter(1),reverse=True)
sorted_d[:100]


# In[308]:


def pearson_similarity(indexes,user_1,user_2,user_1_mean,user_2_mean):
    den1 = 0
    den2 = 0
    numerator = 0
    import math
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


# In[309]:


# User Based Similarity

popular_books_ratings_with_user_data_pivot_users = popular_books_ratings_with_user_data.pivot(index = 'user_id', columns = 'book_title', values = 'book_rating').fillna(0)
popular_books_ratings_with_user_data_pivot_users = popular_books_ratings_with_user_data_pivot_users.replace(0, np.NaN)
popular_books_ratings_with_user_data_pivot_users['mean'] = popular_books_ratings_with_user_data_pivot_users.replace(0, np.NaN).mean(axis=1)
popular_books_ratings_with_user_data_pivot_users = popular_books_ratings_with_user_data_pivot_users.replace(np.NaN,0)


# Storing the df in  new dataframe with mean calculated values
popular_books_ratings_with_user_data_pivot_users_new = popular_books_ratings_with_user_data_pivot_users

popular_books_ratings_with_user_data_pivot_users = popular_books_ratings_with_user_data_pivot_users.drop(['mean'], axis=1)


means = popular_books_ratings_with_user_data_pivot_users_new['mean']

# 273979 274393 is the user_id for which we are finding the similar users
user_index_to_query = int(input("Input the User for Recommendations"))
index_user_similar = popular_books_ratings_with_user_data_pivot_users.index.get_loc(user_index_to_query)
user_1 = popular_books_ratings_with_user_data_pivot_users.iloc[index_user_similar]
user_1 = user_1[user_1!=0]
user_1_mean = means.values[means.index.get_loc(user_index_to_query)]


dict = {}
for i in range(0,popular_books_ratings_with_user_data_pivot_users.index.size):
    if i != index_user_similar:
        user_2 = popular_books_ratings_with_user_data_pivot_users.iloc[i]
        user_2 = user_2[user_2!=0]
        user_2_mean = means.values[means.index.get_loc(popular_books_ratings_with_user_data_pivot_users.index[i])]
        indexes = user_1.index.intersection(user_2.index)
        dict[popular_books_ratings_with_user_data_pivot_users.index[i]] = pearson_similarity(indexes,user_1,user_2,user_1_mean,user_2_mean)

import operator
sorted_d = sorted(dict.items(), key=operator.itemgetter(1),reverse=True)
sorted_d









# In[310]:


def predict_rating(sorted_list,book_name,means,popular_books_ratings_with_user_data_pivot_users):
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


# In[311]:


print(predict_rating(sorted_d,'1984',means,popular_books_ratings_with_user_data_pivot_users))


# In[312]:


book_titles = list(popular_books_ratings_with_user_data_pivot.index.values) 
recommended_books = {}
k = 0
for book in book_titles:
    current_user_index = popular_books_ratings_with_user_data_pivot_users.index.get_loc(user_index_to_query)
    current_user_rating = popular_books_ratings_with_user_data_pivot_users.iloc[current_user_index].get(book)
    if current_user_rating == 0:
        predict_rat = predict_rating(sorted_d,book,means,popular_books_ratings_with_user_data_pivot_users)
        recommended_books[book] = predict_rat
        k+=1
    if k>=40:
        break
import operator
recommended_books_sorted = sorted(recommended_books.items(), key=operator.itemgetter(1),reverse=True)
recommended_books_sorted


# In[313]:


user_book_rating_counssst = merge_ratings_books_data[merge_ratings_books_data['book_rating'] > 7].groupby(by = ['user_id'])['book_rating'].count().reset_index().rename(columns = {'book_rating': 'total_user_rating_count'})


# In[314]:


asd = user_book_rating_count.merge(user_book_rating_counssst, right_on = 'user_id', left_on = 'user_id', how = 'left')
y = asd[asd['total_user_rating_count_x'] == asd['total_user_rating_count_y']]
y.sort_values(by='total_user_rating_count_x',ascending=False)

