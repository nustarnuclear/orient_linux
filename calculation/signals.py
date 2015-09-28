from django.db.models.signals import pre_delete
from django.dispatch import receiver
from calculation.models import EgretTask
from django.conf import settings
import os
import shutil
@receiver(pre_delete,sender=EgretTask)
def del_task_file(sender, instance, **kwargs):
    media_root=settings.MEDIA_ROOT
    pre_rela_file_path=instance.egret_input_file.name
    task_name=instance.task_name
    pre_abs_file_path=os.path.join(media_root,*(pre_rela_file_path.split(sep='/')))
    print(pre_abs_file_path)
    parent_dir=os.path.dirname(pre_abs_file_path)
    os.chdir(os.path.dirname(parent_dir))
    shutil.rmtree(task_name)
    print("%s has been delete successfully"%task_name)
    