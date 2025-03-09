'''
Python script that defines the 3-way toggle switch to toggle between defalut video, another media, and default image.
'''
from PySide6.QtCore import (
    Qt, QSize, QPoint, QPointF, QRectF, Signal,
    QEasingCurve, QPropertyAnimation, QSequentialAnimationGroup,
    Slot, Property)

from PySide6.QtWidgets import QCheckBox, QWidget, QLabel, QHBoxLayout
from PySide6.QtGui import QColor, QBrush, QPaintEvent, QPen, QPainter

class AnimatedToggle(QCheckBox):

    # Signal to emit whenever the position changes
    positionChanged = Signal(float)

    _transparent_pen = QPen(Qt.transparent)
    _light_grey_pen = QPen(Qt.lightGray)

    def __init__(self, parent = None, bar_color = Qt.gray,
        checked_color = "#00B0FF", handle_color = Qt.white,
        pulse_unchecked_color = "#44999999", pulse_checked_color = "#4400B0EE"):
        super().__init__(parent)

        # Save our properties on the object via self, so we can access them later
        # in the paintEvent.
        self._bar_brush = QBrush(bar_color)
        self._bar_checked_brush = QBrush(QColor(checked_color).lighter())

        self._handle_brush = QBrush(handle_color)
        self._handle_checked_brush = QBrush(QColor(checked_color))

        self._pulse_unchecked_animation = QBrush(QColor(pulse_unchecked_color))
        self._pulse_checked_animation = QBrush(QColor(pulse_checked_color))

        # Setup the rest of the widget.
        self.setContentsMargins(8, 0, 8, 0)
        self._handle_position = 0

        self._pulse_radius = 0

        self.animation = QPropertyAnimation(self, b"handle_position", self)
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)
        self.animation.setDuration(200)  # time in ms

        self.pulse_anim = QPropertyAnimation(self, b"pulse_radius", self)
        self.pulse_anim.setDuration(350)  # time in ms
        self.pulse_anim.setStartValue(10)
        self.pulse_anim.setEndValue(20)

        self.animations_group = QSequentialAnimationGroup()
        self.animations_group.addAnimation(self.animation)
        self.animations_group.addAnimation(self.pulse_anim)

        self.stateChanged.connect(self.setup_animation)

    def sizeHint(self):
        # Increase the width-to-height ratio here
        return QSize(100, 35)  # Adjusted for wider slider

    def hitButton(self, pos: QPoint):
        return self.contentsRect().contains(pos)

    @Slot(int)
    def setup_animation(self, value):
        self.animations_group.stop()
        if value:
            self.animation.setEndValue(1)
        else:
            self.animation.setEndValue(0)
        self.animations_group.start()

    def mousePressEvent(self, event):
        # Calculate positions based on clicks
        contRect = self.contentsRect()
        pos = event.pos().x()

        # Three positions: 0 (left), 0.5 (middle), 1 (right)
        if self._handle_position == 0 and pos > contRect.width() / 2:
            # Move to middle from left
            self.setPosition(0.5)
        elif self._handle_position == 1 and pos < contRect.width() / 2:
            # Move to middle from right
            self.setPosition(0.5)
        elif pos < contRect.width() / 3:
            # Only move to left if not already in the left position
            if self._handle_position != 0:
                self.setPosition(0)
        elif pos > 2 * contRect.width() / 3:
            # Only move to right if not already in the right position
            if self._handle_position != 1:
                self.setPosition(1)
        else:
            # Only move to middle if not already in the middle position
            if self._handle_position != 0.5:
                self.setPosition(0.5)

    def paintEvent(self, e: QPaintEvent):

        contRect = self.contentsRect()
        handleRadius = round(0.24 * contRect.height())

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        p.setPen(self._transparent_pen)
        barRect = QRectF(
            0, 0,
            contRect.width() - handleRadius, 0.40 * contRect.height()
        )
        barRect.moveCenter(contRect.center())
        rounding = barRect.height() / 2

        # the handle will move along this line
        trailLength = contRect.width() - 2 * handleRadius

        xPos = contRect.x() + handleRadius + trailLength * self._handle_position

        if self.pulse_anim.state() == QPropertyAnimation.Running:
            p.setBrush(
                self._pulse_checked_animation if
                self.isChecked() else self._pulse_unchecked_animation)
            p.drawEllipse(QPointF(xPos, barRect.center().y()),
                          self._pulse_radius, self._pulse_radius)

        if self.isChecked():
            p.setBrush(self._bar_checked_brush)
            p.drawRoundedRect(barRect, rounding, rounding)
            p.setBrush(self._handle_checked_brush)

        else:
            p.setBrush(self._bar_brush)
            p.drawRoundedRect(barRect, rounding, rounding)
            p.setPen(self._light_grey_pen)
            p.setBrush(self._handle_brush)

        p.drawEllipse(
            QPointF(xPos, barRect.center().y()),
            handleRadius, handleRadius)

        p.end()

    @Property(float)
    def handle_position(self):
        return self._handle_position

    @handle_position.setter
    def handle_position(self, pos):
        """change the property
        we need to trigger QWidget.update() method, either by:
            1- calling it here [ what we're doing ].
            2- connecting the QPropertyAnimation.valueChanged() signal to it.
        """
        self._handle_position = pos
        self.update()

    @Property(float)
    def pulse_radius(self):
        return self._pulse_radius

    @pulse_radius.setter
    def pulse_radius(self, pos):
        self._pulse_radius = pos
        self.update()

    def setPosition(self, position):
        """Set the slider's position manually from outside the class."""
        if position not in [0, 0.5, 1]:
            raise ValueError("Position must be 0, 0.5, or 1.")
        
        # Only process the change if the position is different
        if self._handle_position != position:
            self.animations_group.stop()
            self.animation.setEndValue(position)
            self.animations_group.start()

            self.positionChanged.emit(position)  # Emit the position changed signal
            
class ToggleSwitchWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create layout
        layout = QHBoxLayout(self)

        # Create "Default Video" label
        self.default_video_label = QLabel("Default Video")
        layout.addWidget(self.default_video_label)

        # Create AnimatedToggle slider
        self.toggle_slider = AnimatedToggle()
        layout.addWidget(self.toggle_slider)

        # Create "Default Image" label
        self.default_image_label = QLabel("Default Image")
        layout.addWidget(self.default_image_label)