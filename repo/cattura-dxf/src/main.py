import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QFileDialog, QVBoxLayout, QWidget, QInputDialog, QMessageBox
from PyQt5.QtGui import QPixmap, QPainter, QPen, QImage
from PyQt5.QtCore import Qt, QPoint
from PIL import Image
import ezdxf
import cv2
import numpy as np

class ImageScaler(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Cattura DXF')
        self.image_label = QLabel('Carica un\'immagine', self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.pixmap = None
        self.points = []
        self.scale = None
        self.init_ui()

    def init_ui(self):
        load_btn = QPushButton('Carica Immagine')
        load_btn.clicked.connect(self.load_image)
        paste_btn = QPushButton('Incolla da Appunti (Ctrl+V)')
        paste_btn.clicked.connect(self.paste_image)
        scale_btn = QPushButton('Imposta Scala (misurino)')
        scale_btn.clicked.connect(self.set_scale)
        export_btn = QPushButton('Esporta DXF')
        export_btn.clicked.connect(self.export_dxf)
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(load_btn)
        layout.addWidget(paste_btn)
        layout.addWidget(scale_btn)
        layout.addWidget(export_btn)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Apri Immagine', '', 'Immagini (*.png *.jpg *.bmp)')
        if file_name:
            self.pixmap = QPixmap(file_name)
            self.image_label.setPixmap(self.pixmap)
            self.points = []
            self.scale = None

    def paste_image(self):
        clipboard = QApplication.clipboard()
        mime = clipboard.mimeData()
        if mime.hasImage():
            img = clipboard.image()
            if isinstance(img, QImage):
                self.pixmap = QPixmap.fromImage(img)
                self.image_label.setPixmap(self.pixmap)
                self.points = []
                self.scale = None
        else:
            QMessageBox.warning(self, 'Attenzione', 'Nessuna immagine negli appunti!')

    def mousePressEvent(self, event):
        if self.pixmap and len(self.points) < 2:
            # Calcola la posizione del click relativa all'immagine visualizzata
            label_rect = self.image_label.geometry()
            pixmap = self.image_label.pixmap()
            if pixmap is None:
                return
            pm_w, pm_h = pixmap.width(), pixmap.height()
            lbl_w, lbl_h = self.image_label.width(), self.image_label.height()
            # Centra l'immagine nella QLabel
            x_offset = (lbl_w - pm_w) // 2 if lbl_w > pm_w else 0
            y_offset = (lbl_h - pm_h) // 2 if lbl_h > pm_h else 0
            click_x = event.x() - self.image_label.x() - x_offset
            click_y = event.y() - self.image_label.y() - y_offset
            if 0 <= click_x < pm_w and 0 <= click_y < pm_h:
                self.points.append(QPoint(click_x, click_y))
                self.update_image_with_points()

    def update_image_with_points(self):
        if self.pixmap:
            temp_pixmap = self.pixmap.copy()
            painter = QPainter(temp_pixmap)
            pen = QPen(Qt.red, 5)
            painter.setPen(pen)
            for pt in self.points:
                painter.drawPoint(pt)
            painter.end()
            self.image_label.setPixmap(temp_pixmap)

    def set_scale(self):
        if len(self.points) == 2:
            dist = ((self.points[0].x() - self.points[1].x()) ** 2 + (self.points[0].y() - self.points[1].y()) ** 2) ** 0.5
            real_dist, ok = QInputDialog.getDouble(self, 'Imposta quota reale', 'Distanza reale:', min=0.01)
            if ok and dist > 0:
                self.scale = real_dist / dist

    def export_dxf(self):
        if self.pixmap and self.scale:
            file_name, _ = QFileDialog.getSaveFileName(self, 'Salva DXF', '', 'DXF Files (*.dxf)')
            if file_name:
                doc = ezdxf.new()
                msp = doc.modelspace()
                # Esporta la linea di misura
                if len(self.points) == 2:
                    p1 = self.points[0]
                    p2 = self.points[1]
                    msp.add_line((p1.x() * self.scale, p1.y() * self.scale), (p2.x() * self.scale, p2.y() * self.scale))
                # Vettorializzazione automatica
                # Estrai l'immagine da QPixmap
                image = self.pixmap.toImage()
                width = image.width()
                height = image.height()
                ptr = image.bits()
                ptr.setsize(image.byteCount())
                arr = np.array(ptr).reshape(height, width, 4)
                gray = cv2.cvtColor(arr, cv2.COLOR_BGRA2GRAY)
                _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
                # Rilevamento bordi con Canny
                edges = cv2.Canny(gray, 50, 150, apertureSize=3)
                # Trova linee con HoughLinesP
                lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=80, minLineLength=30, maxLineGap=10)
                if lines is not None:
                    for line in lines:
                        x1, y1, x2, y2 = line[0]
                        y1f = height - y1
                        y2f = height - y2
                        msp.add_line((x1 * self.scale, y1f * self.scale), (x2 * self.scale, y2f * self.scale))
                # Esporta la linea di misura con asse Y corretto
                if len(self.points) == 2:
                    p1 = self.points[0]
                    p2 = self.points[1]
                    y1f = height - p1.y()
                    y2f = height - p2.y()
                    msp.add_line((p1.x() * self.scale, y1f * self.scale), (p2.x() * self.scale, y2f * self.scale))
                doc.saveas(file_name)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageScaler()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())
