from django.urls import include, path
from rest_framework import routers
from django.conf.urls import url
from .views import*


router = routers.DefaultRouter()
router.register(r'user', UserViewSet)
router.register(r'userinfo', UserInfoViewSet)
router.register(r'group', GroupViewSet)
router.register(r'company', CompanyViewSet)
router.register(r'employer', EmployerViewSet)
router.register(r'collection', CollectionViewSet)
router.register(r'formation_pricing', FormationPricingViewSet)
router.register(r'formation', FormationViewSet)
router.register(r'code_subcription', Code_SubscriptionViewSet)
router.register(r'history', HistoryViewSet)
router.register(r'pricing_payment', Pricing_PaymentViewSet)
router.register(r'notification', NotificationViewSet)



urlpatterns = [

    url('', include(router.urls)),
    path('register-user/', Register_User),
    path('login-user/', Login_User),
    path('Social_Auth/',Social_Auth),
    path('setFormation', Save_History),
    path('search-formation/', Search_Formation),
    path('get-recommended/', Get_Recommended),
    path('get-skills-level/', Get_Skills_Level),
    path('get-week-history/', Get_Week_History),
    path('get-history-info/', Get_History_Info),
    path('get-top-empl/', Get_Top_Empl),

    
]

