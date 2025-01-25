
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#libraries 
import matplotlib.pyplot as plt 
import itertools
import copy
import numpy as np 
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Configuración global para matplotlib
plt.rc('font', size=17)  # Tamaño de fuente general
plt.rc('axes', titlesize=22, labelsize=22)  # Tamaño de fuente para títulos y etiquetas de los ejes
plt.rc('xtick', labelsize=22)  # Tamaño de fuente para las etiquetas del eje x
plt.rc('ytick', labelsize=22)  # Tamaño de fuente para las etiquetas del eje y
plt.rc('lines', linewidth=2.5)  # Grosor de las líneas
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def s_parameters_db_deg_unwrap(*network_pairs,enable_cut=False,cut_range = '0.5-6ghz'):

     # Configuramos la unidad de frecuencia para todas las redes
    for ntwk, _ in network_pairs:
        ntwk.frequency.unit = 'ghz'
        
    
    # Definimos los parámetros S a graficar
    s_params = [(0, 0), (1, 0), (0, 1), (1, 1)]
    titles = ['S11', 'S21', 'S12', 'S22']

    line_styles = ['-','-.', '--', ':']   
    marker_styles = ['o','X','v','D'] #['o','X','v']  
    #marker_styles = ['o','X','v','D','|']
    size_styles = [4, 4]
    color_styles_db = ['purple', 'darkorange', 'olivedrab']
    color_styles_deg = ['purple', 'darkorange', 'olivedrab']
    line_cycle = itertools.cycle(line_styles)
    marker_cycle = itertools.cycle(marker_styles)
    size_cycle = itertools.cycle(size_styles)
    color_cycle_db = itertools.cycle(color_styles_db)
    color_cycle_deg = itertools.cycle(color_styles_deg)

    for (m, n), title in zip(s_params, titles):
        plt.figure(figsize=(18, 10))  

        #-------------------------------------------------------------------------------------------------------------   
        # Subplot para la magnitud en dB
        plt.subplot(1, 2, 1)
        plt.title(f'{title}')
        for ntwk, identifier in network_pairs:
            line_style = next(line_cycle)
            marker_style = next(marker_cycle)
            size_style = next(size_cycle )
            color_style_db = next(color_cycle_db)

            if (m==0 and n==0) or (m==1 and n==1):
                ntwk_aux = unwrap_phase_Sparameters(ntwk,m=m, n=n)
                freq = ntwk_aux.f
                s_db = ntwk_aux.s_db[:, m, n]
                s_deg = ntwk_aux.s_deg_unwrap[:,m, n]            

            else:
                freq = ntwk.f                
                s_db = ntwk.s_db[:, m, n]
                s_deg = ntwk.s_deg_unwrap[:,m, n]
            
            # Convertir a numpy arrays
            freq = np.asarray(freq)/1e9
            s_db = np.asarray(s_db)
            s_deg = np.asarray(s_deg)   

            if len(freq) != len(s_db) or len(freq) != len(s_deg):
                raise ValueError("Las longitudes de frecuencia, magnitud y fase no coinciden.")
            
            #-------------------------------------------------------------------------------------------
            if identifier == 'Proposed method':
                plt.plot(freq, s_db, label= identifier, linewidth=size_style,ls=line_style, marker=marker_style, markersize=8, markevery=30, color=color_style_db)

            else: 
                plt.plot(freq, s_db, label= identifier, linewidth=size_style,ls=line_style, marker=marker_style, markersize=8, markevery=30, color=color_style_db) #markerfacecolor='none'

        plt.legend()
       
        #----------------------------------------------------------------------------------------------------------------------
        # Subplot para la fase en grados
        plt.subplot(1, 2, 2)
        plt.title(f'{title}')
        for ntwk, identifier in network_pairs:
            line_style = next(line_cycle)
            marker_style = next(marker_cycle)
            size_style = next(size_cycle )
            color_style_deg = next(color_cycle_deg)


            if (m==0 and n==0) or (m==1 and n==1):
                ntwk_aux = unwrap_phase_Sparameters(ntwk,m=m, n=n)
                freq = ntwk_aux.f
                s_db = ntwk_aux.s_db[:, m, n]
                s_deg = ntwk_aux.s_deg_unwrap[:,m, n]            

            else:
                freq = ntwk.f                
                s_db = ntwk.s_db[:, m, n]
                s_deg = ntwk.s_deg_unwrap[:,m, n]
            
            # Convertir a numpy arrays
            freq = np.asarray(freq)/1e9
            s_db = np.asarray(s_db)
            s_deg = np.asarray(s_deg)   



            if len(freq) != len(s_db) or len(freq) != len(s_deg):
                raise ValueError("Las longitudes de frecuencia, magnitud y fase no coinciden.")
            
            #-------------------------------------------------------------------------------------------
            if identifier == 'Proposed method':
                plt.plot(freq, s_deg, label=identifier,linewidth=size_style, ls=line_style, marker=marker_style, markersize=8, markevery=30,color=color_style_deg) #markerfacecolor='none'
            else: 
                plt.plot(freq, s_deg, label=identifier,linewidth=size_style, ls=line_style, marker=marker_style, markersize=8, markevery=30,color=color_style_deg)

        plt.legend()
       
        #---------------------------------------------------------------------------------------
        plt.show()

def s_parameters_real_imag(*network_pairs,enable_cut=False,cut_range = '0.5-6ghz'):
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    plt.rc('font', size=17)  # Tamaño de fuente general
    plt.rc('axes', titlesize=22, labelsize=22)  # Tamaño de fuente para títulos y etiquetas de los ejes
    plt.rc('xtick', labelsize=22)  # Tamaño de fuente para las etiquetas del eje x
    plt.rc('ytick', labelsize=22)  # Tamaño de fuente para las etiquetas del eje y
    plt.rc('lines', linewidth=2.5)  
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  
    
    # Configuramos la unidad de frecuencia para todas las redes
    for ntwk, _ in network_pairs:
        ntwk.frequency.unit = 'ghz'
    
    # Definimos los parámetros S a graficar
    s_params = [(0, 0), (1, 0), (0, 1), (1, 1)]
    titles = ['$S_{11}$', '$S_{21}$', '$S_{12}$', '$S_{22}$']

    line_styles = ['-','-.', '--', ':']      
    marker_styles = ['o','X','v','D']
    line_cycle = itertools.cycle(line_styles)
    marker_cycle = itertools.cycle(marker_styles)


    for (m, n), title in zip(s_params, titles):
        plt.figure(figsize=(18, 10))
        
        # Subplot para la magnitud en dB
        plt.subplot(1, 2, 1)
        #plt.title(f'{title}')
        for ntwk, identifier in network_pairs:
            line_style = next(line_cycle)
            marker_style = next(marker_cycle)

            if (m==0 and n==0) or (m==1 and n==1):
                    ntwk_aux = unwrap_phase_Sparameters(ntwk,m=m, n=n)
                    freq = ntwk_aux.f
                    s_db = ntwk_aux.s_db[:, m, n]
                    s_deg = ntwk_aux.s_deg_unwrap[:,m, n]            

            else:
                freq = ntwk.f                
                s_db = ntwk.s_db[:, m, n]
                s_deg = ntwk.s_deg_unwrap[:,m, n]


            if enable_cut:
                ntwk[cut_range].plot_s_re(m=m, n=n, label=identifier,ls=line_style,marker=marker_style, markersize=8,markevery=30)
            else:
                ntwk.plot_s_re(m=m, n=n, label=identifier,ls=line_style,marker=marker_style, markersize=8,markevery=30)
        plt.legend()
        plt.ylabel(f'Real part of {title}')
        #plt.grid()
        #-----------------------------------------------------------------------------------------------------------------------------
        # Subplot para la fase en grados
        plt.subplot(1, 2, 2)
        #plt.title(f'{title}')
        for ntwk, identifier in network_pairs:
            line_style = next(line_cycle)
            marker_style = next(marker_cycle)

            if enable_cut:
                ntwk[cut_range].plot_s_im(m=m, n=n, label=identifier,ls=line_style,marker=marker_style, markersize=8,markevery=30)
            else:
                ntwk.plot_s_im(m=m, n=n, label=identifier,ls=line_style,marker=marker_style, markersize=8,markevery=30)

        plt.legend()
        plt.ylabel(f'Imaginary part of {title}')
        #plt.grid()
        
        plt.show()


        
#===========================================================================================================================

def unwrap_phase_Sparameters(network_name, m=0, n=0):


    network_copy = copy.deepcopy(network_name)
    
    # Extract the magnitude and phase (angle) of the S-parameters
    magnitude = np.abs(network_copy.s[:, m, n])
    phase = np.angle(network_copy.s[:, m, n], deg=True)
    
    # Unwrap the phase
    unwrapped_phase = np.unwrap(phase)
    
    # Reconstruct the S-parameter with the original magnitude and unwrapped phase
    network_copy.s[:, m, n] = magnitude * np.exp(1j * np.deg2rad(unwrapped_phase))
    
    return network_copy










