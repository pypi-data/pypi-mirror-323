from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

import os
import sys
from . import LingmoIconDef

packagePath = os.path.dirname(os.path.abspath(__file__))
appid = "com.lingmo.pyui.1.0"
windowIcon = packagePath + "/Image/icon.png"
locale = QLocale()
launcher = QObject()
useSystemAppBar = False
_app = QApplication([])
_translator = QTranslator(QApplication.instance())
QApplication.installTranslator(_translator)
uiLanguages = locale.uiLanguages()
for i in uiLanguages:
    basename = "lingmoui_" + QLocale(i).name()
    if _translator.load(os.path.dirname(sys.argv[0]) + basename):
        _app.translate()
        break


def run():
    _app.exec()


def iconData(keyword):
    arr = QJsonArray()
    for i in LingmoIconDef.__dict__:
        if (keyword in i) or keyword == "":
            value = QJsonValue({"name": i, "icon": LingmoIconDef.__dict__[i]})
            arr.append(value)
