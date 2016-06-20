from rest_framework import serializers
from django.contrib.admin.models import LogEntry
class LogEntrySerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  LogEntry
        fields = ( 'action_time','user','content_type','object_id','object_repr','action_flag','change_message')      