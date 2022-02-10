from django.urls import path
from tenant import views
from .views import LoginAPI, RegisterSuperUser, MakeUserActive, RegisterUser, UserList, TenantList

urlpatterns = [
    path('registerCompany/',views.create_company),
    path('login/', LoginAPI.as_view(), name='login'),
    path('createSuperUser/', RegisterSuperUser.as_view(), name='register'),
    path('createUser/', RegisterUser.as_view(), name='register'),
    path('activateCustomer/', MakeUserActive.as_view()),
    path('user/', UserList.as_view()),
    path('customer/', TenantList.as_view()),
]
