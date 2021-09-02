from django.shortcuts import render
from django.contrib.auth.models import User, Group
from App.models import *
from App.serializers import *
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK,HTTP_201_CREATED
)
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
import patoolib
from datetime import datetime
import os
from django.db.models import Count,Max
from django_elasticsearch_dsl import Document,fields
from django_elasticsearch_dsl.registries import registry
import requests
import json
from elasticsearch_dsl.query import MultiMatch,Q
from django.views import View
from celery import current_app
from django.http import JsonResponse
from celery import shared_task,current_task

from django.db.models.functions import Trunc
from django.core.serializers.json import DjangoJSONEncoder

from App.notification import Send_Notif as SN

from django.core.files import File
from urllib.request import urlopen
from tempfile import NamedTemporaryFile


@registry.register_document
class FormationIndexerDocument(Document):
    
    collection = fields.NestedField(properties={
        'name': fields.TextField(),
        'id': fields.IntegerField()
    })

    license = fields.NestedField(properties={
        'license_status': fields.IntegerField(),
        'total_stage': fields.IntegerField(),
        'student_stage': fields.IntegerField(),
        'basic_stage': fields.IntegerField(),
        'pro_stage': fields.IntegerField(),
        'company_stage': fields.IntegerField(),
        'id': fields.IntegerField()
    })
  
    class Index:
       
        name = 'formationapi'

    class Django:
        model = Formation 
        # related_models = [Collection]

        def get_instances_from_related(self, related_instance):
         
            return related_instance.formation_set.all()
        

        fields = ['id','name','short_description','icon','enrich_formation','full_description','active','created','updated']

      



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_staff=False).order_by('-date_joined')
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['username', 'first_name','last_name']
    filterset_fields = ['username', 'first_name','last_name']


class GroupViewSet(viewsets.ModelViewSet):
 
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class CompanyViewSet(viewsets.ModelViewSet):
 
    queryset = Company.objects.all().order_by("-id")
    serializer_class = CompanySerializer  
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name','email','website','address','phone1']
    filterset_fields = ['name','for_landing']  


class UserInfoViewSet(viewsets.ModelViewSet):
 
    queryset = UserInfo.objects.all()
    serializer_class = UserInfoSerializer    




def get_recursive_emp(queryset,result):
    for x in queryset:
        result.append(x.user.id)
        if x.user.id not in result:
            emp= Employer.objects.filter(added_by=x.user.id)
            if len(emp)>0:
                return get_recursive_emp(emp,result)      

    return result


class EmployerViewSet(viewsets.ModelViewSet):
 
    queryset = Employer.objects.all().order_by("-id")
    serializer_class = EmployerSerializer 
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['user__first_name','user__last_name','user__email','user__username']
    filterset_fields = ['company','added_by','user']
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        try:
            withfilter = request.GET['added_by']
            result = get_recursive_emp(queryset,[])
            result.append(withfilter)
            queryset = Employer.objects.filter(added_by__in=result)
        except:
            pass   
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)  



class CollectionViewSet(viewsets.ModelViewSet):
 
    queryset = Collection.objects.all().order_by("-id")
    serializer_class = CollectionSerializer 
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name']
    filterset_fields = ['name']  

class FormationPricingViewSet(viewsets.ModelViewSet):
 
    queryset = FormationPricing.objects.all().order_by("-id")
    serializer_class = FormationPricingSerializer 
     


def extract_file(path,id):
    if not path:
        return
    path = path.replace(os.getenv('DJANGO_HOST', default="http://127.0.0.1:8000/"),"")
    if path[-4:] =="json":
      return
    now = datetime.now()
    new_path =now.strftime("%mQ%dQ%YQ%HV%MV%S")
    new_path = "./media/"+new_path+"/"
    os.mkdir(new_path) 
    path_to_update = None
    patoolib.extract_archive(path, outdir=new_path)
    for file in os.listdir(new_path):
        for v in os.listdir(new_path+"/"+file):
          if v.endswith(".json"):
            path_to_update=new_path+file+"/"+v

    if not path_to_update :
        return
    Formation.objects.filter(id=id).update(source =path_to_update.replace('./media',''))        



@shared_task
def enrich_formation(data):
    try:
        url = os.getenv('API_ENRICH_HOST', default="http://127.0.0.1:5200/enrich/")
        r= requests.post(url,json={"name":data['name'],"short_description":data['short_description'],"full_description":data['full_description']})
        serializer = FormationSerializer(Formation.objects.get(id=data['id']),data={"enrich_formation":r.text},partial=True)
        if serializer.is_valid(raise_exception=True):
                serializer.save()
    except:
        pass        
 



class FormationViewSet(viewsets.ModelViewSet):
 
    queryset = Formation.objects.all().order_by("-id")
    serializer_class = FormationSerializer 
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    search_fields = ['name','short_description','full_description','enrich_formation']
    filterset_fields = ['license__license_status','active','license__total_stage','collection']
    ordering_fields = ['id']
    # ordering = ['name']


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        extract_file(serializer.data['source'],serializer.data['id'])
        # task = enrich_formation.delay(serializer.data)
        # print(task)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)



    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        extract_file(serializer.data['source'],serializer.data['id'])
        task = enrich_formation.delay(serializer.data)
        print(task)
         

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)      








class Code_SubscriptionViewSet(viewsets.ModelViewSet):
 
    queryset = Code_Subscription.objects.all().order_by("-id")
    serializer_class = Code_SubscriptionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['generated_code']
    filterset_fields = ['generated_code','created_by','company'] 


@shared_task
def index_to_model(data):
    data_index_recommended_system={"user_id":None,"item_id":None,"user_license":None,"current_level":None,"total_level":None}
    fl = Formation.objects.get(id=data['formation']).license
    pr_1 =Employer.objects.filter(user=data['user'],active=True)
    pr_status =0
    try:
        if len(pr_1)>0:
            pr_status= 3
        else :    
            pr_2 = Pricing_Payment.objects.filter(for_user=data['user'],active=True)
            if len(pr_2)>0:
               pr_status = pr_2[0].pricing_status
    except:
        pass        
    
    if pr_status==0:
      total_stages = fl.student_stage
    elif pr_status ==1:
        total_stages = fl.basic_stage
    elif pr_status ==2:
        total_stages = fl.pro_stage
    elif pr_status ==3:
        total_stages = fl.total_stage


    data_index_recommended_system['current_level'] =data['stage']
    data_index_recommended_system['total_level'] =total_stages
    data_index_recommended_system['user_id'] =data['user']
    data_index_recommended_system['item_id'] =data['formation']
    data_index_recommended_system['user_license'] = pr_status

    url = os.getenv('API_RECOMMENDED_SYSTEM_HOST', default="http://127.0.0.1:6200/add_new/")
    try:
      requests.post(url,json=data_index_recommended_system)
    except:
        pass  
    #DATA RECOMMEND SYSTEM

    data_index_skills={"user_id":None,"item_id":None,"timestamp":None,"score":None,"user_license":None,"current_level":None,"total_level":None}
    ts = datetime.now().timestamp()  
    data_index_skills['current_level'] =data['stage']
    data_index_skills['total_level'] =total_stages
    data_index_skills['user_id'] =data['user']
    data_index_skills['item_id'] =data['formation']
    data_index_skills['user_license'] = pr_status
    data_index_skills['score'] = data['score']
    data_index_skills['timestamp'] = ts

    url = os.getenv('API_SKILLS_HOST', default="http://127.0.0.1:7200/add_new/")
    try:
       requests.post(url,json=data_index_skills)
    except:
        pass  
    return 

    



class HistoryViewSet(viewsets.ModelViewSet):
 
    queryset = History.objects.all()
    serializer_class = HistorySerializer 
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['user']
    filterset_fields = ['user','formation']
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        task=index_to_model.delay(serializer.data)
        print(task)
        
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers) 


class Pricing_PaymentViewSet(viewsets.ModelViewSet):
 
    queryset = Pricing_Payment.objects.all()
    serializer_class = Pricing_PaymentSerializer 
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['for_user','for_company']
    filterset_fields = ['for_user','for_company'] 



class NotificationViewSet(viewsets.ModelViewSet):
 
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer 
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['sender_user','to_user']
    filterset_fields = ['sender_user','to_user'] 




@csrf_exempt
@api_view(["POST"])
def Save_History(request):
    data = {"user":None,"formation":None,"score":None,"stages":None}
    user_id = int(request.data.get('UserId'))
    formation_id = request.data.get('FormationId')
    data['user']=User.objects.get(id=user_id)
    data['formation']=Formation.objects.get(id=formation_id)
    data['score']=request.data.get('ScoreTotal')
    data['stages']=request.data.get('stages')
    m = History(**data)
    m.save()
    data2 = {"user":None,"formation":None,"score":None,"stage":None}
    data2['user']=user_id
    data2['formation']=formation_id
    data2['score']=data['score']
    k=0
    for x in request.data.get('stages'):
        if x['Duration'] !=0:
            k+=1
    data2['stage']= k
    task=index_to_model.delay(data2)
    print(task)
    

    return Response({"result":"ok"},status=HTTP_200_OK)


@csrf_exempt
@api_view(["POST"])

def Login_User(request):
    username = request.data.get("username")
    password = request.data.get("password")    
    if username is None or password is None:
        return Response({'error': 'Please provide both username and password'},
                        status=HTTP_400_BAD_REQUEST)
    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Invalid Credentials'},
                        status=HTTP_404_NOT_FOUND)
    token, _ = Token.objects.get_or_create(user=user)
    token = model_to_dict(token)
    user = User.objects.get(id=user.id)
    user_data= UserSerializer(user, many=False).data
    try:
      user_info = UserInfo.objects.get(user=user)
      user_info = UserInfoSerializer(user_info, many=False).data 
    except:
        user_info = UserInfo.objects.create(user=user)
        user_info = UserInfoSerializer(user_info, many=False).data 
        
    return Response({"user":user_data,"user_info":user_info,"tok":token},status=HTTP_200_OK)


@csrf_exempt
@api_view(["POST"])
def Register_User(request):
    user_serializer = UserSerializer(data=request.data.get("user"))
    user_serializer.is_valid(raise_exception=True)
    #STEP 1
    user_info_serializer = UserInfoSerializer(data=request.data.get("user_info"))
    user_info_serializer.is_valid(raise_exception=True)
    #STEP 2
    user_serializer.save()
    user_pass = User.objects.get(id = user_serializer.data['id'])
    user_pass.set_password(request.data.get("user")['password'])
    user_pass.save()
    user_info_data = user_info_serializer.data
    user_info_data['user']=user_serializer.data['id']
    #STEP 3
    user_info_serializer = UserInfoSerializer(data=user_info_data)
    user_info_serializer.is_valid(raise_exception=True)
    user_info_serializer.save()
    #STEP 4
    token, _ = Token.objects.get_or_create(user=User.objects.get(id=user_serializer.data['id']))
    result ={"user":user_serializer.data,"user_info":user_info_serializer.data,"tok":model_to_dict(token)}
    SN(user_serializer.data['id'],None,"0")
    return Response(result, status=HTTP_201_CREATED)




@csrf_exempt
@api_view(["GET"])
def Search_Formation(request):

    key= request.GET.get("key")
    pricing = request.GET.get("pricing")
    collec = request.GET.get("collec")
    page = request.GET.get("page")
    if not page:
        page =1
    s = FormationIndexerDocument.search()
    if key:
      if len(key)>3:  
        url = os.getenv('API_TRANS_HOST', default="http://127.0.0.1:5200/trans/")
        r= requests.post(url,json={"text":key})
        rs = json.loads(r.text)
        key= key.strip() +" "+rs
        s = s.query("query_string", query="*"+key+"*", analyze_wildcard=True,allow_leading_wildcard=True)
        
    if pricing:
       s= s.filter("nested", path='license', query=Q("term",license__license_status=pricing))

    

    if collec: 
        s = s.filter('nested', path='collection', query=Q("term",collection__id=collec))

    s = s.filter("term",active=True)   
    total = s.count()
    
    result = []
    for hit in s[(page-1)*10:page*10]:
        result.append(hit.to_dict())
    pagination =[]
    size =10
    llp = total / size
    nnp = int(round(total / size))
    ccp = nnp+1 if llp> nnp else nnp
    for k in range(ccp):
        pagination.append(k+1)

    return Response({"result":result,"count":total,"pagination":pagination}, status=HTTP_201_CREATED)    

    

class TaskView(View):
    def get(self, request, task_id):
        task = current_app.AsyncResult(task_id)
        response_data = {'task_status': task.status, 'task_id': task.id}
        if task.status == 'SUCCESS':
            response_data['results'] = task.get()
        return JsonResponse(response_data)
    





@csrf_exempt
@api_view(["POST"])
def Get_Recommended(request):
    try:
        url = os.getenv('API_RECOMMENDED_PREDICT', default="http://127.0.0.1:6200/predict_to_user/")
        r= requests.post(url,json={"user_id":request.data.get("user_id"),"user_license":request.data.get("user_license")})
        rs = json.loads(r.text)
    except:
        rs ={"most_item":[]}    
    return Response({"result":rs},status=HTTP_200_OK)  



@csrf_exempt
@api_view(["POST"])
def Get_Skills_Level(request):
    try:
        url = os.getenv('API_SKILLS_PREDICT', default="http://127.0.0.1:7200/predict_to_user/")
        r= requests.post(url,json={"user_id":request.data.get("user_id")})
        rs = json.loads(r.text)
    except:
        rs = {"user_class":0}    
    return Response({"result":rs},status=HTTP_200_OK)    



@csrf_exempt
@api_view(["POST"])
def Get_Week_History(request):
    try:
        r1 = History.objects.filter(user=request.data.get("user")).annotate(day=Trunc('created', 'day')).values('day').annotate(c=Count('formation')).values('day', 'c')
        structure1 = json.dumps(list(r1), cls=DjangoJSONEncoder)
    except:
        return Response({"result":[]},status=HTTP_200_OK)

    return Response({"result":json.loads(structure1)[-7:]},status=HTTP_200_OK) 




def GET_HIST(user_id):
    data={"finnish":0,"to_do":0,"total_score":0,"name_to_do_formation":[],"name_done_formation":[]}
    try:
        r1 = History.objects.filter(user=user_id)
        r2 = r1.values('formation').distinct()

        for x in r2:
            
            ff1=r1.filter(formation=x['formation'])
            mms =ff1.aggregate(Max('score'))
            data['total_score']=mms['score__max']
            k=0
            for y in ff1:
                k=0
                tr = json.loads(y.stages)
                for v in tr:
                    if v['Duration'] !=0:
                        k+=1

            forma = Formation.objects.get(id = x['formation'])            
            if k==len(tr):
                data['finnish']=data['finnish']+1
                data['name_done_formation'].append(forma.name)
            else:
                data['to_do']=data['to_do']+1
                data['name_to_do_formation'].append(forma.name)
    except:
        pass                


    return data 


@csrf_exempt
@api_view(["POST"])
def Get_History_Info(request):

    user_id= request.data.get("user")
    data = GET_HIST(user_id)             
    return Response({"result":data},status=HTTP_200_OK) 


@csrf_exempt
@api_view(["POST"])
def Get_Top_Empl(request):
    result = []
    try:
        comp =request.data.get("company")
        r1 = Employer.objects.filter(company=comp)
        r2 = r1.values('user','user__username').distinct()
        for x in r2:
            data = GET_HIST(x['user'])
            data['username']=x['user__username']
            result.append(data)             
    except:
        pass       
    result = sorted(result, key=lambda k: k['total_score'])[-5:] 
    return Response({"result":result},status=HTTP_200_OK) 





@csrf_exempt
@api_view(["POST"])
def Social_Auth(request):
    email = request.data.get("email")
    password = request.data.get("id")
    first_name = request.data.get("firstName")
    last_name = request.data.get("lastName")
    image_url =request.data.get("photoUrl")
    exist_user = User.objects.filter(email=email)
    login = True if len(exist_user)>0 else False
    
    if (login):
       
        current_user = User.objects.filter(email=email)
        if (len(current_user) > 0):
                   user = current_user[0]


    else:
        current_user = User.objects.filter(email=email)
        if (len(current_user) == 0):
            user = User.objects.create(email=email, first_name=first_name, last_name=last_name, password=password, username=str(first_name + last_name).strip() + "TR")
            user_new_imag = UserInfo.objects.create(user=user)
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(urlopen(image_url).read())
            img_temp.flush()
            user_new_imag.image.save(f"image"+str(user.username)+".png", File(img_temp))
            user_new_imag.save()
            SN(user.id,None,"0")  


    token, _ = Token.objects.get_or_create(user=user)
    token = model_to_dict(token)
    user = User.objects.get(id=user.id)
    user_data= UserSerializer(user, many=False).data
    try:
      user_info = UserInfo.objects.get(user=user)
      user_info = UserInfoSerializer(user_info, many=False).data 
    except:
        user_info = UserInfo.objects.create(user=user)
        user_info = UserInfoSerializer(user_info, many=False).data 

      
    return Response({"user":user_data,"user_info":user_info,"tok":token},status=HTTP_200_OK)       
            

      