**Steps to code Bitscope Virtual Machine regardless of the language and library functions used**


Bitscope understands a set of characters to trigger its modes.The aim is to connect to the serial port and detect the Bitscope
 and then start sending these strings to Bitscope in the correct order which always follows a familiar sequence:
(1) Initialize -> (2) Setup -> (3) Trace <=> (4) Acquire -> (5) Stop
                                        
The double arrow between 4 and 5 shows that the state keeps switching back and forth if multiple sample acquisitions are needed.


###DETAILED DESCRIPTION
1. **Trace Config Settings** :Settings for Tracebuffer, channels , offset, trigger etc.
2. After the register values are assigned, the Spock (>) and configuration (U) commands are normally used to set up the high speed data acquisition hardware
    and to configure signal ranges and other features for the pending trace. 
3. The D command is then issued to commence the trace for x number of samples.
4. When Bitscope completes the trace it returns Status Packets which mostly has the buffer sample address and one or more timestamps to report when the trace commenced and when it completed (which depends on specified trigger and/or timeout values)[More_Detail](https://docs.google.com/document/d/1cZNRpSPAMyIyAvIk_mqgEByaaHzbFTX8hWglAMTlnHY/edit#heading=h.yhkb2o8pro0j).
    It traces from trigger to x number of samples.
5. As a user you need to calculate start address which is = end add - x samples %(modulus) by the buffer memory used (depending upon trace mode used)
6. **Dump/Acquire config Settings** : Settings for Buffer Mode,Dump buffer,Repeat, etc
7. After the dump settings are provided, the Spock (>) command is used.
8. The A command is then issued to commence the acquisition of x number of samples after trigger is detected.


**The different modes can be:

A. Single Analog
B. Dual Analog
C. Mixed (1XAnalog and Digital)
D. Mixed (2XAnalog and Digital)
E. Streaming ( 1XAnalog, 1XAnallog + Logic , 2XAnalog and Digital)
F. Waveform Generator**
 
-----

**A. CHANNEL A -ANALOG**
**1. Trace Config Settings**

     Add                                      Field       - Comments
     [37]@[01]s                               # AnalogAnable (enable CHA input circuits)
     [7b]@[80]s                               # KitchenSinkA (enable hardware comparators)
     [7c]@[80]s                               # KitchenSinkB (enable analog filter)
     [fb]@[00]s                               # LedLevelGRN (turn CHB LED off, VM10 only)
     [fc]@[c0]s                               # LedLevelYEL (turn CHA LED on, VM10 only)
     [64]@[28]s[65]@[1c]s                     # ConvertorLo (set convertor range, low side)
     [66]@[c1]s[67]@[b5]s                     # ConvertorHi (set convertor range, high side)
     [14]@[01]s[15]@[00]s                     # ClockScale (set clock prescaler)
     [2e]@[28]s[2f]@[00]s                     # ClockTicks (set clock divider)
     [31]@[00]s                               # BufferMode (choose the capture buffer mode)
     [21]@[00]s                               # TraceMode (choose the trace mode)
     [22]@[00]s[23]@[00]s[24]@[00]s[25]@[00]s # TraceDelay (set post trigger delay)
     [26]@[80]s[27]@[00]s                     # TraceIntro (set pre-trigger capture count)
     [2a]@[e0]s[2b]@[06]s                     # TraceOutro (set post-trigger capture count)
     [06]@[7f]s                               # TriggerMask (set the trigger logic mask)
     [05]@[80]s                               # TriggerLogic (program the trigger logic)
     [32]@[04]s[33]@[00]s                     # TriggerIntro (set trigger hold-off filter duration)
     [34]@[04]s[35]@[00]s                     # TriggerOutro (set trigger hold-on filter duration)
     [44]@[00]s[45]@[00]s                     # TriggerValue (set digital trigger level, optional)
     [68]@[f5]s[69]@[68]s                     # TriggerLevel (set analog trigger level)
     [07]@[21]s                               # SpockOption (choose edge triggered comparator mode)
     [2c]@[00]s[2d]@[00]s                     # Timeout (specify a timeout, ¿forever¿ in this case)
     [3a]@[00]s[3b]@[00]s                     # Prelude (set the buffer default value; ¿zero¿)
     [08]@[00]s[09]@[00]s[0a]@[00]s           # SampleAddress (assign the trace start address)
     >                                        # (program capture hardware registers)
     U                                        # (programming other hardware registers)
     D                                        # commence the trace!  


**6. Dump Config Settings:**
Eg:  In this case we dump 128(0X80) samples about the trigger point.

     Add                                      Field       - Comments
     [31]@[00]s                               # BufferMode (selected buffer mode)
     [08]@[cc]s[09]@[00]s[0a]@[00]s           # SampleAddress (assign the dump start address)
     [1e]@[00]s                               # DumpMode (dump mode, raw in this case)
     [30]@[00]s                               # DumpChan (channel selected to dump)
     [1c]@[80]s[1d]@[00]s                     # DumpCount (samples to dump, 128 in this case)
     [16]@[01]s[17]@[00]s                     # DumpRepeat (number of times to repeat the dump)
     [18]@[01]s[19]@[00]s                     # DumpSend (points per sample, N/A in this case)
     [1a]@[ff]s[1b]@[ff]s                     # DumpSkip (points per skip, N/A in this case)
     >                                        # (program capture hardware registers)
     A                                        # (commence the data dump)


**B. DUAL CHANNEL (A and B) -ANALOG **
**1. Trace Config Settings**

      Add                                      Field       - Comments
      [37]@[03]s                               # AnalogAnable (enable CHA and CHB input circuits)**
      [7b]@[80]s                               # KitchenSinkA (enable hardware comparators)
      [7c]@[00]s                               # KitchenSinkB (disable analog filter)**
      [fb]@[40]s                               # LedLevelGRN (turn CHB LED on, VM10 only)**
      [fc]@[c0]s                               # LedLevelYEL (turn CHA LED on, VM10 only)
      [64]@[6a]s[65]@[22]s                     # ConvertorLo (set convertor range, low side)
      [66]@[95]s[67]@[ab]s                     # ConvertorHi (set convertor range, high side)
      [14]@[01]s[15]@[00]s                     # ClockScale (set clock prescaler)
      [2e]@[28]s[2f]@[00]s                     # ClockTicks (set clock divider)**
      [31]@[01]s                               # BufferMode (choose the capture buffer mode)**
      [21]@[10]s                               # TraceMode (choose the trace mode)**
      [22]@[00]s[23]@[00]s[24]@[00]s[25]@[00]s # TraceDelay (set post trigger delay)
      [26]@[80]s[27]@[01]s                     # TraceIntro (set pre-trigger capture count)**
      [2a]@[88]s[2b]@[13]s                     # TraceOutro (set post-trigger capture count)**
      [06]@[7f]s                               # TriggerMask (set the trigger logic mask)
      [05]@[80]s                               # TriggerLogic (program the trigger logic)
      [32]@[04]s[33]@[00]s                     # TriggerIntro (set trigger hold-off filter duration)
      [34]@[04]s[35]@[00]s                     # TriggerOutro (set trigger hold-on filter duration)
      [44]@[00]s[45]@[00]s                     # TriggerValue (set digital trigger level, optional)
      [68]@[f5]s[69]@[68]s                     # TriggerLevel (set analog trigger level)
      [07]@[21]s                               # SpockOption (choose edge triggered comparator mode)
      [2c]@[35]s[2d]@[0c]s                     # Timeout (specify a timeout, ¿forever¿ in this case)**
      [3a]@[00]s[3b]@[00]s                     # Prelude (set the buffer default value; ¿zero¿)
      [08]@[00]s[09]@[00]s[0a]@[00]s           # SampleAddress (assign the trace start address)
      >                                        # (program capture hardware registers)
      U                                        # (programming other hardware registers)
      D                                        # commence the trace!  
      ** - The string commands marked with ** have been changed in B(Dual Mode) relative to A (Single Mode)

**6. Dump Config Settings:**
Eg:  In this case we dump 128(0X80) samples about the trigger point.

     Add                                      Field       - Comments
     [31]@[00]s                               # BufferMode (selected buffer mode)
     [08]@[cc]s[09]@[00]s[0a]@[00]s           # SampleAddress (assign the dump start address)
     [1e]@[00]s                               # DumpMode (dump mode, raw in this case)
     [30]@[00]s                               # DumpChan (channel selected to dump)
     [1c]@[80]s[1d]@[00]s                     # DumpCount (samples to dump, 128 in this case)
     [16]@[01]s[17]@[00]s                     # DumpRepeat (number of times to repeat the dump)
     [18]@[01]s[19]@[00]s                     # DumpSend (points per sample, N/A in this case)
     [1a]@[ff]s[1b]@[ff]s                     # DumpSkip (points per skip, N/A in this case)
     >                                        # (program capture hardware registers)
     A                                        # (commence the data dump)

 
[TraceBuffer_setting](https://docs.google.com/document/d/1cZNRpSPAMyIyAvIk_mqgEByaaHzbFTX8hWglAMTlnHY/edit#heading=h.bjsr0s4hrvp0)


  - Depending upon the frequency of the sample , the time period of the sample will be determined since the size of the buffer is limited to 12K.
  - The Maximum freq which can be obtained is 20 MHz if single analog mode is selected.This frequency reduces further if digital or second analog channel is enabled ,
    since the buffer gets distributed and the bitscope uses its sampling frequency to capture other channels in the same time , this happens in the foll way :
    [shown in Table](https://docs.google.com/document/d/1cZNRpSPAMyIyAvIk_mqgEByaaHzbFTX8hWglAMTlnHY/edit#heading=h.bjbbl5xj0doh)
  - Usually the requested and returned value for the sample size and rate will be the same but if you run up against the device constraints they may be different. 
    Further, there are situations where changing one parameter (e.g. channel enable or trace mode) can alter the constraints that apply to others (e.g. sample rate or trace size).
    The general rule is, if device setup parameters are changed some trace parameters may need to be reprogrammed. Follow the recommended programming sequence to avoid any confusion.



 
