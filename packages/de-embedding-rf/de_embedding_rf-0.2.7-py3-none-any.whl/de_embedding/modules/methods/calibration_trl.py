"""
TRL calibration method
"""
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#libraries 
import os
import numpy as np
import skrf as rf
import cmath
from pylab import *
import numpy as np
from numpy.polynomial import Polynomial as P


#modules
from . import unwrap_owm as unwrap

#classes 
from .modify_phase import ModifyPhase


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


class CalibrationTRL:
    def __init__(self,dic_data)->None:

        self.dic_data = dic_data
        self.standard_reflect = self.dic_data['standard-reflect']

        self.phase_coef_reflection_positive = None
        self.phase_coef_reflection_negative = None
        self.phase_coef_reflection_final = None
        self.frequency_data = None

        #constants
        self.constant_a = None
        self.constant_b = None
        self.constant_a_c = None

        self.constant_alpha = None
        self.constant_beta = None
        self.constant_delta = None

        self.constant_r22_p22 = None 

    #----------------------------------------------------------------------------------------------------
    def read_s_parameters(self,impedance=50):

        #1) load red
        self.file_parameters_dut_full = rf.Network(self.dic_data['dut_full'])
        self.file_parameters_thru = rf.Network(self.dic_data['thru'])
        self.file_parameters_line= rf.Network(self.dic_data['line_l1'])

        # 2) data_normalization 
        z_new = impedance
        self.file_parameters_dut_full.renormalize(z_new)
        self.file_parameters_thru .renormalize(z_new)
        self.file_parameters_line.renormalize(z_new)

        if 'reflect_port_2' in self.dic_data:
            name_file_port_1 = self.dic_data['reflect_port_1']
            name_file_port_2 = self.dic_data['reflect_port_2']

            file_parameters_reflect_1 = rf.Network( name_file_port_1 )
            file_parameters_reflect_2 = rf.Network(name_file_port_2)

            #normalization:
            file_parameters_reflect_1.renormalize(z_new)
            file_parameters_reflect_2.renormalize(z_new)


            # read s-parameters

            _, extension_1 = os.path.splitext(name_file_port_1)
            extension_port_1= extension_1.lstrip(".")

            _, extension_2 = os.path.splitext(name_file_port_2)
            extension_port_2= extension_2.lstrip(".")


            if extension_port_1 == 's1p':
                self.reflect_port_1 = file_parameters_reflect_1.s[:,0,0]
            elif extension_port_1 == 's2p':
                self.reflect_port_1 = file_parameters_reflect_1.s[:,0,0]
            else:
                raise TypeError("The extension for reflect port 1 was not found")


            if extension_port_2 == 's1p':
                self.reflect_port_2 = file_parameters_reflect_2.s[:,0,0]
            elif extension_port_2 == 's2p':
                self.reflect_port_2 = file_parameters_reflect_2.s[:,1,1]
            else:
                raise TypeError("The extension for reflect port 2 was not found")

        else:
            file_parameters_reflect_1 = rf.Network(self.dic_data['reflect_port_1'])
            file_parameters_reflect_1.renormalize(z_new)
            self.reflect_port_1 = file_parameters_reflect_1.s[:,0,0]
            self.reflect_port_2 = file_parameters_reflect_1.s[:,1,1]

    #----------------------------------------------------------------------------------------------------
    def de_embedded_dut(self):

        #1) read S parameters:
        self.read_s_parameters()
       
        parameters_s_dut_comp = self.file_parameters_dut_full.s
        parameters_s_thru = self.file_parameters_thru.s
        parameters_s_line = self.file_parameters_line.s
        parameters_s_reflect_1 = self.reflect_port_1
        parameters_s_reflect_2 = self.reflect_port_2
        #----------------------------------------------------------------------------------------------------
        #2) frequency
        freq = self.file_parameters_dut_full.f.reshape(size(self.file_parameters_dut_full.f),1).real
        freq = np.delete(freq,-1)
        #----------------------------------------------------------------------------------------------------
        #3) Conversion of S parameters to R parameters
        parameters_r_dut_comp = rf.network.s2t(parameters_s_dut_comp)
        parameters_r_thru = rf.network.s2t(parameters_s_thru)
        parameters_r_line = rf.network.s2t(parameters_s_line)
        #----------------------------------------------------------------------------------------------------
        #4) compare number of points in the matrix
        size_thru, rows_thru, columns_thru = parameters_s_thru.shape
        size_line, rows_line, columns_line = parameters_s_line.shape
        size_dut_comp, rows_dut_comp, columns_dut_comp = parameters_s_dut_comp.shape
        #----------------------------------------------------------------------------------------------------

        if (size_thru != size_line) or (size_dut_comp != size_line) :
            raise TypeError("The path for the S parameters was not found")

        #----------------------------------------------------------------------------------------------------
        #5) calculation of the matrix T and the constants a/c and b
        matrix_t = complex128(zeros((size_thru,rows_thru,columns_thru)))
        inverse_rt = complex128(zeros((size_thru,rows_thru,columns_thru)))

        constant_2= complex128(zeros(size_thru))
        constant_1= complex128(zeros(size_thru))
        constant_0= complex128(zeros(size_thru))

        roots_1 = complex128(zeros(size_thru))
        roots_2 = complex128(zeros(size_thru))
        const_a_divide_c = complex128(zeros(size_thru))
        const_b = complex128(zeros(size_thru))

        for n in range(size_thru):
            inverse_rt[n,:,:] = np.linalg.inv(parameters_r_thru[n,:,:])
            matrix_t[n,:,:] = np.dot(parameters_r_line[n,:,:],inverse_rt[n,:,:])
        #----------------------------------------------------------------------------------------------------
        #6) root calculation

        for m in range(size_thru):
            constant_2[m] = matrix_t[m,1,0]
            constant_1[m] = matrix_t[m,1,1]-matrix_t[m,0,0]
            constant_0[m] = -1*matrix_t[m,0,1]

            polynomial_quadratic = P([constant_0[m],constant_1[m],constant_2[m]])
            roots_1[m], roots_2[m] = polynomial_quadratic.roots()

            #6.1) discriminating factor
            if abs(roots_1[m])> abs(roots_2[m]):
                const_a_divide_c[m] = roots_1[m]
                const_b[m] = roots_2[m]
            else:
                const_a_divide_c[m] = roots_2[m]
                const_b[m] = roots_1[m]

        const_b = np.delete(const_b, -1)
        const_a_divide_c = np.delete(const_a_divide_c, -1)
        #----------------------------------------------------------------------------------------------------
        #7) calculation of the constant R22_por_rho22, delta, alpha_por_a, beta_over_alpha
        const_d = complex128(zeros(size_thru-1))
        const_e = complex128(zeros(size_thru-1))
        const_f = complex128(zeros(size_thru-1))
        const_g = complex128(zeros(size_thru-1))

        const_r22_rho22 = complex128(zeros(size_thru-1))
        const_delta = complex128(zeros(size_thru-1))
        const_beta_divide_alpha = complex128(zeros(size_thru-1))
        const_A = complex128(zeros(size_thru-1))

        for l in range(size_thru-1):

            const_d[l] = parameters_r_thru[l,0,0]/parameters_r_thru[l,1,1]
            const_e[l] = parameters_r_thru[l,0,1]/parameters_r_thru[l,1,1]
            const_f[l] = parameters_r_thru[l,1,0]/parameters_r_thru[l,1,1]
            const_g[l] = parameters_r_thru[l,1,1]

            const_r22_rho22[l] = const_g[l]*(1-(const_e[l]/const_a_divide_c[l]))/(1-(const_b[l]/const_a_divide_c[l]))
            const_delta[l] = (const_f[l]-(const_d[l]/const_a_divide_c[l]))/(1-(const_e[l]/const_a_divide_c[l]))
            const_beta_divide_alpha[l] = (const_e[l]-const_b[l])/(const_d[l]-(const_b[l]*const_f[l]))
            const_A[l] = (const_d[l]-(const_b[l]*const_f[l]))/(1-(const_e[l]/const_a_divide_c[l]))
        #----------------------------------------------------------------------------------------------------

        #8) calculate a

        const_B = complex128(zeros(size_thru-1))
        const_a_cuadrada = complex128(zeros(size_thru-1))
        const_a = complex128(zeros(size_thru-1))
        assumption_const_a_pos = complex128(zeros(size_thru-1))
        assumption_const_a_neg = complex128(zeros(size_thru-1))

        coef_reflection_r_pos = complex128(zeros(size_thru-1))
        phase_coef_reflection_r_pos = zeros(size_thru-1)
        coef_reflection_r_neg = complex128(zeros(size_thru-1))
        phase_coef_reflection_r_neg = zeros(size_thru-1)
        new_phase_coef_reflection =complex128(zeros(size_thru-1))

        w_1 = parameters_s_reflect_1
        w_2 = parameters_s_reflect_2

        for p in range(size_thru-1):
            const_B[p] = ((w_1[p]-const_b[p])*(1+(w_2[p]*const_beta_divide_alpha[p])))/((w_2[p]+const_delta[p])*(1-(w_1[p]/const_a_divide_c[p])))
            const_a_cuadrada[p] = const_A[p]*const_B[p]

            assumption_const_a_pos[p]  = cmath.sqrt(const_a_cuadrada[p]) # no usar np.sqrt (numpy )
            assumption_const_a_neg[p]  = -1*cmath.sqrt(const_a_cuadrada[p])

        for x in range(size_thru-1):
            coef_reflection_r_pos[x] = (w_1[x]-const_b[x])/(assumption_const_a_pos[x]*(1-(w_1[x]/const_a_divide_c[x])))
            phase_coef_reflection_r_pos[x] = cmath.phase(coef_reflection_r_pos[x])*180/np.pi

            coef_reflection_r_neg[x] = (w_1[x]-const_b[x])/(assumption_const_a_neg[x]*(1-(w_1[x]/const_a_divide_c[x])))
            phase_coef_reflection_r_neg[x] = cmath.phase(coef_reflection_r_neg[x])*180/np.pi


        if self.standard_reflect == 'open':
            for y in range(size_thru-1):
                if (phase_coef_reflection_r_pos[y]<= 90) and (phase_coef_reflection_r_pos[y]>= -90):
                    const_a[y] = assumption_const_a_pos[y]
                    new_phase_coef_reflection[y]= phase_coef_reflection_r_pos[y]
                else:
                    const_a[y] = assumption_const_a_neg[y]
                    new_phase_coef_reflection[y]= phase_coef_reflection_r_neg[y]

                # elif (phase_coef_reflection_r_neg[y]<= 90) and (phase_coef_reflection_r_neg[y]>= -90):
                #     const_a[y] = assumption_const_a_neg[y]
                #     new_phase_coef_reflection[y]= phase_coef_reflection_r_neg[y]


        elif self.standard_reflect == 'short':
            for idx_a in range(size_thru-1):
                if (phase_coef_reflection_r_pos[idx_a]<= 90) and (phase_coef_reflection_r_pos[idx_a]>= -90):
                    const_a[idx_a] = assumption_const_a_neg[idx_a]
                    new_phase_coef_reflection[idx_a]= phase_coef_reflection_r_neg[idx_a]
                else:
                    const_a[idx_a] = assumption_const_a_pos[idx_a]
                    new_phase_coef_reflection[idx_a]= phase_coef_reflection_r_pos[idx_a]
                

                # elif ((phase_coef_reflection_r_neg[y]>= 90) and (phase_coef_reflection_r_neg[y]<= 182)) or ((phase_coef_reflection_r_neg[y]>= -182) and (phase_coef_reflection_r_neg[y]<= -90)):
                #     const_a[y] = assumption_const_a_neg[y]
                #     new_phase_coef_reflection[y]= phase_coef_reflection_r_neg[y]

                # else:
                #     print('didnt find an short circuit')
                #     const_a[y] = assumption_const_a_pos[y]
                #     new_phase_coef_reflection[y]= phase_coef_reflection_r_pos[y]
        else:
            raise TypeError("reflector standard does not identify")

        #----------------------------------------------------------------------------------------------------
        # 9) save reflection coefficient
        self.phase_coef_reflection_positive = phase_coef_reflection_r_pos
        self.phase_coef_reflection_negative = phase_coef_reflection_r_neg
        self.phase_coef_reflection_final = new_phase_coef_reflection
        self.frequency_data = freq

        #----------------------------------------------------------------------------------------------------

        # 10) Calculates the DUT's R and the constants alpha, c y beta
        coef_reflection_r_w2 = complex128(zeros(size_thru-1))
        coef_reflection_r_w1= complex128(zeros(size_thru-1))
        phase_w2 = complex128(zeros(size_thru-1))
        phase_w1 = complex128(zeros(size_thru-1))

        const_alpha = complex128(zeros(size_thru-1))
        const_beta = complex128(zeros(size_thru-1))
        const_c = complex128(zeros(size_thru-1))

        const_R_dut = complex128(zeros(size_thru-1))
        R_dut  = complex128(zeros((size_thru-1,rows_thru,columns_thru)))
        matrix_ra_inv  = complex128(zeros((size_thru-1,rows_thru,columns_thru)))
        matrix_rb_inv  = complex128(zeros((size_thru-1,rows_thru,columns_thru)))


        for f in range(size_thru-1):

            const_alpha[f] = const_A[f]/const_a[f]
            const_beta[f] = const_beta_divide_alpha[f]*const_alpha[f]
            const_c[f] = const_a[f] /const_a_divide_c[f]

            matrix_ra_inv[f,0,0] = complex128(1)
            matrix_ra_inv[f,0,1] = -1*const_b[f]
            matrix_ra_inv[f,1,0] = -1*const_c[f]
            matrix_ra_inv[f,1,1] =  const_a[f]

            matrix_rb_inv[f,0,0] = complex128(1)
            matrix_rb_inv[f,0,1] = -1*const_beta[f]
            matrix_rb_inv[f,1,0] = -1*const_delta[f]
            matrix_rb_inv[f,1,1] =  const_alpha[f]

            coef_reflection_r_w2[f] = (w_2[f]+const_delta[f])/(const_alpha[f]*(1+w_2[f]*const_beta[f]/const_alpha[f]))
            phase_w1[f]=cmath.phase(coef_reflection_r_w1[f])*180/np.pi

            coef_reflection_r_w1[f] = (w_1[f]-const_b[f])/(const_a[f]*(1-(w_1[f]/const_a_divide_c[f])))
            phase_w2[f] = cmath.phase(coef_reflection_r_w2[f])*180/np.pi


            const_R_dut[f] = (1/const_r22_rho22[f])*(1/const_A[f])*(1/(1-(const_b[f]/const_a_divide_c[f])))*(1/(1-(const_beta_divide_alpha[f]*const_delta[f])))
            R_dut[f,:,:] = const_R_dut[f]*np.dot(np.dot(matrix_ra_inv[f,:,:], parameters_r_dut_comp[f,:,:]),matrix_rb_inv[f,:,:])

        
        self.constant_a = const_a
        self.constant_b = const_b
        self.constant_c = const_c

        self.constant_alpha = const_alpha
        self.constant_beta = const_beta
        self.constant_delta = const_delta

        self.constant_r22_p22 = const_r22_rho22
        #----------------------------------------------------------------------------------------------------
        #11) Transformation of R Parameters to S Parameters
        parametros_s_dut_calculated = rf.network.t2s(R_dut)
        ntwk = rf.Network(frequency=freq, s=parametros_s_dut_calculated, name='calculated-trl')

        return ntwk
    
    #-----------------------------------------------------------------------------------------------------
    def fit_phase_unwrap(self):
        
        #1) obtain DUT
        dut_original = self.de_embedded_dut()

        #2) apply unwrap                
      
        s11_phase_trl = unwrap.find_jumps(dut_original.s_deg[:,0,0])        
        s22_phase_trl = unwrap.find_jumps(dut_original.s_deg[:,1,1])
                     
        ntwk_virtual_new = ModifyPhase(dut_original,s11_phase_trl,s22_phase_trl).run()

        return ntwk_virtual_new
    #-----------------------------------------------------------------------------------------------------
    def run(self):
        network_dut = self.de_embedded_dut()
        #network_dut = self.fit_phase_unwrap()

        return network_dut