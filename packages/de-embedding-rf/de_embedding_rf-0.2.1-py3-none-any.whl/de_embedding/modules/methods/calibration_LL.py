"""
LL calibration method
"""
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#libraries 
import numpy as np
import skrf as rf
from pylab import *
import numpy as np
#from numpy.polynomial import Polynomial as P
#import matplotlib.pyplot as plt


# modules
from . import unwrap_owm as unwrap
#import .unwrap_owm as unwrap #dad

#classes 
from .modify_phase import ModifyPhase
from .calculate_propagation_const import CalculatePropagationConstant
from .signal_corrector import SignalCorrector

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


class CalibrationLL:
    def __init__(self,dicc_path_data)->None:
        self.path_dut_full = dicc_path_data['dut_full']
        self.path_line_1 = dicc_path_data['line_l2']
        self.path_line_2 = dicc_path_data['line_l1']
        self.length_line_1 = dicc_path_data['length_line_2']
        self.length_line_2 = dicc_path_data['length_line_1']
        self.length_line_dut = dicc_path_data['length_line_dut']
        
        if 'a_term' in dicc_path_data:
            self.a_term = dicc_path_data['a_term']
        else:
            self.a_term = 'pos'
            
        #initialization:
        self.network_line_1 = None
        self.network_line_1 = None
        self.frequency = None
        self.network_dut_full = None
        self.impedance_zc  = None 
    #-------------------------------------------------------------------------------------
    def read_network(self)->None:
        self.network_line_1 = rf.Network(self.path_line_1)
        self.network_line_2 = rf.Network(self.path_line_2 )
        self.network_dut_full = rf.Network(self.path_dut_full)

        self.frequency = self.network_line_1.f
    #-------------------------------------------------------------------------------------
    def de_embedded_dut(self):

        #1) read data
        self.read_network()

        #2) matrix transformation WCM
        s_parameters_dut_full = self.network_dut_full.s
        s_parameters_line_1 = self.network_line_1.s
        s_parameters_line_2 = self.network_line_2.s

        freq = self.network_dut_full.f
        size_line_l1, rows_line_l1, columns_line_l1 = s_parameters_line_1.shape

        matrix_m1 = rf.network.s2a(s_parameters_line_1 )
        matrix_m2 = rf.network.s2a(s_parameters_line_2 )
        matrix_dut_full = rf.network.s2a(s_parameters_dut_full)
        

        #3) calculation of propagation constant
        propagation_const = CalculatePropagationConstant(self.path_line_1,self.path_line_2,self.length_line_1,self.length_line_2 ).run()

   
        #-----------------------------------------------------------------------------------------------------------------------------
        #4) calculation of the determinant
        aux_det_a = matrix_m1[:,0,0]*np.sinh(propagation_const*self.length_line_2)
        aux_det_b = matrix_m2[:,0,0]*np.sinh(propagation_const*self.length_line_1)
        aux_det_c = np.sinh(propagation_const*self.length_line_2)*np.cosh(propagation_const*self.length_line_1)
        aux_det_d = np.sinh(propagation_const*self.length_line_1)*np.cosh(propagation_const*self.length_line_2)

        det_k = aux_det_a-aux_det_b+aux_det_c-aux_det_d

        #---------------------------------------------------------------------------------------------------------------------
        #5) calculation of characteristic impedance
        aux_zc_numerator_a = matrix_m2[:,0,1]*(np.cosh(propagation_const*self.length_line_1)+matrix_m1[:,0,0])
        aux_zc_numerator_b = matrix_m1[:,0,1]*(np.cosh(propagation_const*self.length_line_2)+matrix_m2[:,1,1])

        aux_impedance_zc =  (aux_zc_numerator_a -aux_zc_numerator_b) / det_k

                
        # 5.1 ) Signal Correction:
        corrector_real = SignalCorrector(aux_impedance_zc.real, self.frequency, noise_filter='median', filter_params=(21,))
        corrector_imag = SignalCorrector(aux_impedance_zc.imag, self.frequency, noise_filter='median', filter_params=(21,))
       
        impedance_zc_real = corrector_real.correct_signal()
        impedance_zc_imag = corrector_imag.correct_signal()

        self.impedance_zc = impedance_zc_real + 1j *impedance_zc_imag 
        
        
        # plt.plot(self.frequency ,impedance_zc_real )
        # plt.plot(self.frequency ,aux_impedance_zc.real)

        # plt.show()

        # plt.plot(self.frequency ,impedance_zc_imag )
        # plt.plot(self.frequency ,aux_impedance_zc.imag)
        # plt.show()

        #-----------------------------------------------------------------------------------------------------------------------------
        #6) calculation of the TL matrix
        matrix_TL = complex128(zeros((size_line_l1,rows_line_l1,columns_line_l1)))

        matrix_TL[:,0,0] = np.cosh(propagation_const*self.length_line_dut )
        matrix_TL[:,0,1] = self.impedance_zc* np.sinh(propagation_const*self.length_line_dut)
        matrix_TL[:,1,0] = (1/self.impedance_zc) * np.sinh(propagation_const*self.length_line_dut)
        matrix_TL[:,1,1] = np.cosh(propagation_const*self.length_line_dut )

        self.result_matrix_TL =  matrix_TL
        #-----------------------------------------------------------------------------------------------------------------------------
        #7) calculation of a12/a11
        aux_a12_numerator_a = matrix_m1[:,0,1]*np.sinh(propagation_const*self.length_line_2)
        aux_a12_numerator_b = matrix_m2[:,0,1]*np.sinh(propagation_const*self.length_line_1)
        const_a12_a11 = (aux_a12_numerator_a-aux_a12_numerator_b) / det_k
        #-----------------------------------------------------------------------------------------------------------------------------
        #8) calculation of a21/a11
        aux_a21_numerator_a = matrix_m1[:,1,0]*np.sinh(propagation_const*self.length_line_2)
        aux_a21_numerator_b = matrix_m2[:,1,0]*np.sinh(propagation_const*self.length_line_1)
        const_a21_a11 = (aux_a21_numerator_a-aux_a21_numerator_b) / det_k
        #-----------------------------------------------------------------------------------------------------------------------------
        #9) calculation of a11**2

        a11_root = np.sqrt(1/(1-(const_a12_a11*const_a21_a11 )))
        #-----------------------------------------------------------------------------------------------------------------------------
        #10) TA matrix formation

        if self.a_term == 'pos':
            a11= a11_root
        elif self.a_term == 'neg':
            a11=-1*a11_root

        
        matrix_TA = complex128(zeros((size_line_l1,rows_line_l1,columns_line_l1)))

        matrix_TA[:,0,0] = a11
        matrix_TA[:,0,1] = const_a12_a11 *a11
        matrix_TA[:,1,0] = const_a21_a11 * a11
        matrix_TA[:,1,1] = a11

        self.result_matrix_TA =  matrix_TA
        #-----------------------------------------------------------------------------------------------------------------------------
        #11) calculation of the DUT matrix
        inverse_TA = complex128(zeros((size_line_l1,rows_line_l1,columns_line_l1)))
        inverse_TL = complex128(zeros((size_line_l1,rows_line_l1,columns_line_l1)))
        matrix_Tdut = complex128(zeros((size_line_l1,rows_line_l1,columns_line_l1)))

        for idx_freq in range(size_line_l1):
            inverse_TA[idx_freq,:,:] = np.linalg.inv(matrix_TA[idx_freq,:,:])
            inverse_TL[idx_freq,:,:] = np.linalg.inv(matrix_TL[idx_freq,:,:])

            aux_matrix_inverse_1 = np.dot(inverse_TL[idx_freq,:,:],inverse_TA[idx_freq,:,:] )
            aux_matrix_inverse_2 = np.dot(aux_matrix_inverse_1 ,matrix_dut_full[idx_freq,:,:])
            matrix_Tdut[idx_freq,:,:] = np.dot (np.dot(aux_matrix_inverse_2 ,inverse_TA[idx_freq,:,:]),inverse_TL[idx_freq,:,:] )
        
        #-----------------------------------------------------------------------------------------------------------------------------
        #12) Transformation of R Parameters to S Parameters
        s_parameter_dut = rf.network.a2s(matrix_Tdut[1:,:,:])
        ntwk = rf.Network(frequency=freq[1:], s=s_parameter_dut, name='calculated-ll-method')


        return ntwk
    
    #------------------------------------------------------------------------------------------------
    def calculate_characteristic_impedance(self):        
        _ = self.de_embedded_dut()
        return self.impedance_zc
    #------------------------------------------------------------------------------------------------
    
    def fit_phase_unwrap(self):
        
        #1) obtain DUT
        dut_original = self.de_embedded_dut()

        #2) apply unwrap                
      
        s11_phase_ll = unwrap.find_jumps(dut_original.s_deg[:,0,0])        
        s22_phase_ll = unwrap.find_jumps(dut_original.s_deg[:,1,1])
                     
        ntwk_virtual_new = ModifyPhase(dut_original,s11_phase_ll,s22_phase_ll).run()

        return ntwk_virtual_new
        
    #--------------------------------------------------------------------------------------------------
    def run(self):
        new_ntwk = self.de_embedded_dut()
        #new_ntwk = self.fit_phase_unwrap()

        return new_ntwk

    #--------------------------------------------------------------------------------------------------
