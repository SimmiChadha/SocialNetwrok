from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class FriendRequest(models.Model):
    
    sender = models.ForeignKey(User, related_name='sent_friend_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_friend_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)
    
    class Meta:
        managed = True
        db_table = 'friend_request'
        unique_together = ('sender', 'receiver')
        
    def __str__(self) -> str:
        return f"{self.sender.email} -> {self.receiver.email}"
