#!/usr/local/bin/python3.4
import os
from  subprocess import Popen,PIPE
from argparse import ArgumentParser,RawDescriptionHelpFormatter
import textwrap
from datetime import datetime
cwd=os.getcwd()
DEFAULT_EGRET_VERSION=195

os.environ['LD_LIBRARY_PATH']='/opt/nustar/lib'  
logfile="myegret.log"
pidfile="myegret.pid"
workspace=".workspace"
sys_user=os.getenv('USER')

parser = ArgumentParser(prog='EGRET',description='Begin egret calculation',
                        formatter_class=RawDescriptionHelpFormatter, 
                        epilog= textwrap.dedent('''
                                **************************************************************
                                EGRET%d                                                         
                                Shanghai Nustar Nuclear Power Technology Co., Ltd.         
                                CNNC Nuclear Power Operations Management Co., Ltd.         
                                All Rights Reserved, 2012~2015                             
                                **************************************************************
                                '''%DEFAULT_EGRET_VERSION))

parser.add_argument('--version', '-v',action='version', version='%(prog)s'+str(DEFAULT_EGRET_VERSION),help='Show the default EGRET version')

parser.add_argument('--input', '-i',dest='input_file',help='input file of the %(prog)s program')

parser.add_argument('--switch', '-s',type=int,choices=[191,192,193,194,195,196],dest='custom_version',help='switch EGRET version')

parser.add_argument('--user', '-u',type=str,default=sys_user,dest='user',help='designate current user')
args = parser.parse_args()

args_dic=vars(args)


#EGRET working directory
#path=args_dic['path']
input_file=args_dic['input_file']
user=args_dic['user']

    
#if present -i or --input option
if input_file:
    log_file=open(logfile,mode='a',buffering=1) 
    log_file.write('----------------------------------------------------------------------------------------------------------\n')
    #if path!=cwd:
        #os.chdir(path)
        #basename=os.path.basename(input_file)
        #designate_file=os.path.join(path,basename)
        #os.link(input_file,designate_file)
        #input_file=designate_file
        
    #if you provide a relative file path
    if not os.path.isabs(input_file):
        #concatenate this file the cwd path
        input_file=os.path.join(cwd,input_file)
    
    #check the file path is correct
    if not os.path.isfile(input_file):
        wrong_time=datetime.now() 
        log_file.write('EGRET went wrong at %s\n'%wrong_time)
        log_file.write('Your file %s does not exist\n'%input_file)
        log_file.close()
        raise AssertionError('The file %s does not exist'%input_file)
        
    #prepare .workspace directory
    workspace_dir=os.path.join(cwd,workspace)
    try:
        os.mkdir(workspace_dir)
    except:
        pass
    
    custom_version=args_dic['custom_version']
    egret_version=custom_version if custom_version else DEFAULT_EGRET_VERSION
    
    log_file.write('Hello %s! Have a good time!!!\n'%user)
    log_file.write('EGRET version is %s\n'%egret_version)
    log_file.write('Current working directory is %s\n'%cwd)
    start_time=datetime.now()
    log_file.write('EGRET starts at %s\n'%start_time)
    
    
    #Begin egret calculation
    
    with Popen(['/opt/nustar/bin/EGRET%d'%egret_version,'-i',input_file],stdout=log_file.fileno(),stderr=PIPE,universal_newlines=True) as proc:
        pidfile=open(pidfile,'w')
        pidfile.write(str(proc.pid))
        pidfile.close()
        outs,errs=proc.communicate()
        
        if errs:
            wrong_time=datetime.now() 
            log_file.write('EGRET went wrong at %s\n'%wrong_time)
            log_file.write('ERROR code is %s\n'%errs)
            log_file.close()
            raise AssertionError('A EGRET error happened,code is %s'%errs)
            
            
    end_time=datetime.now()   
    log_file.write('EGRET ends at %s\n'%end_time)
    log_file.write('Time costs  %s\n'%(end_time-start_time))
    log_file.write('Bye %s! see you next time!!!\n'%user)
    log_file.close()


