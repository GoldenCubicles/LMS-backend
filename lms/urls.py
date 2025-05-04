from django.contrib import admin
from django.urls import path, include
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt
from core.views import upload_chapter_files

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True))),
    path('api/upload-chapter-files/', upload_chapter_files, name='upload_chapter_files'),
] 