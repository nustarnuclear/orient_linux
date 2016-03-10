from __future__ import absolute_import
from datetime import datetime
from celery import shared_task
import os
from subprocess import Popen
from calculation.models import EgretTask,RobinTask,Server,get_ip
from ftplib import FTP
import shutil
@shared_task
def egret_calculation_task(cwd,input_filename,user,pk,version='195'):
    egret_instance=EgretTask.objects.get(pk=pk)
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
    mainhost=Server.objects.get(name="localhost")
    myip=get_ip()
    myhost=Server.objects.get(IP=myip)
    
    robin_instance=RobinTask.objects.get(pk=pk)
    
    cwd=robin_instance.get_cwd()
    os.makedirs(cwd, exist_ok=True)
    os.chdir(cwd)
    #transfer input file by ftp if needed
    input_filename=robin_instance.get_input_filename()
    if mainhost!=myhost:
        ftp=FTP(mainhost.IP)
        ftp.login(user="django",passwd="django")
        ftp.cwd(cwd)
        ftp.retrbinary("RETR %s"%input_filename, open(input_filename,"wb").write)
        ftp.quit()    
    
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
        
    robin_instance.save()    
    #upload log and output file
    if mainhost!=myhost:
        log_filename=robin_instance.get_log_filename()
        output_filename=robin_instance.get_output_filename()
        ftp=FTP(mainhost.IP)
        ftp.login(user="django",passwd="django")
        ftp.cwd(cwd)
        ftp.storbinary("STOR %s"%log_filename, open(log_filename,"rb"))
        ftp.storbinary("STOR %s"%output_filename, open(output_filename,"rb"))
        ftp.quit() 
        
        #remove files if not at localhost
        basename=os.path.basename(cwd)
        dirname=os.path.dirname(cwd)
        os.chdir(dirname)
        shutil.rmtree(basename)
        
    return return_code

    
    
    

        
    
 
      
    
          
    