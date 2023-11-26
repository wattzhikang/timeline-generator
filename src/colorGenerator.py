import random as rand
import matplotlib.colors as mc
import colorsys
import numpy as np

# Stolen from: https://gist.github.com/ihincks/6a420b599f43fcd7dbd79d56798c4e5a
def lighten_color(color, amount=0.5):
    """
    Lightens the given color by multiplying (1-luminosity) by the given amount.
    Input can be matplotlib color string, hex string, or RGB tuple.
    
    Examples:
    >> lighten_color('g', 0.3)
    >> lighten_color('#F034A3', 0.6)
    >> lighten_color((.3,.55,.1), 0.5)
    """
    try:
        c = mc.cnames[color]
    except:
        c = color
    c = np.array(colorsys.rgb_to_hls(*mc.to_rgb(c)))
    return colorsys.hls_to_rgb(c[0],1-amount * (1-c[1]),c[2])

colors = [
    "tab:orange",
    "tab:green",
    "tab:purple",
    "tab:olive",
    "cornflowerblue"
]

def ColorGenerator():
    rand.seed(0)
    lastColor = None
    while True:
        newColor = colors[rand.randint(1, len(colors)-1)]

        # convert named color to rgb
        newColor = mc.to_rgb(newColor)

        # have a lighter version of this color
        whiterColor = lighten_color(newColor, 0.5)
        
        if newColor != lastColor:
            lastColor = newColor
            yield newColor, whiterColor