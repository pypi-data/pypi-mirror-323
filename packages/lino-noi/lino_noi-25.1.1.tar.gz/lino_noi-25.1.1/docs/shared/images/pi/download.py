"""
Note that the icons downloaded by this script are
Copyright (c) 2018 PrimeTek
See https://github.com/primefaces/primeicons/blob/master/LICENSE
"""
import requests
from pathlib import Path

ICON_NAMES = "filter plus plus-circle user refresh trash".split()

dest = Path(__file__).parent.absolute()
root = "https://raw.githubusercontent.com/primefaces/primeicons/master/raw-svg"
for name in ICON_NAMES:
    filename = name + ".svg"
    url = "{}/{}".format(root, filename)
    print("Downloading {} from primeicons master...".format(filename))
    r = requests.get(url, stream=True)
    with open(dest / filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=16 * 1024):
            f.write(chunk)
