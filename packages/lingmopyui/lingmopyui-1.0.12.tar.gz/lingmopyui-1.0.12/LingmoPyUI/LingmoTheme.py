from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from . import LingmoColor
from . import LingmoDefines
from . import LingmoTools


def systemDark():
    palette = QGuiApplication.palette()
    color = palette.color(QPalette.ColorRole.Window)
    return (
        color.red() * 0.2126 + color.green() * 0.7152 + color.blue() * 0.0722
        <= 255.0 / 2
    )


class LingmoTheme(QObject):
    _accentColor = LingmoColor._Blue
    _darkMode = LingmoDefines.DarkMode.Light
    _roundWindowRadius = 10
    _nativeText = False
    _animationEnabled = True
    _systemDark = systemDark()
    _desktopImagePath = ""
    _blurBehindWindowEnabled = False
    _watcher = QFileSystemWatcher()
    _mutex = QMutex()
    darkModeChanged = Signal(type(_darkMode))
    darkChanged = Signal(type(_systemDark))
    accentColorChanged = Signal(type(_accentColor))
    blurBehindWindowEnabledChanged = Signal(type(_blurBehindWindowEnabled))
    desktopImagePathChanged = Signal(type(_desktopImagePath))

    def __init__(self):
        super().__init__()
        self.refreshColors()

    def eventFilter(self, watched, event):
        if (
            event.type() == QEvent.Type.ApplicationPaletteChange
            or event.type() == QEvent.Type.ThemeChange
        ):
            _systemDark = systemDark()
            self.darkChanged.emit(_systemDark)
            event.accept()
            return True
        return False

    @property
    def darkMode(self):
        return self._darkMode

    @darkMode.setter
    def darkMode(self, new_value):
        if self._darkMode != new_value:
            self._darkMode = new_value
            self.darkModeChanged.emit(new_value)

    @property
    def accentColor(self):
        return self._accentColor

    @accentColor.setter
    def accentColor(self, new_value):
        if self._accentColor != new_value:
            self._accentColor = new_value
            self.accentColorChanged.emit(new_value)

    @property
    def blurBehindWindowEnabled(self):
        return self._blurBehindWindowEnabled

    @blurBehindWindowEnabled.setter
    def blurBehindWindowEnabled(self, new_value):
        if self._blurBehindWindowEnabled != new_value:
            self._blurBehindWindowEnabled = new_value
            self.blurBehindWindowEnabledChanged.emit(new_value)

    @property
    def desktopImagePath(self):
        return self._desktopImagePath

    @desktopImagePath.setter
    def desktopImagePath(self, new_value):
        if self._desktopImagePath != new_value:
            self._desktopImagePath = new_value
            self.desktopImagePathChanged.emit(new_value)

    def refreshColors(self):
        isDark = self.dark()
        self.primaryColor = (
            LingmoTheme._accentColor._lighter
            if isDark
            else LingmoTheme._accentColor._dark
        )
        self.backgroundColor = (
            QColor(0, 0, 0, 255) if isDark else QColor(255, 255, 255, 255)
        )
        self.dividerColor = (
            QColor(80, 80, 80, 255) if isDark else QColor(210, 210, 210, 255)
        )
        self.windowBackgroundColor = (
            QColor(32, 32, 32, 255) if isDark else QColor(237, 237, 237, 255)
        )
        self.windowActiveBackgroundColor = (
            QColor(26, 26, 26, 255) if isDark else QColor(243, 243, 243, 255)
        )
        self.fontPrimaryColor = (
            QColor(248, 248, 248, 255) if isDark else QColor(7, 7, 7, 255)
        )
        self.fontSecondaryColor = (
            QColor(222, 222, 222, 255) if isDark else QColor(102, 102, 102, 255)
        )
        self.fontTertiaryColor = (
            QColor(200, 200, 200, 255) if isDark else QColor(153, 153, 153, 255)
        )
        self.itemNormalColor = (
            QColor(255, 255, 255, 0) if isDark else QColor(0, 0, 0, 0)
        )
        self.frameColor = (
            QColor(56, 56, 56, round(255 * 0.8))
            if isDark
            else QColor(243, 243, 243, round(255 * 0.8))
        )
        self.frameActiveColor = (
            QColor(48, 48, 48, round(255 * 0.8))
            if isDark
            else QColor(255, 255, 255, round(255 * 0.8))
        )
        self.itemHoverColor = (
            QColor(255, 255, 255, round(255 * 0.06))
            if isDark
            else QColor(0, 0, 0, round(255 * 0.03))
        )
        self.itemPressColor = (
            QColor(255, 255, 255, round(255 * 0.09))
            if isDark
            else QColor(0, 0, 0, round(255 * 0.06))
        )
        self.itemCheckColor = (
            QColor(255, 255, 255, round(255 * 0.12))
            if isDark
            else QColor(0, 0, 0, round(255 * 0.09))
        )

    def dark(self):
        if self._darkMode == LingmoDefines.DarkMode.Dark:
            return True
        elif self._darkMode == LingmoDefines.DarkMode.System:
            return self._systemDark
        else:
            return False

    def funcToRun(self):
        self._mutex.lock()
        path = LingmoTools.getWallpaperFilePath()
        if self._desktopImagePath != path:
            if self._desktopImagePath == "":
                self._watcher.removePath(self._desktopImagePath)
            self._desktopImagePath = path
            self._watcher.addPath(path)
        self._mutex.unlock()

    def checkUpdateDesktopImage(self):
        if self._blurBehindWindowEnabled:
            QThreadPool.globalInstance().start(QRunnable.create(self.funcToRun))

    def timerEvent(self, event):
        self.checkUpdateDesktopImage()


instance = LingmoTheme()
instance.darkModeChanged.connect(instance.darkChanged.emit)
instance.darkChanged.connect(instance.refreshColors)
instance.accentColorChanged.connect(instance.refreshColors)
instance._watcher.fileChanged.connect(instance.desktopImagePathChanged.emit)
instance.darkModeChanged.connect(instance.refreshColors)
QApplication.instance().installEventFilter(instance)
instance.startTimer(1000)
