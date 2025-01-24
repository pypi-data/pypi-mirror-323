"""
Method for Calculating the Propagation Constant
"""
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#libraries 

import numpy as np
import skrf as rf
from pylab import *
import numpy as np
from numpy.polynomial import Polynomial as P

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++



class CalculatePropagationConstant:
    def __init__(self,path_line_1,path_line_2,length_line_1,length_line_2)->None:
        self.path_line_1 = path_line_1
        self.path_line_2 = path_line_2
        self.length_line_1 = length_line_1
        self.length_line_2 = length_line_2

        #initialization:
        self.network_line_1 = None
        self.network_line_1 = None
        self.frequency = None


    def read_network(self):
        self.network_line_1 = rf.Network(self.path_line_1)
        self.network_line_2 = rf.Network(self.path_line_2 )
        self.frequency = self.network_line_1.f

    def PropagationConstant(self):
        #1) read data:
        self.read_network()

        #2) matrix transformation WCM
        s_parameters_line_1 = self.network_line_1.s
        s_parameters_line_2 = self.network_line_2.s

        matrix_m1 = rf.network.s2t(s_parameters_line_1 )
        matrix_m2 = rf.network.s2t(s_parameters_line_2 )

        #3)  formation of the T matrix
        size_line_l1, rows_line_l1, columns_line_l1 = s_parameters_line_1.shape

        matrix_t = complex128(zeros((size_line_l1,rows_line_l1,columns_line_l1)))
        inverse_m2 = complex128(zeros((size_line_l1,rows_line_l1,columns_line_l1)))

        for idx_freq in range(size_line_l1):
            inverse_m2[idx_freq,:,:] = np.linalg.inv(matrix_m2[idx_freq,:,:])
            matrix_t[idx_freq,:,:] = np.dot(matrix_m1[idx_freq,:,:],inverse_m2[idx_freq,:,:])

        #4) calculation of a/c and b
        constant_2= complex128(zeros(size_line_l1))
        constant_1= complex128(zeros(size_line_l1))
        constant_0= complex128(zeros(size_line_l1))
        roots_1 = complex128(zeros(size_line_l1))
        roots_2 = complex128(zeros(size_line_l1))
        const_a_divide_c = complex128(zeros(size_line_l1))
        const_b = complex128(zeros(size_line_l1))


        for m in range(size_line_l1):
            constant_2[m] = matrix_t[m,1,0]
            constant_1[m] = matrix_t[m,1,1]-matrix_t[m,0,0]
            constant_0[m] = -1*matrix_t[m,0,1]

            polynomial_quadratic = P([constant_0[m],constant_1[m],constant_2[m]])
            roots_1[m], roots_2[m] = polynomial_quadratic.roots()

            # factor discriminante
            if abs(roots_1[m])> abs(roots_2[m]):
                const_a_divide_c[m] = roots_1[m]
                const_b[m] = roots_2[m]
            else:
                const_a_divide_c[m] = roots_2[m]
                const_b[m] = roots_1[m]

        #5) calculation of the propagation constant

        aux_numerator = (const_a_divide_c*matrix_t[:,0,0])-(const_a_divide_c*const_b*matrix_t[:,1,0])-(const_b*matrix_t[:,1,1])+ matrix_t[:,0,1]
        aux_denominator = const_a_divide_c - const_b
        variable_lambda = aux_numerator/aux_denominator

        propagation_constant  = (1/(self.length_line_2-self.length_line_1))*np.log(variable_lambda)

        return propagation_constant

    def run(self):
        propagation_const = self.PropagationConstant()

        return propagation_const




