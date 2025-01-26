from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

_family = QFont().defaultFamily()
caption = QFont()
caption.setFamily(_family)
caption.setPixelSize(12)

body = QFont()
body.setFamily(_family)
body.setPixelSize(13)

bodyStrong = QFont()
bodyStrong.setFamily(_family)
bodyStrong.setPixelSize(13)
bodyStrong.setWeight(QFont.Weight.DemiBold)

subtitle = QFont()
subtitle.setFamily(_family)
subtitle.setPixelSize(20)
subtitle.setWeight(QFont.Weight.DemiBold)

title = QFont()
title.setFamily(_family)
title.setPixelSize(28)
title.setWeight(QFont.Weight.DemiBold)

titleLarge = QFont()
titleLarge.setFamily(_family)
titleLarge.setPixelSize(40)
titleLarge.setWeight(QFont.Weight.DemiBold)

display = QFont()
display.setFamily(_family)
display.setPixelSize(68)
display.setWeight(QFont.Weight.DemiBold)
