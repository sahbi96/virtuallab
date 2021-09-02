from App.models import *
from django.db.models import F

def Send_Notif(to_user,from_user,code):
    try:
        type_notif={"0":{"subject":"Votre compte a été activé !","content":"Vous pouvez commencer votre formation virtuelle en ligne maintenant"}}
        Notification.objects.create(to_user=User.objects.get(id=to_user),sender_user=from_user,subject=type_notif[code]["subject"],content=type_notif[code]["content"])
        UserInfo.objects.filter(user=to_user).update(unread_notification=F('unread_notification') + 1)
    except:
      pass    