from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from . import LingmoTextStyle


class iconSizes:
    small = 16
    smallMedium = 22
    medium = 32
    large = 48
    huge = 64
    enormous = 128


rowHeight = iconSizes.large * 0.95
rowHeightAlt = rowHeight * 0.8
fontMertics = QFontMetrics(LingmoTextStyle._family)
gridUnit = fontMertics.height()
extendBorderWidth = 0
smallSpacing = 6
largeSpacing = smallSpacing * 2
devicePixelRatio = QApplication.primaryScreen().devicePixelRatio()


def roundIconSize(size):
    if size < 16:
        return size
    elif size < 22:
        return 16
    elif size < 32:
        return 22
    elif size < 48:
        return 32
    elif size < 64:
        return 48
    else:
        return size

smallRadius = 8.0
mediumRadius = 10.0
bigRadius = 12.0
hugeRadius = 14.0
windowRadius = 11.0
