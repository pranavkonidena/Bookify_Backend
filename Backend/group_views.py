from Backend.models import Group,GroupBooking
from Backend.serializers import GroupSerializer,GroupBookingSerializer
from rest_framework import generics
from Backend.utils import  addtoGrp,groupReservation,cancelGroupRes
from django.http import HttpResponse
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
import datetime
from rest_framework import status
class GroupList(generics.ListAPIView):
    serializer_class = GroupSerializer
    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        
        queryset = Group.objects.all()
        uid = self.request.query_params.get('id')
        if uid is not None:
            queryset = queryset.filter(member=uid)
        return queryset
        

@api_view(['POST'])
def memberAdd(request):
    grp_id = addtoGrp(request.data["name"] , request.data["id"])
    return Response(grp_id)

@api_view(['POST'])
def groupReservationView(request):
    amenity_id = request.data["amenity_id"]
    start_time = request.data["start_time"]
    end_time = request.data["end_time"]
    group_id = request.data["group_id"]
    date = request.data["date"]
    format = '%Y-%m-%d'
    datetime_str = datetime.datetime.strptime(date , format)
    data = groupReservation(group_id,start_time,end_time,amenity_id,datetime_str)
    data = GroupBookingSerializer(data)
    return Response(data.data)

@api_view(["DELETE"])
def cancelGroupReservation(request):
    try:
        booking_id = request.data.get("booking_id")
        cancelGroupRes(booking_id)
        return Response("Ok" , status=status.HTTP_200_OK)
    except:
        return Response("Error" , status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class GroupBookingSpecific(generics.ListAPIView):
    serializer_class = GroupBookingSerializer
    def get_queryset(self):
        queryset = GroupBooking.objects.filter(id=self.request.query_params.get("id"))
        return queryset