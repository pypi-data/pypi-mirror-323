
"""
TRL-virtual calibration method
"""
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#libraries 

import numpy as np
import skrf as rf
import cmath
from pylab import *
import numpy as np
from numpy.polynomial import Polynomial as P


#modules
from . import unwrap_owm as unwrap
#import modules.methods.unwrap_owm as unwrap

#classes 
from .modify_phase import ModifyPhase

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class CalibrationSymmetricalTRL:
    def __init__(self,dic_data)->None:
        
        #self.opt_root = opt_root
        self.dic_data = dic_data
        self.standard_reflect = self.dic_data['standard-reflect-virtual']
        
        self.phase_coef_reflection_positive = None
        self.phase_coef_reflection_negative = None
        self.phase_coef_reflection_final = None
        self.frequency_data = None
        
               
        if 'option_virtual' in self.dic_data:
            self.option_parameters = self.dic_data['option_virtual']
        else:
            self.option_parameters = 'full'

        #constants
        self.constant_a = None
        self.constant_b = None
        self.constant_a_c = None

        self.constant_alpha = None
        self.constant_beta = None
        self.constant_delta = None

        self.constant_r22_p22 = None
                 
    #-----------------------------------------------------------------------------------

    def virtual_short(self):

        file_parameters_s = self.file_parameters_thru

        s11_line = file_parameters_s.s[:,0,0]
        s12_line = file_parameters_s.s[:,0,1]
        s21_line = file_parameters_s.s[:,1,0]
        s22_line = file_parameters_s.s[:,1,1]

        
        if self.option_parameters =='full':
            
            sdd11 = 0.5*(s11_line-s21_line-s12_line+s22_line)
            sdd11_array = np.squeeze(sdd11)
                      
        
        elif self.option_parameters == 'collapse':
            
            sdd11 = s11_line-s21_line
            sdd11_array = np.squeeze(sdd11)

        elif self.option_parameters == 'mean':
            
            s11_line_mean = (s11_line+s22_line)/2
            s21_line_mean = (s21_line+s12_line)/2

            sdd11 = s11_line_mean-s21_line_mean
            sdd11_array = np.squeeze(sdd11)

        self.test_sdd11 = sdd11_array
            
        return sdd11_array
    #-----------------------------------------------------------------------
    def virtual_open(self):
        #file_parameters_s = self.file_parameters_line
        file_parameters_s = self.file_parameters_thru

        s11_line = file_parameters_s.s[:,0,0]
        s12_line = file_parameters_s.s[:,0,1]
        s21_line = file_parameters_s.s[:,1,0]
        s22_line = file_parameters_s.s[:,1,1]

        scc11 = []
        for i in range(s22_line.shape[0]):
            scc11.append(0.5*(s11_line[i]+s21_line[i]+s12_line[i]+s22_line[i]))

        scc11_array = np.squeeze(np.row_stack(scc11))
        
        return scc11_array
    #-----------------------------------------------------------------------

    def read_s_parameters(self, impedance = 50):
        
        #1) load red
        self.file_parameters_dut_full= rf.Network(self.dic_data['dut_full'])
        self.file_parameters_thru= rf.Network(self.dic_data['thru'])
        self.file_parameters_line= rf.Network(self.dic_data['line_l1'])

        # 2) data_normalization 
        z_new = impedance
        self.file_parameters_dut_full.renormalize(z_new)
        self.file_parameters_thru .renormalize(z_new)
        self.file_parameters_line.renormalize(z_new)
    
    #-----------------------------------------------------------------------

    def de_embedded_dut(self):
        opt_virtual = self.standard_reflect
        self.read_s_parameters()


        #1) read S parameters:
        parameters_s_dut_comp = self.file_parameters_dut_full.s
        parameters_s_thru = self.file_parameters_thru.s
        parameters_s_line = self.file_parameters_line.s
        #--------------------------------------------------------------------------

        #2) frequency
        freq = self.file_parameters_dut_full.f.reshape(size(self.file_parameters_dut_full.f),1).real
        freq = np.delete(freq,-1)
        #--------------------------------------------------------------------------

        # 3) Conversion of S parameters to R parameters
        parameters_r_dut_comp = rf.network.s2t(parameters_s_dut_comp)
        parameters_r_thru = rf.network.s2t(parameters_s_thru)
        parameters_r_line = rf.network.s2t(parameters_s_line)

        #-----------------------------------------------------------------------
        #4) compare number of points in the matrix
        size_thru, rows_thru, columns_thru = parameters_s_thru.shape
        size_line, rows_line, columns_line = parameters_s_line.shape
        size_dut_comp, rows_dut_comp, columns_dut_comp = parameters_s_dut_comp.shape

        if (size_thru != size_line) or (size_dut_comp != size_line):
            raise TypeError("The path for the S parameters was not found")

        #-----------------------------------------------------------------------
        # 5) calculation of the matrix T and the constants a/c and b
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

        #5.1) root calculation
        for m in range(size_thru):
            constant_2[m] = matrix_t[m,1,0]
            constant_1[m] = matrix_t[m,1,1]-matrix_t[m,0,0]
            constant_0[m] = -1*matrix_t[m,0,1]

            polynomial_quadratic = P([constant_0[m],constant_1[m],constant_2[m]])
            roots_1[m], roots_2[m] = polynomial_quadratic.roots()

            # 5.2) discriminating factor
            if abs(roots_1[m])> abs(roots_2[m]):
                const_a_divide_c[m] = roots_1[m]
                const_b[m] = roots_2[m]
            else:
                const_a_divide_c[m] = roots_2[m]
                const_b[m] = roots_1[m]

        const_b = np.delete(const_b, -1)
        const_a_divide_c = np.delete(const_a_divide_c, -1)

        #-----------------------------------------------------------------------
        # 6)  calculation of the constant R22_por_rho22, delta, alpha_por_a, beta_/_alpha
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
        
        #-----------------------------------------------------------------------
        #7) calculate a

        const_a = complex128(zeros(size_thru-1))
        assumption_const_a_pos = complex128(zeros(size_thru-1))
        assumption_const_a_neg = complex128(zeros(size_thru-1))

        coef_reflection_r_pos = complex128(zeros(size_thru-1))
        phase_coef_reflection_r_pos = zeros(size_thru-1)
        coef_reflection_r_neg = complex128(zeros(size_thru-1))
        phase_coef_reflection_r_neg = zeros(size_thru-1)
        new_phase_coef_reflection =complex128(zeros(size_thru-1))

        if opt_virtual =='short':
            w_1 = self.virtual_short()
            w_2 = self.virtual_short()

        elif opt_virtual == 'open':
            w_1 = self.virtual_open()
            w_2 = self.virtual_open()
        else:
            raise TypeError("Invalid option")


        for p in range(size_thru-1):
            assumption_const_a_pos[p]  = cmath.sqrt(const_A[p]) # no usar np.sqrt (numpy )
            assumption_const_a_neg[p]  = -1*cmath.sqrt(const_A[p])

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

 

        elif self.standard_reflect == 'short':
            for y in range(size_thru-1):
                if (phase_coef_reflection_r_pos[y]<= 90) and (phase_coef_reflection_r_pos[y]>= -90):
                    const_a[y] = assumption_const_a_neg[y]
                    new_phase_coef_reflection[y]= phase_coef_reflection_r_neg[y]
                else:
                                        
                    const_a[y] = assumption_const_a_pos[y]
                    new_phase_coef_reflection[y]= phase_coef_reflection_r_pos[y]

        else:
            raise TypeError("reflector standard does not identify")
        
        #-----------------------------------------------------------------------
        # 8) save reflection coefficient
        self.phase_coef_reflection_positive = phase_coef_reflection_r_pos
        self.phase_coef_reflection_negative = phase_coef_reflection_r_neg
        self.phase_coef_reflection_final = new_phase_coef_reflection
        self.frequency_data = freq

        #-----------------------------------------------------------------------  
       
        #9) calculates R of dut and the constants alpha, c and beta
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
        
        #-----------------------------------------------------------------------
        #Transformation of R Parameters to S Parameters
        parametros_s_dut_calculated = rf.network.t2s(R_dut)
        ntwk = rf.Network(frequency=freq, s=parametros_s_dut_calculated, name='calculated-trl-virtual')

        return ntwk
    
    #-----------------------------------------------------------------------
    def fit_phase_unwrap(self):
        
        #1) obtain DUT
        dut_original = self.symmetrical_TRL()

        #2) apply unwrap                
      
        s11_phase_trl_virtual = unwrap.find_jumps(dut_original.s_deg[:,0,0])        
        s22_phase_trl_virtual = unwrap.find_jumps(dut_original.s_deg[:,1,1])
                     
        ntwk_virtual_new = ModifyPhase(dut_original,s11_phase_trl_virtual,s22_phase_trl_virtual).run()

        return ntwk_virtual_new

    def run(self):
         
        network_dut_final = self.de_embedded_dut()
        #network_dut_final = self.fit_phase_unwrap()         

        return network_dut_final

