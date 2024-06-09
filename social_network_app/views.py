from datetime import timedelta
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import APIView
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import FriendRequest

User = get_user_model()


class SearchOtherUsers(APIView):
    
    def get(self, request, format=None):
        
        other_users =[]
        
        if not request.user.is_authenticated:
            return Response({'error':'user must be logged in'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            request_data = request.GET.copy()
            q = request_data.get('q','')
            page = int(request_data.get('page',1))
            limit = int(request_data.get('limit', 10))
            
            other_users = User.objects.exclude(id=request.user.id).filter(Q(email__icontains=q) | Q(name__icontains=q)).values('id', 'email', 'name')
            other_users = self.apply_pagination(page=page, limit=limit, data=other_users)
            return Response(other_users, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def apply_pagination(self, *args, **kwargs):
        
        page = kwargs.get('page')
        limit = kwargs.get('limit')
        data = kwargs.get('data')
        
        page = page - 1
        offset = page * limit if page and limit else 0
        
        if limit == 0:
            pass
        elif offset >= 0 and limit:  
            data = data[offset:offset+limit]
        else:
            data = data[0:10]
        return data      
    

class FriendRequestView(APIView):
    
    ''' handles sending friend requests '''
    
    def post(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'User must be logged in'}, status=status.HTTP_401_UNAUTHORIZED)

        receiver_id = request.data.get('receiver_id')
        if not receiver_id:
            return Response({'error': 'Receiver ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            receiver = User.objects.get(id=receiver_id)
            if receiver == request.user:
                return Response({'error': 'You cannot send a friend request to yourself'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'Receiver not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user has sent more than 3 friend requests within the last minute
        one_minute_ago = timezone.now() - timedelta(minutes=1)
        recent_requests_count = FriendRequest.objects.filter(
            sender=request.user, created_at__gte=one_minute_ago
        ).count()

        if recent_requests_count >= 3:
            return Response({'error': 'You can only send up to 3 friend requests per minute'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Check if the friend request already exists
        if FriendRequest.objects.filter(sender=request.user, receiver=receiver).exists():
            return Response({'error': 'Friend request already sent'}, status=status.HTTP_400_BAD_REQUEST)
        
        friend_request = FriendRequest(sender=request.user, receiver=receiver)
        friend_request.save()
        return Response({'message': 'Friend request sent'}, status=status.HTTP_201_CREATED)

    ''' Handles response to the request '''
    def put(self, request, friend_request_id):
        if not request.user.is_authenticated:
            return Response({'error': 'user must be logged in'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            friend_request = FriendRequest.objects.get(id=friend_request_id, receiver=request.user)
            action = request.data.get('action')
            
            if action == 'accept':
                friend_request.is_accepted = True
                friend_request.save()
                return Response({'message': 'Friend request accepted'}, status=status.HTTP_200_OK)
            elif action == 'reject':
                friend_request.delete()
                return Response({'message': 'Friend request rejected'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
        except FriendRequest.DoesNotExist:
            return Response({'error': 'Friend request not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class ListFriendsView(APIView):
    
    ''' shows list of friends '''
    
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'User must be logged in'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            # Get all accepted friend requests involving the current user
            accepted_friend_requests = FriendRequest.objects.filter(
                (Q(sender=request.user) | Q(receiver=request.user)) & Q(is_accepted=True)
            )
            
            # Create a list of friends
            friends = []
            for friend_request in accepted_friend_requests:
                if friend_request.sender == request.user:
                    friends.append({
                        'id': friend_request.receiver.id,
                        'email': friend_request.receiver.email,
                        'name': friend_request.receiver.name
                    })
                else:
                    friends.append({
                        'id': friend_request.sender.id,
                        'email': friend_request.sender.email,
                        'name': friend_request.sender.name
                    })
            
            return Response(friends, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class ListPendingFriendRequestsView(APIView):
    
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'User must be logged in'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            # Get all pending friend requests received by the current user
            pending_friend_requests = FriendRequest.objects.filter(
                receiver=request.user, is_accepted=False
            )
            
            # Create a list of pending friend requests
            pending_requests = [
                {
                    'id': friend_request.id,
                    'sender_id': friend_request.sender.id,
                    'sender_email': friend_request.sender.email,
                    'sender_name': friend_request.sender.name,
                    'created_at': friend_request.created_at
                }
                for friend_request in pending_friend_requests
            ]
            
            return Response(pending_requests, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)