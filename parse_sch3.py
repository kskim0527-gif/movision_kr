import sys
import re

filename = r"C:\Users\kskim\내 드라이브\JOB\BSD-round\SCHnPCB\esp32\movision_R23\movisionR23.txt"
try:
    with open(filename, 'r', encoding='cp949', errors='replace') as f:
        lines = f.readlines()
        
    part_lines = []
    in_part = False
    for line in lines:
        if line.strip() == '*PART*':
            in_part = True
            continue
        if in_part and line.startswith('*'):
            break
        if in_part and line.strip():
            part_lines.append(line.strip())
            
    print(f"Found {len(part_lines)} parts.")
    for p in part_lines[:20]:
        print(p)
    print("...")
    
    types = {}
    for p in part_lines:
        tokens = p.split()
        if len(tokens) >= 2:
            ptype = tokens[1]
            types[ptype] = types.get(ptype, 0) + 1
            
    print("\nPart Types Summary:")
    for t, c in sorted(types.items()):
        print(f"{t}: {c}")
except Exception as e:
    print(e)
