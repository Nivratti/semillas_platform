# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from rest_framework import generics
from rest_framework import permissions

from semillas_backend.users.models import User

from django.contrib.gis.db.models.functions import Distance

from django.contrib.gis.geos import Point

from .models import Service, Category
from .serializers import ServiceSerializer, CategorySerializer, CreateServiceSerializer

class CreateService(generics.CreateAPIView):
    """ access: curl http://0.0.0.0:8000/api/v1/user/2/
    """
    queryset = Service.objects.all()
    serializer_class = CreateServiceSerializer
    permission_classes = (permissions.IsAuthenticated,)

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

class UpdateService(generics.UpdateAPIView):
    """ access: curl http://0.0.0.0:8000/api/v1/user/2/
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
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
        else:
            return Service.objects.all()

# Filter services by category_id
class FeedServiceList(generics.ListAPIView):
    """ access: GET /api/v1/services/feed
    """
    serializer_class = ServiceSerializer
    permission_classes = (permissions.AllowAny,)
    filter_fields = ('category',)
    # columns to search in
    word_fields = ('title','description',)

    def get_queryset(self):
        queryset = Service.objects.exclude(author=self.request.user)
        # import pdb; pdb.set_trace()
        print("ESTMOS AQUÍII!!!!!!!!!!!!!!!!!! -->>>>> 1!!!!")
        #Order all the services by distance to the requester user location
        if not self.request.user.is_anonymous():
            print("ESTMOS AQUÍII!!!!!!!!!!!!!!!!!! -->>>>> 2!!!!")
            if 'Lat' in self.request.query_params and 'Lon' in self.request.query_params:
                # import pdb; pdb.set_trace()
                print("ESTMOS AQUÍII!!!!!!!!!!!!!!!!!! -->>>>> 3!!!!")
                ref_location = Point(float(self.request.query_params['Lon']),float(self.request.query_params['Lat']),srid=4326)
                return queryset.annotate(dist = Distance('author__location', ref_location)).order_by('dist')
            elif self.request.user.location is not None:
                print("ESTMOS AQUÍII!!!!!!!!!!!!!!!!!! -->>>>> 4!!!!")
                ref_location = self.request.user.location
                if ref_location: 
                    return queryset.annotate(dist = Distance('author__location', ref_location)).order_by('dist')
            
            else:
                print("ESTMOS AQUÍII!!!!!!!!!!!!!!!!!! -->>>>> 5!!!!")
                return queryset.order_by('date')
        
        return queryset.order_by('date')
