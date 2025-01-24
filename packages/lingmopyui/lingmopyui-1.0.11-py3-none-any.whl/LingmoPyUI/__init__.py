version='1.0.11'
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from . import LingmoAccentColor
from . import LingmoApp
from . import LingmoColor
from . import LingmoDefines
from .LingmoFrameless import LingmoFrameless
from . import LingmoIconDef
from . import LingmoTextStyle
from . import LingmoTheme
from . import LingmoTools
from . import LingmoUnits
import math

timerDelay = 1
widgetCount = 0
try:
    from ctypes import windll

    windll.shell32.SetCurrentProcessExplicitAppUserModelID(LingmoApp.appid)
except ImportError:
    pass


class LingmoAnimation(QVariantAnimation):
    Variable = 1
    Callable = 2

    def __init__(self, obj: object, attr: str, updateType=Variable):
        super().__init__()
        self.obj = obj
        self.attr = attr
        self.precision = 1000
        self.updateType = updateType

    def setStartValue(self, value):
        return super().setStartValue(round(value * self.precision))

    def setEndValue(self, value):
        return super().setEndValue(round(value * self.precision))

    def updateCurrentValue(self, value):
        if self.updateType == self.Variable:
            self.obj.__setattr__(self.attr, value / self.precision)
        else:
            (self.obj.__getattr__(self.attr))(value / self.precision)


class LingmoFrame(QFrame):
    pressed = Signal()
    released = Signal()
    hovered = Signal()
    left = Signal()
    rightPressed = Signal()
    rightReleased = Signal()
    needUpdate = Signal()
    moved = Signal()

    def __init__(self, parent=None, show=True):
        global widgetCount
        super().__init__(parent)
        self.timer = QTimer()
        self.needUpdate.connect(self.updateEvent)
        self.timer.timeout.connect(self.__update__)
        self.timer.start(timerDelay)
        self.setMouseTracking(True)
        if show:
            self.show()
        self.styleSheets = {}
        widgetCount += 1
        self.setObjectName("LingmoWidget" + str(widgetCount))
        self.ispressed = False
        if isinstance(parent,(LingmoFrame,LingmoLabel)):
            self.pressed.connect(self.parent().pressed.emit)
            self.released.connect(self.parent().released.emit)
            self.hovered.connect(self.parent().hovered.emit)
            self.left.connect(self.parent().left.emit)
            self.rightPressed.connect(self.parent().rightPressed.emit)
            self.rightReleased.connect(self.parent().rightReleased.emit)
            self.moved.connect(self.parent().moved.emit)

    def __update__(self):
        self.update()
        styleSheetString = "QFrame#" + self.objectName() + "{"
        for i in self.styleSheets:
            styleSheetString += i + ": " + self.styleSheets[i] + ";"
        styleSheetString += "}"
        self.setStyleSheet(styleSheetString)

    def updateEvent(self):
        pass

    def addStyleSheet(self, name, style):
        if isinstance(style, int) or isinstance(style, float):
            style = str(style)
        if isinstance(style, QColor):
            style = style.name(QColor.NameFormat.HexArgb)
        self.styleSheets[name] = style

    def isHovered(self):
        return self.underMouse()

    def mousePressEvent(self, event):
        if self.isEnabled():
            self.setFocus()
            if event.button() == Qt.MouseButton.LeftButton:
                self.pressed.emit()
            if event.button() == Qt.MouseButton.RightButton:
                self.rightPressed.emit()
            self.ispressed = True
        self.needUpdate.emit()

    def mouseReleaseEvent(self, event):
        if self.isEnabled():
            if event.button() == Qt.MouseButton.LeftButton:
                self.released.emit()
            if event.button() == Qt.MouseButton.RightButton:
                self.rightReleased.emit()
            self.ispressed = False
        self.needUpdate.emit()

    def mouseMoveEvent(self, event):
        self.moved.emit()
        self.needUpdate.emit()

    def enterEvent(self, event):
        if self.isEnabled():
            self.hovered.emit()
        self.needUpdate.emit()

    def leaveEvent(self, event):
        if self.isEnabled():
            self.left.emit()
        self.needUpdate.emit()

    def isPressed(self):
        return self.ispressed

    def event(self, e):
        if e.type != e.Type.Paint:
            self.needUpdate.emit()
        return super().event(e)


class LingmoLabel(QLabel):
    pressed = Signal()
    released = Signal()
    hovered = Signal()
    left = Signal()
    rightPressed = Signal()
    rightReleased = Signal()
    needUpdate = Signal()
    moved = Signal()

    def __init__(self, parent=None, show=True, autoAdjust=True):
        global widgetCount
        super().__init__(parent)
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateEvent)
        self.timer.timeout.connect(self.__update__)
        self.timer.start(timerDelay)
        if show:
            self.show()
        self.styleSheets = {}
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        widgetCount += 1
        self.setObjectName("LingmoWidget" + str(widgetCount))
        self.autoAdjust = autoAdjust

    def __update__(self):
        self.update()
        styleSheetString = "QLabel#" + self.objectName() + "{"
        for i in self.styleSheets:
            styleSheetString += i + ": " + self.styleSheets[i] + ";"
        styleSheetString += "}"
        self.setStyleSheet(styleSheetString)
        if self.autoAdjust:
            self.adjustSize()

    def updateEvent(self):
        pass

    def addStyleSheet(self, name, style):
        if isinstance(style, int) or isinstance(style, float):
            style = str(style)
        if isinstance(style, QBrush):
            style = style.color()
        if isinstance(style, QColor):
            style = style.name(QColor.NameFormat.HexArgb)
        self.styleSheets[name] = style

    def isHovered(self):
        return self.underMouse()

    def mousePressEvent(self, event):
        if self.isEnabled():
            if event.button() == Qt.MouseButton.LeftButton:
                self.pressed.emit()
            if event.button() == Qt.MouseButton.RightButton:
                self.rightPressed.emit()
            self.ispressed = True
        self.needUpdate.emit()

    def mouseReleaseEvent(self, event):
        if self.isEnabled():
            if event.button() == Qt.MouseButton.LeftButton:
                self.released.emit()
            if event.button() == Qt.MouseButton.RightButton:
                self.rightReleased.emit()
            self.ispressed = False
        self.needUpdate.emit()

    def mouseMoveEvent(self, event):
        self.moved.emit()
        self.needUpdate.emit()

    def enterEvent(self, event):
        if self.isEnabled():
            self.hovered.emit()
        self.needUpdate.emit()

    def leaveEvent(self, event):
        if self.isEnabled():
            self.left.emit()
        self.needUpdate.emit()

    def isPressed(self):
        return self.ispressed

    def event(self, e):
        if e.type != e.Type.Paint:
            self.needUpdate.emit()
        return super().event(e)


class LingmoAcrylic(LingmoFrame):
    def __init__(
        self,
        parent=None,
        show=True,
        tintOpacity=0.65,
        tintColor=QColor(255, 255, 255, 255),
        luminosity=0.01,
        noiseOpacity=0.02,
        target: QWidget = None,
        blurRadius=32,
        targetRect: QRect = None,
    ):
        super().__init__(parent, show)
        self.tintColor = tintColor
        self.tintOpacity = tintOpacity
        self.luminosity = luminosity
        self.noiseOpacity = noiseOpacity
        self.target = target
        self.blurRadius = blurRadius
        self.targetRect = self.rect() if targetRect == None else targetRect
        self.blurWidget = LingmoFrame(self)
        self.blurEffect = QGraphicsBlurEffect(self.blurWidget)
        self.blurWidget.setGeometry(self.targetRect)
        self.luminosityWidget = LingmoFrame(self)
        self.luminosityWidget.resize(self.size())
        self.tintWidget = LingmoFrame(self)
        self.tintWidget.resize(self.size())
        self.imageWidget = LingmoLabel(self)
        self.imageWidget.resize(self.size())
        self.imageWidget.setPixmap(QPixmap(LingmoApp.packagePath + "/Image/noise.png"))
        self.imageWidget.addStyleSheet("background-repeat", "repeat")

    def updateEvent(self):
        try:
            self.blurEffect.setBlurRadius(self.blurRadius)
            self.blurWidget.setGeometry(self.targetRect)
            self.luminosityWidget.addStyleSheet(
                "background-color", QColor(1, 1, 1, self.luminosity * 255)
            )
            self.tintWidget.addStyleSheet(
                "background-color",
                QColor(
                    self.tintColor.red(),
                    self.tintColor.green(),
                    self.tintColor.blue(),
                    self.tintOpacity,
                ),
            )
            self.imageWidget.setWindowOpacity(self.noiseOpacity)
        except:
            pass

    def setTintColor(self, val):
        self.tintColor = val

    def setTintOpacity(self, val):
        self.tintOpacity = val

    def setLuminosity(self, val):
        self.luminosity = val

    def setNoiseOpacity(self, val):
        self.noiseOpacity = val

    def setTarget(self, val):
        self.target = val

    def setBlurRadius(self, val):
        self.blurRadius = val

    def setTargetRect(self, val):
        self.targetRect = val


class LingmoAppBar(LingmoFrame):
    def __init__(self, parent=None, show=True, title="", icon=""):
        super().__init__(parent, show)
        self.title = title
        self.icon = icon
        self.darkText = self.tr("Dark")
        self.lightText = self.tr("Light")
        self.minimizeText = self.tr("Minimize")
        self.restoreText = self.tr("Restore")
        self.maximizeText = self.tr("Maximize")
        self.closeText = self.tr("Close")
        self.stayTopText = self.tr("Sticky on Top")
        self.stayTopCancelText = self.tr("Cancel Sticky on Top")
        self.textColor = LingmoTheme.instance.fontPrimaryColor
        self.minimizeNormalColor = self.maximizeNormalColor = (
            LingmoTheme.instance.itemNormalColor
        )
        self.minimizeHoverColor = self.maximizeHoverColor = (
            LingmoTheme.instance.itemHoverColor
        )
        self.minimizePressColor = self.maximizePressColor = (
            LingmoTheme.instance.itemPressColor
        )
        self.closeNormalColor = QColor(0, 0, 0, 0)
        self.closeHoverColor = QColor(251, 115, 115, 255)
        self.closePressColor = QColor(251, 115, 115, 255 * 0.8)
        self.showDark = True
        self.showClose = True
        self.showMinimize = True
        self.showMaximize = True
        self.showStayTop = True
        self.titleVisible = True
        self.icon = QSystemTrayIcon.MessageIcon.Information
        self.iconSize = 20
        self.isMac = LingmoTools.isMacos()
        self.borderlessColor = LingmoTheme.instance.primaryColor
        self.btnDark = LingmoIconButton(
            (
                LingmoIconDef.Brightness
                if LingmoTheme.instance.dark()
                else LingmoIconDef.QuietHours
            ),
            parent=self,
            iconSize=15,
            content=self.lightText if LingmoTheme.instance.dark() else self.darkText,
        )
        self.btnStayTop = LingmoIconButton(
            LingmoIconDef.Pinned,
            parent=self,
            iconSize=14,
            content=self.stayTopCancelText if self.stayTop() else self.stayTopText,
        )
        if LingmoTools.isMacos():
            self.btnClose = LingmoImageButton(
                LingmoApp.packagePath + "/Image/btn_close_normal.png",
                parent=self,
                hoveredImage=LingmoApp.packagePath + "/Image/btn_close_hovered.png",
                pushedImage=LingmoApp.packagePath + "/Image/btn_close_pushed.png",
            )
            self.btnMinimize = LingmoImageButton(
                LingmoApp.packagePath + "/Image/btn_min_normal.png",
                parent=self,
                hoveredImage=LingmoApp.packagePath + "/Image/btn_min_hovered.png",
                pushedImage=LingmoApp.packagePath + "/Image/btn_min_pushed.png",
            )
            self.btnMaximize = LingmoImageButton(
                LingmoApp.packagePath + "/Image/btn_max_normal.png",
                parent=self,
                hoveredImage=LingmoApp.packagePath + "/Image/btn_max_hovered.png",
                pushedImage=LingmoApp.packagePath + "/Image/btn_max_pushed.png",
            )
        else:
            self.btnMinimize = LingmoIconButton(
                LingmoIconDef.ChromeMinimize,
                parent=self,
                iconSize=11,
                content=self.minimizeText,
                normalColor=self.minimizeNormalColor,
                hoverColor=self.minimizeHoverColor,
                pressedColor=self.minimizePressColor,
            )
            self.btnMaximize = LingmoIconButton(
                LingmoIconDef.ChromeMaximize,
                parent=self,
                iconSize=11,
                content=self.maximizeText,
                normalColor=self.maximizeNormalColor,
                hoverColor=self.maximizeHoverColor,
                pressedColor=self.maximizePressColor,
            )
            self.btnClose = LingmoIconButton(
                LingmoIconDef.ChromeClose,
                parent=self,
                iconSize=10,
                content=self.closeText,
                normalColor=self.closeNormalColor,
                hoverColor=self.closeHoverColor,
                pressedColor=self.closePressColor,
            )
        self.setVisibleDark(self.showDark)
        self.setVisibleStayTop(
            self.showStayTop and isinstance(self.window(), LingmoWindow)
        )
        if LingmoTools.isMacos():
            self.setVisibleClose(self.showClose)
            self.setVisibleMinimize(self.showMinimize)
            self.setVisibleMaximize(self.showMaximize and self.resizable())
        else:
            self.setVisibleMinimize(self.showMinimize)
            self.setVisibleMaximize(self.showMaximize and self.resizable())
            self.setVisibleClose(self.showClose)
        self.btnDark.pressed.connect(self.darkClickListener)
        self.btnStayTop.pressed.connect(self.stayTopClickListener)
        self.btnMinimize.pressed.connect(self.minClickListener)
        self.btnMaximize.pressed.connect(self.maxClickListener)
        self.btnClose.pressed.connect(self.closeClickListener)
        self.btnDark.setIconBorderSize(40, 30)
        self.btnStayTop.setIconBorderSize(40, 30)
        self.btnMinimize.setIconBorderSize(
            12 if LingmoTools.isMacos() else 40, 12 if LingmoTools.isMacos() else 30
        )
        self.btnMaximize.setIconBorderSize(
            12 if LingmoTools.isMacos() else 40, 12 if LingmoTools.isMacos() else 30
        )
        self.btnClose.setIconBorderSize(
            12 if LingmoTools.isMacos() else 40, 12 if LingmoTools.isMacos() else 30
        )
        self.btnDark.setIconColor(self.textColor)
        self.btnStayTop.setIconColor(
            LingmoTheme.instance.primaryColor if self.stayTop() else self.textColor
        )
        self.btnMinimize.setIconColor(self.textColor)
        self.btnMaximize.setIconColor(self.textColor)
        self.btnClose.setIconColor(self.textColor)
        self.btnDark.setPaddings(0, 0)
        self.btnStayTop.setPaddings(0, 0)
        if not LingmoTools.isMacos():
            self.btnMinimize.setPaddings(0, 0)
            self.btnMaximize.setPaddings(0, 0)
            self.btnClose.setPaddings(0, 0)

    def updateEvent(self):
        try:
            self.raise_()
            self.textColor = LingmoTheme.instance.fontPrimaryColor
            self.addStyleSheet("background-color", "transparent")
            self.resize(self.width(), 30 if self.isVisible() else 0)
            lastButtonX = self.width()
            if LingmoTools.isMacos():
                if self.btnMaximize.isVisible():
                    self.btnMaximize.move(
                        lastButtonX - self.btnMaximize.width(),
                        self.height() / 2 - self.btnMaximize.height() / 2,
                    )
                lastButtonX = (
                    self.btnMaximize.x()
                    if self.btnMaximize.isVisible()
                    else lastButtonX
                )
                if self.btnMinimize.isVisible():
                    self.btnMinimize.move(
                        lastButtonX - self.btnMinimize.width(),
                        self.height() / 2 - self.btnMinimize.height() / 2,
                    )
                lastButtonX = (
                    self.btnMinimize.x()
                    if self.btnMinimize.isVisible()
                    else lastButtonX
                )
                if self.btnClose.isVisible():
                    self.btnClose.move(
                        lastButtonX - self.btnClose.width(),
                        self.height() / 2 - self.btnClose.height() / 2,
                    )
                lastButtonX = (
                    self.btnClose.x() if self.btnClose.isVisible() else lastButtonX
                )
            else:
                if self.btnClose.isVisible():
                    self.btnClose.move(
                        lastButtonX - self.btnClose.width(),
                        self.height() / 2 - self.btnClose.height() / 2,
                    )
                lastButtonX = (
                    self.btnClose.x() if self.btnClose.isVisible() else lastButtonX
                )
                if self.btnMaximize.isVisible():
                    self.btnMaximize.move(
                        lastButtonX - self.btnMaximize.width(),
                        self.height() / 2 - self.btnMaximize.height() / 2,
                    )
                lastButtonX = (
                    self.btnMaximize.x()
                    if self.btnMaximize.isVisible()
                    else lastButtonX
                )
                if self.btnMinimize.isVisible():
                    self.btnMinimize.move(
                        lastButtonX - self.btnMinimize.width(),
                        self.height() / 2 - self.btnMinimize.height() / 2,
                    )
                lastButtonX = (
                    self.btnMinimize.x()
                    if self.btnMinimize.isVisible()
                    else lastButtonX
                )
            if self.btnStayTop.isVisible():
                self.btnStayTop.move(
                    lastButtonX - self.btnStayTop.width(),
                    self.height() / 2 - self.btnStayTop.height() / 2,
                )
            lastButtonX = (
                self.btnStayTop.x() if self.btnStayTop.isVisible() else lastButtonX
            )
            if self.btnDark.isVisible():
                self.btnDark.move(
                    lastButtonX - self.btnDark.width(),
                    self.height() / 2 - self.btnDark.height() / 2,
                )
            if not LingmoTools.isMacos():
                self.btnMaximize.setIconSource(
                    LingmoIconDef.ChromeRestore
                    if self.isRestore()
                    else LingmoIconDef.ChromeMaximize
                )
                self.btnMaximize.setContent(
                    self.restoreText if self.isRestore() else self.maximizeText
                )
                self.btnStayTop.setContent(
                    self.stayTopCancelText if self.stayTop() else self.stayTopText
                )
                self.btnDark.setIconSource(
                    LingmoIconDef.Brightness
                    if LingmoTheme.instance.dark()
                    else LingmoIconDef.QuietHours
                )
                self.btnDark.setIconColor(self.textColor)
                self.btnStayTop.setIconColor(
                    LingmoTheme.instance.primaryColor
                    if self.stayTop()
                    else self.textColor
                )
                self.btnMinimize.setIconColor(self.textColor)
                self.btnMaximize.setIconColor(self.textColor)
                self.btnClose.setIconColor(self.textColor)
        except:
            pass

    def maxClickListener(self):
        if LingmoTools.isMacos():
            if self.window().isFullScreen() or self.window().isMaximized():
                self.window().showNormal()
            else:
                self.window().showFullScreen()
        else:
            if self.window().isMaximized() or self.window().isFullScreen():
                self.window().showNormal()
            else:
                self.window().showMaximized()

    def minClickListener(self):
        self.window().showMinimized()

    def closeClickListener(self):
        self.window().close()

    def stayTopClickListener(self):
        if isinstance(self.window(), LingmoWindow):
            self.window().setStayTop(not self.stayTop())

    def darkClickListener(self):
        if LingmoTheme.instance.dark():
            LingmoTheme.instance.darkMode = LingmoDefines.DarkMode.Light
        else:
            LingmoTheme.instance.darkMode = LingmoDefines.DarkMode.Dark

    def stayTop(self):
        if isinstance(self.window(), LingmoWindow):
            return self.window().stayTop
        else:
            return False

    def isRestore(self):
        return self.window() and (
            self.window().isMaximized() or self.window().isFullScreen()
        )

    def resizable(self):
        return self.window() and not (
            self.window().width() == self.window().maximumWidth()
            and self.window().width() == self.window().minimumWidth()
            and self.window().height() == self.window().maximumHeight()
            and self.window().height() == self.window().minimumHeight()
        )

    def setVisibleDark(self, val):
        self.btnDark.setVisible(val)

    def setVisibleStayTop(self, val):
        self.btnStayTop.setVisible(val)

    def setVisibleMaximize(self, val):
        self.btnMaximize.setVisible(val)

    def setVisibleMinimize(self, val):
        self.btnMinimize.setVisible(val)

    def setVisibleClose(self, val):
        self.btnClose.setVisible(val)

    def setShowDark(self, val):
        self.showDark = val
        self.setVisibleDark(val)

    def setShowStayTop(self, val):
        self.showStayTop = val
        self.setVisibleStayTop(val)

    def setShowMaximize(self, val):
        self.showMaximize = val
        self.setVisibleMaximize(val)

    def setShowMinimize(self, val):
        self.showMinimize = val
        self.setVisibleMinimize(val)

    def setShowClose(self, val):
        self.showClose = val
        self.setVisibleClose(val)


class LingmoButton(LingmoFrame):
    def __init__(
        self,
        parent=None,
        show=True,
        content="",
        normalColor=(
            QColor(62, 62, 62, 255)
            if LingmoTheme.instance.dark()
            else QColor(254, 254, 254, 255)
        ),
        hoverColor=(
            QColor(68, 68, 68, 255)
            if LingmoTheme.instance.dark()
            else QColor(246, 246, 246, 255)
        ),
        disableColor=(
            QColor(59, 59, 59, 255)
            if LingmoTheme.instance.dark()
            else QColor(251, 251, 251, 255)
        ),
        dividerColor=(
            QColor(80, 80, 80, 255)
            if LingmoTheme.instance.dark()
            else QColor(233, 233, 233, 255)
        ),
        textNormalColor=(
            QColor(255, 255, 255, 255)
            if LingmoTheme.instance.dark()
            else QColor(0, 0, 0, 255)
        ),
        textPressedColor=(
            QColor(162, 162, 162, 255)
            if LingmoTheme.instance.dark()
            else QColor(96, 96, 96, 255)
        ),
        textDisabledColor=(
            QColor(131, 131, 131, 255)
            if LingmoTheme.instance.dark()
            else QColor(160, 160, 160, 255)
        ),
        clickShadowChange=True,
        autoResize=True,
    ):
        super().__init__(parent, show)
        self.content = content
        self.normalColor = normalColor
        self.hoverColor = hoverColor
        self.disabledColor = disableColor
        self.dividerColor = dividerColor
        self.textNormalColor = textNormalColor
        self.textPressedColor = textPressedColor
        self.textDisabledColor = textDisabledColor
        self.horizontalPadding = 12
        self.verticalPadding = 0
        self.ctrlBg = LingmoControlBackground(
            self, LingmoTheme.instance._roundWindowRadius
        )
        self.ctrlBg.setGeometry(
            self.horizontalPadding,
            self.verticalPadding,
            self.width() - 2 * self.horizontalPadding,
            self.height() - 2 * self.verticalPadding,
        )
        self.setFont(LingmoTextStyle.body)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.focusRect = LingmoFocusRectangle(self.ctrlBg, radius=4)
        self.focusRect.resize(self.ctrlBg.size())
        self.contentText = LingmoText(self)
        self.contentText.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentText.setFont(self.font())
        self.clickShadowChange = clickShadowChange
        self.autoResize = autoResize
        self.contentText.pressed.connect(self.pressed.emit)

    def updateEvent(self):
        try:
            if self.isEnabled():
                if self.isPressed():
                    self.contentText.setColor(self.textPressedColor)
                else:
                    self.contentText.setColor(self.textNormalColor)
            else:
                self.contentText.setColor(self.textDisabledColor)
            self.ctrlBg.setColor(
                (self.hoverColor if self.isHovered() else self.normalColor)
                if self.isEnabled()
                else self.disabledColor
            )
            if self.clickShadowChange:
                self.ctrlBg.setShadow((not self.isPressed()) and self.isEnabled())
            self.focusRect.setVisible(self.hasFocus())
            self.contentText.setText(self.content)
            self.contentText.move(
                10 + 12, self.height() / 2 - self.contentText.height() / 2
            )
            self.contentText.raise_()
            if self.autoResize:
                self.ctrlBg.resize(self.contentText.width() + 20, self.height())
            self.resize(
                self.ctrlBg.width() + 2 * self.horizontalPadding,
                self.ctrlBg.height() + 2 * self.verticalPadding,
            )
        except:
            pass

    def setContent(self, val):
        self.content = val

    def setClickShadowChange(self, val):
        self.clickShadowChange = val

    def setAutoResize(self, val):
        self.autoResize = val


class LingmoCheckBox(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoClip(LingmoFrame):
    def __init__(self, parent=None, show=True, radius=0):
        super().__init__(parent, show)
        self.color = QColor(0, 0, 0, 0)
        self.effect = QGraphicsOpacityEffect(self)
        self.effect.setOpacity(0.5)
        self.setGraphicsEffect(self.effect)
        self.radius = radius

    def updateEvent(self):
        try:
            self.addStyleSheet("border-radius", self.radius)
        except:
            pass

    def setRadius(self, val):
        self.radius = val


class LingmoControlBackground(LingmoFrame):
    def __init__(
        self,
        parent=None,
        show=True,
        radius: int = 4,
        shadow: bool = True,
        color=(
            QColor(42, 42, 42, 255)
            if LingmoTheme.instance.dark()
            else QColor(254, 254, 254, 255)
        ),
        borderWidths=[1, 1, 1, 1],
    ):
        super().__init__(parent, show)
        self.radius = radius
        self.shadow = shadow
        self.color = color
        self.borderColor = (
            QColor(48, 48, 48, 255)
            if LingmoTheme.instance.dark()
            else QColor(188, 188, 188, 255)
        )
        self.startColor = QColor.lighter(self.borderColor, 125)
        self.endColor = self.borderColor if self.shadow else self.startColor
        self.borderWidths = borderWidths
        self.rectBorder = LingmoFrame(self)
        self.rectBack = LingmoFrame(self)
        self.borderColorUnsetted = True

    def updateEvent(self):
        try:
            self.rectBack.addStyleSheet("border-radius", self.radius)
            self.rectBack.addStyleSheet("background-color", self.color)
            self.rectBack.setGeometry(
                self.borderWidths[0],
                self.borderWidths[1],
                self.width() - self.borderWidths[0] - self.borderWidths[2],
                self.height() - self.borderWidths[1] - self.borderWidths[3],
            )
            self.borderColor = (
                (
                    QColor(48, 48, 48, 255)
                    if LingmoTheme.instance.dark()
                    else QColor(188, 188, 188, 255)
                )
                if self.borderColorUnsetted
                else self.borderColor
            )
            self.startColor = QColor.lighter(self.borderColor, 125)
            self.endColor = self.borderColor if self.shadow else self.startColor
            self.rectBorder.addStyleSheet(
                "background-color",
                """qlineargradient(x1:0 , y1:0 , x2:0 , y2:1,
					stop:0    rgba(%d,%d,%d,%d),
					stop:%d   rgba(%d,%d,%d,%d),
					stop:1.0  rgba(%d,%d,%d,%d))"""
                % (
                    self.startColor.red(),
                    self.startColor.green(),
                    self.startColor.blue(),
                    self.startColor.alpha(),
                    1 - 3 / self.height(),
                    self.startColor.red(),
                    self.startColor.green(),
                    self.startColor.blue(),
                    self.startColor.alpha(),
                    self.endColor.red(),
                    self.endColor.green(),
                    self.endColor.blue(),
                    self.endColor.alpha(),
                ),
            )
            self.rectBorder.addStyleSheet("border-radius", self.radius)
            self.rectBorder.resize(self.size())
        except:
            pass

    def setColor(self, val):
        self.color = val

    def setRadius(self, val):
        self.radius = val

    def setShadow(self, val):
        self.shadow = val

    def setBorderWidths(self, val):
        self.borderWidths = val

    def setLeftMargin(self, val):
        self.borderWidths[0] = val

    def setTopMargin(self, val):
        self.borderWidths[1] = val

    def setRightMargin(self, val):
        self.borderWidths[2] = val

    def setButtomMargin(self, val):
        self.borderWidths[3] = val

    def setBorderWidth(self, val):
        self.borderWidths = [val, val, val, val]

    def setBorderColor(self, val):
        self.borderColor = val
        self.borderColorUnsetted = False


class LingmoCustomDialog(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoDelayButton(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoDropDownBox(LingmoButton):
    def __init__(self, parent=None, show=True, content=""):
        super().__init__(parent, show, autoResize=False, content=content)
        self.icon = LingmoIcon(
            LingmoIconDef.ChevronDown, self, iconSize=15, autoAdjust=True
        )
        self.menu = LingmoMenu(autoResize=False)
        self.menu.showed.connect(self.onAboutToShow)
        self.menu.hided.connect(self.onAboutToHide)
        self.pressed.connect(self.showMenu)
        self.parentWidget().pressed.connect(self.hideMenu)

    def focusOutEvent(self, event):
        self.hideMenu()
        return super().focusOutEvent(event)

    def updateEvent(self):
        super().updateEvent()
        try:
            self.icon.move(
                self.ctrlBg.x() + self.ctrlBg.width() - 20,
                self.height() / 2 - self.icon.height() / 2,
            )
            self.menu.background.resize(
                self.ctrlBg.width(), self.menu.background.height()
            )
            self.moveMenu()
            self.ctrlBg.resize(
                self.contentText.x() + self.contentText.width() + self.icon.width(),
                self.height(),
            )
        except:
            pass

    def moveMenu(self):
        pos = self.ctrlBg.mapTo(self.window(), QPoint(0, 0))
        containerHeight = self.menu.height()
        if self.window().height() > pos.y() + self.height() + containerHeight:
            self.menu.setPosition(
                self.mapToGlobal(QPoint(self.ctrlBg.x() / 2, self.height()))
            )
        elif pos.y() > containerHeight:
            self.menu.setPosition(
                self.mapToGlobal(QPoint(self.ctrlBg.x() / 2, -containerHeight))
            )
        else:
            self.menu.setPosition(
                self.mapToGlobal(
                    QPoint(
                        self.ctrlBg.x() / 2,
                        self.window().height() - (pos.y() + containerHeight),
                    )
                )
            )

    def showMenu(self):
        if self.menu.count() and not self.menu.isVisible():
            self.moveMenu()
            self.menu.showMenu()

    def hideMenu(self):
        if not (self.menu.isHovered() or self.isHovered()):
            self.menu.hideMenu()

    def addItem(self, item):
        self.menu.addItem(item)

    def onAboutToShow(self):
        self.icon.setIconSource(LingmoIconDef.ChevronUp)

    def onAboutToHide(self):
        self.icon.setIconSource(LingmoIconDef.ChevronDown)


class LingmoFilledButton(LingmoFrame):
    def __init__(self, parent=None, show=True, content=""):
        super().__init__(parent, show)
        self.content = content
        self.normalColor = LingmoTheme.instance.primaryColor
        self.hoverColor = (
            self.normalColor.darker(110)
            if LingmoTheme.instance.dark()
            else self.normalColor.lighter(110)
        )
        self.disableColor = (
            QColor(82, 82, 82, 255)
            if LingmoTheme.instance.dark()
            else QColor(199, 199, 199, 255)
        )
        self.pressedColor = (
            self.normalColor.darker(120)
            if LingmoTheme.instance.dark()
            else self.normalColor.lighter(120)
        )
        self.textColor = (
            (
                QColor(173, 173, 173, 255)
                if not self.isEnabled()
                else QColor(0, 0, 0, 255)
            )
            if LingmoTheme.instance.dark()
            else QColor(255, 255, 255, 255)
        )
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.horizontalPaddding = 12
        self.verticalPadding = 0
        self.background = LingmoControlBackground(self)
        self.focusRect = LingmoFocusRectangle(self.background, radius=4)
        self.focusRect.resize(self.background.size())
        self.contentText = LingmoText(self)
        self.contentText.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentText.setFont(self.font())
        self.contentText.pressed.connect(self.pressed.emit)

    def updateEvent(self):
        try:
            if self.isEnabled():
                if self.isPressed():
                    self.bgColor = self.pressedColor
                elif self.isHovered():
                    self.bgColor = self.hoverColor
                else:
                    self.bgColor = self.normalColor
            else:
                self.bgColor = self.disableColor
            self.contentText.setColor(self.textColor)
            self.background.setColor(self.bgColor)
            self.background.setRadius(LingmoTheme.instance._roundWindowRadius)
            self.background.setBorderWidth(1 if self.isEnabled() else 0)
            self.background.setBorderColor(
                self.normalColor.darker(120) if self.isEnabled() else self.disableColor
            )
            self.focusRect.setVisible(self.hasFocus())
            self.contentText.setText(self.content)
            self.contentText.move(
                self.width() / 2 - self.contentText.width() / 2,
                self.height() / 2 - self.contentText.height() / 2,
            )
        except:
            pass


class LingmoFocusRectangle(LingmoFrame):
    def __init__(
        self,
        parent=None,
        show=True,
        color=QColor(0, 0, 0, 0),
        borderWidth=2,
        radius=10,
        borderColor=(
            QColor(255, 255, 255, 255)
            if LingmoTheme.instance.dark()
            else QColor(0, 0, 0, 255)
        ),
    ):
        super().__init__(parent, show)
        self.color = color
        self.borderWidth = borderWidth
        self.radius = radius
        self.borderColor = borderColor

    def updateEvent(self):
        try:
            self.raise_()
            self.addStyleSheet("background-color", self.color)
            self.addStyleSheet("border-width", self.borderWidth)
            self.addStyleSheet("border-radius", self.radius)
            self.addStyleSheet("border-color", self.borderColor)
            self.addStyleSheet("border-style", "solid")
            self.resize(self.parentWidget().size())
        except:
            pass

    def setColor(self, val):
        self.color = val

    def setBorderWidth(self, val):
        self.borderWidth = val

    def setRadius(self, val):
        self.radius = val

    def setBorderColor(self, val):
        self.borderColor = val


class LingmoIcon(LingmoLabel):
    def __init__(
        self,
        iconSource,
        parent=None,
        show=True,
        iconSize=20,
        iconColor: QColor = (
            QColor(255, 255, 255, 255)
            if LingmoTheme.instance.dark()
            else QColor(0, 0, 0, 255)
        ),
        autoAdjust=False,
    ):
        super().__init__(parent, show, autoAdjust)
        self.iconSource = iconSource
        self.iconSize = iconSize
        self.iconColor = iconColor
        self.iconColor = (
            (
                QColor(255, 255, 255, 255)
                if self.isEnabled()
                else QColor(130, 130, 130, 255)
            )
            if LingmoTheme.instance.dark()
            else (
                QColor(0, 0, 0, 255) if self.isEnabled() else QColor(161, 161, 161, 255)
            )
        )

    def updateEvent(self):
        try:
            self.fontDatabase = QFontDatabase()
            self.fontDatabase.addApplicationFont(
                LingmoApp.packagePath + "/Font/FluentIcons.ttf"
            )
            self.fontFamily = QFont(self.fontDatabase.applicationFontFamilies(0)[-1])
            self.fontFamily.setPixelSize(self.iconSize)
            self.setFont(self.fontFamily)
            self.setText(chr(self.iconSource))
            self.addStyleSheet("color", self.iconColor)
            self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        except:
            pass

    def setIconSource(self, val):
        self.iconSource = val

    def setIconSize(self, val):
        self.iconSize = val

    def setIconColor(self, val):
        self.iconColor = val


class LingmoIconButton(LingmoFrame):
    IconOnly = Qt.ToolButtonStyle.ToolButtonIconOnly
    TextOnly = Qt.ToolButtonStyle.ToolButtonTextOnly
    TextUnderIcon = Qt.ToolButtonStyle.ToolButtonTextUnderIcon
    TextBesideIcon = Qt.ToolButtonStyle.ToolButtonTextBesideIcon

    def __init__(
        self,
        iconSource,
        parent=None,
        show=True,
        display=IconOnly,
        iconSize=20,
        radius=LingmoTheme.instance._roundWindowRadius,
        content="",
        hoverColor=LingmoTheme.instance.itemHoverColor,
        pressedColor=LingmoTheme.instance.itemPressColor,
        normalColor=LingmoTheme.instance.itemNormalColor,
        disableColor=LingmoTheme.instance.itemNormalColor,
    ):
        super().__init__(parent, show)
        self.display = display
        self.iconSize = iconSize
        self.iconSource = iconSource
        self.radius = radius
        self.content = content
        self.hoverColor = hoverColor
        self.pressedColor = pressedColor
        self.normalColor = normalColor
        self.disableColor = disableColor
        self.background = LingmoFrame(self)
        self.focusRect = LingmoFocusRectangle(self.background)
        self.tooltip = LingmoToolTip(
            self.background, interval=1000, content=self.content
        )
        self.icon = LingmoIcon(iconSource, show=False)
        self.text = LingmoText(show=False)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.boxLayout = QBoxLayout(QBoxLayout.Direction.LeftToRight, self.background)
        self.background.setLayout(self.boxLayout)
        self.boxLayout.addWidget(self.icon)
        self.boxLayout.setContentsMargins(0, 0, 0, 0)
        self.boxLayout.setSpacing(0)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.iconColor = QColor()
        self.iconColorUnsetted = True
        self.horizontalPadding = 8
        self.verticalPadding = 8
        self.icon.pressed.connect(self.pressed.emit)
        self.text.pressed.connect(self.pressed.emit)

    def updateEvent(self):
        try:
            self.tooltip.setDisabled(
                self.content == "" or self.display != self.IconOnly
            )
            self.tooltip.setContent(self.content)
            self.text.setText(self.content)
            self.color = QColor()
            self.textColor = LingmoTheme.instance.fontPrimaryColor
            if self.isEnabled():
                if self.isPressed():
                    self.color = self.pressedColor
                elif self.isHovered():
                    self.color = self.hoverColor
                else:
                    self.color = self.normalColor
                if self.iconColorUnsetted:
                    self.iconColor = (
                        QColor(255, 255, 255, 255)
                        if LingmoTheme.instance.dark()
                        else QColor(0, 0, 0, 255)
                    )
            else:
                self.color = self.disableColor
                if self.iconColorUnsetted:
                    self.iconColor = (
                        QColor(130, 130, 130, 255)
                        if LingmoTheme.instance.dark()
                        else QColor(161, 161, 161, 255)
                    )
            self.icon.setIconColor(self.iconColor)
            self.icon.setIconSize(self.iconSize)
            self.text.setText(self.content)
            self.text.setFont(LingmoTextStyle.caption)
            self.background.addStyleSheet("border-radius", self.radius)
            self.background.addStyleSheet("background-color", self.color)
            self.text.addStyleSheet("color", self.textColor)
            self.background.move(self.horizontalPadding, self.verticalPadding)
            self.resize(
                self.background.width() + 2 * self.horizontalPadding,
                self.background.height() + 2 * self.verticalPadding,
            )
            self.focusRect.setVisible(self.hasFocus())
        except:
            pass

    def setDisplay(self, val):
        self.display = val
        self.boxLayout.removeWidget(self.icon)
        self.boxLayout.removeWidget(self.text)
        if self.display != self.TextOnly:
            self.boxLayout.addWidget(self.icon)
        if self.display != self.IconOnly:
            self.boxLayout.addWidget(self.text)
        if self.display == self.TextBesideIcon:
            self.boxLayout.setDirection(QBoxLayout.Direction.LeftToRight)
        else:
            self.boxLayout.setDirection(QBoxLayout.Direction.TopToBottom)

    def setIconColor(self, val):
        self.iconColor = val
        self.iconColorUnsetted = False

    def setIconSize(self, val):
        self.iconSize = val

    def setIconBorderWidth(self, val):
        self.background.resize(val, self.icon.height())

    def setIconBorderHeight(self, val):
        self.background.resize(self.icon.width(), val)

    def setIconBorderSize(self, width, height):
        self.background.resize(width, height)

    def setPaddings(self, hori, vert):
        self.horizontalPadding = hori
        self.verticalPadding = vert

    def setIconSource(self, val):
        self.icon.setIconSource(val)

    def setContent(self, val):
        self.content = val

    def closeEvent(self, event):
        self.tooltip.close()
        return super().closeEvent(event)

    def hideEvent(self, event):
        self.tooltip.hide()
        return super().hideEvent(event)


class LingmoImageButton(LingmoFrame):
    def __init__(
        self,
        normalImage: str,
        parent=None,
        show=True,
        hoveredImage: str | None = None,
        pushedImage: str | None = None,
    ):
        super().__init__(parent, show)
        self.normalImage = normalImage
        self.hoveredImage = self.normalImage if hoveredImage == None else hoveredImage
        self.pushedImage = self.normalImage if pushedImage == None else pushedImage
        self.image = LingmoLabel(self)
        self.resize(12, 12)
        self.image.pressed.connect(self.pressed.emit)

    def updateEvent(self):
        try:
            self.resize(self.size())
            if self.isPressed():
                self.image.setPixmap(QPixmap(self.pushedImage))
            elif self.isHovered():
                self.image.setPixmap(QPixmap(self.hoveredImage))
            else:
                self.image.setPixmap(QPixmap(self.normalImage))
        except:
            pass


class LingmoInfoBar(QObject):
    class Mcontrol(QObject):
        const_success = "success"
        const_info = "info"
        const_warning = "warning"
        const_error = "error"

        class ScreenlayoutComponent(LingmoFrame):
            def __init__(self, root: QWidget, maxWidth=300):
                self.spacing = 20
                self.posy = 0
                self.maxWidth = maxWidth
                self.deleted = False
                super().__init__(parent=root)
                self.addStyleSheet("background-color", "transparent")
                self.posYAnimation = LingmoAnimation(self, "posy")
                self.posYAnimation.setEasingCurve(QEasingCurve.Type.OutCubic)
                self.posYAnimation.setDuration(
                    333 if LingmoTheme.instance._animationEnabled else 0
                )

            def updateEvent(self):
                self.raise_()
                if len(self.children()) and isinstance(self.children()[0], QWidget):
                    self.resize(
                        self.parentWidget().width(),
                        len(self.children())
                        * (self.children()[0].height() + self.spacing)
                        + self.spacing,
                    )
                else:
                    self.resize(self.parentWidget().width(), self.spacing)
                self.move(self.x(), self.posy)
                for i in range(len(self.children())):
                    self.children()[i].move(
                        self.children()[i].x(),
                        (
                            self.children()[i - 1].y() + self.children()[i - 1].height()
                            if i > 0
                            else 0
                        ),
                    )

            def childEvent(self, event):
                self.updateEvent()
                if len(self.children()) == 0:
                    self.destroy()
                    self.deleteLater()
                    self.deleted = True

            def setPos(self, x, y):
                self.move(x, self.posy)
                self.posYAnimation.setStartValue(self.posy)
                self.posYAnimation.setEndValue(y)
                self.posYAnimation.start()

            def getLastLoader(self):
                if len(self.children()):
                    return self.children()[-1]
                else:
                    return None

        class ContentComponent(LingmoFrame):
            def __init__(
                self,
                parent,
                duration=1500,
                itemcomponent: QWidget = None,
                type="",
                text="",
                moremsg="",
            ):
                super().__init__(parent)
                self.duration = duration
                self.type = type
                self.text = text
                self.moremsg = moremsg
                self.delayTimer = QTimer()
                self.delayTimer.setInterval(self.duration)
                self.delayTimer.timeout.connect(self.close)
                self.itemcomponent = (
                    itemcomponent
                    if itemcomponent
                    else LingmoInfoBar.Mcontrol.LingmoStyle(self)
                )
                self.itemcomponent.setParent(self)
                self.delayTimer.start()
                self.canBeClosed = False

            def close(self):
                if self.canBeClosed:
                    self.delayTimer.deleteLater()
                    self.destroy()
                    self.deleteLater()
                else:
                    self.canBeClosed = True

            def restart(self):
                self.delayTimer.stop()
                self.delayTimer.start()

            def updateEvent(self):
                try:
                    self.resize(
                        self.itemcomponent.width() + 20,
                        self.itemcomponent.height() + 20,
                    )
                except:
                    pass
                return super().updateEvent()

        class LingmoStyle(LingmoFrame):
            def __init__(self, parent=None):
                if not isinstance(parent, LingmoInfoBar.Mcontrol.ContentComponent):
                    print(
                        "LingmoInfoBar.Mcontrol.LingmoStyle: parent must be LingmoInfoBar.Mcontrol.ContentComponent"
                    )
                    return
                self.color = QColor()
                self.borderColor = QColor()
                self.iconColor = QColor()
                if parent.type == LingmoInfoBar.Mcontrol.const_success:
                    self.iconSource = LingmoIconDef.CompletedSolid
                elif parent.type == LingmoInfoBar.Mcontrol.const_warning:
                    self.iconSource = LingmoIconDef.InfoSolid
                elif parent.type == LingmoInfoBar.Mcontrol.const_info:
                    self.iconSource = LingmoIconDef.InfoSolid
                elif parent.type == LingmoInfoBar.Mcontrol.const_error:
                    self.iconSource = LingmoIconDef.StatusErrorFull
                else:
                    self.iconSource = LingmoIconDef.InfoSolid
                super().__init__(parent=parent)
                self.shadow = LingmoShadow(self, radius=4)
                self.icon = LingmoIcon(
                    self.iconSource, parent=self, iconSize=20, autoAdjust=True
                )
                self.btnClose = LingmoIconButton(
                    LingmoIconDef.ChromeClose, parent=self, iconSize=10
                )
                self.text = LingmoText(self, text=parent.text)
                self.moreMsg = LingmoText(self, text=parent.moremsg)
                self.text.setWordWrap(True)
                self.text.setFixedWidth(self.parentWidget().parentWidget().maxWidth)
                self.moreMsg.setFixedWidth(self.parentWidget().parentWidget().maxWidth)
                self.moreMsg.setWordWrap(True)
                self.moreMsg.setVisible(parent.moremsg != "")
                self.moreMsg.setColor(LingmoColor._Grey120)
                self.btnClose.pressed.connect(parent.close)
                self.btnClose.setIconBorderSize(30, 20)
                self.btnClose.setPaddings(0, 0)
                self.btnClose.setIconColor(
                    QColor(222, 222, 222, 255)
                    if LingmoTheme.instance.dark()
                    else QColor(97, 97, 97, 255)
                )
                self.btnClose.setVisible(parent.duration <= 0)
                self.text.setAlignment(Qt.AlignmentFlag.AlignLeft)
                self.moreMsg.setAlignment(Qt.AlignmentFlag.AlignLeft)

            def updateEvent(self):
                try:
                    if LingmoTheme.instance.dark():
                        if (
                            self.parentWidget().type
                            == LingmoInfoBar.Mcontrol.const_success
                        ):
                            self.color = QColor(57, 61, 27, 255)
                        elif (
                            self.parentWidget().type
                            == LingmoInfoBar.Mcontrol.const_warning
                        ):
                            self.color = QColor(67, 53, 25, 255)
                        elif (
                            self.parentWidget().type
                            == LingmoInfoBar.Mcontrol.const_info
                        ):
                            self.color = QColor(39, 39, 39, 255)
                        elif (
                            self.parentWidget().type
                            == LingmoInfoBar.Mcontrol.const_error
                        ):
                            self.color = QColor(68, 39, 38, 255)
                        else:
                            self.color = QColor(255, 255, 255, 255)
                    else:
                        if (
                            self.parentWidget().type
                            == LingmoInfoBar.Mcontrol.const_success
                        ):
                            self.color = QColor(223, 246, 221, 255)
                        elif (
                            self.parentWidget().type
                            == LingmoInfoBar.Mcontrol.const_warning
                        ):
                            self.color = QColor(255, 244, 206, 255)
                        elif (
                            self.parentWidget().type
                            == LingmoInfoBar.Mcontrol.const_info
                        ):
                            self.color = QColor(244, 244, 244, 255)
                        elif (
                            self.parentWidget().type
                            == LingmoInfoBar.Mcontrol.const_error
                        ):
                            self.color = QColor(253, 251, 233, 255)
                        else:
                            self.color = QColor(255, 255, 255, 255)
                    if LingmoTheme.instance.dark():
                        if (
                            self.parentWidget().type
                            == LingmoInfoBar.Mcontrol.const_success
                        ):
                            self.borderColor = QColor(56, 61, 27, 255)
                        elif (
                            self.parentWidget().type
                            == LingmoInfoBar.Mcontrol.const_warning
                        ):
                            self.borderColor = QColor(66, 53, 25, 255)
                        elif (
                            self.parentWidget().type
                            == LingmoInfoBar.Mcontrol.const_info
                        ):
                            self.borderColor = QColor(38, 39, 39, 255)
                        elif (
                            self.parentWidget().type
                            == LingmoInfoBar.Mcontrol.const_error
                        ):
                            self.borderColor = QColor(67, 39, 38, 255)
                        else:
                            self.borderColor = QColor(255, 255, 255, 255)
                    else:
                        if (
                            self.parentWidget().type
                            == LingmoInfoBar.Mcontrol.const_success
                        ):
                            self.borderColor = QColor(210, 232, 208, 255)
                        elif (
                            self.parentWidget().type
                            == LingmoInfoBar.Mcontrol.const_warning
                        ):
                            self.borderColor = QColor(240, 230, 194, 255)
                        elif (
                            self.parentWidget().type
                            == LingmoInfoBar.Mcontrol.const_info
                        ):
                            self.borderColor = QColor(230, 230, 230, 255)
                        elif (
                            self.parentWidget().type
                            == LingmoInfoBar.Mcontrol.const_error
                        ):
                            self.borderColor = QColor(238, 217, 219, 255)
                        else:
                            self.borderColor = QColor(255, 255, 255, 255)
                    if LingmoTheme.instance.dark():
                        if (
                            self.parentWidget().type
                            == LingmoInfoBar.Mcontrol.const_success
                        ):
                            self.iconColor = QColor(108, 203, 95, 255)
                        elif (
                            self.parentWidget().type
                            == LingmoInfoBar.Mcontrol.const_warning
                        ):
                            self.iconColor = QColor(252, 225, 0, 255)
                        elif (
                            self.parentWidget().type
                            == LingmoInfoBar.Mcontrol.const_info
                        ):
                            self.iconColor = LingmoTheme.instance.primaryColor
                        elif (
                            self.parentWidget().type
                            == LingmoInfoBar.Mcontrol.const_error
                        ):
                            self.iconColor = QColor(255, 153, 164, 255)
                        else:
                            self.iconColor = QColor(255, 255, 255, 255)
                    else:
                        if (
                            self.parentWidget().type
                            == LingmoInfoBar.Mcontrol.const_success
                        ):
                            self.iconColor = QColor(15, 123, 15, 255)
                        elif (
                            self.parentWidget().type
                            == LingmoInfoBar.Mcontrol.const_warning
                        ):
                            self.iconColor = QColor(157, 93, 0, 255)
                        elif (
                            self.parentWidget().type
                            == LingmoInfoBar.Mcontrol.const_info
                        ):
                            self.iconColor = QColor(0, 102, 180, 255)
                        elif (
                            self.parentWidget().type
                            == LingmoInfoBar.Mcontrol.const_error
                        ):
                            self.iconColor = QColor(196, 43, 28, 255)
                        else:
                            self.iconColor = QColor(255, 255, 255, 255)
                    self.addStyleSheet("background-color", self.color)
                    self.addStyleSheet("border-color", self.borderColor)
                    self.addStyleSheet("border-width", 1)
                    self.addStyleSheet("border-style", "solid")
                    self.addStyleSheet("border-radius", 4)
                    self.icon.setIconColor(self.iconColor)
                    self.icon.move(20, 10)
                    self.text.move(self.icon.x() + self.icon.width() + 10, 10)
                    self.moreMsg.move(
                        self.text.x(), self.text.y() + self.text.height() + 5
                    )
                    self.resize(
                        self.text.x()
                        + self.text.width()
                        + (30 if self.btnClose.isVisible() else 48),
                        max(
                            self.icon.y() + self.icon.height(),
                            self.moreMsg.y() + self.moreMsg.height(),
                        )
                        + 10,
                    )
                    self.move(
                        self.parentWidget().width() / 2 - self.width() / 2,
                        self.parentWidget().height() / 2 - self.height() / 2,
                    )
                except:
                    pass

        def __init__(self, root):
            super().__init__()
            self.root = root
            self.maxwidth = 300
            self.screenLayout: LingmoInfoBar.Mcontrol.ScreenlayoutComponent = None

        def create(self, type, text, duration, moremsg):
            try:
                if self.screenLayout:
                    last = self.screenLayout.getLastLoader()
                    if (
                        last.type == type
                        and last.text == text
                        and last.moremsg == moremsg
                    ):
                        last.duration = duration
                        if duration > 0:
                            last.restart()
                        return last
            except:
                pass
            self.initScreenLayout()
            return self.ContentComponent(
                self.screenLayout,
                type=type,
                text=text,
                duration=duration,
                moremsg=moremsg,
            )

        def createCustom(self, itemcomponent, duration):
            self.initScreenLayout()
            if itemcomponent:
                return self.ContentComponent(
                    self.screenLayout, duration=duration, itemcomponent=itemcomponent
                )

        def initScreenLayout(self):
            if self.screenLayout == None or self.screenLayout.deleted:
                self.screenLayout = self.ScreenlayoutComponent(
                    self.root, maxWidth=self.maxwidth
                )
                self.screenLayout.setPos(self.screenLayout.x(), 75)

    def __init__(self, root):
        super().__init__()
        self.root = root
        self.layoutY = 75
        self.mcontrol = self.Mcontrol(self.root)

    def showSuccess(self, text, duration=1000, moremsg=""):
        return self.mcontrol.create(
            self.mcontrol.const_success, text, duration, moremsg if moremsg else ""
        )

    def showInfo(self, text, duration=1000, moremsg=""):
        return self.mcontrol.create(
            self.mcontrol.const_info, text, duration, moremsg if moremsg else ""
        )

    def showWarning(self, text, duration=1000, moremsg=""):
        return self.mcontrol.create(
            self.mcontrol.const_warning, text, duration, moremsg if moremsg else ""
        )

    def showError(self, text, duration=1000, moremsg=""):
        return self.mcontrol.create(
            self.mcontrol.const_error, text, duration, moremsg if moremsg else ""
        )

    def showCustom(self, itemcomponent, duration=1000):
        return self.mcontrol.createCustom(itemcomponent, duration)

    def clearAllInfo(self):
        if self.mcontrol.screenLayout:
            self.mcontrol.screenLayout.destroy()
            self.mcontrol.screenLayout = None


class LingmoLoadingButton(LingmoButton):
    def __init__(self, parent=None, show=True, loading=False):
        super().__init__(parent, show, autoResize=False)
        self.loading = loading
        self.ring = LingmoProgressRing(self, strokeWidth=3)
        self.ringWidth = 16
        self.ringWidthAnimation = LingmoAnimation(self, "ringWidth")
        self.ringWidthAnimation.setDuration(167)
        self.ringWidthAnimation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def updateEvent(self):
        super().updateEvent()
        try:
            self.ring.resize(self.ringWidth, 16)
            self.setDisabled(self.loading)
            self.ring.setVisible(self.ringWidth != 0)
            self.ring.move(
                self.contentText.x() + self.contentText.width() + 6,
                self.height() / 2 - self.ring.height() / 2,
            )
            self.ctrlBg.resize(
                self.contentText.x() + self.contentText.width() + self.ringWidth,
                self.height(),
            )
        except:
            pass

    def setLoading(self, val):
        self.loading = val
        self.setRingWidth(16 if self.loading else 0)

    def setRingWidth(self, val):
        if LingmoTheme.instance._animationEnabled:
            self.ringWidthAnimation.setStartValue(self.ringWidth)
            self.ringWidthAnimation.setEndValue(val)
            self.ringWidthAnimation.start()
        else:
            self.ringWidth = val


class LingmoMenuItem(LingmoFrame):
    def __init__(
        self,
        iconSource=None,
        subMenu=None,
        content="",
        autoClose=True,
        checkable=False,
        mirrored=False,
    ):
        super().__init__(show=False)
        self.iconSpacing = 5
        self.iconSource = iconSource
        self.iconSize = 16
        self.mirrored = mirrored
        self.indicator = LingmoIcon(
            LingmoIconDef.CheckMark, parent=self, show=False, autoAdjust=True
        )
        self.arrow = LingmoIcon(
            LingmoIconDef.ChevronRightMed, parent=self, show=False, autoAdjust=True
        )
        self.text = LingmoText(self)
        self.subMenu = subMenu
        self.checked = False
        self.checkable = checkable
        self.pressed.connect(self.setChecked)
        self.padding = 6
        self.iconWidth = 24
        self.iconHeight = 24
        self.content = content
        if self.iconSource:
            self.icon = LingmoIcon(
                self.iconSource, parent=self, iconSize=self.iconSize, autoAdjust=True
            )
            self.icon.resize(self.iconWidth, self.iconHeight)
        else:
            self.icon = LingmoFrame(self)
        self.text.setText(self.content)
        self.autoClose = autoClose
        self.pressed.connect(self.onPressed)
        self.resize(
            self.icon.width() + self.text.width() + 3 * self.padding,
            (
                max(self.icon.height(), self.text.height()) + 2 * self.padding
                if self.isVisible()
                else 0
            ),
        )
        self.arrowPadding = self.arrow.width() + self.iconSpacing if self.subMenu else 0
        self.indicatorPadding = (
            self.indicator.width() + self.iconSpacing if self.checkable else 0
        )
        self.leftPadding = self.arrowPadding if self.mirrored else self.indicatorPadding
        self.rightPadding = (
            self.indicatorPadding if self.mirrored else self.arrowPadding
        )

    def updateEvent(self):
        try:
            if LingmoTheme.instance.dark():
                if self.isEnabled():
                    if self.isPressed():
                        self.textColor = QColor(162, 162, 162, 255)
                    else:
                        self.textColor = QColor(255, 255, 255, 255)
                else:
                    self.textColor = QColor(131, 131, 131, 255)
            else:
                if self.isEnabled():
                    if self.isPressed():
                        self.textColor = QColor(96, 96, 96, 255)
                    else:
                        self.textColor = QColor(0, 0, 0, 255)
                else:
                    self.textColor = QColor(160, 160, 160, 255)
            self.arrowPadding = (
                self.arrow.width() + self.iconSpacing if self.subMenu else 0
            )
            self.indicatorPadding = (
                self.indicator.width() + self.iconSpacing if self.checkable else 0
            )
            self.leftPadding = (
                self.arrowPadding if self.mirrored else self.indicatorPadding
            )
            self.rightPadding = (
                self.indicatorPadding if self.mirrored else self.arrowPadding
            )
            self.addStyleSheet("border-radius", LingmoTheme.instance._roundWindowRadius)
            self.addStyleSheet(
                "background-color",
                (
                    LingmoTheme.instance.itemHoverColor
                    if self.isHovered()
                    else LingmoTheme.instance.itemNormalColor
                ),
            )
            if self.iconSource:
                self.icon.setGeometry(
                    self.padding + self.leftPadding,
                    self.padding,
                    self.iconWidth,
                    self.iconHeight,
                )
            else:
                self.icon.setGeometry(
                    self.padding + self.leftPadding, self.padding, 0, 0
                )
            self.text.move(
                self.icon.x()
                + self.icon.width()
                + (self.padding if self.iconSource else 0),
                self.height() / 2 - self.text.height() / 2,
            )
            self.resize(self.width(), 36 if self.isVisible() else 0)
            self.indicator.setVisible(self.checked)
            self.arrow.setVisible(bool(self.subMenu))
            self.indicator.move(
                self.width() - self.rightPadding if self.mirrored else 6,
                self.height() / 2 - self.indicator.height() / 2,
            )
            self.arrow.move(
                6 if self.mirrored else self.width() - self.rightPadding,
                self.height() / 2 - self.arrow.height() / 2,
            )
            self.text.setFont(LingmoTextStyle.body)
            if self.iconSource:
                self.icon.setIconColor(self.palette().windowText())
        except:
            pass

    def setChecked(self):
        self.checked = not self.checked if self.checkable else False

    def onPressed(self):
        if self.subMenu and isinstance(self.subMenu, LingmoMenu):
            self.subMenu.setPosition(
                self.parentWidget().mapToGlobal(
                    QPoint(self.x() + self.width() + 2, self.y())
                )
            )
            self.subMenu.showMenu()
        elif self.autoClose and isinstance(
            self.parentWidget().parentWidget(), LingmoMenu
        ):
            self.parentWidget().parentWidget().hideMenu()

    def getWidth(self):
        return (
            self.icon.width()
            + self.text.width()
            + 3 * self.padding
            + self.leftPadding
            + self.rightPadding
        )


class LingmoMenu(LingmoFrame):
    showed = Signal()
    hided = Signal()

    def __init__(self, position=None, animationEnabled=True, autoResize=True):
        super().__init__(show=False)
        self.animationEnabled = animationEnabled
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.scrolled = False
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.opacity = 0
        self.background = LingmoFrame(self)
        self.background.move(5, 5)
        self.background.addStyleSheet(
            "background-color",
            (
                QColor(45, 45, 45, 255)
                if LingmoTheme.instance.dark()
                else QColor(252, 252, 252, 255)
            ),
        )
        self.background.addStyleSheet("border-style", "solid")
        self.background.addStyleSheet("border-width", 1)
        self.background.addStyleSheet(
            "border-color",
            (
                QColor(26, 26, 26, 255)
                if LingmoTheme.instance.dark()
                else QColor(191, 191, 191, 255)
            ),
        )
        self.background.addStyleSheet(
            "border-radius", LingmoTheme.instance._roundWindowRadius + 1
        )
        self.shadow = LingmoShadow(
            self.background, radius=LingmoTheme.instance._roundWindowRadius
        )
        self.position = position
        self.items: list[LingmoMenuItem] = []
        self.showAnimation = LingmoAnimation(self, "opacity")
        self.showAnimation.setStartValue(0)
        self.showAnimation.setEndValue(1)
        self.hideAnimation = LingmoAnimation(self, "opacity")
        self.hideAnimation.setStartValue(1)
        self.hideAnimation.setEndValue(0)
        self.scrollbar = LingmoScrollBar(
            self, target=self.background, orientation=Qt.Orientation.Vertical
        )
        self.scrollbar.setOffsetDecrease(5)
        self.scrollbar.setOffsetIncrease(5)
        self.scrollbar.setOffsetPerpendicalar(5)
        self.autoResize = autoResize
        self.hideAnimation.finished.connect(self.hide)

    def updateEvent(self):
        try:
            if self.position:
                self.move(self.position)
            self.addStyleSheet("background-color", "transparent")
            self.setWindowOpacity(self.opacity)
            self.resize(
                self.background.width() + 10,
                300 if self.scrolled else self.background.height() + 10,
            )
            self.scrollbar.setVisible(self.scrolled)
            maxWidth = 0
            for i in range(len(self.items)):
                maxWidth = max(maxWidth, self.items[i].getWidth())
                if i == 0:
                    self.items[i].move(4, 4)
                else:
                    self.items[i].move(
                        4,
                        self.items[i - 1].y()
                        + self.items[i - 1].height()
                        + (4 if self.items[i - 1].isVisible() else 0),
                    )
            if self.autoResize:

                for i in range(len(self.items)):
                    self.items[i].resize(maxWidth, self.items[i].height())
                self.background.resize(
                    maxWidth + 8,
                    (
                        (self.items[-1].y() + self.items[-1].height() + 4)
                        if len(self.items)
                        else 36
                    ),
                )
            else:
                for i in range(len(self.items)):
                    self.items[i].resize(
                        self.background.width() - 8, self.items[i].height()
                    )
                self.background.resize(
                    self.background.width(),
                    (
                        (self.items[-1].y() + self.items[-1].height() + 4)
                        if len(self.items)
                        else 36
                    ),
                )
            self.scrolled = len(self.items) > 10
        except:
            pass

    def showMenu(self):
        pos = QCursor.pos() if self.position == None else self.position
        self.move(pos)
        self.setVisible(True)
        self.showAnimation.setDuration(
            83
            if LingmoTheme.instance._animationEnabled and self.animationEnabled
            else 0
        )
        self.showAnimation.start()
        self.showed.emit()

    def hideMenu(self):
        self.hideAnimation.setDuration(
            83
            if LingmoTheme.instance._animationEnabled and self.animationEnabled
            else 0
        )
        self.hideAnimation.start()
        for i in self.items:
            if i.subMenu:
                i.subMenu.hideMenu()
        self.hided.emit()

    def addItem(self, item: LingmoMenuItem):
        self.items.append(item)
        item.setParent(self.background)

    def setPosition(self, val):
        self.position = val

    def focusOutEvent(self, event):
        self.hideMenu()
        return super().focusOutEvent(event)

    def count(self):
        return len(self.items)


class LingmoProgressButton(LingmoButton):
    def __init__(self, parent=None, show=True, content="", progress=0):
        super().__init__(parent, show)
        self.progress = progress
        self.ctrlBg.deleteLater()
        self.ctrlBg = LingmoControlBackground(self)
        self.ctrlBg.setRadius(LingmoTheme.instance._roundWindowRadius)
        self.clip = LingmoClip(
            self.ctrlBg, radius=LingmoTheme.instance._roundWindowRadius
        )
        self.rectBack = LingmoFrame(self.clip)
        self.setContent(content)
        self.setClickShadowChange(False)
        self.focusRect = LingmoFocusRectangle(self.ctrlBg)
        self.focusRect.setRadius(4)
        self.rectBackWidth = self.clip.width() * self.progress
        self.rectBackHeight = 3
        self.widthAnimation = LingmoAnimation(self, "rectBackWidth")
        self.widthAnimation.setDuration(167)
        self.heightAnimation = QSequentialAnimationGroup()
        self.heightAnimation1 = QPauseAnimation(
            167 if LingmoTheme.instance._animationEnabled else 0
        )
        self.heightAnimation2 = LingmoAnimation(self, "rectBackHeight")
        self.heightAnimation2.setDuration(167)

    def updateEvent(self):
        try:
            if self.checked():
                self.textNormalColor = (
                    QColor(0, 0, 0, 255)
                    if LingmoTheme.instance.dark()
                    else QColor(255, 255, 255, 255)
                )
                self.textPressedColor = self.textNormalColor
                self.textDisabledColor = (
                    QColor(173, 173, 173, 255)
                    if LingmoTheme.instance.dark()
                    else QColor(255, 255, 255, 255)
                )
            else:
                self.textNormalColor = (
                    QColor(255, 255, 255, 255)
                    if LingmoTheme.instance.dark()
                    else QColor(0, 0, 0, 255)
                )
                self.textPressedColor = (
                    QColor(162, 162, 162, 255)
                    if LingmoTheme.instance.dark()
                    else QColor(96, 96, 96, 255)
                )
                self.textDisabledColor = (
                    QColor(131, 131, 131, 255)
                    if LingmoTheme.instance.dark()
                    else QColor(160, 160, 160, 255)
                )
            super().updateEvent()
            self.normalColor = (
                LingmoTheme.instance.primaryColor
                if self.checked()
                else (
                    QColor(62, 62, 62, 255)
                    if LingmoTheme.instance.dark()
                    else QColor(254, 254, 254, 255)
                )
            )
            self.hoverColor = (
                (
                    self.normalColor.darker(110)
                    if LingmoTheme.instance.dark()
                    else self.normalColor.lighter(110)
                )
                if self.checked()
                else (
                    QColor(68, 68, 68, 255)
                    if LingmoTheme.instance.dark()
                    else QColor(246, 246, 246, 255)
                )
            )
            self.disableColor = (
                (
                    QColor(82, 82, 82, 255)
                    if LingmoTheme.instance.dark()
                    else QColor(199, 199, 199, 255)
                )
                if self.checked()
                else (
                    QColor(59, 59, 59, 255)
                    if LingmoTheme.instance.dark()
                    else QColor(244, 244, 244, 255)
                )
            )
            self.pressedColor = (
                self.normalColor.darker(120)
                if LingmoTheme.instance.dark()
                else self.normalColor.lighter(120)
            )
            self.clip.resize(self.ctrlBg.size())
            if not self.isEnabled():
                self.bgColor = self.disableColor
            elif self.isPressed() and self.checked():
                self.bgColor = self.pressedColor
            elif self.isHovered():
                self.bgColor = self.hoverColor
            else:
                self.bgColor = self.normalColor
            self.ctrlBg.move(self.horizontalPadding, self.verticalPadding)
            self.ctrlBg.setBorderWidth(0 if self.checked() else 1)
            self.ctrlBg.setColor(self.bgColor)
            self.rectBack.resize(self.rectBackWidth, self.rectBackHeight)
            self.rectBack.setVisible(not self.checked())
            self.rectBack.addStyleSheet(
                "background-color", LingmoTheme.instance.primaryColor
            )
        except:
            pass

    def checked(self):
        return self.rectBack.height() == self.ctrlBg.height() and self.progress == 1

    def setRectBackWidth(self, val):
        if val != self.rectBackWidth:
            self.widthAnimation.setStartValue(self.rectBackWidth)
            self.widthAnimation.setEndValue(val)
            self.widthAnimation.start()

    def setRectBackHeight(self, val):
        if val != self.rectBackHeight:
            self.heightAnimation2.setStartValue(self.rectBackHeight)
            self.heightAnimation2.setEndValue(val)
            self.heightAnimation.start()

    def setProgress(self, val):
        self.progress = val
        self.setRectBackWidth(self.clip.width() * self.progress)
        self.setRectBackHeight(self.clip.height() if self.progress == 1 else 3)


class LingmoPopup(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoProgressRing(LingmoFrame):
    def __init__(
        self,
        parent=None,
        show=True,
        duration=2000,
        strokeWidth=6,
        progressVisible=False,
        color=LingmoTheme.instance.primaryColor,
        indeterminate=True,
        clip=True,
        progress=0,
    ):
        super().__init__(parent, show)
        self.duration = duration
        self.strokeWidth = strokeWidth
        self.progressVisible = progressVisible
        self.color = color
        self.backgroundColor = (
            QColor(99, 99, 99, 255)
            if LingmoTheme.instance.dark()
            else QColor(214, 214, 214, 255)
        )
        self.indeterminate = indeterminate
        self.clip = clip
        self.resize(56, 56)
        self.addStyleSheet("background-color", "transparent")
        self.addStyleSheet("border-color", self.backgroundColor)
        self.addStyleSheet("border-width", self.strokeWidth)
        self.addStyleSheet("border-style", "solid")
        self.visualPosition = progress
        self.startAngle = 0
        self.sweepAngle = 0
        self.startAngleAnimation = QSequentialAnimationGroup()
        self.sweepAngleAnimation = QSequentialAnimationGroup()
        self.startAngleAnimation1 = LingmoAnimation(self, "startAngle")
        self.startAngleAnimation1.setStartValue(0)
        self.startAngleAnimation1.setEndValue(450)
        self.startAngleAnimation2 = LingmoAnimation(self, "startAngle")
        self.startAngleAnimation2.setStartValue(450)
        self.startAngleAnimation2.setEndValue(1080)
        self.sweepAngleAnimation1 = LingmoAnimation(self, "sweepAngle")
        self.sweepAngleAnimation1.setStartValue(0)
        self.sweepAngleAnimation1.setEndValue(180)
        self.sweepAngleAnimation2 = LingmoAnimation(self, "sweepAngle")
        self.sweepAngleAnimation2.setStartValue(180)
        self.sweepAngleAnimation2.setEndValue(0)
        self.startAngleAnimation.addAnimation(self.startAngleAnimation1)
        self.startAngleAnimation.addAnimation(self.startAngleAnimation2)
        self.sweepAngleAnimation.addAnimation(self.sweepAngleAnimation1)
        self.sweepAngleAnimation.addAnimation(self.sweepAngleAnimation2)
        self.startAngleAnimation.setLoopCount(-1)
        self.sweepAngleAnimation.setLoopCount(-1)
        self.startAngleAnimation1.setDuration(self.duration / 2)
        self.startAngleAnimation2.setDuration(self.duration / 2)
        self.sweepAngleAnimation1.setDuration(self.duration / 2)
        self.sweepAngleAnimation2.setDuration(self.duration / 2)
        if indeterminate:
            self.startAngleAnimation.start()
            self.sweepAngleAnimation.start()
        self.text = LingmoText(self)

    def updateEvent(self):
        try:
            self.addStyleSheet("border-radius", self.width() / 2)
            self._radius = self.width() / 2 - self.strokeWidth
            self._progress = 0 if self.indeterminate else self.visualPosition
            self.text.setVisible((not self.indeterminate) and self.progressVisible)
            self.text.setText(str(int(self.visualPosition * 100)) + "%")
            self.text.move(
                self.width() / 2 - self.text.width() / 2,
                self.height() / 2 - self.text.height() / 2,
            )
        except:
            pass

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen()
        pen.setColor(self.color)
        pen.setWidth(self.strokeWidth / 6 * 7)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        if self.indeterminate:
            painter.drawArc(
                self.strokeWidth / 2,
                self.strokeWidth / 2,
                self.width() - self.strokeWidth,
                self.height() - self.strokeWidth,
                self.startAngle * 16,
                self.sweepAngle * 16,
            )
        else:
            painter.drawArc(
                self.strokeWidth / 2,
                self.strokeWidth / 2,
                self.width() - self.strokeWidth,
                self.height() - self.strokeWidth,
                -0.5 * math.pi,
                self._progress * 360 * 16,
            )

    def setIndeterminate(self, val):
        self.indeterminate = val
        if val:
            self.startAngleAnimation.start()
            self.sweepAngleAnimation.start()
        else:
            self.startAngleAnimation.stop()
            self.sweepAngleAnimation.stop()

    def setProgress(self, val):
        self.visualPosition = val
    
    def setStrokeWidth(self, val):
        self.strokeWidth = val


class LingmoScrollBar(LingmoFrame):
    def __init__(
        self,
        parent=None,
        target: QWidget = None,
        show=True,
        orientation=Qt.Orientation.Horizontal,
        color=(
            QColor(159, 159, 159, 255)
            if LingmoTheme.instance.dark()
            else QColor(138, 138, 138, 255)
        ),
        autoOffsetDecrease=False,
        autoOffsetIncrease=False,
    ):
        super().__init__(parent, show)
        self.orientation = orientation
        self.target = target
        self.color = color
        self.pressedColor = (
            QColor.darker(self.color)
            if LingmoTheme.instance.dark()
            else QColor.lighter(self.color)
        )
        self.minLine = 2
        self.maxLine = 6
        self.position = 0
        self.stepLength = 10
        self.horizontalPadding = 15 if self.horizontal() else 3
        self.verticalPadding = 15 if self.vertical else 3
        self.horiDecrButton = LingmoIconButton(
            LingmoIconDef.CaretLeftSolid8, parent=self
        )
        self.horiIncrButton = LingmoIconButton(
            LingmoIconDef.CaretRightSolid8, parent=self
        )
        self.vertDecrButton = LingmoIconButton(LingmoIconDef.CaretUpSolid8, parent=self)
        self.vertIncrButton = LingmoIconButton(
            LingmoIconDef.CaretDownSolid8, parent=self
        )
        self.bar = LingmoFrame(self)
        self.barWidth = self.minLine
        self.horiDecrButton.setPaddings(2, 2)
        self.horiIncrButton.setPaddings(2, 2)
        self.vertDecrButton.setPaddings(2, 2)
        self.vertIncrButton.setPaddings(2, 2)
        self.horiDecrButton.pressed.connect(self.decrease)
        self.horiIncrButton.pressed.connect(self.increase)
        self.vertDecrButton.pressed.connect(self.decrease)
        self.vertIncrButton.pressed.connect(self.increase)
        self.animation = QSequentialAnimationGroup()
        self.animation1 = QPauseAnimation()
        self.animation2 = LingmoAnimation(self, "barWidth")
        self.animation2.setDuration(167)
        self.animation2.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.addAnimation(self.animation1)
        self.animation.addAnimation(self.animation2)
        self.hovered.connect(lambda: self.setBarWidth(self.maxLine))
        self.left.connect(lambda: self.setBarWidth(self.minLine))
        self.scrolling = False
        self.scrollPos = QPoint()
        self.barFirstPos = QPoint()
        self.bar.pressed.connect(lambda: self.setScrolling(True))
        self.bar.released.connect(lambda: self.setScrolling(False))
        self.offsetDecrease = 0
        self.offsetIncrease = 0
        self.offsetPerpendicular = 0
        self.autoOffsetDecrease = autoOffsetDecrease
        self.autoOffsetIncrease = autoOffsetIncrease

    def updateEvent(self):
        try:
            self.horizontalPadding = 15 if self.horizontal() else 3
            self.verticalPadding = 15 if self.vertical() else 3
            self.raise_()
            self.horiDecrButton.setVisible(self.horizontal())
            self.horiIncrButton.setVisible(self.horizontal())
            self.vertDecrButton.setVisible(self.vertical())
            self.vertIncrButton.setVisible(self.vertical())
            self.horiDecrButton.setIconBorderSize(8, 8)
            self.horiIncrButton.setIconBorderSize(8, 8)
            self.vertDecrButton.setIconBorderSize(8, 8)
            self.vertIncrButton.setIconBorderSize(8, 8)
            self.horiDecrButton.setIconSize(8)
            self.horiIncrButton.setIconSize(8)
            self.vertDecrButton.setIconSize(8)
            self.vertIncrButton.setIconSize(8)
            self.horiDecrButton.setIconColor(self.color)
            self.horiIncrButton.setIconColor(self.color)
            self.vertDecrButton.setIconColor(self.color)
            self.vertIncrButton.setIconColor(self.color)
            self.horiDecrButton.move(
                2, self.height() / 2 - self.horiDecrButton.height() / 2
            )
            self.horiIncrButton.move(
                self.width() - 2 - self.horiIncrButton.width(),
                self.height() / 2 - self.horiIncrButton.height() / 2,
            )
            self.vertDecrButton.move(
                self.width() / 2 - self.vertDecrButton.width() / 2, 2
            )
            self.vertIncrButton.move(
                self.width() / 2 - self.vertDecrButton.width() / 2,
                self.height() - 2 - self.vertIncrButton.height(),
            )
            self.barSize = (
                (
                    self.target.parentWidget().width() / self.target.width()
                    if self.horizontal()
                    else self.target.parentWidget().height() / self.target.height()
                )
                if self.target != None
                else 1
            )
            self.bar.resize(
                (
                    self.barSize * (self.width() - 2 * self.horizontalPadding)
                    if self.horizontal()
                    else self.barWidth
                ),
                (
                    self.barSize * (self.height() - 2 * self.verticalPadding)
                    if self.vertical()
                    else self.barWidth
                ),
            )
            self.addStyleSheet(
                "background-color",
                (
                    QColor(44, 44, 44, 255)
                    if LingmoTheme.instance.dark()
                    else QColor(255, 255, 255, 255)
                ),
            )
            self.addStyleSheet("border-radius", 5)
            if self.bar.isPressed():
                self.bar.addStyleSheet("background-color", self.pressedColor)
            else:
                self.bar.addStyleSheet("background-color", self.color)
            self.bar.addStyleSheet("border-radius", self.barWidth / 2)
            self.resize(
                (
                    self.parentWidget().width()
                    - self.offsetDecrease
                    - self.offsetIncrease
                    if self.horizontal()
                    else self.horizontalPadding * 2 + self.vertDecrButton.width()
                ),
                (
                    self.parentWidget().height()
                    - self.offsetDecrease
                    - self.offsetIncrease
                    if self.vertical()
                    else self.verticalPadding * 2 + self.horiDecrButton.height()
                ),
            )
            self.move(
                (
                    self.offsetDecrease
                    if self.horizontal()
                    else self.parentWidget().width()
                    - self.width()
                    - self.offsetPerpendicular
                ),
                (
                    self.offsetDecrease
                    if self.vertical()
                    else self.parentWidget().height()
                    - self.height()
                    - self.offsetPerpendicular
                ),
            )
            self.bar.setVisible(self.barSize < 1)
            self.visualPosition = self.position if self.barSize < 1 else 0
            self.target.move(
                (
                    -self.visualPosition
                    * (self.target.width() - self.target.parentWidget().width())
                    if self.horizontal()
                    else self.target.x()
                ),
                (
                    -self.visualPosition
                    * (self.target.height() - self.target.parentWidget().height())
                    if self.vertical()
                    else self.target.y()
                ),
            )
            if self.scrolling:
                pos = QCursor.pos()
                if self.horizontal():
                    self.bar.move(
                        min(
                            max(
                                self.barFirstPos.x() - (self.scrollPos.x() - pos.x()),
                                self.horizontalPadding,
                            ),
                            self.width() - self.bar.width() - self.horizontalPadding,
                        ),
                        self.barFirstPos.y(),
                    )
                else:
                    self.bar.move(
                        self.barFirstPos.x(),
                        min(
                            max(
                                self.barFirstPos.y() - (self.scrollPos.y() - pos.y()),
                                self.verticalPadding,
                            ),
                            self.height() - self.bar.height() - self.verticalPadding,
                        ),
                    )
                self.position = (
                    (self.bar.x() - self.horizontalPadding)
                    / (self.width() - self.bar.width() - 2 * self.horizontalPadding)
                    if self.horizontal()
                    else (self.bar.y() - self.verticalPadding)
                    / (self.height() - self.bar.height() - 2 * self.verticalPadding)
                )
            else:
                self.bar.move(
                    (
                        self.horizontalPadding
                        + self.position
                        * (self.width() - 2 * self.horizontalPadding - self.bar.width())
                        if self.horizontal()
                        else self.width() / 2 - self.bar.width() / 2
                    ),
                    (
                        self.verticalPadding
                        + self.position
                        * (self.height() - 2 * self.verticalPadding - self.bar.height())
                        if self.vertical()
                        else self.height() / 2 - self.bar.height() / 2
                    ),
                )
            if self.autoOffsetDecrease:
                self.setOffsetDecrease(
                    self.width() if self.vertical() else self.height()
                )
            if self.autoOffsetIncrease:
                self.setOffsetIncrease(
                    self.width() if self.vertical() else self.height()
                )
        except:
            pass

    def horizontal(self):
        return self.orientation == Qt.Orientation.Horizontal

    def vertical(self):
        return self.orientation == Qt.Orientation.Vertical

    def increase(self):
        if self.target != None:
            if self.horizontal():
                self.position += 10 / (
                    self.target.width() - self.target.parentWidget().width()
                )
            else:
                self.position += 10 / (
                    self.target.height() - self.target.parentWidget().height()
                )
            self.position = min(self.position, 1)

    def decrease(self):
        if self.target != None:
            if self.horizontal():
                self.position -= 10 / (
                    self.target.width() - self.target.parentWidget().width()
                )
            else:
                self.position -= 10 / (
                    self.target.height() - self.target.parentWidget().height()
                )
            self.position = max(self.position, 0)

    def setBarWidth(self, val):
        if val == self.maxLine:
            self.animation1.setDuration(450)
        else:
            self.animation1.setDuration(150)
        self.animation2.setStartValue(self.barWidth)
        self.animation2.setEndValue(val)
        self.animation.start()

    def setScrolling(self, val):
        if val == True:
            self.scrollPos = QCursor.pos()
            self.barFirstPos = self.bar.pos()
        self.scrolling = val

    def setOrientation(self, val):
        self.orientation = val

    def setOffsetDecrease(self, val):
        self.offsetDecrease = val

    def setOffsetIncrease(self, val):
        self.offsetIncrease = val

    def setOffsetPerpendicalar(self, val):
        self.offsetPerpendicular = val


class LingmoShadow(LingmoFrame):
    def __init__(
        self, parent: QWidget = None, elevation=5, color=QColor(0, 0, 0, 255), radius=4
    ):
        self.parentObject = parent
        super().__init__(show=False)
        self.elevation = elevation
        self.color = color
        self.radius = radius
        self.widgets = [
            LingmoFrame(self.parentObject.parentWidget()) for i in range(self.elevation)
        ]
        self.timer.timeout.connect(self.updateEvent)

    def updateEvent(self):
        try:
            geometry = self.parentObject.geometry()
            hPadding = (
                self.parentObject.horizontalPadding
                if hasattr(self.parentObject, "horizontalPadding")
                else 0
            )
            vPadding = (
                self.parentObject.verticalPadding
                if hasattr(self.parentObject, "verticalPadding")
                else 0
            )
            self.parentObject.raise_()
            for i in range(1, len(self.widgets) + 1):
                self.widgets[i - 1].setGeometry(
                    geometry.left() - i + hPadding,
                    geometry.top() - i + vPadding,
                    geometry.width() + 2 * i - 2 * hPadding,
                    geometry.height() + 2 * i - 2 * vPadding,
                )
                self.widgets[i - 1].addStyleSheet("background-color", "#00000000")
                self.widgets[i - 1].addStyleSheet("border-width", i)
                self.widgets[i - 1].addStyleSheet("border-style", "solid")
                self.widgets[i - 1].addStyleSheet("border-radius", self.radius + i)
                self.widgets[i - 1].addStyleSheet(
                    "border-color",
                    QColor(
                        self.color.red(),
                        self.color.green(),
                        self.color.blue(),
                        255 * 0.01 * (self.elevation - i + 1),
                    ),
                )
        except:
            pass


class LingmoSlider(LingmoFrame):
    def __init__(
        self,
        parent=None,
        show=True,
        tooltipEnabled=True,
        orientation=Qt.Orientation.Horizontal,
    ):
        super().__init__(parent, show)
        self.tooltipEnabled = tooltipEnabled
        self.background = LingmoFrame(self)
        self.backgroundLength = 180
        self.backgroundWidth = 6
        self.addPage = LingmoFrame(self.background)
        self.handle = LingmoFrame(self)
        self.horizontalPadding = 10
        self.verticalPadding = 10
        self.visualPosition = 0.7
        self.stepSize = 1
        self.fromValue = 0
        self.toValue = 100
        self.orientation = orientation
        self.iconScale = 1
        self.value = 0
        self.shadow = LingmoShadow(self.handle, radius=10)
        self.icon = LingmoIcon(
            LingmoIconDef.FullCircleMask, self.handle, autoAdjust=True
        )
        self.iconScaleAnimation = LingmoAnimation(self, "iconScale")
        self.iconScaleAnimation.setDuration(167)
        self.iconScaleAnimation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.handle.pressed.connect(lambda: self.setIconScale(0.8))
        self.handle.released.connect(
            lambda: self.setIconScale(1.2 if self.isHovered() else 1.0)
        )
        self.handle.hovered.connect(lambda: self.setIconScale(1.2))
        self.handle.left.connect(lambda: self.setIconScale(1.0))
        self.handle.pressed.connect(lambda: self.setSliding(True))
        self.handle.released.connect(lambda: self.setSliding(False))
        self.tooltip = LingmoToolTip(self.handle)
        self.sliding = False
        self.slidePos = QPoint()
        self.handleFirstPos = QPoint()
        self.icon.pressed.connect(self.handle.pressed.emit)
        self.icon.released.connect(self.handle.released.emit)

    def updateEvent(self):
        try:
            self.handle.resize(20, 20)
            self.handle.addStyleSheet("border-radius", 10)
            self.handle.addStyleSheet(
                "background-color",
                (
                    QColor(69, 69, 69, 255)
                    if LingmoTheme.instance.dark()
                    else QColor(255, 255, 255, 255)
                ),
            )
            self.icon.move(
                self.handle.width() / 2 - self.icon.width() / 2,
                self.handle.height() / 2 - self.icon.height() / 2,
            )
            self.icon.setIconSize(self.iconScale * 10)
            self.icon.setIconColor(LingmoTheme.instance.primaryColor)
            self.background.setFixedSize(
                self.backgroundLength if self.horizontal() else self.backgroundWidth,
                self.backgroundWidth if self.horizontal() else self.backgroundLength,
            )
            self.background.addStyleSheet("border-radius", 2)
            self.background.addStyleSheet(
                "background-color",
                (
                    QColor(162, 162, 162, 255)
                    if LingmoTheme.instance.dark()
                    else QColor(138, 138, 138, 255)
                ),
            )
            self.background.move(self.horizontalPadding, self.verticalPadding)
            self.addPage.move(
                0,
                (
                    0
                    if self.horizontal()
                    else self.background.height()
                    - self.visualPosition * self.background.height()
                    + (1 if self.visualPosition != 1 else 0)
                ),
            )
            self.addPage.resize(
                (
                    self.visualPosition * self.background.width()
                    if self.horizontal()
                    else 6
                ),
                (
                    6
                    if self.horizontal()
                    else self.visualPosition * self.background.height()
                ),
            )
            self.addPage.addStyleSheet("border-radius", 3)
            self.addPage.addStyleSheet(
                "background-color", LingmoTheme.instance.primaryColor
            )
            self.resize(
                self.horizontalPadding * 2 + self.background.width(),
                self.verticalPadding * 2 + self.background.height(),
            )
            self.tooltip.setDisabled(not self.tooltipEnabled)
            self.value = (
                (self.fromValue + self.visualPosition * (self.toValue - self.fromValue))
                * self.stepSize
                // self.stepSize
            )
            self.value = int(self.value) if self.value % 1 == 0 else self.value
            self.tooltip.setContent("  " + str(self.value) + "  ")
            if self.sliding:
                pos = QCursor.pos()
                if self.horizontal():
                    self.handle.move(
                        min(
                            max(
                                self.handleFirstPos.x() - (self.slidePos.x() - pos.x()),
                                self.handle.width() / 2,
                            ),
                            self.background.width() - self.handle.width() / 2,
                        ),
                        self.handleFirstPos.y(),
                    )
                else:
                    self.handle.move(
                        self.handleFirstPos.x(),
                        min(
                            max(
                                self.handleFirstPos.y() - (self.slidePos.y() - pos.y()),
                                self.handle.height() / 2,
                            ),
                            self.background.height() - self.handle.height() / 2,
                        ),
                    )
                self.visualPosition = (
                    (self.handle.x() - self.handle.width() / 2)
                    / (self.background.width() - self.handle.width())
                    if self.horizontal()
                    else 1
                    - (self.handle.y() - self.handle.height() / 2)
                    / (self.background.height() - self.handle.height())
                )
            else:
                self.handle.move(
                    self.horizontalPadding
                    + (self.visualPosition if self.horizontal() else 0.5)
                    * (self.background.width() - self.handle.width()),
                    self.verticalPadding
                    + (0.5 if self.horizontal() else (1 - self.visualPosition))
                    * (self.background.height() - self.handle.height()),
                )
        except:
            pass

    def setIconScale(self, val):
        self.iconScaleAnimation.setStartValue(self.iconScale)
        self.iconScaleAnimation.setEndValue(val)
        self.iconScaleAnimation.start()

    def setSliding(self, val):
        if val == True:
            self.slidePos = QCursor.pos()
            self.handleFirstPos = self.handle.pos()
        self.sliding = val

    def horizontal(self):
        return self.orientation == Qt.Orientation.Horizontal

    def vertical(self):
        return self.orientation == Qt.Orientation.Vertical

    def setOrientation(self, val):
        self.orientation = val


class LingmoText(LingmoLabel):
    def __init__(
        self,
        parent=None,
        show=True,
        text="",
        color=LingmoTheme.instance.fontPrimaryColor,
        autoAdjust=True,
    ):
        super().__init__(parent, show, autoAdjust=autoAdjust)
        self.colorEnabled = True
        self.color = color
        self.renderType = (
            Qt.TextFormat.PlainText
            if LingmoTheme.instance._nativeText
            else Qt.TextFormat.AutoText
        )
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setFont(LingmoTextStyle.body)
        self.setText(text)

    def updateEvent(self):
        self.addStyleSheet(
            "color",
            QColor(
                self.color
                if self.colorEnabled
                else (
                    qRgba(131, 131, 131, 255)
                    if LingmoTheme.instance.dark()
                    else qRgba(160, 160, 160, 255)
                )
            ),
        )
        self.setTextFormat(self.renderType)

    def setColorEnabled(self, val: bool):
        self.colorEnabled = val

    def setColor(self, val):
        self.color = val


class LingmoTextBox(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoTextBoxBackground(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoTextBoxMenu(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoTextButton(LingmoFrame):
    def __init__(
        self,
        parent=None,
        show=True,
        content="",
        normalColor=LingmoTheme.instance.primaryColor,
        hoverColor: QColor = None,
        pressedColor: QColor = None,
        disableColor=(
            QColor(82, 82, 82, 255)
            if LingmoTheme.instance.dark()
            else QColor(199, 199, 199, 255)
        ),
        backgroundHoverColor=LingmoTheme.instance.itemHoverColor,
        backgroundPressedColor=LingmoTheme.instance.itemPressColor,
        backgroundNormalColor=LingmoTheme.instance.itemNormalColor,
        backgroundDisableColor=LingmoTheme.instance.itemNormalColor,
        textBold=True,
    ):
        super().__init__(parent, show)
        self.content = content
        self.normalColor = normalColor
        self.hoverColor = (
            (
                QColor.darker(self.normalColor, 115)
                if LingmoTheme.instance.dark()
                else QColor.lighter(self.normalColor, 115)
            )
            if hoverColor == None
            else hoverColor
        )
        self.pressedColor = (
            (
                QColor.darker(self.normalColor, 130)
                if LingmoTheme.instance.dark()
                else QColor.lighter(self.normalColor, 130)
            )
            if pressedColor == None
            else pressedColor
        )
        self.disableColor = disableColor
        self.backgroundNormalColor = backgroundNormalColor
        self.backgroundHoverColor = backgroundHoverColor
        self.backgroundPressedColor = backgroundPressedColor
        self.backgroundDisableColor = backgroundDisableColor
        self.textBold = textBold
        self.horizontalPadding = 12
        self.verticalPadding = 0
        self.ctrlBg = LingmoFrame(self)
        self.ctrlBg.setGeometry(
            self.horizontalPadding,
            self.verticalPadding,
            self.width() - 2 * self.horizontalPadding,
            self.height() - 2 * self.verticalPadding,
        )
        self.setFont(LingmoTextStyle.body)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.focusRect = LingmoFocusRectangle(self.ctrlBg, radius=8)
        self.focusRect.resize(self.ctrlBg.size())
        self.contentText = LingmoText(self)
        self.contentText.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contentText.setFont(self.font())

    def updateEvent(self):
        try:
            self.textColor = self.normalColor
            self.backgroundColor = self.backgroundNormalColor
            if not self.isEnabled():
                self.textColor = self.disableColor
                self.backgroundColor = self.backgroundDisableColor
            elif self.isPressed():
                self.textColor = self.pressedColor
                self.backgroundColor = self.backgroundPressedColor
            elif self.isHovered():
                self.textColor = self.hoverColor
                self.backgroundColor = self.backgroundHoverColor
            self.ctrlBg.addStyleSheet("background-color", self.backgroundColor)
            self.ctrlBg.addStyleSheet(
                "border-radius", LingmoTheme.instance._roundWindowRadius
            )
            self.contentText.addStyleSheet("color", self.textColor)
            self.focusRect.setVisible(self.hasFocus())
            self.contentText.setText(self.content)
            self.contentText.move(
                self.width() / 2 - self.contentText.width() / 2,
                self.height() / 2 - self.contentText.height() / 2,
            )
        except:
            pass

    def setContent(self, val):
        self.content = val

    def setTextBold(self, val):
        self.textBold = val


class LingmoToolTip(LingmoFrame):
    def __init__(self, parent: QWidget, interval=0, content="", padding=6, margins=6):
        self.parentObject = parent
        super().__init__(show=False)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.background = LingmoFrame(self)
        self.text = LingmoText(self.background)
        self.content = content
        self.text.setText(content)
        self.text.setWordWrap(True)
        self.padding = padding
        self.margins = margins
        self.background.setGeometry(
            self.padding,
            self.padding,
            self.text.width() + self.padding,
            self.text.height() + self.padding,
        )
        self.text.setFont(LingmoTextStyle.body)
        self.listening = False
        self.timer1 = QTimer()
        self.interval = interval
        self.shadow = LingmoShadow(
            self.background, radius=LingmoTheme.instance._roundWindowRadius
        )
        self.timer1.timeout.connect(lambda: self.isVisible())

    def updateEvent(self):
        try:
            self.addStyleSheet("background-color", "transparent")
            self.resize(
                self.background.width() + self.margins * 2,
                self.background.height() + self.margins * 2,
            )
            self.move(
                self.parentObject.mapToGlobal(
                    QPoint(
                        self.parentObject.width() / 2 - self.width() / 2,
                        -self.height() - 3,
                    )
                )
            )
            self.background.setGeometry(
                self.padding,
                self.padding,
                self.text.width() + self.padding,
                self.text.height() + self.padding,
            )
            self.text.move(
                self.background.width() / 2 - self.text.width() / 2,
                self.background.height() / 2 - self.text.height() / 2,
            )
            self.background.addStyleSheet(
                "background-color",
                (
                    QColor(50, 49, 48, 255)
                    if LingmoTheme.instance.dark()
                    else QColor(255, 255, 255, 255)
                ),
            )
            self.background.addStyleSheet(
                "border-radius", LingmoTheme.instance._roundWindowRadius
            )
            if (
                not (self.listening)
                and self.parentObject.underMouse()
                and self.isEnabled()
            ):
                self.listen()
            elif self.isVisible() and not (self.parentObject.underMouse()):
                self.listening = False
                self.hide()
            self.text.setText(self.content)
        except:
            pass

    def listen(self):
        self.listening = True
        self.timer1.timeout.connect(self.showText)
        self.timer1.start(self.interval)

    def showText(self):
        self.show()
        self.timer1.stop()

    def setContent(self, val):
        self.content = val


class LingmoWindow(LingmoFrame):
    lazyLoad = Signal()
    initArgument = Signal(tuple)

    def __init__(
        self,
        parent=None,
        title="Lingmo Window",
        windowIcon=LingmoApp.windowIcon,
        launchMode=LingmoDefines.LaunchMode.Stantard,
        argument=({}),
        fixSize=False,
        fitsAppBarWindows=False,
        tintOpacity=0.80 if LingmoTheme.instance.dark() else 0.75,
        blurRadius=60,
        stayTop=False,
        showDark=False,
        showClose=True,
        showMinimize=True,
        showMaximize=True,
        showStayTop=False,
        autoMaximize=False,
        autoVisible=True,
        autoCenter=True,
        autoDestroy=True,
        useSystemAppBar=LingmoApp.useSystemAppBar,
        margins=0,
        width=640,
        height=480,
    ):
        super().__init__(parent, show=False)
        self.resize(width, height)
        self.loadWidget = LingmoFrame(show=False)
        self.loadWidget.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip
        )
        self.loadWidget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.loadBackground = LingmoFrame(self.loadWidget)
        self.loadBackground.addStyleSheet("background-color", "#44000000")
        self.loadRing = LingmoProgressRing(self.loadBackground)
        self.loadText = LingmoText(self.loadBackground, text=self.tr("Loading..."))
        self.loadWidget.show()
        self.isLazyInit = True
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.launchMode = launchMode
        self.argument = argument
        self.fitsAppBarWindows = fitsAppBarWindows
        self.tintOpacity = tintOpacity
        self.blurRadius = blurRadius
        self.windowIconPath = windowIcon
        self.setWindowTitle(title)
        self.setMouseTracking(True)
        self.stayTop = stayTop
        self.background = LingmoFrame(self)
        self.appbar = LingmoAppBar(
            self.background, title=self.windowTitle(), icon=self.windowIcon()
        )
        self.frameless = LingmoFrameless(
            self,
            self.appbar,
            self.appbar.btnMaximize,
            self.appbar.btnMinimize,
            self.appbar.btnClose,
            disabled=useSystemAppBar,
            fixSize=fixSize,
            show=autoVisible,
            useSystemEffect=not LingmoTheme.instance.blurBehindWindowEnabled,
        )
        self.imgBack = LingmoLabel(self.background, show=False)
        self.ancrylic = LingmoAcrylic(
            self.background,
            target=self.imgBack,
            tintOpacity=self.tintOpacity,
            blurRadius=self.blurRadius,
            tintColor=(
                QColor(0, 0, 0, 255)
                if LingmoTheme.instance.dark()
                else QColor(255, 255, 255, 255)
            ),
            targetRect=QRect(
                self.x() - self.screen().virtualGeometry().x(),
                self.y() - self.screen().virtualGeometry().y(),
                self.width(),
                self.height(),
            ),
            show=False,
        )
        self.contentItem = LingmoFrame(self.background)
        LingmoTheme.instance.desktopImagePathChanged.connect(
            self.onDesktopImagePathChanged
        )
        LingmoTheme.instance.blurBehindWindowEnabledChanged.connect(
            self.onBlurBehindWindowEnabledChanged
        )
        self.moved.connect(self.frameless.onMouseMove)
        self.pressed.connect(self.frameless.onMousePress)
        self.released.connect(self.frameless.onMouseRelease)
        self.setStayTop(stayTop)
        self.margins = margins
        self.resizeBorderWidth = 1
        self.resizeBorderColor = QColor()
        self.backgroundColor = QColor()
        self.hideShadow = False
        self.useSystemAppbar = useSystemAppBar
        if autoVisible:
            if autoMaximize:
                self.showMaximized()
            else:
                self.show()
        if autoCenter:
            self.moveWindowToDesktopCenter()
        self.setWindowIcon(QPixmap(self.windowIconPath))
        self.setShowDark(showDark)
        self.setShowStayTop(showStayTop)
        self.setShowMinimize(showMinimize)
        self.setShowMaximize(showMaximize)
        self.setShowClose(showClose)
        self.autoDestroy = autoDestroy
        self.timerUpdateImage = QTimer()
        self.timerUpdateImage.timeout.connect(self.onTimerTimeout)
        self.timerUpdateImage.start(150)
        self.infoBar = LingmoInfoBar(self.contentItem)
        self.loadWidgetOpacity = 1
        self.loadWidgetOpacityAnimation = QSequentialAnimationGroup()
        self.loadWidgetOpacityAnimation.addPause(83)
        self.loadWidgetOpacityAnimation1 = LingmoAnimation(self, "loadWidgetOpacity")
        self.loadWidgetOpacityAnimation1.setDuration(167)
        self.loadWidgetOpacityAnimation.addAnimation(self.loadWidgetOpacityAnimation1)
        self.unloaded = True
        self.cancel = False
        self.loadBackground.pressed.connect(self.cancelLoading)

    def updateEvent(self):
        try:
            self.resizeBorderColor = (
                (
                    QColor(51, 51, 51, 255)
                    if LingmoTheme.instance.dark()
                    else QColor(110, 110, 110, 255)
                )
                if self.isActiveWindow()
                else (
                    QColor(61, 61, 61, 255)
                    if LingmoTheme.instance.dark()
                    else QColor(167, 167, 167, 255)
                )
            )
            if self.frameless.effective and self.isActiveWindow():
                if self.frameless.effect == "dwm-blur":
                    self.backgroundColor = LingmoTools.withOpacity(
                        LingmoTheme.instance.windowActiveBackgroundColor
                    )
                else:
                    self.backgroundColor = "transparent"
            elif self.isActiveWindow():
                self.backgroundColor = LingmoTheme.instance.windowActiveBackgroundColor
            else:
                self.backgroundColor = LingmoTheme.instance.windowBackgroundColor
            self.background.addStyleSheet("background-color", self.backgroundColor)
            self.background.addStyleSheet(
                "border-radius",
                (
                    0
                    if self.isMaximized() or self.isFullScreen()
                    else LingmoTheme.instance._roundWindowRadius
                ),
            )
            self.background.resize(self.size())
            self.appbar.resize(
                self.width(),
                30 if not (self.useSystemAppbar or self.fitsAppBarWindows) else 0,
            )
            self.contentItem.setGeometry(
                self.resizeBorderWidth,
                self.appbar.height(),
                self.background.width() - 2 * self.resizeBorderWidth,
                self.background.height()
                - self.appbar.height()
                - 2 * self.resizeBorderWidth,
            )
            self.background.addStyleSheet("border-style", "solid")
            self.background.addStyleSheet("border-color", self.resizeBorderColor)
            self.background.addStyleSheet("border-width", self.resizeBorderWidth)
            self.appbar.resize(self.background.width(), self.appbar.height())
            self.imgBack.resize(LingmoTools.desktopAvailableGeometry(self).size())
            self.loadWidget.setGeometry(self.geometry())
            self.loadBackground.resize(self.loadWidget.size())
            self.loadWidget.show()
            self.ancrylic.resize(self.size())
            self.ancrylic.addStyleSheet(
                "border-radius",
                (
                    0
                    if self.isMaximized() or self.isFullScreen()
                    else LingmoTheme.instance._roundWindowRadius
                ),
            )
            if self.unloaded:
                self.unloaded = False
                self.setLoadWidgetOpacity(0)
            self.loadWidget.setWindowOpacity(self.loadWidgetOpacity)
            self.loadRing.move(
                self.background.width() / 2 - self.loadRing.width() / 2,
                self.height() / 2
                - (self.loadRing.height() + 8 + self.loadText.height()) / 2,
            )
            self.loadText.move(
                self.background.width() / 2 - self.loadText.width() / 2,
                self.loadRing.y() + self.loadRing.height() + 8,
            )
        except:
            pass

    def setStayTop(self, val):
        self.stayTop = val
        self.frameless.setWindowTopMost(val)

    def setWindowIconPath(self, val):
        self.windowIconPath = val
        self.setWindowIcon(QIcon(val))

    def setShowDark(self, val):
        return self.appbar.setShowDark(val)

    def setShowStayTop(self, val):
        return self.appbar.setShowStayTop(val)

    def setShowMinimize(self, val):
        return self.appbar.setShowMinimize(val)

    def setShowMaximize(self, val):
        return self.appbar.setShowMaximize(val)

    def setShowClose(self, val):
        return self.appbar.setShowClose(val)

    def moveWindowToDesktopCenter(self):
        availableGeometry = LingmoTools.desktopAvailableGeometry(self)
        self.move(
            availableGeometry.width() / 2 - self.width() / 2,
            availableGeometry.height() / 2 - self.height() / 2,
        )

    def showEvent(self, event):
        if self.isVisible and self.isLazyInit:
            self.lazyLoad.emit()
            self.isLazyInit = False
        return super().showEvent(event)

    def closeEvent(self, event):
        self.closeListener()

    def closeListener(self):
        if self.autoDestroy:
            self.loadWidget.destroy()
            self.loadWidget.deleteLater()
            self.destroy()
            self.deleteLater()
        else:
            self.hide()

    def fixWindowSize(self):
        if self.frameless.fixSize:
            self.setMaximumSize(self.size())
            self.setMinimumSize(self.size())

    def setHitTestVisible(self, val):
        self.frameless.setHitTestVisible(val)

    def onTimerTimeout(self):
        self.imgBack.setPixmap(QPixmap(LingmoTheme.instance._desktopImagePath))

    def onDesktopImagePathChanged(self):
        self.timerUpdateImage.stop()
        self.timerUpdateImage.start()

    def onBlurBehindWindowEnabledChanged(self):
        if LingmoTheme.instance.blurBehindWindowEnabled:
            self.imgBack.setPixmap(QPixmap(LingmoTheme.instance._desktopImagePath))
        else:
            self.imgBack.setPixmap(QPixmap())

    def showSuccess(self, text, duration=1000, moremsg=""):
        return self.infoBar.showSuccess(text, duration, moremsg)

    def showInfo(self, text, duration=1000, moremsg=""):
        return self.infoBar.showInfo(text, duration, moremsg)

    def showWarning(self, text, duration=1000, moremsg=""):
        return self.infoBar.showWarning(text, duration, moremsg)

    def showError(self, text, duration=1000, moremsg=""):
        return self.infoBar.showError(text, duration, moremsg)

    def clearAllInfo(self):
        return self.infoBar.clearAllInfo()

    def setLoadWidgetOpacity(self, val):
        self.loadWidgetOpacityAnimation1.setStartValue(self.loadWidgetOpacity)
        self.loadWidgetOpacityAnimation1.setEndValue(val)
        self.loadWidgetOpacityAnimation.start()

    def showLoading(self, text="", cancel=True):
        if text == "":
            text = self.tr("Loading...")
        self.cancel = cancel
        self.setLoadWidgetOpacity(1)

    def hideLoading(self):
        self.setLoadWidgetOpacity(0)

    def cancelLoading(self):
        if self.cancel:
            self.hideLoading()


class LingmoBusyIndicator(LingmoFrame):
    def __init__(
        self,
        running=True
    ):
        self.running=running
        self.ring=LingmoProgressRing()
    
    def updateEvent(self):
        self.ring.setStrokeWidth(
            3 if self.ring.width() > 40 else 4
        )
        self.ring.setVisible(self.running)
        self.ring.resize(
            max(self.width(),self.height()),
            max(self.width(),self.height())
        )
        self.ring.move(
            self.width() / 2 - self.ring.width() / 2,
            self.height() / 2 - self.ring.width() / 2
        )


class LingmoCheckDelegate(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoCheckIndicator(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoComboBox(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoDial(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoDialog(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoDialogButtonBox(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoDrawer(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoGroupBox(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoHorizontalHeaderView(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoItemDelegate(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoMenuBar(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoMenuBarItem(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoMenuSeparator(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoPage(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoPageIndicator(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoPane(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoProgressBar(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoRadioButton(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoRadioDelegate(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoRadioIndicator(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoRangeSlider(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoRoundButton(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoScrollIndicator(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoScrollView(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoSelectionRectangle(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoSpinBox(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoSplitView(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoStackView(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoSwipeDelegate(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoSwitch(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoSwitchDelegate(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoSwitchIndicator(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoTabBar(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoTabButton(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoTextArea(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoTextField(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoToolBar(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoToolButton(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoToolSeparator(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class Tumbler(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass


class LingmoVerticalHeaderView(LingmoFrame):
    def __init__(
        self
    ):
        pass
    
    def updateEvent(self):
        pass