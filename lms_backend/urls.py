"""
URL configuration for lms_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from django.views.static import serve

# Custom media file serving view to set content-type headers
def serve_media_with_content_type(request, path, document_root=None):
    # File extensions that need special content-type handling
    content_types = {
        '.mp4': 'video/mp4',
        '.webm': 'video/webm',
        '.ogg': 'video/ogg',
        '.mov': 'video/quicktime',
        '.pdf': 'application/pdf',
    }
    
    # Get content-type from query parameter if provided
    content_type_param = request.GET.get('type')
    
    if content_type_param:
        # Use the requested content type from the query parameter
        response = serve(request, path, document_root)
        response['Content-Type'] = content_type_param
        response['Content-Disposition'] = 'inline'
        print(f"Serving {path} with content-type: {content_type_param} (from query)")
        return response
    
    # Otherwise, determine content type from file extension
    for ext, ctype in content_types.items():
        if path.lower().endswith(ext):
            response = serve(request, path, document_root)
            response['Content-Type'] = ctype
            response['Content-Disposition'] = 'inline'
            print(f"Serving {path} with content-type: {ctype} (from extension)")
            return response
    
    # Default serve behavior for non-matching files
    return serve(request, path, document_root)

urlpatterns = [
    path('', RedirectView.as_view(url='/api/', permanent=False)),
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True))),
    
    # Explicitly serve media files with proper content types
    re_path(r'^media/(?P<path>.*)$', serve_media_with_content_type, {
        'document_root': settings.MEDIA_ROOT,
    }),
]

# Add static URLs for development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Add this for backwards compatibility with existing code
    # but our custom view will handle the actual media serving
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
