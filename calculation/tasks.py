from __future__ import absolute_import
from datetime import datetime
from celery import shared_task
import os
from subprocess import Popen
from calculation.models import EgretTask,RobinTask,Server,get_ip
import socket
# from ftplib import FTP
# import shutil
@shared_task
def egret_calculation_task(cwd,input_filename,user,pk,version='196'):
    #set server
    hostname=socket.gethostname()
    myhost=Server.objects.get(name=hostname)
    egret_instance=EgretTask.objects.get(pk=pk)
    egret_instance.server=myhost
    egret_instance.task_status=1
    egret_instance.save()
    os.chdir(cwd)
    process=Popen(['/opt/nustar/bin/myegret','-i',input_filename,'-s',version,'-u',user])
    return_code=process.wait()
    #if process went wrong
    if return_code!=0:
        egret_instance.task_status=6
        wrong_time=datetime.now()
        egret_instance.end_time=wrong_time
        egret_instance.save()
        return return_code
        
    end_time=datetime.now()
    egret_instance.end_time=end_time
    egret_instance.task_status=4
    egret_instance.save()
    egret_instance.mv_case_res_lp_file()
    egret_instance.clear_extra_subtasks()
    #unlock the pre egret task if exists
    pre_egret_task=egret_instance.pre_egret_task
    task_type=egret_instance.task_type
    if pre_egret_task and task_type=='SEQUENCE':
        pre_egret_task.locked=False
        pre_egret_task.save()
    return return_code

@shared_task
def robin_calculation_task(pk):
    hostname=socket.gethostname()
    myhost=Server.objects.get(name=hostname)
    robin_instance=RobinTask.objects.get(pk=pk)
    if robin_instance.task_status==4:
        return
    cwd=robin_instance.get_cwd()
    os.makedirs(cwd, exist_ok=True)
    os.chdir(cwd)
    input_filename=robin_instance.get_input_filename()
    start_time=datetime.now()
    robin_instance.start_time=start_time
    robin_instance.task_status=1
    robin_instance.server=myhost
    robin_instance.save(update_fields=['start_time','task_status','server'])
    process=Popen(['/opt/nustar/bin/myrobin','-i',input_filename]) 
    return_code=process.wait()
    end_time=datetime.now()
    robin_instance.end_time=end_time
    
    #if process went wrong
    if return_code!=0:  
        robin_instance.task_status=6  
    else:
        robin_instance.task_status=4
        
    robin_instance.save()           
    return return_code
    
@shared_task
def stop_task(model,pk):
    task=model.objects.get(pk=pk)
    task_status=task.task_status
    #waiting
    if task_status==0:
        task.cancel_calculation()
              
    elif task_status==1: 
        task.stop_calculation() 
        
 

        
    
 
      
    
          
    