from __future__ import absolute_import
from datetime import datetime
from celery import shared_task
import os
from subprocess import Popen
from django.db.models import F
#from celery.contrib.abortable import AbortableTask
#from orient.celery import app
@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)

@shared_task
def egret_calculation_task(egret_cal_instance):
    egret_instance=egret_cal_instance.egret_instance
    cwd=egret_instance.get_cwd()
    os.chdir(cwd)
    input_filename=egret_instance.get_input_filename() 
    #egret_instance.calculation_identity=egret_cal_instance.id
    start_time=datetime.now()
    egret_instance.start_time=start_time
    egret_instance.task_status=1
    egret_instance.save()
    process=Popen(['runegret','-i',input_filename])
    return_code=process.wait()
    print('return code is {}'.format(return_code))
    end_time=datetime.now()
    egret_instance.end_time=end_time
    egret_instance.task_status=4
    egret_instance.save()
    return return_code

class EgretCalculationTask:
    
    #the time to wait if not available
  
    
    def __init__(self,egret_instance):
        self.egret_instance=egret_instance
        #self.id=id
    
    def start_calculation(self,countdown=0):
        result=egret_calculation_task.apply_async((self,),countdown=countdown)
        #egret_instance=self.egret_instance
        #egret_instance.calculation_identity=F('calculation_identity')+result.id
        #egret_instance.save()
        #egret_instance.refresh_from_db()
        #print('calculation identity is %s'%egret_instance.calculation_identity)
        return result.id
    
    

        
    
 
      
    
          
    