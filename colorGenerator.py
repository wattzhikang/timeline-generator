import random as rand

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
        if newColor != lastColor:
            lastColor = newColor
            yield newColor