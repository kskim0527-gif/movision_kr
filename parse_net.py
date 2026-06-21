import sys

filename = r"C:\Users\kskim\내 드라이브\JOB\BSD-round\SCHnPCB\esp32\movision_R23\movisionR23.txt"
try:
    with open(filename, 'r', encoding='cp949', errors='replace') as f:
        lines = f.readlines()
        
    # Build netlist from *CONNECTION* and *SIGNAL*
    # Actually simpler: just find 'U1.xx' and what it's connected to.
    
    # 1. Map labels/offpages to signals
    label_to_sig = {}
    cur_sig = None
    for line in lines:
        if line.startswith('*SIGNAL*'):
            cur_sig = line.split()[1]
        elif cur_sig and '@@@' in line:
            for token in line.split():
                if token.startswith('@@@'):
                    label_to_sig[token] = cur_sig
                    
    # 2. Map U1 pins to labels
    u1_pins = {}
    for line in lines:
        if line.strip().startswith('U1.') and '@@@' in line:
            parts = line.strip().split()
            pin = parts[0].replace('U1.', '')
            for token in parts:
                if token.startswith('@@@'):
                    if token in label_to_sig:
                        u1_pins[pin] = label_to_sig[token]

    for pin in sorted(u1_pins.keys(), key=lambda x: int(x) if x.isdigit() else 0):
        print(f"Pin {pin}: {u1_pins[pin]}")

except Exception as e:
    print(e)
