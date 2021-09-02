from json import loads, dumps
from django.contrib.auth.models import User,Group
from rest_framework import serializers
from App.models import *
from django.contrib.auth.hashers import make_password


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = "__all__"  



class UserSerializer(serializers.ModelSerializer):

    user_info = serializers.SerializerMethodField()

    def validate_email(self, value):
            value = value.lower()
            check_query = User.objects.filter(email=value)
            if self.instance:
                check_query = check_query.exclude(pk=self.instance.pk)
            if self.parent is not None and self.parent.instance is not None:
                genre = getattr(self.parent.instance, self.field_name)
                check_query = check_query.exclude(pk=genre.pk)
            if check_query.exists():
                raise serializers.ValidationError('A Genre with this name already exists.')
            if not value:
                raise serializers.ValidationError('Email is required.')
            return value

    def validate_password(self, value):
            request = self.context.get('request', None)
            if request and getattr(request, 'method', None) == "POST":
                if not value:
                    raise serializers.ValidationError('Password is required.')
            elif request and getattr(request, 'method', None) == "PUT":
                if not value:
                    user = User.objects.get(id=self.instance.pk)
                    return user.password
            return make_password(value) 

    class Meta:
        model = User
        fields = [ 'id','username', 'email','first_name','last_name','password','date_joined','groups','user_info']
        extra_kwargs = {'email': {'required': True,       
                                  'allow_blank': False},'password':{'write_only': True , 'required':True,
                                  'allow_blank': True}
                                  
                                  
                                  ,'first_name': {'required': True,
                                  'allow_blank': False},'last_name': {'required': True,
                                  'allow_blank': False},'username': {'required': True,
                                  'allow_blank': False}}



        def create(self, validated_data):
           user = User.objects.create_user(**validated_data)
           return user                          

    def get_user_info(self, user_info):
        qs = UserInfo.objects.filter(user =user_info)
        if len(qs)>0:
            qs =qs[0]
        rs = UserInfoSerializer(qs, many=False).data
        return rs


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"  


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"
        extra_kwargs = {'name': {'required': True,       
                                  'allow_blank': False},'email': {'required': True,       
                                  'allow_blank': False},'address': {'required': True,       
                                  'allow_blank': False},'phone1': {'required': True,       
                                  'allow_blank': False}  }  




class EmployerSerializer(serializers.ModelSerializer):
    user_data = serializers.SerializerMethodField()
    class Meta:
        model = Employer
        fields = "__all__" 

    def get_user_data(self, user_data):
        qs = User.objects.get(id =user_data.user.id)
        rs = UserSerializer(qs, many=False).data
        return rs    


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = "__all__" 

class FormationPricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormationPricing
        fields = "__all__"          


class FormationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Formation
        fields = "__all__"  
        extra_kwargs = {'name': {'required': True,       
                                  'allow_blank': False}}


class Code_SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Code_Subscription
        fields = "__all__"  



class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = "__all__"  





class Pricing_PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pricing_Payment
        fields = "__all__"  


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"  


 
 


        
        

        