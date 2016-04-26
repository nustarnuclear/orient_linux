from django.db.models.signals import pre_delete
from django.dispatch import receiver
from calculation.models import EgretTask,MultipleLoadingPattern,PreRobinTask,RobinTask
from tragopan.models import del_fieldfile
import os
import shutil
@receiver(pre_delete,sender=EgretTask)
def del_task_file(sender, instance, **kwargs):
    base_dir=instance.get_base_dir()
    task_name=os.path.basename(base_dir)
    try:
        os.chdir(os.path.dirname(base_dir))
        shutil.rmtree(task_name)
        print("%s has been deleted successfully"%task_name)
    except Exception:
        pass
#     
@receiver(pre_delete,sender=MultipleLoadingPattern)
def del_loading_pattern(sender, instance, **kwargs):
    xml_file=instance.xml_file
    xml_file.delete()
    del_fieldfile.send(sender=sender,pk=instance.pk)
     

@receiver(pre_delete,sender=PreRobinTask)
def del_prerobin_task_file(sender, instance, **kwargs):
    abs_file_path=instance.abs_file_path
    base_name=os.path.basename(abs_file_path)
    try:
        os.chdir(os.path.dirname(abs_file_path))
        shutil.rmtree(base_name)
        print("%s has been deleted successfully"%base_name)
    except Exception:
        pass
    
@receiver(pre_delete,sender=RobinTask)
def del_robin_task_file(sender, instance, **kwargs):
    cwd=instance.get_cwd()
    task_name=os.path.basename(cwd)
    try:
        os.chdir(os.path.dirname(cwd))
        shutil.rmtree(task_name)
        print("%s has been deleted successfully"%task_name)
    except Exception:
        pass
    
@receiver(del_fieldfile,sender=MultipleLoadingPattern)
def del_loading_pattern_xml(sender, **kwargs):
    pk=kwargs['pk']
    obj=sender.objects.get(pk=pk)
    try:
        filepath=obj.FILE.path
        os.remove(filepath)
    except:
        pass