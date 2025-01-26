from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *


class LingmoAccentColor:
    def __init__(self):
        self._darkest = self._darker = self._dark = self._normal = self._light = (
            self._lighter
        ) = self._lightest = QColor()

    def darkest(self, color: QColor):
        self._darkest = color

    def darker(self, color: QColor):
        self._darker = color

    def dark(self, color: QColor):
        self._dark = color

    def normal(self, color: QColor):
        self._normal = color

    def light(self, color: QColor):
        self._light = color

    def lighter(self, color: QColor):
        self._lighter = color

    def lightest(self, color: QColor):
        self._lightest = color
