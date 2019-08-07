import gc

import ssd1306
import sh1106
import utime
import gfx

from machine import I2C, Pin, SPI

oled_reset_pin = Pin(16, Pin.OUT)
oled_reset_pin.value(1)

spi = SPI(1, baudrate=20000000)

display = sh1106.SH1106_SPI(128, 64, spi, dc=Pin(26), res=oled_reset_pin, cs=Pin(5))
utime.sleep(1)

display.sleep(False)
display.rotate(1)
utime.sleep(1)

i2c = I2C(scl=Pin(15), sda=Pin(4))

oled = ssd1306.SSD1306_I2C(128, 64, i2c)
utime.sleep(1)

graphics = gfx.GFX(128, 64, oled.pixel)
graphics1 = gfx.GFX(128, 64, display.pixel)

oled.fill(0)
oled.text('oled init',0,0,1)
graphics.circle(63, 32, 10, 1)

display.fill(0)
display.text('display init',0,0,1)
graphics1.circle(63, 32, 10, 1)

oled.show()
display.show()

utime.sleep(2)


gc.collect()
