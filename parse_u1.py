import sys

filename = r"C:\Users\kskim\내 드라이브\JOB\BSD-round\SCHnPCB\esp32\movision_R23\movisionR23.txt"
try:
    with open(filename, 'r', encoding='cp949', errors='replace') as f:
        lines = f.readlines()
        
    cur_sig = None
    u1_pins = {}
    for line in lines:
        if line.startswith('*SIGNAL*'):
            tokens = line.split()
            if len(tokens) >= 2:
                cur_sig = tokens[1]
        elif line.strip().startswith('U1.'):
            # line example: U1.43     @@@D26       2 0
            tokens = line.strip().split()
            pin_token = tokens[0] # U1.43
            if '.' in pin_token:
                pin = pin_token.split('.')[1]
                u1_pins[pin] = cur_sig
                
    for pin in sorted(u1_pins.keys(), key=lambda x: int(x) if x.isdigit() else 0):
        print(f"Pin {pin}: {u1_pins[pin]}")

except Exception as e:
    print(e)
