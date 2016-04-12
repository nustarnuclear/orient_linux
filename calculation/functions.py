import os
from calculation.models import FuelAssemblyType
from xml.dom import minidom
from django.conf import settings
from tragopan.models import ControlRodCluster
media_root=settings.MEDIA_ROOT

def generate_base_core(unit):
    plant=unit.plant
    plant_name=plant.abbrEN
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
    zero_direction=reactor_model.set_zero_to_direction
    clockwise_increase=int(reactor_model.clockwise_increase)
    core_geo_xml.setAttribute("num_side_asms",str(max_row))
    core_geo_xml.setAttribute("zero_direction",zero_direction)
    core_geo_xml.setAttribute("clockwise_increase",str(clockwise_increase))
    base_core_xml.appendChild(core_geo_xml)
    #row column symbol
    row_symbol=reactor_model.row_symbol
    column_symbol=reactor_model.column_symbol
    letter_order=reactor_model.letter_order
    row_symbol_xml=doc.createElement("row_symbol")
    core_geo_xml.appendChild(row_symbol_xml)
    num_str=' '.join(map(str,range(1,max_row+1)))
    if row_symbol=='Number':
        row_symbol_xml.appendChild(doc.createTextNode(num_str))
    else:
        row_symbol_xml.appendChild(doc.createTextNode(letter_order))
    column_symbol_xml=doc.createElement("column_symbol")
    core_geo_xml.appendChild(column_symbol_xml)
    if column_symbol=='Number':
        column_symbol_xml.appendChild(doc.createTextNode(num_str))
    else:
        column_symbol_xml.appendChild(doc.createTextNode(letter_order))
        
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
    
    #bank_id_lst=reactor_model.control_rod_clusters.all()
  
    for position in reactor_positions:
        control_rod_cluster=position.control_rod_cluster
        if control_rod_cluster:
            control_rod_cluster_lst.append(control_rod_cluster.cluster_name)
        else:
            control_rod_cluster_lst.append('0')
     
    index=1 
    for control_rod_cluster in ControlRodCluster.objects.all():
        if control_rod_cluster.reactor_model==reactor_model:
            bank_id_xml=doc.createElement('bank_id')
            bank_id_xml.setAttribute('index', str(index))
            bank_id_xml.setAttribute('basez', str(control_rod_cluster.basez))
            bank_id_xml.appendChild(doc.createTextNode(control_rod_cluster.cluster_name))
            index+=1
            rcca_xml.appendChild(bank_id_xml) 
        
    map_xml=doc.createElement('map')
    map_xml.appendChild(doc.createTextNode(' '.join(control_rod_cluster_lst)))
    rcca_xml.appendChild(map_xml)
    
    step_size_xml=doc.createElement('step_size')
    step_size_xml.appendChild(doc.createTextNode(str(reactor_model.control_rod_step_size)))
    rcca_xml.appendChild(step_size_xml)
    
    default_step_xml=doc.createElement('default_step')
    default_step_xml.appendChild(doc.createTextNode(str(reactor_model.default_step)))
    rcca_xml.appendChild(default_step_xml)
    
    max_step_xml=doc.createElement('max_step')
    max_step_xml.appendChild(doc.createTextNode(str(reactor_model.max_step)))
    rcca_xml.appendChild(max_step_xml)
    
    
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
                
    unit_dir=unit.unit_dir
    file_path=os.path.join(unit_dir,'base_core.xml')
    try:
        os.makedirs(unit_dir)
    except OSError:
        pass
    f = open(file_path,"w")
    doc.writexml(f,indent='  ',addindent='  ', newl='\n',)
    f.close()
                
                

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
        
    

         
          
    
    
    
    
    
        
    
    

    
    
       
    
    
                            
            