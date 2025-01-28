from django.urls import path
from . import views

urlpatterns = [
    path(r'user/', views.UserList.as_view({"get": "list"}), name="Get User List"),
    path(r'user/permission/', views.PermissionList.as_view({"get": "list"}), name="Get Permission List"),
    path(r'user/create/', views.UserCreate.as_view({"post": "create"}), name="Create One User"),
    path(r'user/setpermission/', views.UserPermission.as_view({"post": "create"}), name="Set Permission For User"),
    path(r'user/changepwd/', views.UserChangePWD.as_view({"post": "create"}), name="Change Password"),
    path(r'user/lock/', views.UserLock.as_view({"post": "create"}), name="Lock & Unlock User"),
    path(r'user/delete/', views.UserDelete.as_view({"post": "create"}), name="Delete One User"),
]
