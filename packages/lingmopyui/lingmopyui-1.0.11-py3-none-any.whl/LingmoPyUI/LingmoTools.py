from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtDBus import *

import base64
import ctypes
from ctypes import wintypes
import sys

from . import LingmoTheme

user32 = ctypes.WinDLL("user32", use_last_error=True)
SPI_GETDESKWALLPAPER = 0x73

prime = 0x100000001B3
basis = 0xCBF29CE484222325


def hash_(str):
    ret = basis
    for i in str:
        ret ^= ord(i)
        ret *= prime
    return ret


def hash_compile_time(s, last_value=basis):
    return (
        hash_compile_time(s[1:], (s[0] ^ last_value) * prime) if s != "" else last_value
    )


def darkLightToggle(dark: QColor, light: QColor):
    if LingmoTheme.instance.dark():
        return dark
    else:
        return light


def clipText(text):
    QApplication.clipboard().setText(text)


def uuid():
    return "".join(QUuid.createUuid().toString().split("-")).strip("{").strip("}")


def readFile(fileName):
    content = ""
    file = QFile(fileName)
    if file.open(QIODevice.OpenModeFlag.ReadOnly):
        stream = QTextStream(file)
        content = stream.readAll()
    return content


def isMacos():
    return sys.platform == "darwin"


def isLinux():
    return sys.platform == "linux"


def isWin():
    return sys.platform == "win32"


def qtMajor():
    return int(qVersion().split(".")[0])


def qtMinor():
    return int(qVersion().split(".")[1])


def setQuitOnLastWindowClosed(val):
    QApplication.setQuitOnLastWindowClosed(val)


def setOverrideCursor(shape):
    QApplication.setOverrideCursor(shape)


def restoreOverrideCursor():
    QApplication.restoreOverrideCursor()


def deleteLater(p: QObject):
    if p:
        p.deleteLater()


def toLocalPath(url: QUrl):
    return url.toLocalFile()


def getFileNameByUrl(url: QUrl):
    return QFileInfo(url.toLocalFile()).fileName()


def html2PlantText(html):
    textDocument = QTextDocument()
    textDocument.setHtml(html)
    return textDocument.toPlainText()


def getVirtualGeometry():
    return QApplication.primaryScreen().virtualGeometry()


def getApplicationDirPath():
    return QApplication.applicationDirPath()


def getUrlByFilePath(path):
    return QUrl.fromLocalFile(path)


def withOpacity(color: QColor, opacity):
    alpha = round(opacity * 255) & 0xFF
    return QColor.fromRgba((alpha << 24) | (color.rgba() & 0xFFFFFF))


def md5(text: str):
    return QCryptographicHash.hash(
        text.encode("utf-8"), QCryptographicHash.Algorithm.Md5
    ).toHex()


def toBase64(text: str):
    return base64.b64encode(text.encode("utf-8"))


def fromBase64(text: str):
    return base64.b64decode(text.encode("utf-8"))


def removeDir(dirPath):
    dir = QDir(dirPath)
    dir.removeRecursively()


def removeFile(filePath):
    file = QFile(filePath)
    file.remove()


def sha256(text: str):
    return QCryptographicHash.hash(
        text.encode("utf-8"), QCryptographicHash.Algorithm.Sha256
    ).toHex()


def showFileInFolder(path: str):
    if isWin():
        QProcess.startDetached(
            "explorer.exe", ["/select", QDir.toNativeSeparators(path)]
        )
    elif isLinux():
        fileInfo = QFileInfo(path)
        process = "xdg-open"
        arguments = [fileInfo.absoluteDir().absolutePath()]
        QProcess.startDetached(process, arguments)
    elif isMacos:
        QProcess.execute(
            "/usr/bin/osascript",
            ["-e", 'tell application "Finder" to reveal POSIX file "' + path + '"'],
        )
        QProcess.execute(
            "/usr/bin/osascript", ["-e", 'tell application "Finder" to activate']
        )


def isSoftWare():
    return True


def cursorPos():
    return QCursor.pos()


def currentTimestamp():
    return QDateTime.currentMSecsSinceEpoch()


def windowIcon():
    return QApplication.windowIcon()


def cursorScreenIndex():
    screenIndex = 0
    for i in range(QApplication.screens().count()):
        if QApplication.screens()[i].geometry().contains(QCursor.pos()):
            screenIndex = i
            break
    return screenIndex


def windowBuildNumber():
    if isWin():
        regKey = QSettings(
            R"(HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion)",
            QSettings.Format.NativeFormat,
        )
        if regKey.contains("CurrentBuildNumber"):
            buildNumber = int(regKey.value("CurrentBuildNumber"))
            return buildNumber
    return -1


isWindows11OrGreaterVar = None


def isWindows11OrGreater():
    if isWindows11OrGreaterVar == None:
        if isWin():
            buildNumber = windowBuildNumber()
            if buildNumber >= 22000:
                isWindows11OrGreaterVar = True
                return True
        isWindows11OrGreaterVar = False
        return False
    else:
        return False


isWindows10OrGreaterVar = None


def isWindows10OrGreater():
    if isWindows10OrGreaterVar == None:
        if isWin():
            buildNumber = windowBuildNumber()
            if buildNumber >= 10240:
                isWindows10OrGreaterVar = True
                return True
        isWindows10OrGreaterVar = False
        return False
    else:
        return False


def desktopAvailableGeometry(window: QWidget):
    return window.screen().availableGeometry()


def getWallpaperFilePath():
    if isWin():
        path = []
        if (
            user32.SystemParametersInfoW(
                SPI_GETDESKWALLPAPER, wintypes.MAX_PATH, path, False
            )
            == False
        ):
            return []
        return path
    elif isLinux():
        typeSys = QSysInfo.productType()
        if hash_(typeSys) == hash_compile_time("uos"):
            interface = QDBusInterface(
                "com.deepin.wm",
                "/com/deepin/wm",
                "com.deepin.wm",
                QDBusConnection.sessionBus(),
            )
            if not interface.isValid():
                qWarning(QDBusConnection.sessionBus().lastError().message())
                return ""
            reply = interface.call(
                "GetCurrentWorkspaceBackgroundForMonitor",
                "string:'" + currentTimestamp() + "'",
            )
            if reply.isValid():
                qWarning(reply.error().message())
                return ""
            result = reply.value().trimmed()
            startIndex = result.indexOf("file:///")
            if startIndex != -1:
                path = result.mid(startIndex + 7, result.length() - startIndex - 8)
                return path
        elif hash_(typeSys) == hash_compile_time("lingmo"):
            interface = QDBusInterface(
                "com.lingmo.Settings",
                "/Theme",
                "org.freedesktop.DBus.Properties",
                QDBusConnection.sessionBus(),
            )
            if not interface.isValid:
                qWarning(QDBusConnection.sessionBus().lastError().message())
                return ""
            reply = interface.call("Get", "com.lingmo.Theme", "wallpaper")
            if not reply.isValid():
                qWarning("Error getting property:" + reply.error().message())
                return ""
            result = reply.value()
            return result
    elif isMacos():
        process = QProcess()
        process.start(
            "osascript",
            '-e(tell application "Finder" to get POSIX path of (desktop picture as alias))',
        )
        process.waitForFinished()
        result = process.readAllStandardOutput().trimmed()
        if result.isEmpty():
            return "/System/Library/CoreServices/DefaultDesktop.heic"
        return result


def imageMainColor(image: QImage, bright: float):
    step = 20
    t = r = g = b = 0
    for i in range(image.width()):
        for j in range(image.height()):
            if image.valid(i, j):
                t += 1
                c = image.pixelColor(i, j)
                r += c.red()
                g += c.green()
                b += c.blue()
    return QColor(
        min(int(bright * r / t), 255),
        min(int(bright * g / t), 255),
        min(int(bright * b / t), 255),
    )
