# SDSmap
SDSmap is a simple Python library designed to parse the .fun file format used for saving maps in the game Supreme Duelist Stickman.

## 📖 Description
This library was originally designed to create maps in the game with impossible block sizes and spawn positions, but it can also be used to make other types of maps that are difficult to create manually.

## 🚀 Installation
You can install the library using pip
```bash
pip install sdsmap
```

## 🛠️ Usage

decoding
```python
import sdsmap

data = sdsmap.decode_map_file("test.fun")
print(data)
```

encoding
```python
import sdsmap

data = [{'id': 0, 'position': {'x': 0.0, 'y': 5.0}, 'scale': {'x': 2.5, 'y': -2.5}, 'rotation': 0.0}]
sdsmap.encode_file(data, "mapp.fun")
```

The `data` field may also contain other values, which are metadata values: 
 - background
 - liquid
 - spawn

If these values haven't changed in the map, they won't be included during decoding and encoding
data sample with metadata:
`{'blocks': [{'id': 0, 'position': {'x': 2.5, 'y': 6.25}, 'scale': {'x': 22.5, 'y': -7.5}, 'rotation': 0.0}], 'background': {'color1': {'r': 255, 'g': 255, 'b': 255, 'a': 255}, 'color2': {'r': 0, 'g': 0, 'b': 0, 'a': 255}}, 'liquid': {'type': 1, 'name': 'lava'}, 'spawn': {'position': {'x': 0.0, 'y': 12.82}}}`

## 💻 Impossible values
During testing, it was discovered that you can set an invalid block size (in the game, block sizes are determined by a grid) as well as an invalid player spawn position (in the game, the player’s position can only be moved within limited ranges along the y-axis, but the library allows it to be moved freely along both the x and y axes).
The background color also has an alpha parameter, changing it doesn't do anything, but I've included the option to decode it anyway
