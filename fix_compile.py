import sys

file_path = "c:\\vscode\\movision_kr\\main\\main.c"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Remove s_touch_sem
content = content.replace("static SemaphoreHandle_t s_touch_sem = NULL;\n", "")

# Fix 2: Remove references to last_x, last_y, last_event in the "Clean Release" block
target_block = """  // No valid touch (Clean Release)
  if (start_x != -1 && !swiped) {
      int final_dx = last_x - start_x;
      int final_dy = last_y - start_y;
      // ESP_LOGI("TOUCH", "[CLEAN_RELEASE] Start: (%d, %d) -> End: (%d, %d) | Total dx: %d, dy: %d", 
      //          start_x, start_y, last_x, last_y, final_dx, final_dy);
      
      if (abs(final_dx) <= 15 && abs(final_dy) <= 30) {
           // ESP_LOGI("TOUCH", "[SWIPE_FAIL] Distance too short. Recognized as single touch (Tap).");
      } else {
           // ESP_LOGI("TOUCH", "[SWIPE_FAIL] Distance sufficient, but did not match strict swipe direction.");
      }
  }

  data->state = LV_INDEV_STATE_REL;
  start_x = -1;
  start_y = -1;
  swiped = false;
  // 릴리???last_x/y/event 초기??(?음 ?치????벤?로 ?식)
  last_x = 0xFFFF;
  last_y = 0xFFFF;
  last_event = 0xFF;"""

replace_block = """  data->state = LV_INDEV_STATE_REL;
  start_x = -1;
  start_y = -1;
  swiped = false;"""

# Using a simpler string replacement since the encoding/comments might not match perfectly
import re
pattern = re.compile(r"  // No valid touch \(Clean Release\).*?last_event = 0xFF;", re.DOTALL)
content = pattern.sub(replace_block, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixed")
