import machine, neopixel

n = 9
p = 13
np = neopixel.NeoPixel(machine.Pin(p), n, bpp=4)


np[0] = (255, 0, 0)
np[3] = (125, 204, 223)
np[7] = (120, 153, 23)
np[8] = (255, 0, 153)
np.write()

