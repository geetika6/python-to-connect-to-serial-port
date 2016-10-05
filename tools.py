from struct import *
import time
from math import *

# No checks! Does a straight copy of the whole tree!
def copy_dict(src, dest):
    for key in src.keys():
        if isinstance(src[key], dict):
            dest[key] = {}
            copy_dict(src[key], dest[key])
        elif isinstance(src[key], list):
            dest[key] = list(src[key])
        else:
            dest[key] =  src[key]

def l_endian_hexify(dec, bytes = 2):
    hd = bytes * 2
    b = hex(dec) # Turn into hex
    b = b[2:] # Take the 0x off
    b = ("0" * (hd - len(b)) + b) # Append needed "0"s
    ls = []
    if len(b) > hd:
        print dec, "too big for the", bytes,"byte(s) requested."
    else:
        for byte in range(hd, 0, -2):
            ls.append(b[byte-2:byte])
        return tuple(ls)
        
def unhexify(hex_n):
    return int(hex_n, 16)

def convert_12bit_bin_dump(dump):
    dump_len = len(dump)
    dump_len_arg = ">" + str(dump_len / 2) + "h"
    return unpack(dump_len_arg, dump)

def convert_8bit_dump(dump):
    return map(ord, dump)
    
def convert_logic_dump(dump):
    bin_ls = []
    bin_ls = map(num_to_bin, map(ord, dump))
    return bin_ls
    
def convert_logic_to_streams(input, output):
    if input:
        for stream in range(len(output)):
            t = []
            for sample in input:
                t.append(int(sample[stream]))
            output[stream] = t
    
def float_range(start, stop, step):
    mult = 100000
    start = int(start * mult)
    stop = int(stop * mult)
    step = int(step * mult)
    return [float(x) / mult for x in xrange(start, stop, step)]

def num_to_bin(num):
    # Start at 128
    div = 128
    bin = []
    while div != 0:
        bit = 0
        if num >= div:
            # No need for an if statement, just multiply div by bit and then subtract.
            bit = 1
            num -= div
        bin.append(bit)
        div /= 2
        
    return bin
    
def to_span(offset, scale, model="BS0005"):
    offset = -offset # Invert for good luck.
    d = 16.0 # Impedance min
    f = 12.0 # Impedance scaling
    b = 300.0 # Divider resister value
    m = 65536 # Register size
    # Offset and range (normalised)
    ref_range = 18.3
    ref_offset = 0.41
    ground = 0.0
    o = ref_offset - (offset - ground) / ref_range
    r = scale / ref_range
    
    h = o + r / 2 # A/D ref voltage (high)
    l = o - r / 2 # A/D ref voltage (low)
    if model == "BS0005":
        ah = 2 * h - 1; ah = d + f * ah * ah # D/A impedance (high)
        al = 1 - 2 * l; al = d + f * al * al # D/A impedance (low)
        dh = ((b + 2 * ah) * h - ah * (l + 1)) / b # D/A voltage (high)
        dl = ((b + 2 * al) * l - al * h) / b # D/A voltage (low)
        
        fv_hi = ensure_range(dh, dl, 1) # Register value (high)
        fv_lo = ensure_range(dl, 0, dh) # Register value (low)
        
    elif model == "BS0010":
        fv_hi = ensure_range(h, l, 1) # Register value (high)
        fv_lo = ensure_range(l, 0, h) # Register value (low)
    
    # One last correction
    fv_hi = int(round(fv_hi * m, 0)) - 1
    fv_lo = int(round(fv_lo * m, 0))
    return fv_hi, fv_lo
    
def ensure_range(num, minimum, maximum):
    if num > minimum and num < maximum:
        return num
    elif num >= maximum:
        return maximum
    elif num <= minimum:
        return minimum
        
def increment(value, inc, minimum, maximum):
    newValue = value + inc
    newValue = ensure_range(newValue, minimum, maximum)
    
    changed = newValue != value
    
    return newValue, changed
        
def to_range(val, from_range, to_range):
    fr = from_range
    tr = to_range
    slope = float(tr[1] - tr[0]) / float(fr[1] - fr[0])
    output = tr[0] + slope * float(val - fr[0])
    return output

def from_bin_array(bits):
    new_bits = (8 - len(bits)) * "0"
    for bit in bits:
        new_bits += str(int(bit))
    
    return int(new_bits, 2)

def freq_to_intervals(khz): # DEPRECATED; use function below and divide by 25
    # Convert to Hz
    speed = khz * 1000
    # Convert to 25ns intervals
    return int((speed ** -1) / 0.000000025)
    
def freq_to_ns(khz):
    # Convert to ns
    return (khz ** -1) * 1000000
    
def inc_125_pattern(num, inc):
    """ 1, 2, 5, 10 pattern helper. """
    sn = str(num).replace("0", "").replace(".", "")
    if inc > 0:
        if sn[0] == "2":
            num *= 2.5
        else:
            num += num
    if inc < 0:
        if sn[0] == "5":
            num *= 0.4
        else:
            num *= 0.5
    return num

def snap_to_125_pattern(num):
    """ Snap number to 1, 2, 5, 10 sequence """
    multCount = 0
    while num < 1:
        num *= 10.0
        multCount += 1
    divCount = 0
    while num >= 10:
        num *= 0.1
        divCount += 1
    num = round(num, 0)
    if num == 3:
        num = 2
    elif num == 4 or 6 <= num <= 7:
        num = 5
    elif 8 <= num <= 9:
        num = 10        
    
    num = num * (10 ** divCount)
    num = num * (10 ** -multCount)
    return num
    
def inc_exponent_pattern(num, inc):
    multCount = 0
    divCount = 0
    if num != 0:
        while num < 1:
            num *= 10.0
            multCount += 1
        while num >= 10:
            num *= 0.1
            divCount += 1
    else:
        inc = inc * 0.1
        
    if num + inc < 1.0:
        inc = inc * 0.1
    num += inc
    num = num * (10 ** divCount)
    num = num * (10 ** -multCount)
    
    return num
    
def snap_to_exponent_pattern(num):
    multCount = 0
    divCount = 0
    if num != 0:
        while num < 1:
            num *= 10.0
            multCount += 1
        while num >= 10:
            num *= 0.1
            divCount += 1
    else:
        return num
    
    if num >= 5:
        num = 10
    else:
        num = 1
        
    num = num * (10 ** divCount)
    num = num * (10 ** -multCount)
    
    return num

def round_to_n(value, n):
    neg_zeroes = -int(floor(log10(abs(value))))
    return round(value, neg_zeroes + (n - 1))
