# Необходимо разработать Standalone приложение на Python с использованием PySIde или PyQT.
# Приложение обладает следующим функционалом: 
# Resizable окно, в котором расположена кнопка Add
# При нажатии на кнопку появляетсяпоп-ап, в который можно перетащить одну или несколько картинок drag-n-drop’ом 
# Пользователь перетаскивает картинку / картинки  и нажимает кнопку ОК 
# После этого в окне появляется Grid View с картинкаим, каждую из которых можно открыть нажатием нее в отдельном окне на просмотр.  
# При ресайзе окна grid view должен отрабатывать корректно


import sys
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QGridLayout, QLabel, \
                            QPushButton, QWidget, QScrollArea, QMainWindow, QVBoxLayout


# default class for application's windows
# scrolling added
 
class ScrollableAppWin(QMainWindow):
    def __init__(self):    
        super().__init__()
        self.resize(1200, 700)
        self.move(15,15)
        self.setAcceptDrops(True)
        self.mainLayout = QGridLayout()
        self.mainLayout.horizontalSpacing = 3
        self.mainLayout.verticalSpacing = 3 
        self.widget = QWidget()  #  just for scrolling
        self.widget.setLayout(self.mainLayout)       
        self.widget.setStyleSheet("background-color: gray;")
        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)
        self.setCentralWidget(self.scroll)


# The first resizable window with "Add" button
# which launches the second window

class StartWindow(QWidget):
    
    def __init__(self):
        super().__init__()
        self.initializeUI()

    def initializeUI(self):  
        self.resize(200, 100)
        self.setWindowTitle('Image Collector')
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        self.drag_win = ImgWindow()
        button = QPushButton("Add", self)
        layout.addWidget(button, alignment=Qt.AlignCenter)
        button.clicked.connect(self.the_button_was_clicked)
        self.move(10,10)
        self.show()
    
    def the_button_was_clicked(self):
        self.drag_win.show()
 

# The second window with "OK" button and drag-n-drop features
# Pressing "OK" launnches the 3rd window

class ImgWindow(ScrollableAppWin):

    col_counter = 0
    row_counter = 1
    file_list = []
    
    def __init__(self):
        super().__init__()        
        button = QPushButton("OK", self)
        self.popwin = GridWindow()
        button.clicked.connect(self.the_button_was_clicked)
        scr_width = QDesktopWidget().availableGeometry().width()
        self.scale_to = int(scr_width/9)
        button.move(int((self.scale_to-button.width())/2), int(self.scale_to/2)-30)
    
    def the_button_was_clicked(self):
        self.popwin.setfilelist(self.file_list)
        self.popwin.show()

    def dragEnterEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasImage:
            event.setDropAction(Qt.CopyAction)
            for f in range(len(event.mimeData().urls())):
                file_path = event.mimeData().urls()[f].toLocalFile()
                self.file_list.append(file_path)
                self.set_image(file_path,self.col_counter,self.row_counter)              
                self.show()
                self.row_counter +=1
                if self.row_counter == 5:
                    self.row_counter = 0
                    self.col_counter += 1               
            event.accept()
        else:
            event.ignore()

    def set_image(self, file_path,c,r):      
        self.photoViewer = QLabel()
        self.mainLayout.addWidget(self.photoViewer,c,r)
        self.pixmap = QPixmap(file_path)
        self.photoViewer.setPixmap(self.pixmap.scaled(self.scale_to,self.scale_to,Qt.KeepAspectRatio))    

# The 3rd window containing grid view of previously selected images
# When clicking on image, the pop-up with a larger view of an image appears

class GridWindow(ScrollableAppWin):

    file_list = []
    
    def __init__(self):
        super().__init__()

    def setfilelist(self, filelist):
        self.file_list = filelist[:]
        scr_width = QDesktopWidget().availableGeometry().width()
        self.scale_to = int(scr_width/9)
        self.pic_dict = {}                                      
        c = 0
        r = 0       
        for f in self.file_list:
            self.pic = QLabel()            # current Qlable description
            self.pic.installEventFilter(self)                   
            self.mainLayout.addWidget(self.pic, r, c)
            pixmap = QPixmap(f)
            self.pic.setPixmap(pixmap.scaled(self.scale_to,self.scale_to,Qt.KeepAspectRatio))
            f_key = str(self.pic)                               
            self.pic_dict[f_key] = f       # QLable info and path are saved as key:value pair in a dict                    
            if c == 4:
                c = 0
                r += 1
            else:
                c += 1
 
    def eventFilter(self, object, event):                       
        if (event.type() == QEvent.MouseButtonPress):
            #getting path of an image which was loaded into this QLable using the dict:
            path = self.pic_dict[str(object)] 
            print(path)
            self.vw = ViewWindow()
            self.vw.displayLabels(path)
        return False          


# The last window - pop-up with one image

class ViewWindow(QWidget):

    def __init__(self):
        super().__init__()  
        self.setWindowTitle('Image View')

    def openImage(self, image):
        try:
            with open(image):
                w_image = QLabel(self)
                pixmap = QPixmap(image)
                system_width = QDesktopWidget().availableGeometry().width()
                system_height = QDesktopWidget().availableGeometry().height()
                if system_width<pixmap.width():
                    pixmap = pixmap.scaledToWidth(system_width)
                if system_height<pixmap.height():
                    pixmap = pixmap.scaledToWidth(system_height)
                w_image.setPixmap(pixmap)
                self.resize(pixmap.width(), pixmap.height())
        except FileNotFoundError:
            print("Image not found.")

    def displayLabels(self, image):
        self.openImage(image)
        self.show()


if __name__ == '__main__':
    app = QApplication([])
    window = StartWindow()
    sys.exit(app.exec_())