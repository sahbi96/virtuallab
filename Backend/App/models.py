from django.db import models
from django.contrib.auth.models import User
import string    
import random 
import jsonfield





class UserInfo(models.Model):
    user =models.OneToOneField(User,default=None,blank=True,null=True,on_delete=models.CASCADE)
    address = models.TextField(null=True, blank=True, default=None)
    phone = models.TextField(null=True, blank=True, default=None)
    image = models.ImageField(blank=True, null=True,default=None)
    unread_notification = models.IntegerField(blank=True,null=False,default=0)
    fcm_token = models.TextField(blank=True,null=True,default=None)
    active = models.BooleanField(blank=True,null=False,default=True)
    email_active = models.BooleanField(blank=True,null=False,default=False)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)


class Company(models.Model):
    
    name = models.TextField(null=False, blank=False, default=None)
    email = models.TextField(null=False, blank=False, default=None)
    website = models.TextField(null=True, blank=True, default=None)
    address = models.TextField(null=False, blank=False, default=None)
    phone1 = models.TextField(null=False, blank=False, default=None)
    image = models.ImageField(blank=True, null=True,default=None)
    max_account_nb = models.IntegerField(blank=True,null=True,default=0)
    active=models.BooleanField(blank=True,null=False,default=True)
    for_landing=models.BooleanField(blank=True,null=False,default=False)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)




class Collection(models.Model):
    name = models.TextField(null=False, blank=False, default=None)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

class FormationPricing(models.Model):
    license_status = models.IntegerField(blank=True,null=True,default=0)
    total_stage = models.IntegerField(blank=True,null=True,default=None)
    student_stage = models.IntegerField(blank=True,null=True,default=None)
    basic_stage = models.IntegerField(blank=True,null=True,default=None)
    pro_stage = models.IntegerField(blank=True,null=True,default=None)
    company_stage = models.IntegerField(blank=True,null=True,default=None)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

class Formation(models.Model):
    name = models.TextField(null=False, blank=False, default=None)
    collection = models.ForeignKey(Collection,related_name="formation_collection",default=None,blank=True,null=True,on_delete=models.SET_NULL)
    icon = models.ImageField(blank=True, null=True,default=None)
    short_description = models.TextField(null=True, blank=True, default=None)
    full_description = models.TextField(null=True, blank=True, default=None)
    source = models.FileField(blank=True, null=True,default=None) 
    license = models.ForeignKey(FormationPricing,related_name="formation_pricing",default=None,blank=True,null=True,on_delete=models.SET_NULL)
    enrich_formation = models.TextField(null=True, blank=True, default=None)
    active = models.BooleanField(blank=True,null=False,default=True) 
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)





class Employer(models.Model):
    company = models.ForeignKey(Company,related_name="user_company",default=None,blank=True,null=True,on_delete=models.CASCADE)
    added_by = models.ForeignKey(User,related_name="added_user_employer",default=None,blank=True,null=True,on_delete=models.CASCADE)
    user = models.OneToOneField(User,related_name="user_employer",default=None,blank=True,null=True,on_delete=models.CASCADE)
    position = models.TextField(null=True, blank=True, default=None)
    active = models.BooleanField(blank=True,null=False,default=False)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)


def generate_code():
    S = 10 
    ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = S))   
    return str(ran)

class Code_Subscription(models.Model):
    company = models.ForeignKey(Company,related_name="subscription_company",default=None,blank=True,null=True,on_delete=models.CASCADE)
    created_by = models.ForeignKey(User,related_name="created_by_user_subscription",default=None,blank=True,null=True,on_delete=models.CASCADE)
    active=models.BooleanField(blank=True,null=False,default=True)
    generated_code = models.TextField(null=True, blank=True, default=None) 
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True) 
    def save(self, *args, **kwargs):
        self.generated_code=generate_code()
        super(Code_Subscription, self).save(*args, **kwargs)



class History(models.Model):
    user = models.ForeignKey(User,related_name="user_history",default=None,blank=True,null=True,on_delete=models.CASCADE)
    formation = models.ForeignKey(Formation,related_name="user_formation",default=None,blank=True,null=True,on_delete=models.CASCADE)
    stages = jsonfield.JSONField(blank=True, null=True, default=None)
    score = models.FloatField(blank=True,null=True,default=None)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)


class Pricing_Payment(models.Model):
    for_user =models.ForeignKey(User,related_name="pricing_payment_user",default=None,blank=True,null=True,on_delete=models.CASCADE)
    for_company =models.ForeignKey(Company,related_name="pricing_payment_company",default=None,blank=True,null=True,on_delete=models.CASCADE)
    price = models.FloatField(blank=True,null=True,default=0)
    pricing_status = models.IntegerField(blank=True,null=True,default=0)
    pricing_options = jsonfield.JSONField(blank=True, null=True, default=None)
    subscription_period = models.IntegerField(blank=True,null=True,default=0)
    active = models.BooleanField(blank=True,null=False,default=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)



class Notification(models.Model):
    sender_user =models.ForeignKey(User,related_name="sender_user_notification",default=None,blank=True,null=True,on_delete=models.CASCADE)
    to_user =models.ForeignKey(User,related_name="to_user_notification",default=None,blank=True,null=True,on_delete=models.CASCADE)
    subject = models.TextField(null=False, blank=False, default=None)
    content = models.TextField(null=False, blank=False, default=None)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)




    
