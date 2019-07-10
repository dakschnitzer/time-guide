# for esp8266 board
wget http://micropython.org/resources/firmware/esp8266-20190529-v1.11.bin
esptool.py --port /dev/tty.SLAB_USBtoUART erase_flash
esptool.py --port /dev/tty.SLAB_USBtoUART --baud 460800 write_flash --flash_size=detect 0 esp8266-20190529-v1.11.bin

ampy --port /dev/tty.SLAB_USBtoUART --baud 115200 put ssd1306.py
ampy --port /dev/tty.SLAB_USBtoUART --baud 115200 put sh1106.py
ampy --port /dev/tty.SLAB_USBtoUART --baud 115200 put gfx.py

ampy --port /dev/tty.SLAB_USBtoUART --baud 115200 put main.py

screen /dev/tty.SLAB_USBtoUART 115200

ampy --port /dev/tty.SLAB_USBtoUART --baud 115200 put rotary.py
ampy --port /dev/tty.SLAB_USBtoUART --baud 115200 put rotary_irq_esp.py

# for esp32 board
wget http://micropython.org/resources/firmware/esp32-20190622-v1.11-50-gb80bccccf.bin
esptool.py --chip esp32 --port /dev/tty.SLAB_USBtoUART erase_flash
esptool.py --chip esp32 --port /dev/tty.SLAB_USBtoUART --baud 460800 write_flash -z 0x1000 esp32-20190622-v1.11-50-gb80bccccf.bin