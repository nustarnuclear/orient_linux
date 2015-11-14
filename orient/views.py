from rest_framework.decorators import api_view,renderer_classes,parser_classes,authentication_classes
from django.contrib.auth import hashers
from rest_framework.response import Response
from rest_framework.parsers import FormParser
from rest_framework_xml.renderers import XMLRenderer
from rest_framework.authentication import TokenAuthentication

@api_view(['POST','PUT'])
@parser_classes((FormParser,))
@renderer_classes((XMLRenderer,)) 
@authentication_classes((TokenAuthentication,))
def change_password(request,format=None):
    data=request.data
    user=request.user
    old_password=data['old_password']
    new_password=data['new_password']
    try:
    
        if hashers.check_password(old_password,user.password):
            new_encoded_password=hashers.make_password(new_password)
            if not hashers.is_password_usable(new_encoded_password):
                error_message={'error_message':'the new password you provide is not correct'}
                return Response(data=error_message,status=404)
                
            user.password=new_encoded_password
            user.save()
            success_message={'success_message':'your password has been changed successfully'}
            return Response(data=success_message,status=200)
        else:
            error_message={'error_message':'you have no permission'}
            return Response(data=error_message,status=404)
        
    except Exception as e:
        print(e)
        error_message={'error_message':e}
        return Response(data=error_message,status=404,)