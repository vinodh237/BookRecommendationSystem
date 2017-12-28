
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
import sqlite3 as sl


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

new_books = pd.read_csv(r'C:\Users\Vinodh\Downloads\Book\BX-Books.csv', sep=';', encoding="latin-1", error_bad_lines=False)
new_books.columns = ['isbn', 'book_title', 'book_author', 'year_of_publication', 'publisher', 'image_url_s', 'image_url_m', 'image_url_l']

filt_books = new_books.loc[new_books['book_title'].isin(plist_books)]
filt_books_final = filt_books[filt_books.groupby(by = ['book_title'])['isbn'].transform(max)==filt_books['isbn']]
len(books)
len(filt_books)
filt_users = users.loc[users['user_id'].isin(plist_user_ids)]
filt_users

filt_users.to_csv("filt_users", sep=',',index=False, encoding='utf-8')
filt_books_final.to_csv("filt_books", sep=',',index=False, encoding='utf-8')

popular_books_ratings.to_csv("user_books", sep=',',index=False, encoding='utf-8')




