#!/usr/bin/env python

#############################################################################
##
## Copyright (C) 2015 Velizar Hristov
## Copyright (C) 2013 Riverbank Computing Limited.
## Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
##
## This program is based on one of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
#############################################################################


from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import (QApplication, QBoxLayout, QSlider,
        QGridLayout, QGroupBox, QLabel, QSpinBox, QStackedWidget,
        QWidget, QPushButton, QPlainTextEdit)

# global variables

# primary screen id (int) or None
primary = None

# list of pairs (screen_name, brightness: 0.0 to 1.0)
screen_data = []

# dict(screen_data) for current brightness
current_state = {}

class SlidersGroup(QGroupBox):

    valueChanged = pyqtSignal(int)

    def __init__(self, commandBox, parent=None):
        super(SlidersGroup, self).__init__("", parent)
        self.slidersLayout = QBoxLayout(QBoxLayout.LeftToRight)
        self.commandBox = commandBox

        self.sliders = []
#        self.spinBoxes = []
        self.labels = []
        if len(screen_data) == 1:
            self.slidersLayout.addStretch()
        for i, (name, value) in enumerate(screen_data):
            self.createBrightnessCtrl(name, value, i)

        if len(screen_data) > 1:
            self.createBrightnessCtrl("All", 100, None)
            self.sliders[-1].valueChanged.connect(self.setAllValues)

        self.setLayout(self.slidersLayout)

        self.refreshCurrentValues()

    def createBrightnessCtrl(self, name, value, i):
        sl = QSlider(Qt.Vertical)
        sl.setFocusPolicy(Qt.StrongFocus)
        sl.setTickPosition(QSlider.TicksBothSides)
        sl.setTickInterval(10)
        sl.setSingleStep(1)
        sl.setMinimum(0)
        sl.setMaximum(100)
        sl.setValue(value)

        sb = QSpinBox()
        sb.setRange(0, 100)
        sb.setSingleStep(10)
        sb.setValue(value)

        sl.valueChanged.connect(sb.setValue)
        sb.valueChanged.connect(sl.setValue)
        if i != None:
            sl.valueChanged.connect(self.setValuePartial(i))
            sb.valueChanged.connect(self.setValuePartial(i))

        boxLayout = QBoxLayout(QBoxLayout.LeftToRight)
        lbl = QLabel(name)
        boxLayout.addWidget(lbl)
        boxLayout.addWidget(sb)

        boxLayout.addWidget(sl)

        self.slidersLayout.addLayout(boxLayout)
        # stretch is between (label, spinner, slider) groups
        if i != None:
            self.slidersLayout.addStretch()

        self.sliders.append(sl)
#        self.spinBoxes.append(sl)
        self.labels.append(lbl)

    def setValue(self, i, value):
        global screen_data
        screen_data[i] = (screen_data[i][0], value)
        self.refreshCommandBox()

    def setValuePartial(self, i):
        s = self.setValue
        return lambda value: s(i, value)

    def setAllValues(self, value):
        for sl in self.sliders:
            sl.setValue(value)

    def refreshCurrentValues(self):
        for i in range(len(screen_data)):
            lbl = self.labels[i]
            name, value = screen_data[i]
            if i == primary and len(screen_data) > 1:
                name += " (primary) "
            lbl.setText(name + " (" + str(value) + ")")
        self.refreshCommandBox()

    def refreshCommandBox(self):
        self.commandBox.document().setPlainText("# apply changes")
        for command in get_apply_commands():
            self.commandBox.appendPlainText(command)

class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        global current_state
        current_state = dict(screen_data)

        self.createControls()
        self.createCommandBox()

        self.brightnessSliders = SlidersGroup(self.commandBox)

        self.stackedWidget = QStackedWidget()
        self.stackedWidget.addWidget(self.brightnessSliders)

        layout = QBoxLayout(QBoxLayout.TopToBottom)
        layout.addWidget(self.stackedWidget)
        layout.addWidget(self.commandBoxGroup)
        layout.addWidget(self.controlsGroup)
        self.setLayout(layout)

        self.setWindowTitle("Brightness editor")
        self.resize(850, 500)

        command = "# get display names and brightness values\n" + \
                  get_brightness_command                 + "\n" + \
                  "# results (formatted): " + str(screen_data)
        if primary != None:
            command += " primary: " + screen_data[primary][0]
        self.commandBox.document().setPlainText(command)

    def createControls(self):
        self.controlsGroup = QGroupBox("")

        applyBtn = QPushButton("Apply")
        applyBtn.clicked.connect(self.applyClicked)

        controlsLayout = QGridLayout()
        controlsLayout.addWidget(applyBtn, 2, 1)
        self.controlsGroup.setLayout(controlsLayout)

    def createCommandBox(self):
        self.commandBoxGroup = QGroupBox("Command info")
        self.commandBoxGroup.setMaximumHeight(105)

        self.commandBox = QPlainTextEdit()
        self.commandBox.setReadOnly(True)
        self.commandBox.setStyleSheet("font-family: monospace; font-size: 13px")

        layout = QGridLayout()
        layout.addWidget(self.commandBox, 2, 1)

        self.commandBoxGroup.setLayout(layout)

    # apply changes
    def applyClicked(self):
        from os import system
        for command in get_apply_commands():
            system(command)

        global current_state
        current_state = dict(screen_data)

        self.brightnessSliders.refreshCurrentValues()

def get_apply_commands():
    commands = []
    for name, value in screen_data:
        if value != current_state[name]:
            dec_value = value / 100.0
            cmd = "xrandr --output " + name + " --brightness " + str(dec_value)
            commands.append(cmd)
    return commands

get_brightness_command = "xrandr -q --verbose " \
                       + "| grep -w 'connected\|Brightness' " \
                       + "| awk '{print $(2-NR%2), $3}'"

def get_screen_data():
    from subprocess import getoutput
    raw_data = getoutput(get_brightness_command).split("\n")
    print("raw_data:", raw_data)

    screen_data = []
    global primary
    for i in range(0, len(raw_data), 2):
        name, second_field = raw_data[i].split(" ")
        if second_field == "primary":
            primary = i
        value = int(float(raw_data[i + 1]) * 100)
        screen_data.append((name, value))
    return screen_data

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    screen_data = get_screen_data()
    window = Window()
    window.show()
    sys.exit(app.exec_())
