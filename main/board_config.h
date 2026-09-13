// board_config.h - movisionR23 Schematic Board Pinout
#ifndef BOARD_CONFIG_H
#define BOARD_CONFIG_H
#include "driver/gpio.h"

// LCD Pin Definitions (movisionR23 schematic)
#define PIN_NUM_LCD_CS    (GPIO_NUM_9)   // U1 Pin 14 (GPIO9)
#define PIN_NUM_LCD_PCLK  (GPIO_NUM_10)  // U1 Pin 15 (GPIO10 / QSPI_SCL)
#define PIN_NUM_LCD_DATA0 (GPIO_NUM_11)  // U1 Pin 16 (GPIO11 / QSPI_D0)
#define PIN_NUM_LCD_DATA1 (GPIO_NUM_12)  // U1 Pin 17 (GPIO12 / QSPI_D1)
#define PIN_NUM_LCD_DATA2 (GPIO_NUM_13)  // U1 Pin 18 (GPIO13 / QSPI_D2)
#define PIN_NUM_LCD_DATA3 (GPIO_NUM_14)  // U1 Pin 19 (GPIO14 / QSPI_D3)
#define PIN_NUM_LCD_RST   (GPIO_NUM_8)   // U1 Pin 13 (GPIO8)
#define PIN_NUM_LCD_TE    (GPIO_NUM_17)  // U1 Pin 23 (GPIO17)
#define PIN_NUM_LCD_VCI_EN (GPIO_NUM_17)

// Touch Pins (movisionR23 schematic)
#define PIN_TOUCH_SDA GPIO_NUM_6   // U1 Pin 11 (GPIO6)
#define PIN_TOUCH_SCL GPIO_NUM_7   // U1 Pin 12 (GPIO7)
#define PIN_TOUCH_INT GPIO_NUM_4   // U1 Pin 9  (GPIO4)
#define PIN_TOUCH_RST GPIO_NUM_5   // U1 Pin 10 (GPIO5)
#endif

