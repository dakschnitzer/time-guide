import machine, neopixel
import utime as time

n = 14
p = 13
np = neopixel.NeoPixel(machine.Pin(p), n, bpp=4)



def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b, 0)


def rainbow_cycle(wait):
    for j in range(255):
        for i in range(n):
            pixel_index = (i * 256 // n) + j
            np[i] = wheel(pixel_index & 255)
        np.write()
        time.sleep(wait)


while True:
    # # Comment this line out if you have RGBW/GRBW NeoPixels
    # # np.fill((255, 0, 0))
    # # Uncomment this line if you have RGBW/GRBW NeoPixels
    # np.fill((255, 0, 0, 0))
    # np.write()
    # time.sleep(1)

    # # Comment this line out if you have RGBW/GRBW NeoPixels
    # # np.fill((0, 255, 0))
    # # Uncomment this line if you have RGBW/GRBW NeoPixels
    # np.fill((0, 255, 0, 0))
    # np.write()
    # time.sleep(1)

    # # Comment this line out if you have RGBW/GRBW NeoPixels
    # # np.fill((0, 0, 255))
    # # Uncomment this line if you have RGBW/GRBW NeoPixels
    # np.fill((0, 0, 255, 0))
    # np.write()
    # time.sleep(1)

    rainbow_cycle(0.001)  # rainbow cycle with 1ms delay per step
    

# def demo(np):

#     # cycle
#     for i in range(4 * n):
#         for j in range(n):
#             np[j] = (0, 0, 0, 0)
#         np[i % n] = (255, 255, 255, 255)
#         np.write()
#         time.sleep_ms(100)

#     # bounce
#     for i in range(4 * n):
#         for j in range(n):
#             np[j] = (75, 156, 211, 0)
#         if (i // n) % 2 == 0:
#             np[i % n] = (0, 0, 0, 0)
#         else:
#             np[n - 1 - (i % n)] = (0, 0, 0, 0)
#         np.write()
#         time.sleep_ms(500)

#     # fade in/out
#     for i in range(0, 4 * 256, 8):
#         for j in range(n):
#             if (i // 256) % 2 == 0:
#                 val = i & 0xff
#             else:
#                 val = 255 - (i & 0xff)
#             np[j] = (val, 0, 0, 0)
#         np.write()

#     # clear
#     for i in range(n):
#         np[i] = (0, 0, 0, 0)
#     np.write()

# demo(np)



