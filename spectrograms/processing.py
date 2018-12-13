#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 12 19:17:03 2018

@author: anubhav
"""

from __future__ import print_function
import audioread
import sys
import os
import wave
import contextlib
import matplotlib.pyplot as plt
import numpy as np
import wave
from scipy.signal import butter, lfilter
from scipy import signal

#Convert Audio
def decode(filename):
    filename = os.path.abspath(os.path.expanduser(filename))
    if not os.path.exists(filename):
        print("File not found.", file=sys.stderr)
        sys.exit(1)

    try:
        with audioread.audio_open(filename) as f:
            print('Input file: %i channels at %i Hz; %.1f seconds.' %
                  (f.channels, f.samplerate, f.duration),
                  file=sys.stderr)
            print('Backend:', str(type(f).__module__).split('.')[1],
                  file=sys.stderr)
            filename = filename.split('/')
            newFileName = os.path.join("../decoded-input/" , filename[-1])
            with contextlib.closing(wave.open(newFileName + '.wav', 'w')) as of:
                of.setnchannels(f.channels)
                of.setframerate(f.samplerate)
                of.setsampwidth(2)

                for buf in f:
                    of.writeframes(buf)

    except audioread.DecodeError:
        print("File could not be decoded.", file=sys.stderr)
        sys.exit(1)
    
def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y    

for file in os.listdir("../decoded-input"):
    os.remove(os.path.join("../../decoded-input/" , file))
    
for file in os.listdir("../audio-recording-input"):
    if file.endswith(".aac"):
        print(os.path.join(file))
        
        decode(os.path.join("../audio-recording-input/" , file))
    #    decode('zambani_sitting.aac')
        
        #Fetch WAV Audio
        directSig = wave.open('../no-obstacle.aac.wav','r')
         
        directSig = directSig.readframes(-1)
        directSig = np.fromstring(directSig, 'Int16')
        
        # =============================================================================
        # fig = plt.figure(1)
        # plt.title('Direct Signal Wave...')
        # plt.plot(directSig)
        # plt.show()
        # fig.savefig('direct-sig.png' , dpi=128)
        # =============================================================================
        
        fs = 48e3
        lowcut = 20000.0
        highcut = 22000.0
        
        directSigFiltered = butter_bandpass_filter(directSig, lowcut, highcut, fs, order=6)
        
        # =============================================================================
        # fig = plt.figure(2)
        # plt.title('Direct Signal Filtered Wave')
        # plt.plot(directSigFiltered)
        # plt.show()
        # fig.savefig('direct-sig-filter.png' , dpi=128)
        # =============================================================================
        
    #    testSig = wave.open('zambani_sitting.aac.wav','r')
        testSig = wave.open(os.path.join("../decoded-input/" , file) + '.wav','r')
        
        testSig = testSig.readframes(-1)
        testSig = np.fromstring(testSig, 'Int16')
        
        # =============================================================================
        # fig = plt.figure(3)
        # plt.title('Test Signal Wave')
        # plt.plot(testSig)
        # plt.show()
        # fig.savefig('test-sig.png' , dpi=128)
        # =============================================================================
        
        
        testSigFiltered = butter_bandpass_filter(testSig, lowcut, highcut, fs, order=6)
        
        # =============================================================================
        # fig = plt.figure(4)
        # plt.title('Test Signal Filtered Wave')
        # plt.plot(testSigFiltered)
        # plt.show()
        # fig.savefig('test-sig-filter.png' , dpi=128)
        # =============================================================================
        
        correlated = signal.correlate(testSigFiltered, directSigFiltered, mode='same')
        fig = plt.figure(1)
        Pxx, freqs, bins, im = plt.specgram(correlated, NFFT=128, Fs=fs, 
                                            window=np.hanning(128), 
                                            noverlap=127)
        
        plt.title('Spectrogram of Correlated Signal')
        plt.ylabel('Frequency [Hz]')
        plt.xlabel('Time [sec]')
#       fig.colorbar()
#       plt.show()

        fig.savefig(os.path.join(file) + '-spectrogram.jpg' , dpi=128)