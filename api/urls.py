from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from api.routers import get_combined_router


router = get_combined_router() # MEH: Combined all routers.py in apps

urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'), # MEH: xml schema file
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'), # MEH: Swagger-ui api document
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'), # MEH: Redoc api document
    path('auth/', include('rest_framework.urls', namespace='rest_framework')), # MEH: DRF login form
    path('', include(router.urls)), # MEH: All app ViewSet
    path('', include('user.urls')), # MEH: JWT Token urls
]
