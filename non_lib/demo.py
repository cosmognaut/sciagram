import io
import urllib.request
from PIL import Image
URL = "https://upload.wikimedia.org/wikipedia/commons/2/2d/John_Carmack_2025.jpg"
# wikimedia images are not retrievable for some reason.
# URL = "https://i.pinimg.com/736x/4f/87/8c/4f878cd14e14ba72c5479897b60e228a.jpg"
request = urllib.request.Request(URL)
request.add_header('User-Agent', 'urllib-example/0.1 (Contact: . . .)')
with urllib.request.urlopen(request) as file:
    # raw_bytes = io.BytesIO(file.read())
    # what happens if you don't use this?
    img = Image.open(file.read())
img.show()
