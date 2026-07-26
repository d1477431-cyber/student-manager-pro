from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from students.api import router, api_stats, api_me
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

api_urlpatterns = [
    path('api/', include(router.urls)),
    path('api/auth/', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/stats/', api_stats, name='api_stats'),
    path('api/me/', api_me, name='api_me'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('students.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Ajouter les endpoints de l'API REST
urlpatterns += api_urlpatterns