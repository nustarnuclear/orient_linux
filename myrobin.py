#!/usr/local/bin/python3.4
import os
from  subprocess import Popen,PIPE
from argparse import ArgumentParser,RawDescriptionHelpFormatter
import textwrap
from datetime import datetime
cwd=os.getcwd()
DEFAULT_ROBIN_VERSION=190


logfile="myrobin.log"
#workspace=".workspace"
sys_user=os.getenv('USER')

parser = ArgumentParser(prog='ROBIN',description='Begin ROBIN calculation',
                        formatter_class=RawDescriptionHelpFormatter, 
                        epilog= textwrap.dedent('''
                                **************************************************************
                                ROBIN%d                                                         
                                Shanghai Nustar Nuclear Power Technology Co., Ltd.         
                                CNNC Nuclear Power Operations Management Co., Ltd.         
                                All Rights Reserved, 2012~2016                             
                                **************************************************************
                                '''%DEFAULT_ROBIN_VERSION))

parser.add_argument('--version', '-v',action='version', version='%(prog)s'+str(DEFAULT_ROBIN_VERSION),help='Show the default EGRET version')
parser.add_argument('--input', '-i',dest='input_file',help='input file of the %(prog)s program')
parser.add_argument('-lib',dest='lib',default='/opt/nustar/lib/rlib_1.04c',help='designate the rlib path')
parser.add_argument('-omp',dest='omp',default='1',help='designate threads number')
parser.add_argument('--user', '-u',type=str,default=sys_user,dest='user',help='designate current user')
parser.add_argument('--table','-t',default='/opt/nustar/lib/hydro.table',dest='table',help='hydro.table must be absolute path')
args = parser.parse_args()
args_dic=vars(args)


#ROBIN working directory
#path=args_dic['path']
input_file=args_dic['input_file']
lib=args_dic['lib']
omp=args_dic['omp']
table=args_dic['table']
user=args_dic['user']

#link hydro table
cwd_table=os.path.join(cwd,'hydro.table')

try:
    if os.path.isfile(cwd_table):
        pass
    elif os.path.islink(cwd_table):
        pass
    else:
        os.symlink(table,cwd_table,)     
except:
    pass

if input_file.endswith('.inp'):
    input_file=input_file.strip('.inp')
    
#if present -i or --input option
if input_file:
    log_file=open(logfile,mode='a',buffering=1) 
    log_file.write('----------------------------------------------------------------------------------------------------------\n')
    log_file.write('Hello %s! Have a good time!!!\n'%user)
    log_file.write('ROBIN version is %s\n'%DEFAULT_ROBIN_VERSION)
    log_file.write('Current working directory is %s\n'%cwd)
    start_time=datetime.now()
    log_file.write('ROBIN starts at %s\n'%start_time)
    
    #Begin ROBIN calculation
    
    with Popen(['/opt/nustar/bin/ROBIN%d'%DEFAULT_ROBIN_VERSION,'-i',input_file,'-lib',lib,'-omp',omp],stdout=log_file.fileno(),stderr=PIPE,universal_newlines=True) as proc:
        outs,errs=proc.communicate()
        
        if errs:
            wrong_time=datetime.now() 
            log_file.write('ROBIN went wrong at %s\n'%wrong_time)
            log_file.write('ERROR code is %s\n'%errs)
            log_file.close()
            raise AssertionError('A ROBIN error happened,code is %s'%errs)
            
            
    end_time=datetime.now()   
    log_file.write('ROBIN ends at %s\n'%end_time)
    log_file.write('Time costs  %s\n'%(end_time-start_time))
    log_file.write('Bye %s! see you next time!!!\n'%user)
    log_file.close()


