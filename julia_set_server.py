import numpy as np
import itertools
import random
import matplotlib.pyplot as plt
import matplotlib.cm as cm

import server

nbr_phones = len(server.PHONES)

# Image width and height in pixels; parameters for the plot
width, height = 200 * nbr_phones, 200 * nbr_phones # Make sure these are divisble by nbr_phones
i_max = 1000
zabs_max = 10.0
xmin, xmax = -1.5, 1.5
dx = xmax - xmin
ymin, ymax = -1.5, 1.5
dy = ymax - ymin

# Map pixel position to a point in the complex plane
def z(i, j):
    return complex(
        i / width * dx + xmin,
        j / height * dy + ymin
    )

def julia(z, c=complex(-0.1, 0.65)):
    i = 0

    while abs(z) <= zabs_max and i < i_max:
        z = z**2 + c
        i += 1

    # Do the iterations
    ratio = i / i_max

    return ratio

# Initialize Julia set
J = np.zeros((width, height))

class FractalThread (server.PhoneThread):
    def __init__(self, phone_index, width_, height_, coords):
        self.phone_index, self.width_, self.height_, self.coords = phone_index, width_, height_, coords
        super().__init__(phone_index, 'julia_set', [width_, height_, *coords])

    def run(self):
        res = super().run()
        J[(self.phone_index * self.width_):((self.phone_index + 1) * self.width_), :] = np.reshape([float(s) for s in res.read().splitlines()], (self.width_, self.height_))

threads = [
    FractalThread(
        i,
        int(width / nbr_phones),
        height,
        [
            xmax - dx * i / nbr_phones,
            ymax,
            xmax - dx * (i + 1) / nbr_phones,
            ymin
        ]
    )
    for i in range(nbr_phones)
]

use_phones = True
if use_phones:
    for t in threads: t.start()
    for t in threads: t.join()
else:
    indices = list(itertools.product(range(width), range(height)))
    batches = np.array_split(indices, 10)
    for b in batches:
        for (i, j) in b:
            J[i, j] = julia(z(i, j))

fig, ax = plt.subplots()
ax.imshow(J, interpolation='nearest', cmap=cm.hot)
plt.show()

