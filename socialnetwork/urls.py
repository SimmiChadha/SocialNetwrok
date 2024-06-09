"""
URL configuration for socialnetwork project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from users.views import RegisterUser, LoginUser
from social_network_app.views import SearchOtherUsers, FriendRequestView, ListFriendsView, ListPendingFriendRequestsView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', LoginUser.as_view(), name='login'),
    path('search/', SearchOtherUsers.as_view(), name='search'),
    path('friend-request/', FriendRequestView.as_view(), name='send_friend_request'),
    path('friend-request/<int:friend_request_id>/', FriendRequestView.as_view(), name='respond_friend_request'),
    path('friends/', ListFriendsView.as_view(), name='list_friends'),
    path('friend-requests/pending/', ListPendingFriendRequestsView.as_view(), name='list_pending_friend_requests'),
]
