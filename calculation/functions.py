import os
from tragopan.models import Plant,UnitParameter
from calculation.models import Ibis,BaseFuelComposition,FuelAssemblyType,BaseFuel
from xml.dom import minidom
from tragopan.functions import fuel_assembly_loading_pattern
from django.conf import settings
import tempfile
media_root=settings.MEDIA_ROOT

def generate_base_fuel():
    ibis_files=Ibis.objects.all()
    base_fuels=BaseFuel.objects.all()
    #clear all the existent base fuels
    base_fuels.delete()
    index=0
    for ibis_file in ibis_files:
        index +=1
        base_fuel=BaseFuel(fuel_identity='B'+str(index))
        base_fuel.save()
        #contains burnable poison assembly
        if ibis_file.burnable_poison_assembly:
            relative_ibis_file=Ibis.objects.filter(fuel_assembly_type=ibis_file.fuel_assembly_type,burnable_poison_assembly=None).get()
            relative_base_fuel_composition=BaseFuelComposition(base_fuel=base_fuel,ibis=relative_ibis_file,height=7.45750)
            relative_base_fuel_composition.save()
            base_fuel_composition=BaseFuelComposition(base_fuel=base_fuel,ibis=ibis_file,height=365.8000-7.45750)
            base_fuel_composition.save()
        
        else:
            base_fuel_composition=BaseFuelComposition(base_fuel=base_fuel,ibis=ibis_file,height=365.8000)
            base_fuel_composition.save()
        


def generate_base_component(plant_name):
    plant=Plant.objects.get(abbrEN=plant_name)
    base_fuels=BaseFuel.objects.filter(plant=plant)
    unit=UnitParameter.objects.get(plant=plant,unit=1)
    reactor_model=unit.reactor_model
    control_rod_clusters=reactor_model.control_rod_clusters.all()
    core_id=reactor_model.name
    #start xml 
    doc = minidom.Document()
    base_componenet_xml = doc.createElement("base_component")
    base_componenet_xml.setAttribute("basecore_ID",core_id)
    doc.appendChild(base_componenet_xml)
    
    #base fuel
    for base_fuel in base_fuels:
        base_fuel_xml=doc.createElement("base_fuel")
        base_componenet_xml.appendChild(base_fuel_xml)
        base_fuel_composition=base_fuel.composition.all()
        
        offset=base_fuel.offset
        base_fuel_xml.setAttribute("offset",'1' if offset else '0')
        
        
        fuel_id=base_fuel.fuel_identity
        base_fuel_xml.setAttribute("fuel_id",fuel_id)
        
        #not offset
        if not offset:
            base_bottom=base_fuel.base_bottom
            base_fuel_xml.setAttribute("base_bottom",str(base_bottom))
            
            data=[]
            for item in base_fuel_composition:
                data.append((item.height,item.ibis.ibis_name))
            data.sort()
            
             
            
            height_lst=[]
            ibis_lst=[item[1] for item in data]
            
            #for item in data:
            #   ibis_lst.append(item[1])
            #    try:
            #        height_lst.append(item[0]-height_lst[-1])
            #    except IndexError:
            #        height_lst.append(item[0])
            for i in range(len(data)):
                if i==0:
                    height_lst.append(data[i][0])
                else:
                    height_lst.append(data[i][0]-data[i-1][0])
                    
            height_lst_str=[str(i) for i in height_lst] 
            #active length attribute
            active_length=sum(height_lst)
            base_fuel_xml.setAttribute("active_length",str(active_length))       
            axial_ratio_xml=doc.createElement("axial_ratio")
            axial_ratio_xml.appendChild(doc.createTextNode(' '.join(height_lst_str)))
            axial_color_xml=doc.createElement("axial_color")
            axial_color_xml.appendChild(doc.createTextNode(' '.join(ibis_lst)))
            
            base_fuel_xml.appendChild(axial_ratio_xml)
            base_fuel_xml.appendChild(axial_color_xml)
            
            fuel_assembly_model=base_fuel.axial_composition.all()[0].fuel_assembly_type.model
            grid_positions=fuel_assembly_model.grid_pos.all()
            for grid_position in grid_positions:
                hight=grid_position.height
                grid=grid_position.grid
                width=grid.sleeve_height
                grid_type="1" if grid.functionality=='fix' else '2'
                if hight<active_length:
                    spacer_grid_xml=doc.createElement("spacer_grid")
                    spacer_grid_xml.appendChild(doc.createTextNode(grid_type))
                    
                    spacer_grid_xml.setAttribute("hight",str(hight+width/2))
                    spacer_grid_xml.setAttribute("width",str(width))
                    base_fuel_xml.appendChild(spacer_grid_xml)
        
        #offset
        else:
            quadrant_1=base_fuel.quadrant_one.fuel_identity
            quadrant_2=base_fuel.quadrant_two.fuel_identity
            quadrant_3=base_fuel.quadrant_three.fuel_identity
            quadrant_4=base_fuel.quadrant_four.fuel_identity
            index=1
            for item in [quadrant_1,quadrant_2,quadrant_3,quadrant_4]:
                
                inner_part_xml=doc.createElement("inner_part")
                inner_part_xml.appendChild(doc.createTextNode(item))
                inner_part_xml.setAttribute("quadrant",str(index))
                index +=1
                base_fuel_xml.appendChild(inner_part_xml)
        
        #base_componenet_xml.appendChild(base_fuel_xml)        
        
    #control rod xml   
    type_lst=[]
    for item in control_rod_clusters:
        type=item.type
        #grep rod
        if type not in type_lst : 
            type_lst.append(type)    
            base_control_rod_xml=doc.createElement("base_control_rod")
            base_control_rod_xml.setAttribute("cr_id","CR%d"%type)
            base_control_rod_xml.setAttribute("spider","0")
            base_componenet_xml.appendChild(base_control_rod_xml)

            axial_length_xml=doc.createElement("axial_length")
            axial_length_xml.appendChild(doc.createTextNode('400'))
            
            axial_type_xml=doc.createElement("axial_type")
            axial_type_xml.appendChild(doc.createTextNode(str(type)))
            base_control_rod_xml.appendChild(axial_length_xml)
            base_control_rod_xml.appendChild(axial_type_xml)
    
    file_dir=os.path.join(media_root,plant_name)   
    file_path=os.path.join(file_dir,'base_component.xml')
    try:
        os.makedirs(file_dir)
    except OSError:
        pass
    f = open(file_path,"w")
    doc.writexml(f,indent='  ',addindent='  ', newl='\n',)
    f.close()
    print('finished')
        
        
                
                
def generate_loading_pattern(plant_name,unit_num):
    plant=Plant.objects.get(abbrEN=plant_name)
    base_fuels=BaseFuel.objects.filter(plant=plant)
    unit=UnitParameter.objects.get(plant=plant,unit=unit_num)
    cycles=unit.cycles.all()
    reactor_model=unit.reactor_model
    reactor_positions=reactor_model.positions.all()
    basecore_id=reactor_model.name
    core_id=plant_name+'_U%d'%unit_num
    #start xml 
    doc = minidom.Document()
    loading_pattern_xml = doc.createElement("loading_pattern")
    loading_pattern_xml.setAttribute("basecore_ID",basecore_id)
    loading_pattern_xml.setAttribute("core_id",core_id)
    doc.appendChild(loading_pattern_xml)
    
    #control rod xml
    
    for cycle in cycles:
        control_rod_assembly_loading_patterns=cycle.control_rod_assembly_loading_patterns.all()
        if control_rod_assembly_loading_patterns:
            control_rod_xml=doc.createElement("control_rod")
            control_rod_xml.setAttribute("cycle",str(cycle.cycle))
            loading_pattern_xml.appendChild(control_rod_xml)
            
            map_xml=doc.createElement("map")
            control_rod_xml.appendChild(map_xml)
            cra_position_lst=[]
            for reactor_position in reactor_positions:
                cra_pattern=control_rod_assembly_loading_patterns.filter(reactor_position=reactor_position)
                if cra_pattern:
                    cra=cra_pattern.get().control_rod_assembly
                    type=cra.type
                    cra_position_lst.append('CR%d'%type)
                else:
                    cra_position_lst.append('0')
                    
            map_xml.appendChild(doc.createTextNode((' '.join(cra_position_lst))))
    
    #fuel xml
    for cycle in cycles: 
        fuel_lst=[]
        previous_cycle_lst=[]
        rotation_lst=[]
        for reactor_position in reactor_positions:
                fuel_assembly_loading_pattern=cycle.fuel_assembly_loading_patterns.get(reactor_position=reactor_position)
                bpa_patterns=cycle.bpa_loading_patterns.filter(reactor_position=reactor_position)
                fuel_assembly_type=fuel_assembly_loading_pattern.fuel_assembly.type
                
                #rotation
                rotation_degree=fuel_assembly_loading_pattern.rotation_degree
                if rotation_degree!='0':
                    rotation_lst.append([rotation_degree,reactor_position.row,reactor_position.column])
                    
                
                #not fresh
                if fuel_assembly_loading_pattern.get_previous():
                    [previous_cycle,previous_position_row,previous_position_column]=fuel_assembly_loading_pattern.get_previous().split('-')
                    position='{}{}'.format(previous_position_row.zfill(2), previous_position_column.zfill(2))
                    fuel_lst.append(position)
                    #not from last cycle
                    if previous_cycle!=cycle.cycle-1:
                        
                        previous_cycle_lst.append([previous_cycle,reactor_position.row,reactor_position.column])
                       
                
                #fresh       
                else:
                    if bpa_patterns:
                        bpa_pattern=bpa_patterns.get()
                        sysmetry_quadrant=bpa_pattern.get_sysmetry_quadrant()
                        bpa=bpa_pattern.burnable_poison_assembly
                        sub_bpa=bpa.get_substitute_bpa()
                        
                        #offset
                        if sub_bpa:
                            #contains bpa basefuel
                            bpa_ibis=Ibis.objects.get(plant=plant,fuel_assembly_type=fuel_assembly_type,burnable_poison_assembly=sub_bpa)
                            sub_base_fuel=bpa_ibis.base_fuels.get()
                            
                            #not contain bpa basefuel
                            fuel_ibis=Ibis.objects.get(plant=plant,fuel_assembly_type=fuel_assembly_type,burnable_poison_assembly=None)
                            fuel_base_fuels=fuel_ibis.base_fuels.all()
                            
                            for item in fuel_base_fuels:
                                if not item.if_insert_burnable_fuel():
                                    fuel_base_fuel=item
                                    
                            #reactor position quadrant
                            quadrant_lst=[] 
                              
                            for num in [1,2,3,4]:
                                if num in sysmetry_quadrant:
                                    quadrant_lst.append(sub_base_fuel)
                                else:
                                    quadrant_lst.append(fuel_base_fuel)
                                    
                            print(quadrant_lst,bpa_patterns)
    
                              
                            base_fuel=BaseFuel.objects.get(quadrant_one=quadrant_lst[0],quadrant_two=quadrant_lst[1],quadrant_three=quadrant_lst[2],quadrant_four=quadrant_lst[3])       
                                        
                                    
                                
                        else:
                            ibis=Ibis.objects.get(plant=plant,fuel_assembly_type=fuel_assembly_type,burnable_poison_assembly=bpa)
                            base_fuel=ibis.base_fuels.get()
                            
                        fuel_lst.append(base_fuel.fuel_identity)
                    else:
                        ibis=Ibis.objects.get(plant=plant,fuel_assembly_type=fuel_assembly_type,burnable_poison_assembly=None)
                        base_fuels=ibis.base_fuels.all()     
                        for base_fuel in base_fuels:
                            if not base_fuel.if_insert_burnable_fuel():
                                fuel_lst.append(base_fuel.fuel_identity)
                             
        
        fuel_xml = doc.createElement("fuel")
        fuel_xml.setAttribute("cycle",str(cycle.cycle))
        loading_pattern_xml.appendChild(fuel_xml)
        
        fuel_map_xml=doc.createElement("map")
        fuel_xml.appendChild(fuel_map_xml)
        fuel_map_xml.appendChild(doc.createTextNode((' '.join(fuel_lst))))
        
        #handle the fuel assembly not from last cycle
        for previous_cycle_info in previous_cycle_lst:
            if int(previous_cycle_info[0])!=cycle.cycle-1:
                
                cycle_xml=doc.createElement("cycle")
                cycle_xml.setAttribute('row',str(previous_cycle_info[1]))
                cycle_xml.setAttribute('col',str(previous_cycle_info[2]))
                cycle_xml.appendChild(doc.createTextNode(previous_cycle_info[0]))
                fuel_xml.appendChild(cycle_xml)
                
        
        #handle fuel assembly rotation
        for item in rotation_lst:
            rotation_xml=doc.createElement("rotation")
            rotation_xml.setAttribute('row',str(item[1]))
            rotation_xml.setAttribute('col',str(item[2]))
            rotation_xml.appendChild(doc.createTextNode(str(int(item[0])/90+1)))
            fuel_xml.appendChild(rotation_xml)
            
                
    file_dir=os.path.join(os.path.join(media_root,plant_name),'unit'+str(unit_num))
    file_path=os.path.join(file_dir,'loading_pattern.xml')
    try:
        os.makedirs(file_dir)
    except OSError:
        pass
    f = open(file_path,"w")
    doc.writexml(f,indent='  ',addindent='  ', newl='\n',)
    f.close()
    print('finished') 
    
def generate_base_core(plant_name,unit_num):
    plant=Plant.objects.get(abbrEN=plant_name)
    unit=plant.units.get(unit=unit_num)
    cycle=unit.cycles.get(cycle=1)
    reactor_model=unit.reactor_model
    reactor_positions=reactor_model.positions.all()
    basecore_id=reactor_model.name
    core_type=reactor_model.reactor_type 
    max_row=reactor_model.get_max_row_column()[0]
    fuel_pitch=reactor_model.fuel_pitch
    active_height=reactor_model.active_height
    #start xml 
    doc = minidom.Document()
    base_core_xml = doc.createElement("base_core")
    base_core_xml.setAttribute("ID",basecore_id)
    base_core_xml.setAttribute("core_type",core_type)
    doc.appendChild(base_core_xml)
    
    #PLANT DATA
    plant_data_xml = doc.createElement("plant_data")
    base_core_xml.appendChild(plant_data_xml)
    system_pressure=unit.primary_system_pressure
    rated_power=unit.thermal_power
    flowrate_inlet=unit.best_estimated_cool_mass_flow_rate
    coolant_volume=unit.coolant_volume
    
    system_pressure_xml = doc.createElement("system_pressure")
    system_pressure_xml.appendChild(doc.createTextNode(str(system_pressure)))
    plant_data_xml.appendChild(system_pressure_xml)
    
    rated_power_xml = doc.createElement("rated_power")
    rated_power_xml.appendChild(doc.createTextNode(str(rated_power)))
    plant_data_xml.appendChild(rated_power_xml)
    
    flowrate_inlet_xml = doc.createElement("flowrate_inlet")
    flowrate_inlet_xml.appendChild(doc.createTextNode(str(flowrate_inlet)))
    plant_data_xml.appendChild(flowrate_inlet_xml)
    
    coolant_volume_xml = doc.createElement("coolant_volume")
    coolant_volume_xml.appendChild(doc.createTextNode(str(coolant_volume)))
    plant_data_xml.appendChild(coolant_volume_xml)
    
    HZP_cool_inlet_temp=unit.HZP_cool_inlet_temp
    HFP_cool_inlet_temp=unit.HFP_cool_inlet_temp
    mid_power_cool_inlet_temp=unit.mid_power_cool_inlet_temp
    
    inlet_temperature_xml = doc.createElement("inlet_temperature")
    plant_data_xml.appendChild(inlet_temperature_xml)
    #tin xml
    HZP_tin_xml = doc.createElement("tin")
    HZP_tin_xml.appendChild(doc.createTextNode(str(HZP_cool_inlet_temp)))
    HZP_tin_xml.setAttribute('power', '0.0')
    inlet_temperature_xml.appendChild(HZP_tin_xml)
    
    
    mid_tin_xml = doc.createElement("tin")
    #handle QNPC_I specially
    if plant_name=='QNPC_I':
        mid_tin_xml.appendChild(doc.createTextNode('556.05'))
        mid_tin_xml.setAttribute('power', '0.15')
    else:  
        mid_tin_xml.appendChild(doc.createTextNode(str(mid_power_cool_inlet_temp)))
        mid_tin_xml.setAttribute('power', '0.5')
    inlet_temperature_xml.appendChild(mid_tin_xml)
    
    HFP_tin_xml = doc.createElement("tin")
    HFP_tin_xml.appendChild(doc.createTextNode(str(HFP_cool_inlet_temp)))
    HFP_tin_xml.setAttribute('power', '1.0')
    inlet_temperature_xml.appendChild(HFP_tin_xml)
    
    
    
    
    #core geometry
    core_geo_xml = doc.createElement("core_geo")
    core_geo_xml.setAttribute("num_side_asms",str(max_row))
    base_core_xml.appendChild(core_geo_xml)
    
    fuel_pitch_xml = doc.createElement("fuel_pitch")
    fuel_pitch_xml.appendChild(doc.createTextNode(str(fuel_pitch)))
    core_geo_xml.appendChild(fuel_pitch_xml)
    
    std_fuel_len_xml = doc.createElement("std_fuel_len")
    std_fuel_len_xml.appendChild(doc.createTextNode(str(active_height)))
    core_geo_xml.appendChild(std_fuel_len_xml)
    
    fuel_map_lst=[]
    for i in range(1,max_row+1):
        for j in range(1,max_row+1):
            fuel_position=reactor_model.positions.filter(row=i,column=j)
            if fuel_position:
                fuel_map_lst.append('1')
            else:
                fuel_map_lst.append('0')
    
    fuel_map_xml = doc.createElement("fuel_map")
    fuel_map_xml.appendChild(doc.createTextNode(' '.join(fuel_map_lst)))
    core_geo_xml.appendChild(fuel_map_xml)
    
    rcca_xml = doc.createElement("rcca")
    base_core_xml.appendChild(rcca_xml)  
    
    control_rod_cluster_lst=[]
    bank_id_lst=reactor_model.control_rod_clusters.all()

        
    for position in reactor_positions:
        control_rod_cluster=position.control_rod_cluster
        if control_rod_cluster:
            control_rod_cluster_lst.append(control_rod_cluster.cluster_name)
        else:
            control_rod_cluster_lst.append('0')
     
    index=1 
    for item in bank_id_lst:
        bank_id_xml=doc.createElement('bank_id')
        bank_id_xml.setAttribute('index', str(index))
        bank_id_xml.setAttribute('basez', str(item.basez))
        bank_id_xml.appendChild(doc.createTextNode(item.cluster_name))
        index+=1
        rcca_xml.appendChild(bank_id_xml) 
        
    map_xml=doc.createElement('map')
    map_xml.appendChild(doc.createTextNode(' '.join(control_rod_cluster_lst)))
    rcca_xml.appendChild(map_xml)
    
    step_size_xml=doc.createElement('step_size')
    step_size_xml.appendChild(doc.createTextNode(str(bank_id_lst[0].step_size)))
    rcca_xml.appendChild(step_size_xml)
    
    egret_calc_xml=doc.createElement('egret_calc')
    base_core_xml.appendChild(egret_calc_xml)
    if plant_name=='QNPC_I':
        calc_data={'subdivision':'2','num_radial_brs':'2','bot_br_size':'15.263','top_br_size':'15.263','fold_core':'1','axial_df':'0','axial_mesh':'15.3',
                   'cyclen_std_bu':'50.0 150.0 500.0 1000.0 2000.0 3000.0 5000.0 7000.0 10000.0 13000.0 16000.0 20000.0 24000.0 28000.0 ',
        }
    elif plant_name=='FJS':
        calc_data={'subdivision':'2','num_radial_brs':'2','bot_br_size':'19.251','top_br_size':'19.251','fold_core':'1','axial_df':'1','axial_mesh':'20.0',
                   'cyclen_std_bu':'50.0 150.0 500.0 1000.0 2000.0 3000.0 5000.0 7000.0 10000.0 13000.0 16000.0 20000.0 24000.0 28000.0 ',
        }  
    
    elif plant_name=='QNPC_II':
        calc_data={'subdivision':'2','num_radial_brs':'2','bot_br_size':'19.251','top_br_size':'19.251','fold_core':'1','axial_df':'1','axial_mesh':'20',
                   'cyclen_std_bu':'50.0 150.0 500.0 1000.0 2000.0 3000.0 5000.0 7000.0 10000.0 13000.0 16000.0 20000.0 24000.0 28000.0 ',
        }
        
    else:
        pass
    
    for key,value in calc_data.items():
        key_xml=doc.createElement(key)
        key_xml.appendChild(doc.createTextNode(value))
        egret_calc_xml.appendChild(key_xml)
        
    #reflector
    reflector_xml=doc.createElement('reflector')
    base_core_xml.appendChild(reflector_xml)
    
    if plant_name=='QNPC_I':
        reflector_data={'bot_br':'BR_BOT',
                        'top_br':'BR_TOP',
                        'radial_br':[('BR3  BR3  BR3  BR9  BR6  BR5  BR7  BR3  BR3  BR9  BR6  BR5  BR7  BR9',{'index':'1'}),
                                     ('BR4  BR4  BR4 BR10 BR12 BR11  BR8  BR4  BR4 BR10 BR12 BR11  BR8 BR10 BR12',{'index':'2'})]
        }
    elif plant_name=='FJS':
        reflector_data={'bot_br':'BR_BOT',
                        'top_br':'BR_TOP',
                        'radial_br':[('BR3  BR3  BR3  BR9  BR6  BR5  BR7  BR3  BR3  BR9  BR6  BR5  BR7  BR9  BR6 BR5',{'index':'1'}),
                                     ('BR4  BR4  BR4 BR10 BR12 BR11  BR8  BR4  BR4 BR10 BR12 BR11  BR8 BR10 BR12 BR11 BR8 ',{'index':'2'})]
        }
        
    elif plant_name=='QNPC_II':
        reflector_data={'bot_br':'BR_BOT',
                        'top_br':'''BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP
                        BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP
                        BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP
                        BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP
                        BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP
                        BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP
                        BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP BR_TOP
                        BR_TOP BR_TOP BR_TOP
                        BR_TOP BR_TOP BR_TOP''',
                        'radial_br':[('BR3  BR3  BR3  BR9  BR6  BR5  BR7  BR3  BR3  BR9  BR6  BR5  BR7  BR9 ',{'index':'1'}),
                                     ('BR4  BR4  BR4 BR10 BR12 BR11  BR8  BR4  BR4 BR10 BR12 BR11  BR8 BR10 BR12',{'index':'2'})]
        }  
    else:
        pass  
    
    for key,value in reflector_data.items():
        if type(value)==str:
            key_xml=doc.createElement(key)
            key_xml.appendChild(doc.createTextNode(value))
            reflector_xml.appendChild(key_xml)
        else:
            for item in value:
                key_xml=doc.createElement(key)
                key_xml.appendChild(doc.createTextNode(item[0]))
                try:
                    attr_dic=item[1]
                    for attr_key,attr_value in attr_dic.items():
                        key_xml.setAttribute(attr_key,attr_value)
                except:
                    pass
                
                reflector_xml.appendChild(key_xml)
                
    file_dir=os.path.join(os.path.join(media_root,plant_name),'unit'+str(unit_num))
    file_path=os.path.join(file_dir,'base_core.xml')
    try:
        os.makedirs(file_dir)
    except OSError:
        pass
    f = open(file_path,"w")
    doc.writexml(f,indent='  ',addindent='  ', newl='\n',)
    f.close()
    print('finished')
                
                
                
def multiple_loading_pattern(cycle):

    unit=cycle.unit
    plant=unit.plant
    
    #start xml 
    doc = minidom.Document()
    loading_pattern_xml = doc.createElement("loading_pattern")
    loading_pattern_xml.setAttribute("cycle_num",str(cycle.cycle))
    loading_pattern_xml.setAttribute("unit_num",str(unit.unit))
    loading_pattern_xml.setAttribute("plant_name",plant.abbrEN)
    doc.appendChild(loading_pattern_xml)
    
    #FUEL INFO 
    fuel_xml=doc.createElement('fuel')
    loading_pattern_xml.appendChild(fuel_xml)
    fuel_assembly_loading_patterns=cycle.fuel_assembly_loading_patterns.all()
    
    for item in fuel_assembly_loading_patterns:
        #position info
        fuel_position_xml=doc.createElement('position')
        fuel_xml.appendChild(fuel_position_xml)
        reactor_position=item.reactor_position
        row=reactor_position.row
        column=reactor_position.column
        fuel_position_xml.setAttribute('row', str(row))
        fuel_position_xml.setAttribute('column', str(column))
        
        #assembly info
        fuel_assembly_xml=doc.createElement('fuel_assembly')
        fuel_position_xml.appendChild(fuel_assembly_xml)
        fuel_assembly=item.fuel_assembly
        pk=fuel_assembly.pk
        type=fuel_assembly.type
        enrichment=type.assembly_enrichment
        fuel_assembly_xml.appendChild(doc.createTextNode(str(type.pk)))
        fuel_assembly_xml.setAttribute('id', str(pk))
        fuel_assembly_xml.setAttribute('enrichment', str(enrichment))
        #previous cycle info
        previous=item.get_previous()
        if previous:
            previous_xml=doc.createElement('previous')
            fuel_position_xml.appendChild(previous_xml)
            data=previous.split(sep='-') 
            previous_xml.setAttribute('row', data[1])
            previous_xml.setAttribute('column', data[2])
            previous_xml.appendChild(doc.createTextNode(data[0]))
            
        first=fuel_assembly.get_first_loading_pattern()
        first_cycle=first.cycle
        first_position=first.reactor_position
        first_xml=doc.createElement('first')
        fuel_position_xml.appendChild(first_xml)
        first_xml.setAttribute('row', str(first_position.row))
        first_xml.setAttribute('column', str(first_position.column))
        first_xml.appendChild(doc.createTextNode(str(first_cycle.cycle)))
    
    
    #BPA
    bpa_xml=doc.createElement('bpa')
    loading_pattern_xml.appendChild(bpa_xml)
    bpa_loading_patterns=cycle.bpa_loading_patterns.all()
    for item in bpa_loading_patterns:
        #position info
        bpa_position_xml=doc.createElement('position')
        bpa_xml.appendChild(bpa_position_xml)
        reactor_position=item.reactor_position
        row=reactor_position.row
        column=reactor_position.column
        bpa_position_xml.setAttribute('row', str(row))
        bpa_position_xml.setAttribute('column', str(column))
        
        #bpa info
        burnable_poison_assembly=item.burnable_poison_assembly
        burnable_poison_assembly_xml=doc.createElement('burnable_poison_assembly')
        bpa_position_xml.appendChild(burnable_poison_assembly_xml)
        rod_num=burnable_poison_assembly.get_poison_rod_num()
        rod_height=burnable_poison_assembly.get_poison_rod_height()
        burnable_poison_assembly_xml.setAttribute('id', str(burnable_poison_assembly.pk))
        burnable_poison_assembly_xml.setAttribute('height', str(rod_height))
        burnable_poison_assembly_xml.appendChild(doc.createTextNode(str(rod_num)))
    
    
    #CRA
    cra_xml=doc.createElement('cra')
    loading_pattern_xml.appendChild(cra_xml)
    cra_loading_patterns=cycle.control_rod_assembly_loading_patterns.all()
    for item in cra_loading_patterns:
        #position info
        cra_position_xml=doc.createElement('position')
        cra_xml.appendChild(cra_position_xml)
        reactor_position=item.reactor_position
        row=reactor_position.row
        column=reactor_position.column
        cra_position_xml.setAttribute('row', str(row))
        cra_position_xml.setAttribute('column', str(column))
        
        #cra info
        control_rod_assembly=item.control_rod_assembly
        control_rod_assembly_xml=doc.createElement('control_rod_assembly')
        cra_position_xml.appendChild(control_rod_assembly_xml)
        
        cluster_name=control_rod_assembly.cluster_name
        type=control_rod_assembly.type
        step_size=control_rod_assembly.step_size
        basez=control_rod_assembly.basez
        control_rod_assembly_xml.setAttribute('id', str(control_rod_assembly.pk))
        control_rod_assembly_xml.setAttribute('type', str(type))
        control_rod_assembly_xml.setAttribute('step_size', str(step_size))
        control_rod_assembly_xml.setAttribute('basez', str(basez))
        control_rod_assembly_xml.appendChild(doc.createTextNode(cluster_name))
    
    f = tempfile.TemporaryFile()
    doc.writexml(f,indent='  ',addindent='  ', newl='\n',)
    
    return f




def sum_fuel_node(*mlps):
    doc = minidom.Document()
    loading_pattern_xml=doc.createElement('loading_pattern')
    doc.appendChild(loading_pattern_xml)
    unit=mlps[0].cycle.unit
    reactor_model=unit.reactor_model
    reactor_positions=reactor_model.positions.all()
    basecore_id=reactor_model.name
    core_id=unit.plant.abbrEN+'_U%d'%(unit.unit)
    
    loading_pattern_xml.setAttribute("basecore_ID",basecore_id)
    loading_pattern_xml.setAttribute("core_id",core_id)
    
    #control rod xml

    for mlp in mlps:
        current_cycle=mlp.cycle
        control_rod_assembly_loading_patterns=current_cycle.control_rod_assembly_loading_patterns.all()
        if control_rod_assembly_loading_patterns:
            control_rod_xml=doc.createElement("control_rod")
            control_rod_xml.setAttribute("cycle",str(current_cycle.cycle))
            loading_pattern_xml.appendChild(control_rod_xml)
            
            map_xml=doc.createElement("map")
            control_rod_xml.appendChild(map_xml)
            cra_position_lst=[]
            for reactor_position in reactor_positions:
                cra_pattern=control_rod_assembly_loading_patterns.filter(reactor_position=reactor_position)
                if cra_pattern:
                    cra=cra_pattern.get().control_rod_assembly
                    type=cra.type
                    cra_position_lst.append('CR%d'%type)
                else:
                    cra_position_lst.append('0')
                    
            map_xml.appendChild(doc.createTextNode((' '.join(cra_position_lst))))
            
    #fuel xml
        fuel_node=mlp.generate_fuel_node()    
        loading_pattern_xml.appendChild(fuel_node) 
    return doc
    
def position_node_by_excel(cycle,row,column,position_or_type):
    '''
    cycle->current cycle object or previous cycle;
    row column-> current position;
    position_or_type->previous position(3_5),fresh fuel assembly type(pk);
    '''
    
    
    doc = minidom.Document()
    position_node = doc.createElement("position")
    position_node.setAttribute('row', str(row))
    position_node.setAttribute('column', str(column))
    
    fuel_assembly_node=doc.createElement("fuel_assembly")
    position_node.appendChild(fuel_assembly_node)
    
    
    try:
        #fresh
        type_id=int(position_or_type)
        
        fat=FuelAssemblyType.objects.get(pk=type_id)
        #first node
        first_node=doc.createElement("first")
        first_node.setAttribute('row', str(row))
        first_node.setAttribute('column', str(column))
        first_node.appendChild(doc.createTextNode(str(cycle.cycle)))
    except ValueError:
        [pre_row,pre_column]=position_or_type.split(sep='_')
       
        pre_falp=cycle.get_loading_pattern_by_pos(int(pre_row),int(pre_column))
       
        #previous node 
        previous_node=doc.createElement("previous")
        previous_node.setAttribute('row', pre_row)
        previous_node.setAttribute('column', pre_column)
        previous_node.appendChild(doc.createTextNode(str(cycle.cycle)))
        position_node.appendChild(previous_node)
       
        fa=pre_falp.fuel_assembly
        
            
        first_loading_pattern=fa.get_first_loading_pattern()
        first_positon=first_loading_pattern.reactor_position
        first_cycle=first_loading_pattern.cycle
        #firt node
        first_node=doc.createElement("first")
        first_node.setAttribute('row', str(first_positon.row))
        first_node.setAttribute('column', str(first_positon.column))
        first_node.appendChild(doc.createTextNode(str(first_cycle.cycle)))
        
        id=fa.pk
        
        fuel_assembly_node.setAttribute('id', str(id))
        fat=fa.type
        type_id=fat.pk
    
    position_node.appendChild(first_node)
    
    enrichment=fat.assembly_enrichment
    fuel_assembly_node.setAttribute('enrichment', str(enrichment))
    fuel_assembly_node.appendChild(doc.createTextNode(str(type_id)))
    
    return position_node
    


        
def get_same_group_users(user):
   
    user_lst=[] 
    groups=user.groups.all()
    for group in groups:
        for item in group.user_set.all():
            if item not in user_lst:
                user_lst.append(item)
                
    return user_lst
        
    

         
          
    
    
    
    
    
        
    
    

    
    
       
    
    
                            
            