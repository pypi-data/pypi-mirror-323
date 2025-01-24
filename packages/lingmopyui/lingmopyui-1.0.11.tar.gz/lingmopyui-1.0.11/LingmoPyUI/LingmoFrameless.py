from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from . import LingmoTools
from . import LingmoTheme


class LingmoFrameless(QObject):
    def __init__(
        self,
        parent: QWidget,
        appbar,
        maximizeButton,
        minimizeButton,
        closeButton,
        topmost=False,
        disabled=False,
        fixSize=False,
        effect="normal",
        effective=False,
        availableEffects=[],
        isDarkMode=False,
        useSystemEffect=False,
        show=True,
    ):
        super().__init__(parent)
        self.appbar = appbar
        self.maximizeButton = maximizeButton
        self.minimizeButton = minimizeButton
        self.closeButton = closeButton
        self.topmost = topmost
        if self.topmost:
            self.setWindowTopMost(self.topmost)
        self.disabled = disabled
        self.fixSize = fixSize
        self.effect = effect
        self.effective = effective
        self.availableEffects = availableEffects
        self.isDarkMode = isDarkMode
        self.useSystemEffect = useSystemEffect
        self.hitTestList = []
        self.edges = 0
        self.clickTimer = 0
        self.margins = 8
        self.current = 0
        self.componentComplete()
        if show:
            self.parent().show()

    def componentComplete(self):
        if self.disabled:
            return
        w = self.parent().width()
        h = self.parent().height()
        self.current = self.parent().winId()
        if LingmoTools.isLinux():
            self.parent().setWindowFlags(
                Qt.WindowType.CustomizeWindowHint | Qt.WindowType.FramelessWindowHint
            )
        self.parent().setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.parent().addStyleSheet("border-width", 1)
        self.parent().addStyleSheet("border-style", "solid")
        if self.maximizeButton:
            self.setHitTestVisible(self.maximizeButton)
        if self.minimizeButton:
            self.setHitTestVisible(self.minimizeButton)
        if self.closeButton:
            self.setHitTestVisible(self.closeButton)
        appbarHeight = self.appbar.height()
        h = round(h + appbarHeight)
        if self.fixSize:
            self.parent().setMaximumSize(w, h)
            self.parent().setMinimumSize(w, h)
        else:
            self.parent().setMaximumHeight(self.parent().maximumHeight() + appbarHeight)
            self.parent().setMinimumHeight(self.parent().minimumHeight() + appbarHeight)
        self.parent().resize(w, h)

    def hitAppBar(self):
        for i in self.hitTestList:
            if i.isHovered():
                return False
        return self.appbar.isHovered()

    def hitMaximizeButton(self):
        return self.maximizeButton.isHovered()

    def updateCursor(self, edges):
        if edges == 0:
            self.parent().setCursor(Qt.CursorShape.ArrowCursor)
        elif edges == Qt.Edge.LeftEdge or self.edges == Qt.Edge.RightEdge:
            self.parent().setCursor(Qt.CursorShape.SizeHorCursor)
        elif edges == Qt.Edge.TopEdge or self.edges == Qt.Edge.BottomEdge:
            self.parent().setCursor(Qt.CursorShape.SizeVerCursor)
        elif (edges == Qt.Edge.LeftEdge | Qt.Edge.TopEdge) or (
            edges == Qt.Edge.RightEdge | Qt.Edge.BottomEdge
        ):
            self.parent().setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif (edges == Qt.Edge.RightEdge | Qt.Edge.TopEdge) or (
            edges == Qt.Edge.LeftEdge | Qt.Edge.BottomEdge
        ):
            self.parent().setCursor(Qt.CursorShape.SizeBDiagCursor)

    def setHitTestVisible(self, val):
        if not (val in self.hitTestList):
            self.hitTestList.append(val)

    def setWindowTopMost(self, topmost):
        if self.parent().windowHandle():
            if topmost:
                self.parent().windowHandle().setFlag(
                    Qt.WindowType.WindowStaysOnTopHint, True
                )
            else:
                self.parent().windowHandle().setFlag(
                    Qt.WindowType.WindowStaysOnTopHint, False
                )
            self.parent().windowHandle().setIcon(QPixmap(self.parent().windowIconPath))

    def onMousePress(self):
        if self.edges != 0:
            self.updateCursor(self.edges)
            self.parent().windowHandle().startSystemResize(self.edges)

        else:
            if self.hitAppBar():
                clickTimer = QDateTime.currentMSecsSinceEpoch()
                offset = clickTimer - self.clickTimer
                self.clickTimer = clickTimer
                if offset < 300:
                    self.appbar.maxClickListener()
                else:
                    self.parent().windowHandle().startSystemMove()

    def onMouseRelease(self):
        self.edges = 0

    def onMouseMove(self):
        if not (self.parent().isMaximized() or self.parent().isFullScreen()):
            if not self.fixSize:
                p = self.parent().mapFromGlobal(QCursor.pos())
                if (
                    p.x() >= self.margins
                    and p.x() <= self.parent().width() - self.margins
                    and p.y() >= self.margins
                    and p.y() <= self.parent().height() - self.margins
                ):
                    self.edges = 0
                    self.updateCursor(self.edges)
                else:
                    self.edges = 0
                    if p.x() < self.margins and p.y() < self.margins:
                        self.edges = Qt.Edge.LeftEdge | Qt.Edge.TopEdge
                    elif (
                        p.x() > self.parent().width() - self.margins
                        and p.y() < self.margins
                    ):
                        self.edges = Qt.Edge.RightEdge | Qt.Edge.TopEdge
                    elif (
                        p.x() < self.margins
                        and p.y() > self.parent().height() - self.margins
                    ):
                        self.edges = Qt.Edge.LeftEdge | Qt.Edge.BottomEdge
                    elif (
                        p.x() > self.parent().width() - self.margins
                        and p.y() > self.parent().height() - self.margins
                    ):
                        self.edges = Qt.Edge.RightEdge | Qt.Edge.BottomEdge
                    elif p.x() < self.margins:
                        self.edges = Qt.Edge.LeftEdge
                    elif p.x() > self.parent().width() - self.margins:
                        self.edges = Qt.Edge.RightEdge
                    elif p.y() < self.margins:
                        self.edges = Qt.Edge.TopEdge
                    elif p.y() > self.parent().height() - self.margins:
                        self.edges = Qt.Edge.BottomEdge
                    self.updateCursor(self.edges)

    def setEffective(self, val):
        self.effective = val
        if val:
            LingmoTheme.instance.blurBehindWindowEnabled = False
