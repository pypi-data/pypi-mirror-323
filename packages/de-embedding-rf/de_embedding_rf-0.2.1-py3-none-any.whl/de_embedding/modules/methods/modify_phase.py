#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#libraries 
import numpy as np
import copy
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class ModifyPhase:
    def __init__(self,network_original,new_phase_s11,new_phase_s22)->None:

        self.network_original =copy.deepcopy(network_original)
        self.new_phase_s11 = new_phase_s11
        self.new_phase_s22 = new_phase_s22
    #--------------------------------------------------------------------------------------
    def modify_s11_s22(self):
        #1) read data original 
        s_parameters = self.network_original.s

        # S11
        s11_complex = s_parameters[:, 0, 0]  # S11 en formato complejo
        s11_magnitude = np.abs(s11_complex) 
        s11_phase = np.angle(s11_complex, deg=True)  # Fase de S11 en grados
        # S22
        s22_complex = s_parameters[:, 1, 1]  # S22 en formato complejo
        s22_magnitude = np.abs(s22_complex) 
        s22_phase = np.angle(s22_complex, deg=True)  # Fase de S22 en grados


        #2) convert
        assert len(self.new_phase_s11) == len(s11_phase), "phase vectors must have the same length- s11"
        assert len(self.new_phase_s22) == len(s22_phase), "phase vectors must have the same length - s22"
 
        new_phase_rad_s11 = np.deg2rad(self.new_phase_s11)
        new_s11 = s11_magnitude * np.exp(1j * new_phase_rad_s11)
        s_parameters[:, 0, 0] = new_s11

        new_phase_rad_s22 = np.deg2rad(self.new_phase_s22)
        new_s22 = s22_magnitude * np.exp(1j * new_phase_rad_s22)
        s_parameters[:, 1, 1] = new_s22

        
        self.network_original.s = s_parameters

        return self.network_original
    
    def run(self):
        modified_network = self.modify_s11_s22()

        return modified_network

