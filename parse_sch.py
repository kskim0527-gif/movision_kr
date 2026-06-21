import sys

filename = r"C:\Users\kskim\내 드라이브\JOB\BSD-round\SCHnPCB\esp32\movision_R23\movisionR23.txt"
try:
    with open(filename, 'r', encoding='cp949', errors='replace') as f:
        lines = f.readlines()
        
    parts_section = False
    parts = []
    
    for line in lines:
        line = line.strip()
        if line.startswith('*PART'):
            parts_section = True
            continue
        elif line.startswith('*') and len(line) > 1 and parts_section:
            parts_section = False
            
        if parts_section and line:
            parts.append(line)
            
    print("Parts section lines:", len(parts))
    for p in parts[:20]:
        print(p)
        
    # extract part types
    types = set()
    for p in parts:
        tokens = p.split()
        if len(tokens) >= 2:
            types.add(tokens[1])
    print("\nUnique Part Types:")
    for t in sorted(list(types)):
        print(t)
        
except Exception as e:
    print(f"Error: {e}")
