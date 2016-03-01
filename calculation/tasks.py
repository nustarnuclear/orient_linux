from __future__ import absolute_import
from datetime import datetime
from celery import shared_task
import os
from subprocess import Popen
from calculation.models import EgretTask,RobinTask
#from calculation.models import EgretTask
#from celery.contrib.abortable import AbortableTask
from orient.celery import app
@app.task(bind=True)
def add(self,x, y):
    print(self.AsyncResult)
    print(self.request.id)
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)

@shared_task
def egret_calculation_task(cwd,input_filename,user,pk,version='195'):
    egret_instance=EgretTask.objects.get(pk=pk)
    egret_instance.task_status=1
    egret_instance.save()
    os.chdir(cwd)
    process=Popen(['/opt/nustar/bin/myegret','-i',input_filename,'-s',version,'-u',user])
    return_code=process.wait()
    print('return code is {}'.format(return_code))
    
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
    egret_instance.mv_case_res_file()
    
    #unlock the pre egret task if exists
    pre_egret_task=egret_instance.pre_egret_task
    task_type=egret_instance.task_type
    if pre_egret_task and task_type=='SEQUENCE':
        pre_egret_task.locked=False
        pre_egret_task.save()
    return return_code

@shared_task
def robin_calculation_task(pk):
    robin_instance=RobinTask.objects.get(pk=pk)
    cwd=robin_instance.get_cwd()
    os.chdir(cwd)
    input_filename=robin_instance.get_input_filename()
    start_time=datetime.now()
    robin_instance.start_time=start_time
    robin_instance.task_status=1
    robin_instance.save(update_fields=['start_time','task_status'])
    process=Popen(['/opt/nustar/bin/myrobin','-i',input_filename,])
    return_code=process.wait()
    end_time=datetime.now()
    robin_instance.end_time=end_time
    
    #if process went wrong
    if return_code!=0:  
        robin_instance.task_status=6  
    else:
        robin_instance.task_status=4
        
    robin_instance.save(update_fields=['end_time','task_status'])
    return return_code

    
    
    

        
    
 
      
    
          
    