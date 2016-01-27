#!/usr/local/bin/python3.4
import os
from subprocess import Popen,PIPE
from datetime import datetime
cwd=os.getcwd()
DEFAULT_IDYLL_VERSION=160
os.environ['LD_LIBRARY_PATH']='/opt/nustar/lib'
logfile="myidyll.log"
user=os.getenv('USER')
#if present -i or --input option
log_file=open(logfile,mode='w',buffering=1) 
log_file.write('----------------------------------------------------------------------------------------------------------\n')
log_file.write('Hello %s! Have a good time!!!\n'%user)
log_file.write('IDYLL version is %s\n'%DEFAULT_IDYLL_VERSION)
log_file.write('Current working directory is %s\n'%cwd)
start_time=datetime.now()
log_file.write('IDYLL starts at %s\n'%start_time)

#Begin IDYLL calculation
with Popen(['/opt/nustar/bin/IBIS',],stdout=log_file.fileno(),stderr=PIPE,universal_newlines=True) as proc:
    log_file.write("IDYLL's pid is  %s\n"%proc.pid)
    outs,errs=proc.communicate()
    if errs:
        wrong_time=datetime.now() 
        log_file.write('IDYLL went wrong at %s\n'%wrong_time)
        log_file.write('ERROR code is %s\n'%errs)
        log_file.close()
        raise AssertionError('A IDYLL error happened,code is %s'%errs)
              
end_time=datetime.now()   
log_file.write('IDYLL ends at %s\n'%end_time)
log_file.write('Time costs  %s\n'%(end_time-start_time))
log_file.write('Bye %s! see you next time!!!\n'%user)
log_file.close()