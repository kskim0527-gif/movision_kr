import sys
import re

filename = r"C:\Users\kskim\내 드라이브\JOB\BSD-round\SCHnPCB\esp32\movision_R23\movisionR23.txt"
try:
    with open(filename, 'r', encoding='cp949', errors='replace') as f:
        lines = f.readlines()
        
    for i, line in enumerate(lines):
        if line.startswith('*PART'):
            print(f"Found {line.strip()} at line {i}")
            for j in range(i+1, min(i+100, len(lines))):
                if lines[j].startswith('*'):
                    break
                if lines[j].strip():
                    print(lines[j].strip())
            break
except Exception as e:
    print(e)
