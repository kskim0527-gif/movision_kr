// board_config.h - R23 Hardware Pinout (docs/movisionR23.txt)
#ifndef BOARD_CONFIG_H
#define BOARD_CONFIG_H
#include "driver/gpio.h"

// LCD Pin Definitions (SH8601 QSPI AMOLED)
#define PIN_NUM_LCD_CS    (GPIO_NUM_9)   // U1 Pin 14
#define PIN_NUM_LCD_PCLK  (GPIO_NUM_10)  // U1 Pin 15 (QSPI_SCL)
#define PIN_NUM_LCD_DATA0 (GPIO_NUM_11)  // U1 Pin 16 (QSPI_D0)
#define PIN_NUM_LCD_DATA1 (GPIO_NUM_12)  // U1 Pin 17 (QSPI_D1)
#define PIN_NUM_LCD_DATA2 (GPIO_NUM_13)  // U1 Pin 18 (QSPI_D2)
#define PIN_NUM_LCD_DATA3 (GPIO_NUM_14)  // U1 Pin 19 (QSPI_D3)
#define PIN_NUM_LCD_RST   (GPIO_NUM_8)   // U1 Pin 13
#define PIN_NUM_LCD_TE    (GPIO_NUM_17)  // U1 Pin 23
#define PIN_NUM_LCD_VCI_EN (GPIO_NUM_NC) // Power hardwired to VDD3V3

// Touch Pins (CST92xx I2C Touch)
#define PIN_TOUCH_SDA GPIO_NUM_6         // U1 Pin 11
#define PIN_TOUCH_SCL GPIO_NUM_7         // U1 Pin 12
#define PIN_TOUCH_INT GPIO_NUM_4         // U1 Pin 9
#define PIN_TOUCH_RST GPIO_NUM_5         // U1 Pin 10

// Ambient Light Sensor (LDR RC Circuit)
#define PIN_NUM_LDR       GPIO_NUM_38    // U1 Pin 43 (Net LD_IN)
#define PIN_NUM_LD_IN     PIN_NUM_LDR
#endif
