from Backend.models import User,IndividualBooking,Event,GroupBooking,Amenity,Group
from Backend.serializers import UserSerializer,IndividualBookingSerializer,TimeSerializer,EventSerializer
from rest_framework import generics
from Backend.utils import GetSlot,doOauth,makeIndiRes,cancelIndiRes
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
import os
import requests
from dotenv import load_dotenv
load_dotenv()
# Create your views here.

class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class SpecificUser(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = User.objects.all()
        uid = self.request.query_params.get('id')
        if uid is not None:
            queryset = queryset.filter(id=uid)
        return queryset


class IndividualBookingView(generics.ListAPIView):
    serializer_class = IndividualBookingSerializer

    def get_queryset(self):
        queryset = IndividualBooking.objects.all()
        uid = self.request.query_params.get('id')
        if uid is not None:
            queryset = queryset.filter(booker_id=uid)
        return queryset


import datetime
def serialize_datetime(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")

@api_view(['POST'])
def getAvailableSlots(request):
    date = request.data["date"]
    format = '%b %d %Y'
    datetime_str = datetime.datetime.strptime(date , format)

    if("location" in request.data and "amenity" in request.data):
        data = GetSlot(request.data["duration"] ,datetime_str, location = request.data["location"] , amenity=request.data["amenity"])
    elif("amenity" in request.data):
        data = GetSlot(request.data["duration"] ,datetime_str , amenity = request.data["amenity"])
    elif("location" in request.data):
        data = GetSlot(request.data["duration"],datetime_str,location=request.data["location"])
    else:
        data = GetSlot(request.data["duration"],datetime_str)
    serialized_data = []
    print(len(serialized_data))
    if(len(data) == 0):
        return Response("No slots")
    else:
        if("start_time" in request.data):
            for item in data:
                for free_slot in item["free_slots"]:
                    start_time , end_time = free_slot
                    string_as_list = request.data["start_time"].split(":")
                    hours = int(string_as_list[0])
                    minutes = string_as_list[1]
                    if(abs(hours-int(start_time.hour)) < 1):
                        data2 = {
                                'start_time': start_time.strftime('%H:%M'),
                                'end_time': end_time.strftime('%H:%M'),
                                'amenity_id' : item["id"],
                                    }
                        serializer = TimeSerializer(data=data2)
                        if serializer.is_valid():
                            serialized_data.append(serializer.validated_data)
                        else:
                            print(serializer.errors)
            return Response(serialized_data)
        else:
            for item in data:
                for free_slot in item["free_slots"]:
                    start_time , end_time = free_slot
                    data2 = {
                            'start_time': start_time.strftime('%H:%M'),
                            'end_time': end_time.strftime('%H:%M'),
                            'amenity_id' : item["id"],
                                }
                    serializer = TimeSerializer(data=data2)
                    if serializer.is_valid():
                        serialized_data.append(serializer.validated_data)
                    else:
                        print(serializer.errors)
            return Response(serialized_data)

from django.http import HttpResponseRedirect
data_filled = None
@api_view(["GET"])
def userAuth(request):
    code = request.query_params.get("code")
    print(code)
    data_filled = doOauth(code)
    return Response(data_filled)
    


@api_view(["GET"])
def getuserAuth(request):
    global data_filled
    if(data_filled != None):
        return Response(data_filled)
    else:
        return Response(status=500)


@api_view(["GET"])
def redirectuserAuth(request):
   oauth_uri = os.environ.get("OAUTH_URI")
   return HttpResponseRedirect(oauth_uri)

@api_view(["POST"])
def makeIndiReservation(request):
    amenity_id = request.data["amenity_id"]
    start_time = request.data["start_time"]
    end_time = request.data["end_time"]
    id_user = request.data["id_user"]
    date = request.data["date"]
    format = '%b %d %Y'
    date_time_str = datetime.datetime.strptime(date , format)
    data = makeIndiRes(id_user,amenity_id,start_time,end_time,date_time_str)

    data = IndividualBookingSerializer(data)
    return Response(data.data)

@api_view(["GET"])
def cancelIndiReservation(request):
    booking_id= request.query_params.get("booking_id")
    cancelIndiRes(booking_id)
    return Response("OK")

class EventsList(generics.ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
import json
import pytz
@api_view(["GET"])
def getBooking(request):
    user_id = request.query_params.get("id")
    indi = IndividualBooking.objects.filter(booker_id=user_id)
    groups = Group.objects.filter(member=user_id)
   
    bookings = []
   
    for item in indi:
        print(item.id)
        amenity = Amenity.objects.get(id=item.amenity.id)
        entry = {}
        entry["type"] = "individual"
        entry["time_of_slot"] = str(item.time_of_slot)
        entry["duration_of_booking"] = item.duration_of_booking
        entry["timestamp_of_booking"] = str(item.timestamp_of_booking)
        entry["amenity"] = {"name" : amenity.name, "venue" : amenity.venue}
        json_entry = json.dumps(entry)
        bookings.append(json_entry)
    
    time = datetime.datetime.now()
    for item in groups:
        bookings_groups = GroupBooking.objects.filter(booker=item.id)
        group_entry = {}
        group_entry["name"] = item.name
        group_entry["members"] = [member.id for member in item.member.all()]  # Convert ManyToMany to a list of IDs
        group_entries = []
        
        for booking in bookings_groups:
            if(booking.time_of_slot >  pytz.timezone("Asia/Kolkata").localize(time)):
            # if(time_diff > 0):
                amenity = Amenity.objects.get(id=booking.amenity.id)
                entry = {}
                entry["type"] = "group"
                entry["time_of_slot"] = str(booking.time_of_slot)
                entry["duration_of_booking"] = booking.duration_of_booking
                entry["timestamp_of_booking"] = str(booking.timestamp_of_booking)
                entry["amenity"] = {"name": amenity.name, "venue": amenity.venue}
                entry["group"] = group_entry
                group_entries.append(entry)
        
        bookings.extend(group_entries)

    return Response(bookings)