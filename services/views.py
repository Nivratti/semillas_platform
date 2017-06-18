# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from rest_framework import generics
from rest_framework import permissions
from rest_framework import views
from rest_framework import parsers
from rest_framework.response import Response
from rest_framework import status

from semillas_backend.users.models import User

from django.contrib.gis.db.models.functions import Distance

from django.contrib.gis.geos import Point

from .models import Service, Category
from .serializers import *

class ServiceList(generics.ListAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = (permissions.IsAdminUser,)

class ServiceDetail(generics.RetrieveAPIView):
    """ access: curl http://0.0.0.0:8000/api/v1/user/2/
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = (permissions.AllowAny,)
    lookup_field = 'uuid'

class CreateService(generics.CreateAPIView):
    """ access: curl http://0.0.0.0:8000/api/v1/user/2/
    """
    queryset = Service.objects.all()
    serializer_class = CreateServiceSerializer
    permission_classes = (permissions.IsAuthenticated,)


class UpdateService(generics.UpdateAPIView):
    """ access: curl http://0.0.0.0:8000/api/v1/user/2/
    """
    queryset = Service.objects.all()
    serializer_class = UpdateServiceSerializer
    # TODO: Make parmission only owner can edit
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'uuid'

class CategoryList(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (permissions.AllowAny,)

class UserServiceList(generics.ListAPIView):
    serializer_class = ServiceSerializer
    permission_classes = (permissions.AllowAny,)
    def get_queryset(self):
        if 'user_uuid' in self.kwargs:
            pk = self.kwargs['user_uuid']
            u=User.objects.get(uuid=pk)
            if u:
                return Service.objects.filter(author=u.id)
        return Response("User not found", status=status.HTTP_400_BAD_REQUEST)

# Filter services by category_id
class FeedServiceList(generics.ListAPIView):
    """ Main endpoint. This is the list of services being offered.
        get:
        params:
            search: string to search in title and description
            lat:    latitude to order the services by distance
            lon:    longitude to order the services by distance
            category: int the category id to filter by
    """
    serializer_class = ServiceSerializer
    permission_classes = (permissions.AllowAny,)
    filter_fields = ('category',)
    # columns to search in
    word_fields = ('title','description',)

    def get_queryset(self):
        queryset = Service.objects.all()
        #Order all the services by distance to the requester user location
        if 'lat' in self.request.query_params and 'lon' in self.request.query_params:
            ref_location = Point(float(self.request.query_params['lon']),float(self.request.query_params['lat']),srid=4326)
            if not self.request.user.is_anonymous():
                self.request.user.location = ref_location
                self.request.user.save()
            return queryset.annotate(dist=Distance('author__location', ref_location)).order_by('dist')
        elif not self.request.user.is_anonymous and (self.request.user.location is not None):
            ref_location = self.request.user.location
            if ref_location:
                return queryset.annotate(dist = Distance('author__location', ref_location)).order_by('dist')

        else:
            return queryset.order_by('date')


#class ServicePhotoUpload(views.APIView):
class ServicePhotoUpload(generics.CreateAPIView):
    """ Test this view with the following Curl Command:
    curl -X PUT
    -H "Content-Type:multipart/form-data"
    -H "Content-Disposition: attachment; filename*=UTF-8''joaquin.jpg"
    -H "Authorization: Token 04601a00e6499ade89b55caf37dba949ec99b082"
    -F "file=@/home/ismael/Downloads/heroquest.jpg"
    http://localhost:8000/api/v1/service/photo_upload/c561b263-06e4-44d6-b72c-7d8ad2b03986/
    """

    # queryset = ServicePhoto.objects.all()
    serializer_class = ServicePhotoUploadSerializer
    parser_classes = (parsers.MultiPartParser,)
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        service_id = Service.objects.get(uuid=kwargs['uuid']).id
        request.data['service'] = service_id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
