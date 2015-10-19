from django.db.models.signals import pre_delete
from django.db.models.signals import post_save
from django.dispatch import receiver
from calculation.models import EgretTask,EgretInputXML
from tragopan.models import FuelAssemblyLoadingPattern
from django.conf import settings
import os
import shutil
from subprocess import Popen
from django.core.files import File
@receiver(pre_delete,sender=EgretTask)
def del_task_file(sender, instance, **kwargs):
    media_root=settings.MEDIA_ROOT
    pre_rela_file_path=instance.egret_input_file.name
    task_name=instance.task_name
    pre_abs_file_path=os.path.join(media_root,*(pre_rela_file_path.split(sep='/')))
    print(pre_abs_file_path)
    parent_dir=os.path.dirname(pre_abs_file_path)
    try:
        os.chdir(os.path.dirname(parent_dir))
        shutil.rmtree(task_name)
        print("%s has been deleted successfully"%task_name)
    except Exception:
        pass
    
    
@receiver(post_save,sender=FuelAssemblyLoadingPattern)
def generate_egret_input_xml(sender,created, instance, **kwargs):
    '''
    if not created:
        tmp_dir=settings.TMP_DIR
        os.chdir(tmp_dir)
        ip_file=open('ip_addr.txt',mode='w')
        p=Popen('ifconfig',stdout=ip_file)
        p.wait()
        ip_file.close()
        
        ip_file=open('ip_addr.txt')
        s=ip_file.read().split()
        ip_addr=''
        for item in s:
            if item.startswith('addr:'):
                tmp_lst=item.split(sep=':')
                print(tmp_lst)
                if tmp_lst[1] and tmp_lst[1]!='127.0.0.1':
                    ip_addr=tmp_lst[1]
        print(ip_addr)
        cycle=instance.cycle
        unit=cycle.unit
        plant=unit.plant
        #base_component='http://{}:8000/calculation/base_component/{}/'.format(ip_addr,plant.abbrEN)
        #basecore='http://{}:8000/calculation/basecore/{}/unit{}/'.format(ip_addr,plant.abbrEN,unit.unit)
        loading_pattern='http://{}:8000/calculation/loading_pattern/{}/unit{}/'.format(ip_addr,plant.abbrEN,unit.unit)           
        #p1=Popen(['curl','-u','public:public',base_component,'-o','base_component.xml'])
        #p1.wait()
        #p2=Popen(['curl','-u','public:public',basecore,'-o','basecore.xml'])
        #p2.wait()
        p3=Popen(['curl','-u','public:public',loading_pattern,'-o','loading_pattern.xml'])
        p3.wait()
        #f1=File(open('base_component.xml'))
        #f2=File(open('basecore.xml'))
        f3=File(open('loading_pattern.xml'))
        
        eix=EgretInputXML.objects.get(unit=unit)
        #eix.base_component_xml=f1
        #eix.base_core_xml=f2
        eix.loading_pattern_xml=f3
        eix.save()
    '''
    pass  