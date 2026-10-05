import sys
import os

BOARD_CONFIG_FILE = "main/board_config.h"

R23_PINS = """// board_config.h - R23 Hardware Pinout (docs/movisionR23.txt)
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
"""

B0223_PINS = """// board_config.h - movision (0223 Legacy Hardware)
#ifndef BOARD_CONFIG_H
#define BOARD_CONFIG_H
#include "driver/gpio.h"

// LCD Pin Definitions
#define PIN_NUM_LCD_CS    (GPIO_NUM_14)
#define PIN_NUM_LCD_PCLK  (GPIO_NUM_7)
#define PIN_NUM_LCD_DATA0 (GPIO_NUM_8)
#define PIN_NUM_LCD_DATA1 (GPIO_NUM_13)
#define PIN_NUM_LCD_DATA2 (GPIO_NUM_6)
#define PIN_NUM_LCD_DATA3 (GPIO_NUM_12)
#define PIN_NUM_LCD_RST   (GPIO_NUM_9)
#define PIN_NUM_LCD_TE    (GPIO_NUM_NC)
#define PIN_NUM_LCD_VCI_EN (GPIO_NUM_18)

// Touch Pins
#define PIN_TOUCH_SDA GPIO_NUM_10
#define PIN_TOUCH_SCL GPIO_NUM_17
#define PIN_TOUCH_INT GPIO_NUM_11
#define PIN_TOUCH_RST GPIO_NUM_15

// Ambient Light Sensor (LDR)
#define PIN_NUM_LDR       GPIO_NUM_38
#define PIN_NUM_LD_IN     PIN_NUM_LDR
#endif
"""

WS_PINS = """// board_config.h - Waveshare ESP32-S3-Touch-AMOLED-1.8
#ifndef BOARD_CONFIG_H
#define BOARD_CONFIG_H
#include "driver/gpio.h"

// LCD Pin Definitions
#define PIN_NUM_LCD_CS    (GPIO_NUM_12)
#define PIN_NUM_LCD_PCLK  (GPIO_NUM_38)
#define PIN_NUM_LCD_DATA0 (GPIO_NUM_4)
#define PIN_NUM_LCD_DATA1 (GPIO_NUM_5)
#define PIN_NUM_LCD_DATA2 (GPIO_NUM_6)
#define PIN_NUM_LCD_DATA3 (GPIO_NUM_7)
#define PIN_NUM_LCD_RST   (GPIO_NUM_39)
#define PIN_NUM_LCD_TE    (GPIO_NUM_18)
#define PIN_NUM_LCD_VCI_EN (GPIO_NUM_18)

// Touch Pins
#define PIN_TOUCH_SDA GPIO_NUM_15
#define PIN_TOUCH_SCL GPIO_NUM_14
#define PIN_TOUCH_INT GPIO_NUM_11
#define PIN_TOUCH_RST GPIO_NUM_40
#endif
"""

def apply_config(board_type="mp"):
    b = str(board_type).lower()
    if b in ["kr", "movision_kr", "r23", "movision_r23", "movision"]:
        content = R23_PINS
        target_name = "Movision_kr (R23: LCD CS=9, PCLK=10, DATA=11..14, RST=8, Touch=6,7,4,5)"
    elif b in ["mp", "movision_mp", "0223", "b0223", "movision_0223", "legacy", "default"]:
        content = B0223_PINS
        target_name = "movision_mp (0223: LCD CS=14, PCLK=7, DATA=8,13,6,12, RST=9, Touch=10,17,11,15)"
    elif b in ["ws", "waveshare", "hd1", "movision_ws"]:
        content = WS_PINS
        target_name = "movision_ws (Waveshare Dev Board: GPIO 12, 38, 4..7)"
    else:
        print(f"Unknown board type: {board_type}")
        return False
    
    with open(BOARD_CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Applied {target_name} pin configuration to {BOARD_CONFIG_FILE}")
    return True

if __name__ == "__main__":
    board = sys.argv[1] if len(sys.argv) > 1 else "mp"
    apply_config(board)


