# classes

from de_embedding.load_data import load_example

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def CreateDict_TRL(dut_embedding,thru,line,reflect1,reflect2,example=True):

    #initizalition: 
    dut_full = dut_embedding
    p_thru = thru
    p_line = line
    p_reflect1 = reflect1 
    p_reflect2 = reflect2 

    #-------------------------------------------------------------------------------------------------
    #1) load data:
    if example:
        
        path_dut_full = load_example(dut_full)
        
        path_thru = load_example(p_thru)
        path_line_1 = load_example(p_line) # Short Line - line lambda/4
        path_reflect_1 = load_example(p_reflect1)
        path_reflect_2 = load_example(p_reflect2)
    else: 
        
        path_dut_full = dut_full        
        path_thru = p_thru
        path_line_1 = p_line # Short Line - line lambda/4
        path_reflect_1 = p_reflect1
        path_reflect_2 = p_reflect2


    #-------------------------------------------------------------------------------------------------
    # 2) Create Dictionary:

    dic_data = {
        'dut_full':path_dut_full,
        'standard-reflect':'open',
        'thru':path_thru,
        'line_l1':path_line_1,
        'reflect_port_1':path_reflect_1,
        'reflect_port_2':path_reflect_2
    }

    return dic_data

#----------------------------------------------------------------------------------------------------

def CreateDict_TVRL(dut_embedding,thru,line,reflect='open',example=True):

    #initizalition: 
    dut_full = dut_embedding
    p_thru = thru
    p_line = line
    c_reflect = reflect

    #------------------------------------------------------------------------------------------------
    #1) load data:
    if example:      
        
        path_dut_full = load_example(dut_full)        
        path_thru = load_example(p_thru)
        path_line_1 = load_example(p_line) # Short Line - line lambda/4

    else: 
        path_dut_full = dut_full
        path_thru = p_thru
        path_line_1 =  p_line



    #-------------------------------------------------------------------------------------------------
    # 2) Create Dictionary:

    dic_data = {
        'dut_full':path_dut_full,
        'standard-reflect-virtual':c_reflect,
        'thru':path_thru,
        'line_l1':path_line_1,

    }

    return dic_data

#-------------------------------------------------------------------------------------------------------------
def CreateDict_LL(dut_embedding,thru,line1,line2,len_line1= 0.006495 + 0.03,len_line2= 0.010495 + 0.03,len_dut= 0.015,example=True):

    #initizalition: 
    dut_full = dut_embedding
    p_thru = thru
    p_line1 = line1
    p_line2 = line2
    l_line1 = len_line1
    l_line2 = len_line2
    l_dut = len_dut
    

    #-------------------------------------------------------------------------------------------------
    #1) load data:
    if example:
        
        path_dut_full = load_example(dut_full)

        path_thru = load_example(p_thru)
        path_line_1 = load_example(p_line1)# Short Line - line lambda/4
        path_line_2 = load_example(p_line2) 
    else: 
        
        path_dut_full = dut_full       
        path_thru = p_thru
        path_line_1 = p_line1# Short Line - line lambda/4
        path_line_2 = p_line2 


    #-------------------------------------------------------------------------------------------------
    # 2) Create Dictionary:

    dic_data = {
        'dut_full':path_dut_full,
        'thru':path_thru,
        'line_l1':path_line_1,
        'line_l2': path_line_2,
        'length_line_1' : l_line1,
        'length_line_2' : l_line2,
        'length_line_dut' : l_dut

    }


    return dic_data
