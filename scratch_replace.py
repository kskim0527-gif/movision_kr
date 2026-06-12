import sys

with open('main/main.c', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace address
old_addr = '// Touch Pins (CST816T I2C)\n#define TOUCH_I2C_ADDR 0x15\n#define TOUCH_I2C_FREQ_HZ 100000'
new_addr = '// Touch Pins (CST92xx I2C)\n#define TOUCH_I2C_ADDR 0x5A\n#define TOUCH_I2C_FREQ_HZ 100000'
content = content.replace(old_addr, new_addr)

# Find start and end of touch_read_cb
start_str = 'static void touch_read_cb(lv_indev_drv_t *indev_drv, lv_indev_data_t *data) {'
end_str = 'static void show_restart_msg(void) {'
start_idx = content.find(start_str)
end_idx = content.find(end_str)

if start_idx == -1 or end_idx == -1:
    print('Failed to find touch_read_cb bounds')
    sys.exit(1)

new_func = """static void touch_read_cb(lv_indev_drv_t *indev_drv, lv_indev_data_t *data) {
  static int start_x = -1;
  static int start_y = -1;
  static bool swiped = false;

  // Read buffer size: points * 5 + 5 overhead (safe size 20)
  uint8_t read_buf[20] = {0};
  uint8_t write_buf[3] = {0};

  // Reverted INT check to polling for better sensitivity (in case of missed
  // pulses)
  // 1. Read Command 0xD000
  write_buf[0] = (CST92XX_READ_COMMAND >> 8) & 0xFF;
  write_buf[1] = CST92XX_READ_COMMAND & 0xFF;

  // Reduced timeout or silent fail to avoid log spam on occasional glich
  if (i2c_master_transmit_receive(s_touch_dev_handle, write_buf, 2, read_buf,
                                  sizeof(read_buf),
                                  pdMS_TO_TICKS(50)) != ESP_OK) {
    // ESP_LOGW("TOUCH", "I2C Read Failed"); // Optional: uncomment if needed
    data->state = LV_INDEV_STATE_REL;
    start_x = -1;
    start_y = -1;
    swiped = false;
    return;
  }

  // 2. Send Handshake ACK: 0xD0 0x00 0xAB
  write_buf[2] = CST92XX_ACK;
  i2c_master_transmit(s_touch_dev_handle, write_buf, 3, pdMS_TO_TICKS(50));

  // 3. Verify Device ACK (Index 6)
  if (read_buf[6] != CST92XX_ACK) {
    // ESP_LOGW("TOUCH", "Invalid ACK: 0x%02X", read_buf[6]);
    data->state = LV_INDEV_STATE_REL;
    start_x = -1;
    start_y = -1;
    swiped = false;
    return;
  }

  // 4. Parse Data
  uint8_t point_count = read_buf[5] & 0x0F;

  if (point_count > 0 && point_count <= CST92XX_MAX_FINGER_NUM) {
    // Parse Point 0 (Index 0..4)
    // Structure: [id:4][pressed:4] [x_high] [y_high] [x_low:4][y_low:4]
    uint8_t pressed = read_buf[0] & 0x0F;
    if (pressed == 0x06 || pressed == 0x01 || pressed == 0x03) {
      uint16_t x = ((read_buf[1] << 4) | (read_buf[3] >> 4));
      uint16_t y = ((read_buf[2] << 4) | (read_buf[3] & 0x0F));

      data->state = LV_INDEV_STATE_PR;
      // Flip X and Y coordinates to resolve inverted touch input
      data->point.x = (LCD_H_RES - 1 - x);
      data->point.y = y;

      if (start_x == -1) {
        start_x = x;
        start_y = y;
        swiped = false;
        ESP_LOGI("TOUCH", "[PRESS] Start coordinate saved: (%d, %d)", start_x, start_y);
      } else if (!swiped) {
        int dx = x - start_x;
        int dy = y - start_y;

        // Horizontal Swipe (Mode Change) detection
        if (abs(dx) > abs(dy) && abs(dx) > 15) {
          ESP_LOGI("TOUCH", "========== SWIPE TRIGGERED ==========");
          ESP_LOGI("TOUCH", "Type: Software Drag");
          ESP_LOGI("TOUCH", "Start: (%d, %d) -> End: (%d, %d)", start_x, start_y, x, y);
          ESP_LOGI("TOUCH", "Distance: dx=%d, dy=%d", dx, dy);
          ESP_LOGI("TOUCH", "=====================================");

          // [User Request] Ignore ALL touch inputs in Virtual Drive mode
          if (s_virt_drive_active) {
            ESP_LOGI("TOUCH", "Horizontal touch ignored in Virtual Drive mode");
            swiped = true;
          } else {
            ESP_LOGI("TOUCH", "HORIZONTAL SWIPE: dx=%d dy=%d", dx, dy);
            // OTA 모드에서는 가로 스와이프 무시 (실수 방지)
            if (s_current_mode == DISPLAY_MODE_OTA) {
              swiped = true; // 다산, 메세지만 더이상 발생 안 함
            } else {
              int next_mode;
              if (dx > 0) { // Right to Left (Next)
                switch (s_current_mode) {
                case DISPLAY_MODE_GUIDE: next_mode = DISPLAY_MODE_CLOCK; break;
                case DISPLAY_MODE_CLOCK: next_mode = DISPLAY_MODE_ALBUM; break;
                case DISPLAY_MODE_ALBUM: next_mode = DISPLAY_MODE_SETTING; break;
                case DISPLAY_MODE_SETTING: next_mode = DISPLAY_MODE_GUIDE; break;
                default: next_mode = DISPLAY_MODE_GUIDE; break;
                }
              } else { // Left to Right (Prev)
                switch (s_current_mode) {
                case DISPLAY_MODE_GUIDE: next_mode = DISPLAY_MODE_SETTING; break;
                case DISPLAY_MODE_SETTING: next_mode = DISPLAY_MODE_ALBUM; break;
                case DISPLAY_MODE_ALBUM: next_mode = DISPLAY_MODE_CLOCK; break;
                case DISPLAY_MODE_CLOCK: next_mode = DISPLAY_MODE_GUIDE; break;
                default: next_mode = DISPLAY_MODE_GUIDE; break;
                }
              }

              if (next_mode == DISPLAY_MODE_ALBUM && s_current_mode != DISPLAY_MODE_ALBUM) {
                reset_album_to_default_image();
              }
              s_is_manual_mode_switch = true;
              switch_display_mode(next_mode);
              s_is_manual_mode_switch = false;
              swiped = true;
            }
          }
        }
        // Vertical Swipe
        else if (abs(dy) > abs(dx) && abs(dy) > 30) {
          if (s_virt_drive_active) {
            ESP_LOGI("TOUCH", "Vertical touch ignored in Virtual Drive mode");
            swiped = true;
          } else if (s_current_mode == DISPLAY_MODE_GUIDE) {
            ESP_LOGI("TOUCH", "Vertical swipe disabled in GUIDE mode");
            swiped = true;
          } else if (s_current_mode == DISPLAY_MODE_ALBUM) {
            if (dy < 0) load_image_from_sd(1);
            else load_image_from_sd(-1);
            swiped = true;
          } else if (s_current_mode == DISPLAY_MODE_CLOCK) {
            s_clock_option = (s_clock_option == 0) ? 1 : 0;
            ESP_LOGI("TOUCH", "Clock option toggled via vertical swipe: %d", s_clock_option);
            s_is_manual_mode_switch = true;
            switch_display_mode(DISPLAY_MODE_CLOCK);
            s_is_manual_mode_switch = false;
            swiped = true;
          } else if (s_current_mode == DISPLAY_MODE_BOOT) {
            uint32_t now = xTaskGetTickCount();
            if (s_secret_swipe_count == 0 || (now - s_secret_swipe_start_tick) > pdMS_TO_TICKS(10000)) {
              s_secret_swipe_count = 1;
              s_secret_swipe_start_tick = now;
              ESP_LOGI("TOUCH", "Secret Trigger: Swipe 1/5 detected (10s timer started)");
            } else {
              s_secret_swipe_count++;
              ESP_LOGI("TOUCH", "Secret Trigger: Swipe %d/5 detected", s_secret_swipe_count);
              if (s_secret_swipe_count >= 5) {
                ESP_LOGW("TOUCH", "SECRET TRIGGER ACTIVATED! Entering Virtual Drive...");
                toggle_virtual_drive(true);
                s_secret_swipe_count = 0;
              }
            }
            swiped = true;
          } else if (s_current_mode == DISPLAY_MODE_SETTING) {
            setting_page_cb(NULL);
            swiped = true;
          } else if (s_current_mode == DISPLAY_MODE_OTA) {
            s_is_manual_mode_switch = true;
            switch_display_mode(DISPLAY_MODE_SETTING);
            s_is_manual_mode_switch = false;
            swiped = true;
          }
        }
      }
      return;
    }
  }

  // No valid touch
  data->state = LV_INDEV_STATE_REL;
  start_x = -1;
  start_y = -1;
  swiped = false;
}

"""

content = content[:start_idx] + new_func + content[end_idx:]

with open('main/main.c', 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully replaced touch configurations in main.c!")
