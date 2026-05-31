#!/usr/bin/env python3
"""
EEG rhythm cluster — ARA from base-cycle rise/decay asymmetry (raw-refined).
============================================================================
Replaces 5 over-2 catalogue nodes (Gamma/Beta/Alpha/Theta/Delta). A rhythm is
NOT exempt from ARA: each base cycle has a rising build and falling release.
Narrow bandpass alone forces a symmetric sine (ARA->1 artifact), so we use the
bycycle discipline (Cole & Voytek 2017): the bandpass only LOCATES cycle
boundaries; rise/decay times are measured on the RAW signal between raw-refined
extrema, preserving true waveform asymmetry.

Data: PhysioNet slpdb slp01a, channel 'EEG (C4-A1)', fs=250 Hz, 10-min segment.
  rise  = trough -> next peak  on raw (BUILD / accumulation)
  decay = peak   -> next trough on raw (RELEASE)
  ARA   = median(decay)/median(rise);  symmetric => 1.0 (ridge/pacemaker).
"""
import numpy as np
from scipy.signal import butter, sosfiltfilt
fs=250
raw=np.load('eeg_seg.npy').astype(float); raw=raw-np.mean(raw)
seg=raw[:fs*600]

BANDS={'Delta 2Hz':(1,4),'Theta 6Hz':(4,8),'Alpha 10Hz':(8,12),
       'Beta 20Hz':(13,30),'Gamma 40Hz':(30,48)}

def bandpass(sig,lo,hi):
    sos=butter(4,[lo,hi],btype='band',fs=fs,output='sos'); return sosfiltfilt(sos,sig)

def rdsym(rawsig, lo, hi):
    f=bandpass(rawsig,lo,hi)
    # zero crossings of filtered signal -> cycle boundaries
    zc=np.where(np.diff(np.sign(f))!=0)[0]
    rises=[]; decays=[]
    halfwin=int(fs/(hi)/2)+1   # search window ~ quarter period of fastest in band
    # between consecutive rising and falling zero crossings, refine extrema on RAW
    rising=zc[(f[zc+1]>f[zc])]   # upward crossings
    for i in range(len(rising)-1):
        a=rising[i]; b=rising[i+1]
        if b-a < 2 or b-a > fs/lo*1.5: continue   # reject non-physiological cycle lengths
        cyc=rawsig[a:b]
        pk=a+np.argmax(cyc); tr=a+np.argmin(cyc)
        if tr<pk:           # trough(build start)->peak->(next) ; ensure ordering within cycle
            rises.append((pk-tr)/fs)
            # decay = peak to next trough (search forward to next minimum)
            fwd=rawsig[pk:b]
            if len(fwd)>2: decays.append((np.argmin(fwd))/fs)
        else:
            decays.append((tr-pk)/fs)
    rises=[r for r in rises if r>0]; decays=[d for d in decays if d>0]
    if len(rises)<10 or len(decays)<10: return None
    return np.median(rises), np.median(decays), len(rises), len(decays)

results={}
for name,(lo,hi) in BANDS.items():
    r=rdsym(seg,lo,hi)
    if not r: results[name]={'ARA':None}; continue
    rise,decay,nr,nd=r
    results[name]={'rise_ms':round(rise*1000,2),'decay_ms':round(decay*1000,2),
        'ARA':round(decay/rise,4),'rdsym_rise_frac':round(rise/(rise+decay),3),
        'n_rise':nr,'n_decay':nd}

import json
print(json.dumps(results,indent=2))
print("\n--- EEG band ARA (raw-refined waveform asymmetry, real C4-A1) ---")
for k,v in results.items():
    if v.get('ARA'): print(f"{k:12s} ARA={v['ARA']:.3f}  rise {v['rise_ms']:.1f}ms / decay {v['decay_ms']:.1f}ms  (rdsym {v['rdsym_rise_frac']})  old >2")
