from django.db.models.signals import post_save,pre_delete
from django.dispatch import receiver
from .models import OperationMonthlyParameter,OperationBankPosition,OperationDistributionData,BasicMaterial
from .functions import OperationDataHandler

@receiver(post_save,sender=OperationMonthlyParameter)
def parse_raw_file(sender, instance, created=False, **kwargs):
    if created:
        file_obj=instance.raw_file
        file_path=file_obj.path
        cycle=instance.cycle
        unit=cycle.unit
        plant=unit.plant
        reactor_model=unit.reactor_model
        reactor_positions=reactor_model.positions.all()
        core_max=reactor_model.dimension
        
        #parse the file
        handler=OperationDataHandler(plant.abbrEN,unit.unit,cycle.cycle,core_max,file_path)
        
        basic_core_state=handler.basic_core_state
        core_FQ=handler.core_FQ
        core_AO=handler.core_AO
        bank_position=handler.get_bank_position()
        if plant.abbrEN in ('FJS','QNPC_II'):
            power_distribution=handler.parse_distribution_data(type=1)[0]
            AO_distribution=handler.parse_distribution_data(type=2)[1]
            FDH_distribution=handler.parse_distribution_data(type=3)[0]
        elif plant.abbrEN=='QNPC_I':
            power_distribution=handler.parse_distribution_data(type=1)[1]
            AO_distribution=[None]*len(reactor_positions)
            FDH_distribution=handler.parse_distribution_data(type=3)[1]
            
            
       
       
        #update database
        instance.date=basic_core_state[0]
        instance.avg_burnup=basic_core_state[3]
        instance.relative_power=basic_core_state[4]
        instance.boron_concentration=basic_core_state[5]
        instance.axial_power_offset=core_AO
        instance.FQ=core_FQ
        instance.save()
        
        
        if bank_position:
            #create bank position
            control_rod_clusters=reactor_model.control_rod_clusters
            for bank_name,bank_position in bank_position.items():
                try:
                    control_rod_cluster=control_rod_clusters.get(cluster_name=bank_name)
                    OperationBankPosition.objects.create(operation=instance,control_rod_cluster=control_rod_cluster,step=bank_position)
                except:
                    pass
                
        
        
        print(len(reactor_positions),len(power_distribution),len(AO_distribution),len(FDH_distribution))
        assert(len(reactor_positions)==len(power_distribution)==len(FDH_distribution))
 
        for i in range(len(reactor_positions)):
            reactor_position=reactor_positions[i]
            power=power_distribution[i]
            try:
                AO=AO_distribution[i]
            except:
                AO=None
            #rotate
            if plant.abbrEN=='QNPC_II':
                reactor_position=reactor_position.get_rotate_pos()
            FDH=FDH_distribution[i]
            OperationDistributionData.objects.create(operation=instance,reactor_position=reactor_position,relative_power=power,FDH=FDH,axial_power_offset=AO)
        
   

@receiver(pre_delete,sender=OperationMonthlyParameter)   
def del_raw_file(sender, instance, **kwargs):
    try:
        raw_file=instance.raw_file
        raw_file.delete()
        print("%s has been deleted successfully"%instance.cycle)
    except:
        pass
    
    
@receiver(post_save,sender=BasicMaterial)
def generate_material_lib(sender, instance, **kwargs): 
    BasicMaterial.generate_material_lib()
    
# @receiver(post_save,sender=FuelPelletType)   
# @receiver(post_save,sender=Material)
# def generate_material_databank_xml(sender, instance, **kwargs): 
#     Material.generate_material_databank_xml()
   
    