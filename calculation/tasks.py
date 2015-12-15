#from __future__ import absolute_import
from datetime import datetime
from celery import shared_task
import os
from subprocess import Popen

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
def egret_calculation_task(egret_instance,version='195'):
    #egret_instance=egret_calculation_task.egret_instance
    cwd=egret_instance.get_cwd()
    user=egret_instance.user.username
    os.chdir(cwd)
    input_filename=egret_instance.get_input_filename() 
    #egret_instance.calculation_identity=egret_cal_instance.id
    start_time=datetime.now()
    egret_instance.start_time=start_time
    egret_instance.task_status=1
    egret_instance.save()
    
    process=Popen(['myegret','-i',input_filename,'-s',version,'-u',user])
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
    return return_code


    
    
    

        
    
 
      
    
          
    