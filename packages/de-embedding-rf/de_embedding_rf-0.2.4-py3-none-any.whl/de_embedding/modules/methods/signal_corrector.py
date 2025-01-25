
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#libraries 
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter, find_peaks, medfilt
from scipy.interpolate import interp1d
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


class SignalCorrector:
    def __init__(self, signal, time, window_length=31, polyorder=5, noise_filter='savgol', filter_params=(51, 3)):
        self.signal = signal
        self.time = time
        self.window_length = window_length
        self.polyorder = polyorder
        self.noise_filter = noise_filter
        self.filter_params = filter_params
    #-----------------------------------------------------------------------
    def _apply_noise_filter(self):
        if self.noise_filter == 'savgol':
            return savgol_filter(self.signal, *self.filter_params)
        elif self.noise_filter == 'median':
            return medfilt(self.signal, self.filter_params[0])
        elif self.noise_filter == 'moving_average':
            window_size = self.filter_params[0]
            return np.convolve(self.signal, np.ones(window_size)/window_size, mode='same')
        else:
            raise ValueError("Unsupported noise filtering method.")
    
    #-----------------------------------------------------------------------
    def correct_signal(self):
        # Filter the noise
        filtered_signal = self._apply_noise_filter()

        # Detect peaks in the signal
        peaks, _ = find_peaks(np.abs(np.diff(filtered_signal)), distance=50, height=0.5)

        # Create a mask for the smoothed signal
        mask = np.ones_like(filtered_signal, dtype=bool)
        for peak in peaks:
            if peak > 0 and peak < len(filtered_signal) - 1:
                start = max(0, peak - 50)
                end = min(len(filtered_signal), peak + 50)
                mask[start:end] = False

        # Apply the Savitzky-Golay filter to the entire signal
        smooth_signal = savgol_filter(filtered_signal, self.window_length, self.polyorder)

        # Interpolate based on detected peaks
        t_smooth = self.time[mask]
        signal_smooth = smooth_signal[mask]
        f = interp1d(t_smooth, signal_smooth, kind='cubic', fill_value="extrapolate")

        # Create the final smoothed signal
        final_signal = f(self.time)

        return final_signal
    
    #-----------------------------------------------------------------------
    def plot(self, corrected_signal):
        plt.figure(figsize=(12, 6))
        plt.plot(self.time, self.signal, label='Signal with noise and spikes', alpha=0.5)
        plt.plot(self.time, corrected_signal, label='Corrected signal', linestyle='--')
        plt.title('Reconstruction of the Signal without Spikes')
        plt.xlabel('Time')
        plt.ylabel('Amplitude')
        plt.legend()
        plt.grid()
        plt.show()
