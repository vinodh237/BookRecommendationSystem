
from . import views
from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
#
# login_required(profile_decorator.required_user_types(SUPER_ADMIN, ENTERPRISE_ADMIN, SUPERVISOR, USER)(views.Dashboard.as_view())),
#         name='dashboard')
urlpatterns = [
    url(r'^$', views.Login.as_view(), name='admin-login'),
    url(r'^books/',views.Books.as_view(), name='books'),
    url(r'^books/users/',views.Books.as_view(), name='bookss'),
    url(r'^search',views.SearchBook.as_view(), name='search'),
    url(r'^user/recommendations',views.UserRecommend.as_view(), name='user Recoomend'),
    url(r'^updateRating',views.UpdateRating.as_view(), name='update Rating'),
    url(r'logout/$', views.Logout.as_view(), name='admin-logout'),
    ]