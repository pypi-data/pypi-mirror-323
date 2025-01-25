#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#libraries 
import numpy as np 
import matplotlib.pyplot as plt 
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def find_jumps(signal_raw,variation_threshold=0.1,*args):

    signal = signal_raw/np.max(np.abs(signal_raw))

    cumulative_variation = np.cumsum(np.abs(np.diff(signal)))

    # Find indices where there are significant changes in cumulative variation
    jump_indices = np.where(np.abs(np.diff(cumulative_variation)) > variation_threshold)[0] + 1

    # Values of the abrupt jumps
    jump_values = signal_raw[jump_indices]

    corrected_signal = np.copy(signal_raw)
    #---------------------------------------------------------------------------
    for idx, idx_value in enumerate(jump_indices):
        dif_before = 0
        if jump_indices[idx]-1 != jump_indices[idx-1]:
             dif_before = signal_raw[idx_value]- signal_raw[idx_value-1]
        else: 
            jump_indices_cut = jump_indices[:idx]
            for idx_aux, idx_value_aux in enumerate(jump_indices_cut):
                if jump_indices_cut[idx_aux]-1 != jump_indices_cut[idx_aux-1]: 
                    dif_before = signal_raw[idx_value_aux]- signal_raw[idx_value_aux-1]


        dif_jump = (signal_raw[idx_value]- signal_raw[idx_value+1]) + dif_before
        corrected_signal[idx_value+1:] += dif_jump
    #-------------------------------------------------------------------------------


    #visualization:
    if args:
        if args[0]:
            print(f'limits found - {args[1]}: {jump_indices}')
            print(f'length - {args[1]}: {len(jump_indices)}')

            plt.figure(figsize=(10,8))
            plt.subplot(1,2,1)
            plt.plot(np.abs(np.diff(cumulative_variation)),label=str(args[1]))
            plt.legend()

            plt.subplot(1,2,2)
            plt.plot(signal_raw,label=str(args[1]))
            plt.plot(corrected_signal )
            plt.scatter(jump_indices,jump_values ,marker='*',color='red')

            plt.legend()
            plt.grid()
            plt.show()

    return  np.array(corrected_signal)