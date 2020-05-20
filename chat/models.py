from django.contrib.auth import get_user_model
from django.db import models
from uuid import uuid4

User = get_user_model()

def _generate_unique_uri():
    return str(uuid4()).replace('-', '')[:15]

def deserialize_user(user):

    return {
        'id': user.id, 'username': user.username, 'email': user.email,
        'first_name': user.first_name, 'last_name': user.last_name
    }

class TrackableDateModel(models.Model):
  

    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ChatSession(TrackableDateModel):

    owner = models.ForeignKey(User, on_delete=models.PROTECT)
    uri = models.URLField(default=_generate_unique_uri)


class ChatSessionMessage(TrackableDateModel):

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    chat_session = models.ForeignKey(
        ChatSession, related_name='messages', on_delete=models.PROTECT
    )
    
    message = models.TextField(max_length=2000)  
    def to_json(self):
        readers = [reader.to_json() 
            for reader in self.readers.all()]
        return{
                'id':self.pk,
                'user': deserialize_user(self.user),
                'message': self.message,
                'readers': readers
        }       
         
class Reader(models.Model):
   user = models.ForeignKey(User, on_delete=models.PROTECT)
   isRead = models.ForeignKey(ChatSessionMessage, related_name='readers', on_delete=models.PROTECT)        
   def to_json(self):
        return { 
            'reader': deserialize_user(self.user)
        } 
        
class ChatSessionMember(TrackableDateModel):

    chat_session = models.ForeignKey(
        ChatSession, related_name='members', on_delete=models.PROTECT
    )
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    def to_json(self):
        return { 
            'id':self.pk,
            'member': deserialize_user(self.user)
        }    