# LingmoPyUI

LingmoPyUI is a GUI library based on QtWidgets from Qt 6 and written in Python, every Lingmo **Python** application uses it.

LingmoPyUI is the Python version of [LingmoUI](https://github.com/LingmoOS/LingmoUI)

## Features

**Features from LingmoUI:**

* Light and Dark Mode
* Borderless window (Wayland & XCB Window move & resize)
* Blurred window
* Window shadow
* Desktop-level menu

**New features:**
* `addStyleSheet()`add the stylesheet to the end of stylesheets,this won't cover the previous stylesheet or influence the children widgets.
* Auto-Show Option 
* ...

## Structures

* `__init__.py`: All the Widgets

## Installing

Run this in the Shell
```shell
pip install lingmopyui
```

## Using

Place this at the beginning of the source file:
```python
import LingmoPyUI
``` 
Place this at the end of the file:
```python
LingmoPyUI.LingmoApp.run()
```


## License

LingmoPyUI is licensed under GPLv3.