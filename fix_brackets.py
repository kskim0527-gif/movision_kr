import sys

file_path = "c:\\vscode\\movision_kr\\main\\main.c"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = """      return;
    }

  // No valid touch (Clean Release)"""

replace = """      return;
    }
  }

  // No valid touch (Clean Release)"""

if target in content:
    content = content.replace(target, replace)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed")
else:
    print("Target not found")
