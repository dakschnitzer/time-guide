import board
import neopixel
np = neopixel.NeoPixel(board.D18, 9)

np.fill((0, 255, 0, 0))
np.show()
