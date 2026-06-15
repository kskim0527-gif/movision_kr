import sys
import re

file_path = "c:\\vscode\\movision_kr\\main\\main.c"
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target1 = """    s_touch_indev = lv_indev_drv_register(&indev_drv);
    if (s_touch_indev && s_touch_indev->driver && s_touch_indev->driver->read_timer) {
        lv_timer_pause(s_touch_indev->driver->read_timer);
    }
  }"""
replace1 = """    s_touch_indev = lv_indev_drv_register(&indev_drv);
  }"""
content = content.replace(target1, replace1)

pattern = re.compile(
    r"static void IRAM_ATTR touch_isr_handler\(void \*arg\) \{.*?uint8_t gesture = read_buf\[1\]; // CHSC6413 clone puts Gesture ID in \[1\]",
    re.DOTALL
)

replacement2 = """static esp_err_t init_touch(void) {
  i2c_master_bus_config_t i2c_bus_conf = {
      .clk_source = I2C_CLK_SRC_DEFAULT,
      .i2c_port = I2C_NUM_0,
      .scl_io_num = PIN_TOUCH_SCL,
      .sda_io_num = PIN_TOUCH_SDA,
      .glitch_ignore_cnt = 7,
      .flags.enable_internal_pullup = true,
  };
  esp_err_t ret = i2c_new_master_bus(&i2c_bus_conf, &s_i2c_bus_handle);
  if (ret != ESP_OK)
    return ret;

  i2c_device_config_t dev_conf = {
      .dev_addr_length = I2C_ADDR_BIT_LEN_7,
      .device_address = TOUCH_I2C_ADDR,
      .scl_speed_hz = TOUCH_I2C_FREQ_HZ,
  };
  ret = i2c_master_bus_add_device(s_i2c_bus_handle, &dev_conf,
                                  &s_touch_dev_handle);
  if (ret != ESP_OK)
    return ret;

  gpio_config_t rst_gpio_conf = {.mode = GPIO_MODE_OUTPUT,
                                 .pin_bit_mask = 1ULL << PIN_TOUCH_RST};
  gpio_config(&rst_gpio_conf);
  gpio_set_level(PIN_TOUCH_RST, 0);
  vTaskDelay(pdMS_TO_TICKS(20));
  gpio_set_level(PIN_TOUCH_RST, 1);
  vTaskDelay(pdMS_TO_TICKS(100));

  // Configure Touch INT pin as input (Polling mode for CST92xx)
  gpio_config_t int_gpio_conf = {.mode = GPIO_MODE_INPUT,
                                 .pin_bit_mask = 1ULL << PIN_TOUCH_INT,
                                 .pull_up_en = GPIO_PULLUP_ENABLE,
                                 .pull_down_en = GPIO_PULLDOWN_DISABLE,
                                 .intr_type = GPIO_INTR_DISABLE};
  gpio_config(&int_gpio_conf);

  ESP_LOGI(TAG, "Touch initialization successful (CST92xx)");
  return ESP_OK;
}

static void touch_read_cb(lv_indev_drv_t *indev_drv, lv_indev_data_t *data) {
  static int start_x = -1;
  static int start_y = -1;
  static bool swiped = false;

  // Read buffer size: points * 5 + 5 overhead (safe size 20)
  uint8_t read_buf[20] = {0};
  uint8_t write_buf[3] = {0};

  write_buf[0] = (CST92XX_READ_COMMAND >> 8) & 0xFF;
  write_buf[1] = CST92XX_READ_COMMAND & 0xFF;

  if (i2c_master_transmit_receive(s_touch_dev_handle, write_buf, 2, read_buf,
                                  sizeof(read_buf),
                                  pdMS_TO_TICKS(50)) != ESP_OK) {
    data->state = LV_INDEV_STATE_REL;
    start_x = -1;
    start_y = -1;
    swiped = false;
    return;
  }

  write_buf[2] = CST92XX_ACK;
  i2c_master_transmit(s_touch_dev_handle, write_buf, 3, pdMS_TO_TICKS(50));

  if (read_buf[6] != CST92XX_ACK) {
    data->state = LV_INDEV_STATE_REL;
    start_x = -1;
    start_y = -1;
    swiped = false;
    return;
  }

  uint8_t point_count = read_buf[5] & 0x0F;

  if (point_count > 0 && point_count <= CST92XX_MAX_FINGER_NUM) {
    uint8_t pressed = read_buf[0] & 0x0F;
    if (pressed == 0x06) {
      uint16_t x = ((read_buf[1] << 4) | (read_buf[3] >> 4));
      uint16_t y = ((read_buf[2] << 4) | (read_buf[3] & 0x0F));
      
      data->state = LV_INDEV_STATE_PR;
      data->point.x = (LCD_H_RES - 1 - x);
      data->point.y = y;

      int dx = 0;
      int dy = 0;
      bool do_swipe_check = false;

      uint8_t gesture = 0; // Force software swipe tracking"""

content = pattern.sub(replacement2, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Done")
