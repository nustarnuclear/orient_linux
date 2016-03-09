#!/usr/local/bin/python3.4
import os
from subprocess import Popen,PIPE
from argparse import ArgumentParser,RawDescriptionHelpFormatter
import textwrap
from datetime import datetime
logfile="myprerobin.log"
os.environ['LD_LIBRARY_PATH']='/opt/nustar/lib'
DEFAULT_PreROBIN_VERSION=120
parser = ArgumentParser(prog='PreROBIN',description='Begin PreROBIN calculation',
                        formatter_class=RawDescriptionHelpFormatter, 
                        epilog= textwrap.dedent('''
                                **************************************************************
                                PreRobin%d                                                         
                                Shanghai Nustar Nuclear Power Technology Co., Ltd.         
                                CNNC Nuclear Power Operations Management Co., Ltd.         
                                All Rights Reserved, 2012~2016                             
                                **************************************************************
                                '''%DEFAULT_PreROBIN_VERSION))

parser.add_argument('--version', '-v',action='version', version='%(prog)s'+str(DEFAULT_PreROBIN_VERSION),help='Show the default EGRET version')
parser.add_argument('--input', '-i',dest='input_file',help='input file of the %(prog)s program')

args = parser.parse_args()
args_dic=vars(args)
input_file=args_dic['input_file']

    
if input_file:
    log_file=open(logfile,mode='a',buffering=1) 
    if input_file.endswith('.inp'):
        input_file=input_file.rstrip('.inp')
        
    cwd=os.getcwd()
    log_file.write('PreROBIN version is %s\n'%DEFAULT_PreROBIN_VERSION)
    log_file.write('Current working directory is %s\n'%cwd)
    start_time=datetime.now()
    log_file.write('PreROBIN starts at %s\n'%start_time)
 
    with Popen(['/opt/nustar/bin/PreROBIN%d'%DEFAULT_PreROBIN_VERSION,'-i',input_file],stdout=log_file.fileno(),stderr=PIPE,universal_newlines=True) as proc:
        outs,errs=proc.communicate()
        
        if errs:
            wrong_time=datetime.now() 
            log_file.write('PreROBIN went wrong at %s\n'%wrong_time)
            log_file.write('ERROR code is %s\n'%errs)
            log_file.close()
            raise AssertionError('A PreROBIN error happened,code is %s'%errs)
            
            
    end_time=datetime.now()   
    log_file.write('PreROBIN ends at %s\n'%end_time)
    log_file.write('Time costs  %s\n'%(end_time-start_time))
    log_file.close()
    