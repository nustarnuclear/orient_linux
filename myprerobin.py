#!/usr/local/bin/python3.4
import os
from subprocess import Popen
from argparse import ArgumentParser,RawDescriptionHelpFormatter
import textwrap
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
    if input_file.endswith('.inp'):
        input_file=input_file.rstrip('.inp')
    print(input_file)   
    process=Popen(['/opt/nustar/bin/PreROBIN%d'%DEFAULT_PreROBIN_VERSION,'-i',input_file])
    process.wait()
    