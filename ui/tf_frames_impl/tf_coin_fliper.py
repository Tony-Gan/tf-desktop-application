import random
import os
import sys
import pygame
from PyQt6.QtGui import QPainter, QImage, QResizeEvent, QMouseEvent
from PyQt6.QtCore import QTimer
from ui.tf_draggable_window import TFDraggableWindow

@DeprecationWarning
class TFCoinFliper(TFDraggableWindow):
    def __init__(self, parent=None, size=(600, 400), title="Default Game", max_count=1, message_bar=None):
        super().__init__(parent, size=size, title=title, max_count=max_count, message_bar=message_bar)
        self.initPygame()
        self.initTimer()
        self.flip_flag = False

    def initPygame(self):
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.init()
        pygame.display.init()
        pygame.display.set_mode((1, 1)) 

        self.surface = pygame.Surface((self.width(), self.height()), pygame.SRCALPHA)

        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            image1_path = os.path.join(script_dir, '../../static', 'images', 'coin_1.png')
            image2_path = os.path.join(script_dir, '../../static', 'images', 'coin_2.png')

            image1 = pygame.image.load(image1_path).convert_alpha()
            image2 = pygame.image.load(image2_path).convert_alpha()
            self.coin_images = [image1, image2]
        except pygame.error as e:
            print("Pygame error while loading images:", e)
            sys.exit()
        self.current_image = self.coin_images[0]

    def initTimer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updatePygame)
        self.timer.start(30)

    def updatePygame(self):
        if self.flip_flag:
            self.current_image = random.choice(self.coin_images)
            self.flip_flag = False
        self.surface.fill((255, 255, 255, 0)) 
        rect = self.current_image.get_rect()
        rect.center = (self.width() // 2, self.height() // 2)
        self.surface.blit(self.current_image, rect)
        self.update()

    def paintEvent(self, event):
        data = pygame.image.tostring(self.surface, 'RGBA')
        image = QImage(data, self.surface.get_width(), self.surface.get_height(), QImage.Format.Format_RGBA8888)
        painter = QPainter(self)
        painter.drawImage(0, 0, image)

    def resizeEvent(self, event: QResizeEvent):
        self.surface = pygame.Surface((self.width(), self.height()), pygame.SRCALPHA)
        super().resizeEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        self.flip_flag = True
        super().mousePressEvent(event)
