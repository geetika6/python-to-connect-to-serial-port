
CONFIG_FILE = "/home/geetika/Documents/pilab_new/singleanalog.conf"
import serial
from serial_tools import Serial_Tools
from tools import *
import time
import const

class ScopeSingleAnalog(object):
    def __init__(self):
        """Serial Setup"""
        self.ser = None
        self.s_t = Serial_Tools(self.ser)
        self.s_t.show_messages = True
        self.config=self.load_configuration()

        self.state = self.s_find_device
        
        self.trace_size = const.SAMPLE_SIZE  # Samples
        print self.trace_size 
        self.extra_trace = const.EXTRA_SAMPLE_SIZE 
        self.whole_trace = self.trace_size + self.extra_trace
        self.dump_size = self.trace_size
        self.extra_dump = self.extra_trace
        self.whole_dump = self.dump_size + self.extra_dump
        
        self.write_buffer = ""
        
        self.buffer_size = 3 * 4096
        self.accepted_models=["BS0005", "BS0010"]
        self.trigger_level=const.TRIIGER_LEVEL
      #  """Data exposed through API"""
      #  self.data = {
      #      "device":{"connected":False, "model":None},
      #      "accepted_models":["BS0005", "BS0010"],
      #      "ch":{"active":{}},
      #      "trigger_level":32000,
      #      "trigger_display":0,
      #      "range_data":{"top":32000, "bot":0},
      #      "range":{"min":-5.8, "max":5.8, "high":4.0, "low":-1.0, "offset":1.5, "span":5.0},
      #      "timebase":{"min":15, "max":535, "value":40, "display":""},
      #      "current_channel":"a",
      #      "waveform":0,
      #      "symetry":32768,
      #      "symetry_percentage":50,
      #      "frequency":4,
      #      "on_time":0,
      #      "off_time":0
      #  }
      #          
      #  self.data['ch']['active'] = {
      #      "trace":[],
      #      "display_trace":[]
      #  }
      #  
      #  self.data['spock_option'] = [0,0,0,0,0,0,0,0] # This is BEian (7 -> 0)
        
    def load_configuration(self):
        """
        Loads the configuration file. The file's path
        is set using the "CONFIG_FILE" variable.
        """

        try:
            conf_file = open(CONFIG_FILE,"r")
        except IOError as (errno, strerr):
            print "Could not load config file at '%s': %s" % (CONFIG_FILE, strerr)
            sys.exit(1)
        config = conf_file.read()
        exec(config)
        return

    """ Utility States """
    def s_find_device(self):
        self.ser = self.s_t.find_device()
        if self.ser != None:
            self.device_connected = True
            self.state = self.s_check_model
            
        else:
            self.device_connected = True
            self.state = self.s_find_device

    def s_check_model(self):
        self.ser.read(10000) # Try to get anything in the buffer.
        self.s_t.clear_waiting() # Force the counter to reset.
        self.s_t.issue_wait("?")
        model = (self.ser.read(7)[1:7])
        print model
        self.device_model = model

        if model in self.accepted_models:
            self.state = self.s_setup_bs
            print self.device_model + " Connected."
        else:
            self.state = self.s_check_model
    
    """ States """
    def s_setup_bs(self):
        siw = self.s_t.issue_wait
        si = self.s_t.issue
        leh = l_endian_hexify
        #d = self.data
        print self.whole_dump
        print leh(self.whole_dump) # Dump size
        ### General ###
        siw("!") # Reset!
        si(
            "[1c]@[%s]sn[%s]s" % leh(self.whole_dump) # Dump size
            + "[1e]@[00]s" # Dump mode
            + "[21]@[00]s" # Trace mode
            + "[08]@[00]sn[00]sn[00]s" # Default spock address
            + "[16]@[01]sn[00]s" # Iterations to 1
            + "[2a]@[e0]sn[06]s" #% leh(self.whole_trace) # Post trig cap
            + "[30]@[00]s" # Dump channel
            + "[31]@[00]s" # Buffer mode
            + "[37]@[01]s" # Analogue chan enable
            + "[26]@[01]sn[00]s" # Pre trig capture
            + "[22]@[00]sn[00]sn[00]sn[00]s" # Trigger checking delay period.
            + "[2c]@[00]sn[0a]s" # Timeout
            + "[2e]@[28]sn[00]s"# % leh(d['timebase']['value']) # Set clock ticks
            + "[14]@[01]sn[00]s" # Clock scale

            ### Trigger ###
            + "[06]@[7f]s" # TriggerMask
            + "[05]@[80]s" # TriggerLogic
            + "[32]@[04]sn[00]s" # TriggerIntro
            + "[34]@[04]sn[00]s" # TriggerOutro
            + "[44]@[00]sn[00]s" # TriggerValue
            + "[68]@[f5]sn[68]s"# % leh(d['trigger_level'], 2) # TriggerLevel
            + "[07]@[21]s" #% leh(from_bin_array(d['spock_option']), 1) # SpockOption
            + "[64]@[28]s[65]@[1c]s"                     # ConvertorLo (set convertor range, low side)
            + "[66]@[c1]s[67]@[b5]s"                     # ConvertorHi (set convertor range, high side)
        )
        ### Range / Span ###
        #TODO high, low = to_span(d['range']['offset'], d['range']['span'], d['device']['model'])
        #si(
        #"[66]@[%s]sn[%s]s" % l_endian_hexify(high)
        #+ "[64]@[%s]sn[%s]s" % l_endian_hexify(low)
        #)
        
       # siw(
       #     # Translate
       #     "[47]@[00]s" # CV, Op Mode
       #     + "[4a]@[e8]sn[03]sn[00]sn[00]sn[00]sn[00]s" # Size, Index, Address
       #     + "[54]@[ff]sn[ff]sn[00]sn[00]s" # Level, Offset
       #     + "[5a]@[26]sn[31]sn[08]sn[00]s" # Phase Ratio
       #     + "X"
       # )
       # siw(
       #     # Generate
       #     "[48]@[f4]sn[80]s[52]@[e8]sn[03]s" # Option, Modulo
       #     + "[50]@[%s]sn[%s]s" % leh(self.freq_to_ticks()) # Clock ticks
       #     + "[5e]@[0a]sn[01]sn[01]sn[00]s" # Mark, Space
       #     + "[78]@[00]sn[7f]s" # Dac Output
       #     + "[46]@[02]s"
       #     + "Z"
       # )
        
        ### Update ###
        self.s_t.issue_wait(">")
        siw("U")
        self.s_t.clear_waiting()
        self.ser.flushInput()
        
        self.state = self.s_init_req
        
    def s_init_req(self):
        self.s_t.clear_waiting()
        self.ser.flushInput()
        self.s_t.issue_wait(">")
        self.s_t.issue("D")
        
        self.state = self.s_dump
        
    def s_dump(self):
        self.s_t.clear_waiting()
        self.ser.read(24)
        end_address = unhexify(self.ser.read(8))
        self.ser.read(1)
        start_address = ((end_address + self.buffer_size) - self.whole_trace) % self.buffer_size
        self.s_t.issue("[08]@[%s]sn[%s]sn[%s]s" % l_endian_hexify(start_address, 3))
        print "hex start add=","[%s][%s][%s]",l_endian_hexify(start_address, 3) 
        self.s_t.issue_wait(">")
        self.s_t.issue("A")
        self.state = self.s_proc_req
        
    def s_proc_req(self):
        self.s_t.clear_waiting()
        self.ser.read(self.extra_dump)
        self.received_data = convert_8bit_dump(self.ser.read(self.dump_size))
        print "received data=",self.received_data
        if self.write_buffer:
            self.s_t.issue(self.write_buffer)
            self.s_t.issue_wait("U")
            self.write_buffer = ""
        
        self.s_t.issue_wait(">")
        self.s_t.issue("D")
        
        self.state = self.s_dump
        
    """Data Processing Functions"""

    """Update Functions"""

    def update(self):
        try:
            self.state()
        except serial.SerialException:
            print "Device disconected | Error: SE"
            self.state = self.s_find_device
        except serial.SerialTimeoutException:
            print "Device disconected | Error: STE"
            self.state = self.s_find_device
