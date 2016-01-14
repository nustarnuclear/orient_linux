#function that handle the transformation between weight and mole
from decimal import Decimal,InvalidOperation
from .models import FuelAssemblyType,FuelElementTypePosition,FuelElementType,Plant,Cycle,FuelAssemblyLoadingPattern,FuelAssemblyRepository,UnitParameter,WimsNuclideData,WmisElementComposition,WmisElementData,BasicMaterial
import os
import re
import io
from builtins import zip
from xml.dom import minidom

def generate_assembly_position(number=17):
    positions=[]
    for i in range(1,number*number+1):
        md=i%number
        if md ==0:
            column=number
        else:
            column=md
        row=(i-column)/number+1
        positions.append([round(row),column])
    return positions 
def get_U_enrichment(u):
    u234=round(1.036*u-0.449,5)
    u236=round(0.0201*u+0.0459,5)
    u238=100-round(u234+u236+u,5)
    return [u,u234,u236,u238]

def add_fuel_assembly_type(id1,id2):
    '''id1 represent the fuel assembly type,
    id2 represent the fuel element type'''
    
    #get the fuel assembly type
    ft=FuelAssemblyType.objects.get(pk=id1)
    #get the fuel assembly model
    fm=ft.model
    #get the fuel position
    fp=fm.positions.filter(type='fuel')
    #get the fuel element type
    fe=FuelElementType.objects.get(pk=id2)
    for position in fp:
        ftp=FuelElementTypePosition(fuel_assembly_type=ft,fuel_assembly_position=position,fuel_element_type=fe)
        ftp.save()
    
def add_fuel_assembly_repository(id1,id2,num):
    '''id1 represent the fuel assembly type;
    id2 represent the plant;num represent the number of fuel assembly you want to add '''
    #get the fuel assembly type
    ft=FuelAssemblyType.objects.get(pk=id1)
    #get the plant
    pl=Plant.objects.get(pk=id2)
    
    for i in range(num):
        far=FuelAssemblyRepository(type=ft,plant=pl)
        far.save()
        
def add_cycle_position(id):
    '''id represent the cycle;'''
    #get the cycle
    cy=Cycle.objects.get(pk=id)
    #get the reactor model
    rm=cy.unit.reactor_model
    #get the reactor model positions 
    positions=rm.positions.all()
    for position in positions:
        falp=FuelAssemblyLoadingPattern(cycle=cy,reactor_position=position)
        falp.save()
        
def fuel_assembly_loading_pattern(id,filename):
    '''id represent the cycle;'''
    #get the fuel assembly loading pattern corresponding to the cycle
    falps=FuelAssemblyLoadingPattern.objects.filter(cycle_id=id)
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR=os.path.join(BASE_DIR, 'data')
    FILE_PATH=os.path.join(DATA_DIR,filename+'.txt')
    f=open(FILE_PATH,'r')
    num_lst=f.read().split()
    #the number in num represent the fuel assembly id
    num=[int(i) for i in num_lst ]
    f.close()
    for i in range(len(num)):
        #get the fuel assembly
        fa=FuelAssemblyRepository.objects.get(pk=num[i])
        falp=falps[i]
        falp.fuel_assembly=fa
        falp.save()
        
        
def generate_relative_position(plant_id,unit_num,cycle_id,*ids):
    '''ids represent all the fresh assembly start id'''
    #get the plant
    p=Plant.objects.get(pk=plant_id)
    #get the unit
    u=p.unitparameter_set.filter(unit=unit_num).get()
    #get the reactor model
    rm=u.reactor_model
    #get the fuel assembly loading pattern corresponding to the cycle
    falps=FuelAssemblyLoadingPattern.objects.filter(cycle_id=cycle_id)
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR=os.path.join(os.path.join(BASE_DIR, 'data'),'position')
    FILE_PATH=os.path.join(DATA_DIR,str(plant_id)+'-'+str(unit_num)+'-C'+str(cycle_id)+'.txt')
    f=open(FILE_PATH,'r')
    x=f.read().split()
    y=[]
    index=[0 for i in range(len(ids))]
    for i in range(len(x)):
        lst=x[i].split('_')
        if len(lst)!=2:
            lst.append(cycle_id-1)
            
        if lst[0].upper() !='NEW':
            row=ord(lst[0][0])
            if row<73:
                row -=64
            else:
                row -=65
                
            column=int(lst[0][1:3])
            pre_cycle=Cycle.objects.get(pk=int(lst[1]))
            position_num=rm.positions.filter(row=row,column=column).get()
            pattern=FuelAssemblyLoadingPattern.objects.filter(cycle=pre_cycle,reactor_position=position_num).get()
            assembly_num=pattern.fuel_assembly.pk
            result=assembly_num
        else:
            start_id=ids[int(lst[1])-1]
            interval=index[int(lst[1])-1]
            index[int(lst[1])-1] +=1
            result=start_id+interval
                 
        y.append(result)
    
    for i in range(len(y)):
        #get the fuel assembly
        fa=FuelAssemblyRepository.objects.get(pk=y[i])
        falp=falps[i]
        falp.fuel_assembly=fa
        falp.save()
        
    f.close()
    return y 

def count_fresh_num(plant_id,unit_num,cycle_id,num):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR=os.path.join(os.path.join(BASE_DIR, 'data'),'position')
    FILE_PATH=os.path.join(DATA_DIR,str(plant_id)+'-'+str(unit_num)+'-C'+str(cycle_id)+'.txt')
    f=open(FILE_PATH,'r')
    x=f.read().split()
    index=[0 for i in range(num)]
    
    for i in range(len(x)):
        lst=x[i].split('_')
        if lst[0].upper() =='NEW':
            index[int(lst[1])-1] +=1
    print(index)
    f.close()
    return index

def map_to_position(plant,unit):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR=os.path.join(os.path.join(os.path.join(BASE_DIR, 'data'),plant),unit)
    FILE_PATH=os.path.join(DATA_DIR,'c1.txt')
    f=open(FILE_PATH)
    t=f.read()
    s=t.split(sep='\n')
    
    positions=[]
    for i in range(len(s)):
        p=s[i].split(sep='\t')
        row=i+1
        for j in range(len(p)):
            try:
                int(p[j])
                column=j+1
                positions.append([row,column])
            except ValueError:
                pass
    f.close()   
    return positions

        
        
def add_wmis_nuclide_data(filename):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR=os.path.join(BASE_DIR, 'data')
    FILE_PATH=os.path.join(DATA_DIR,filename)
    print(FILE_PATH)
    f=open(FILE_PATH)
    t=f.read()
    print(t)
    s=t.split(sep='\n')
    print(s)
    
    for i in s:
        tmp=i.split()
        id_wims=int(tmp[1])
        wn=WimsNuclideData.objects.get(id_wims=id_wims)
        wn.id_self_defined=int(tmp[0])
        wn.save()
    
    
def add_wmis_element_data(filename):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR=os.path.join(BASE_DIR, 'data')
    FILE_PATH=os.path.join(DATA_DIR,filename)
    f=open(FILE_PATH)
    t=f.read()
    
    s=t.split()
    for i in range(len(s)):
        try:
            Decimal(s[i])
        except:
            name=s[i]
            try:
                obj=WmisElementData.objects.get(element_name=name)
            except:
                obj=WmisElementData(element_name=name)
                obj.save()
                
            num=int(s[i+1])
            for j in range(i+1,i+1+2*num):
                if j%2==0:
                    wn=WimsNuclideData.objects.get(id_self_defined=int(s[j]))
                    wp=Decimal(s[j+1])*100
                    we=WmisElementComposition(wmis_element=obj,wmis_nuclide=wn,weight_percent=wp)
                    we.save()
                    print(we)
        
    print(s)
    
def add_cycle(filename,plantname,unit_num):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR=os.path.join(BASE_DIR, 'data')
    FILE_PATH=os.path.join(DATA_DIR,filename)
    f=open(FILE_PATH)
    t=f.read()
    s=t.split(sep='/')
    lst=[]
    print(s)
    

    for item in s:
        value=item.split()
        lst.append(value)

    for i in range(len(lst)):
        for j in range(len(lst[i])):
            pos=lst[i][j]
            try:
                lst[i][j]=int(pos)
            except ValueError:
                tmp=pos.split('_')
                if len(tmp)!=2:
                    tmp.append(i)
                    
                cycle=int(tmp[1])
                
                if plantname=='QNPC_II':
                    row=ord(tmp[0][0])
                    if row<73:
                        row -=64
                    else:
                        row -=65
                        
                    column=int(tmp[0][1:3])
                elif plantname=='QNPC_I':
                    row=int(tmp[0][1:3])
                    num_dic={'N':1,'M':2,'L':3,'K':4,'J':5,'H':6,'G':7,'F':8,'E':9,'D':10,'C':11,'B':12,'A':13}
                    column=num_dic[tmp[0][0]]
                elif plantname=='FJS':
                    row=int(tmp[0][1:3])
                    num_dic={'R':1,'P':2,'N':3,'M':4,'L':5,'K':6,'J':7,'H':8,'G':9,'F':10,'E':11,'D':12,'C':13,'B':14,'A':15}
                    column=num_dic[tmp[0][0]]
                else:
                    pass
                lst[i][j]=[cycle,row,column]
    f.close()

    plant=Plant.objects.get(abbrEN=plantname)
    unit=UnitParameter.objects.get(plant=plant,unit=unit_num)
    reactor_model=unit.reactor_model
    reactor_positions=reactor_model.positions.all()
    pos_lst=[]
    for reactor_position in reactor_positions:
        pos_lst.append([reactor_position.row,reactor_position.column])
        
    print(pos_lst)
    print(len(pos_lst))
    print(reactor_positions)
    
    for i in range(len(lst)):
        cycle_num=i+1
        cycle=Cycle.objects.get_or_create(unit=unit,cycle=cycle_num)[0]
        
        for j in range(len(lst[i])):
            pattern=lst[i][j]
            position=reactor_positions[j]
            print(position)
            #FRESH
            if type(pattern)==int:
                fuel_assembly_type=FuelAssemblyType.objects.get(pk=pattern)
                fuel_assembly=FuelAssemblyRepository.objects.create(type=fuel_assembly_type,plant=plant)
                fuel_assembly_loading_pattern=FuelAssemblyLoadingPattern.objects.create(cycle=cycle,reactor_position=position,fuel_assembly=fuel_assembly)
            else:
                previous_cycle_num=pattern[0]
                previous_cycle_row=pattern[1]
                previous_cycle_column=pattern[2]
                previous_cycle=Cycle.objects.get(unit=unit,cycle=previous_cycle_num)
                previous_position=reactor_positions.filter(row=previous_cycle_row,column=previous_cycle_column).get()
                previous_pattern=FuelAssemblyLoadingPattern.objects.get(cycle=previous_cycle,reactor_position=previous_position)
                previous_fuel_assembly=previous_pattern.fuel_assembly
                fuel_assembly_loading_pattern=FuelAssemblyLoadingPattern.objects.create(cycle=cycle,reactor_position=position,fuel_assembly=previous_fuel_assembly)
                
            
    return lst







###########################################################################################################
#class to handle monthly operation data
class OperationDataHandler:
    
    def __init__(self,plant_name,unit_num,cycle_num,core_max,filepath):
        self.plant_name=plant_name
        self.unit_num=unit_num
        self.cycle_num=cycle_num
        self.filepath=filepath
        self.core_max=core_max
        
        
    @property   
    def line_lst(self):
        if self.plant_name=="QNPC_I":
            f=open(self.filepath,encoding='GB2312')
        else:
            f=open(self.filepath)
        line_lst=f.readlines()
        f.close()
        return line_lst
    
    @property
    def start_index_pattern(self):
        if self.plant_name in ('FJS','QNPC_II'):
            basic_core_state_pattern=re.compile('Power Plant')
            power_start_pattern=re.compile('RADIAL MAP OF 3D POWER INTEGRATED OVER THE ACTIVE CORE HEIGHT AND ESTIMATED BY')
            AO_start_pattern=re.compile('RADIAL MAP OF ASSEMBLIES MEAN POWER \(PDH\) AND AXIAL OFFSET')
            FDH_start_pattern=re.compile('RADIAL MAP OF THE MAXIMUM ESTIMATED FUEL ROD POWER AND THE C/R DEVIATIONS')
            date_pattern=re.compile('created on')
            bank_position_pattern=re.compile('Banks position')
            core_FQ_pattern=re.compile('LOCAL MAXIMUM POWER LEVEL')
            core_AO_pattern=re.compile('AND AN AXIAL-OFFSET OF')
            
        
        if self.plant_name=='QNPC_I':
            basic_core_state_pattern=re.compile('Qinshan Nuclear Power Plant Cycle')
            power_start_pattern=re.compile('MEASURED AND PREDICTED ASSEMBLY POWER')
            AO_start_pattern=None
            FDH_start_pattern=re.compile('MEASURED AND EXPECTED HOT ROD F-DELTA-H')
            date_pattern=re.compile('Input File')
            bank_position_pattern=re.compile('5B')
            core_FQ_pattern=None
            core_AO_pattern=re.compile('CORE AVERAGE')
            
        
        return (basic_core_state_pattern,power_start_pattern,AO_start_pattern,FDH_start_pattern,date_pattern,bank_position_pattern,core_FQ_pattern,core_AO_pattern)
            
    @property
    def basic_core_state(self):
        '''
        date,unit_num,cycle_num,avg_burnup,relative_power,boron_concentration
        '''
        line_num=0
        line_lst=self.line_lst
        basic_core_state_pattern=self.start_index_pattern[0]
        date_pattern=self.start_index_pattern[4]
        
            
        
        for line in line_lst:
            line_num +=1
            if self.plant_name in ('FJS','QNPC_II'):
                #handle date
                if date_pattern.search(line): 
                  
                    date=line.split(sep=':')[1].split()[0].replace('/','-')
                    
                
                    
                #handle core state
                if basic_core_state_pattern.search(line):
                    basic_core_state_lst=line.split()
                    
                    [unit_num,cycle_num]=[int(i) for i in basic_core_state_lst if i.isdigit()][:2]
                    #process to next line
                    next_line=line_lst[line_num].split()
                    decimal_lst=[]
                    for item in next_line:
                        try:
                            decimal_lst.append(Decimal(item))
                        except InvalidOperation:
                            pass
                    [avg_burnup,relative_power,boron_concentration]=decimal_lst[:3]
                            
                            
                    
                
            elif self.plant_name=='QNPC_I':
                if date_pattern.search(line):
                    date=line.split(sep=':')[1].split(sep='.')[0].strip()
                
                unit_num=1
                
                avg_burnup=None
                
                if basic_core_state_pattern.search(line):
                    core_state_data=line.split(sep=":")
                    print(core_state_data)
                    cycle_num=int(core_state_data[0].split(sep="-")[-1])
                    relative_power=Decimal(core_state_data[1].split()[0].strip('%FP'))/100
                    boron_concentration=Decimal(core_state_data[2].split()[0].strip('ppm'))
                    break
                
        return (date,unit_num,cycle_num,avg_burnup,relative_power,boron_concentration)
                    
            
    @property
    def core_AO(self):
        line_lst=self.line_lst
        core_AO_pattern=self.start_index_pattern[7]
        if self.plant_name in ('FJS','QNPC_II'):
            
            for line in line_lst:
                if core_AO_pattern.search(line):
                    core_AO= Decimal(line.split()[-2])
                    break
        
        elif self.plant_name=='QNPC_I':
            index=0
            for line in line_lst:
                if core_AO_pattern.search(line):
                    core_AO=Decimal(line_lst[index+5].split()[-1])  
                    break 
                index +=1
        
        return  core_AO      
    
    @property
    def core_FQ(self):
        if self.plant_name in ('FJS','QNPC_II'):
            line_lst=self.line_lst
            core_FQ_pattern=self.start_index_pattern[6]
            for line in line_lst:
                if core_FQ_pattern.search(line):
                    return Decimal(line.split(sep=':')[1].split()[0])
                
        elif self.plant_name=='QNPC_I':
            return None
               
            
    def get_bank_position(self):  
        #handle bankposition   
        line_lst=self.line_lst
        bank_position_result={} 
        bank_position_pattern=self.start_index_pattern[5] 
        if self.plant_name in ('FJS','QNPC_II'):
            for line in line_lst:
                if bank_position_pattern.search(line):
                    line_splitted_lst=[]
                    for item in line.split(sep=':'):
                        line_splitted_lst +=item.split()
                        
                    for i in range(len(line_splitted_lst)):
                        try:
                            step=Decimal(line_splitted_lst[i])
                            name=line_splitted_lst[i-1]
                            bank_position_result[name]=step
                        except InvalidOperation:
                            pass  
            
            
        elif self.plant_name=='QNPC_I':
            for line in line_lst:
                if bank_position_pattern.search(line):
                    line_splitted_lst=line.split()[:6]
                    print(line_splitted_lst)
                    rod_name=['T1','T2','T3','T4','A1','A2']
                    for item in zip(rod_name,line_splitted_lst):
                        bank_position_result[item[0]]=Decimal(item[1])
                        
        return bank_position_result           
    
    def check_file_format(self):
        basic_core_state=self.basic_core_state
        if self.unit_num==basic_core_state[1] and self.cycle_num==basic_core_state[2]:
            return True
        else:
            return False
      
    def search_index_num(self,type):
        '''
        1: power;
        2:AO;
        3:FDH;
        '''
        line_num=0
        
        for line in self.line_lst:
            line_num+=1
            
            index=self.start_index_pattern[type]
        
            if re.search(index,line):
                return line_num-1
                
    def parse_distribution_data(self,type):
        '''
        1: power;
        2:AO;
        3:FDH;
        '''
        line_lst=self.line_lst
        index_num=self.search_index_num(type)
        num_pattern=re.compile('^[1-9]+')
        current_result=[]
        beside_result=[]
        while index_num:
            item=line_lst[index_num]
            index_num +=1
            
            
            
            splitted_lst=item.split(sep='|')
          
            first_element=splitted_lst[0].strip()
            #to find the row
            if num_pattern.match(first_element):
                row=int(first_element) 
                print(splitted_lst)
                for rp in splitted_lst[1:-1]:
                    try:   
                        current_result.append(Decimal(rp))
                    except InvalidOperation:
                        pass
                
                if self.plant_name in ('FJS','QNPC_II'):
                    shift=0
                    
                elif self.plant_name=='QNPC_I':
                    shift=-2
                    
                beside_splitted_lst=line_lst[index_num+shift].split(sep='|')
                for rp in beside_splitted_lst[1:-1]:
                    try:
                        beside_result.append(Decimal(rp))
                    except InvalidOperation:
                        pass  
               
                    
                if row==self.core_max:
                    break
                index_num += 1          
        return (current_result,beside_result)
    
    
################################################################################
#pre robin functions
def format_line(lst,width=16):
    result_lst=[]
    for item in lst:
        blank_num=width-len(str(item))
        result_lst.append(str(item)+' '*blank_num)
    result_lst.append('\n')
    return ''.join(result_lst)     
    
    
def generate_material_lib(dir='/home/django/Desktop/material_element.lib'):
    f=open(dir,'w')
    #write general info
    general_descrip=['nuclides','elements','compounds','mixtures']
    f.write(format_line(general_descrip))
    
    nuclide_num=WimsNuclideData.objects.count()
    element_num=WmisElementData.objects.count()
    compound_num=BasicMaterial.objects.filter(type=1).count()
    mixture_num=BasicMaterial.objects.filter(type=2).count()
    f.write(format_line([nuclide_num,element_num,compound_num,mixture_num]))
    f.write('\n')
    #write nuclides info
    nuclide_descrip=['isotope','ID in lib','amu','res_trig','dep_trig']
    f.write(format_line(nuclide_descrip))
    for item in WimsNuclideData.generate_nuclide_lib():
        f.write(format_line(item))
    f.write('\n')    
    
    #write elements info
    f.write('elements:\n')
    for element in WmisElementData.objects.all():
        element_descrip=[element.element_name,element.get_nuclide_num()]
        f.write(format_line(element_descrip))
        for compo in element.nuclides.all():
            nuclide_info=[' ',compo.wmis_nuclide.pk,compo.weight_percent/100] 
            f.write(format_line(nuclide_info))
    f.write('\n')        
    #write compounds info
    f.write('compounds:\n')
    for compound in BasicMaterial.objects.filter(type=1):
        compound_descrip=[compound.name,compound.get_element_num(),compound.density]
        f.write(format_line(compound_descrip))
        for compo in compound.elements.all():
            element_info=[' ',compo.wims_element.element_name,compo.weight_percent/100 if compo.weight_percent else compo.element_number]
            f.write(format_line(element_info))
    f.write('\n') 
    
    #write mixture info
    f.write('mixtures:\n')
    for mixture in BasicMaterial.objects.filter(type=2):
        mixture_descrip=[mixture.name,mixture.get_element_num(),mixture.density]
        f.write(format_line(mixture_descrip))
        for compo in mixture.elements.all():
            element_info=[' ',compo.wims_element.element_name,compo.weight_percent/100 if compo.weight_percent else compo.element_number]
            f.write(format_line(element_info))
    f.write('\n')
           
    f.close()
    
#####################################################################
#SREAD format file handler
class SreadNode(object):
    def __init__(self,tagName,value=None,childNodes=[]):
        self.tagName=tagName
        self.childNodes=childNodes
        self.value=value
        
        
    def tosread(self,indent="\t", newl="\n",):
        writer = io.StringIO()
        self.writesread(writer, "", indent, newl)
        
    def writesread(self,writer, indent="", newl=""):
        if self.value is not None:
            writer.write(indent+self.tagName+':'+newl)
            writer.write(indent+'/',+self.tagName+newl)
        else:
            writer.write("{}{} = {}{}".format(indent,self.tagName,self.value,newl))
           
    def appendChild(self, node):
        self.childNodes.append(node)

class Sread_doc(object):
    def __init__(self,rootNode):
        self.rootNode=rootNode

def xml_to_sread(filepath='/home/django/Desktop/material_databank.xml'):
    #parse xml
    dom=minidom.parse(filepath)
    root_element=dom.documentElement
    root_name=root_element.tagName
    
    doc=Sread_doc()
    #create root node
    Sroot_node=SreadNode(root_name)
    
    root_childNodes=root_element.childNodes
    
    for childNode in root_childNodes:
        name=childNode.tagName
        firstChild=childNode.firstChild
        #when first child node is text
        if firstChild.nodeType==firstChild.TEXT_NODE:
            value=firstChild.data
            Schild_node=SreadNode(tagName=name,value=value)
        else:
            Schild_node(tagName=name)
        Sroot_node.appendChild(Schild_node)   
        
        
def generate_child_nodes(element):  
    for childNode in element.childNodes:
    
        grand_child=childNode.firstChild
        #if grand child is a text, show that it reach the final cycle
        if grand_child.nodeType==grand_child.TEXT_NODE:
            lable_name=element.tagName
            Slable_node=SreadNode(lable_name)
            
            
            name=childNode.tagName
            value=childNode.firstChild.data
            Schild_node=SreadNode(tagName=name,value=value)
            Slable_node.appendChild(Schild_node)
        
    #recursion    
    else:
        for item in element.childNodes: 
            generate_child_nodes(item)
            
from rest_framework_xml.parsers import XMLParser            
class MyXMLParser(XMLParser):
    
    def __init__(self,list_item='list-item'):
        self.list_item=list_item
        
    def _xml_convert(self, element):
        """
        convert the xml `element` into the corresponding python object
        """

        children = list(element)

        if len(children) == 0:
            return self._type_convert(element.text)
        else:
            # if the fist child tag is list-item means all children are list-item
            if children[0].tag == self.list_item:
                data = []
                for child in children:
                    data.append(self._xml_convert(child))
            else:
                data = {}
                for child in children:
                    data[child.tag] = self._xml_convert(child)

            return data
            
def parse_xml_to_lst(path='/home/django/Desktop/material_databank.xml'):
    f=open(path)
    line_lst=f.readlines()
    f.close()
    title=re.compile('<\?.*\?>')
    start=re.compile('<.*>')
    end=re.compile('</.*>')
    total=re.compile('<.*>.*</.*>',re.DOTALL)
    result_lst=[]
    for i in range(len(line_lst)):
        line=line_lst[i]
        
        #this is a tile 
        if title.search(line):
            continue
        #this is a end element
        end_element=end.search(line)  
        if end_element:
            matched=end_element.group(0)
            if re.search(matched.replace('/',''), result_lst[-1]):
                result_lst[-1] +=line
            else:
                result_lst.append(line)
                
            continue    
        #this is a start element
        if start.search(line):
            result_lst.append(line)
            continue
        #this is a context    
        else:
            result_lst[-1] +=line
            
    index=0
    for i in range(len(result_lst)):
        line=result_lst[i]
        split_lst=re.split('[<>]', line)
        print(split_lst)
        if total.search(line):
            assert(len(split_lst)==5)
            result_lst[i]='  '*index+split_lst[1]+' = '+split_lst[2]+'\n'
        else:
            if split_lst[1].startswith('/'):
                index -=1
                result_lst[i]='  '*index+split_lst[1]+'\n'
            else:
                result_lst[i]='  '*index+split_lst[1]+':'+'\n'
                index +=1
                 
    sfile=open('/home/django/Desktop/material_databank.txt','w')
    sfile.writelines(result_lst)
    sfile.close()
        
        
        
def generate_one_eighth_pos(side_num=17):
    half=int(side_num/2)+1
    
    for row in range(half,side_num+1):
        for col in range(half,row+1):
            yield (row,col)
    