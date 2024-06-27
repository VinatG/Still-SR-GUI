import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout, QWidget,QComboBox
from PySide6.QtCore import QUrl, Qt
import onnxruntime as rt
import gc
from scripts.utils import model_path
from scripts.mpw import MediaPlayerWidget

#Dictioary to map the scale to the model name
model_scale_map = {'2x' : 'realworldsr-diffirs2-ganx2-v2', '4x' : 'realworldsr-diffirs2-ganx4-v2'}

class SuperResolutionGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        #Setting up the default model and the default scale. Initialising the 4x model on tthe CPU.
        self.sr_model = 'realworldsr-diffirs2-ganx4-v2'
        self.current_sr_model_scale = '4x'
        providers_list=rt.get_available_providers()
        self.provider=providers_list[-1]
        self.sess = rt.InferenceSession(model_path(model_scale_map['4x']), providers=[ self.provider])
        self.github_link_text='<a href="https://github.com/Zj-BinXia/DiffIR">GitHub Repository</a>'
        self.paper_link_text='<a href="https://arxiv.org/pdf/2303.09472.pdf">Research Paper</a>'
        self.initUI()

    #Initialization of the components of the app's UI
    def initUI(self):
        self.setWindowTitle("Super Resolution GUI")

        # Initialising the 'Select Still button', and the 'Providers dropdown'.
        self.select_still_button = QPushButton("Select Still", self)
        self.select_still_button.clicked.connect(self.select_still)
        self.select_still_button.setMaximumWidth(250)

        self.providers_drop_down = QComboBox(self) #Providers Drop Down: Drop down to select the hardware on which to run the model(CPU/GPU)
        providers_list=rt.get_available_providers()
        self.provider=providers_list[-1]
        for i in reversed(providers_list):
            self.providers_drop_down.addItem(i)

        self.providers_drop_down.currentTextChanged.connect(self.change_providers)
        self.providers_drop_down.setMaximumWidth(250)

        #Creating the media player widget that provides the 3 views along with the buttons to switch the input view and switch between the 4x and 2x models 
        self.media_player_widget = MediaPlayerWidget(self.sess, model_scale_map[self.current_sr_model_scale])
        self.media_player_widget.output_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        #Button on the output side to toggle between the 2x and the 4x model.
        self.media_player_widget.scale_toggle_button.clicked.connect(self.change_model_scale)

        #Qlabels to display the github link and the paper link
        self.github_link = QLabel(self.github_link_text)
        self.github_link.setOpenExternalLinks(True)
        self.paper_link = QLabel(self.paper_link_text)
        self.paper_link.setOpenExternalLinks(True)

        #Status bar
        self.statusBar().showMessage("Still Super-Resolution")       

        #Creating Layouts and combining horizontal elements
        #Buttons layout
        self.buttons = QHBoxLayout()
        self.buttons.addWidget(self.select_still_button)
        self.buttons.addWidget(self.providers_drop_down)
   
        #Horizontal layout for the QLabels that display the links
        self.hbox_links=QHBoxLayout()
        self.hbox_links.addWidget(self.github_link)
        self.hbox_links.addWidget(self.paper_link)

        #Combining all the horizontal layouts together
        vbox_main = QVBoxLayout()
        vbox_main.addLayout(self.buttons)
        vbox_main.addWidget(self.media_player_widget)
        vbox_main.addLayout(self.hbox_links)
        central_widget = QWidget(self)
        central_widget.setLayout(vbox_main)
        self.setCentralWidget(central_widget)

    #Function to load the new session and set it innside the media_player_widget
    def update_session(self):
        self.sess = rt.InferenceSession(model_path(model_scale_map[self.current_sr_model_scale]), providers=[ self.provider])
        self.media_player_widget.setSession(self.sess)
   
    #Function to select the image
    def select_still(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Still", "", "Images (*.jpg *.jpeg *.png *.bmp);;All Files (*)", options = options)
        if file_name:
            url = QUrl.fromLocalFile(file_name)
            if QUrl.fileName(url).rsplit('.', 1)[1] in ['bmp', 'jpg', 'jpeg', 'png']:
                self.media_player_widget.setSource(url)
            
    #Function to change the provider if the user uses the drop-down
    def change_providers(self,text):
        self.provider = text
        self.update_session()

    #Function to change the model scale
    def change_model_scale(self):
        scale = self.media_player_widget.scale_toggle_button.text()
        self.sr_model = model_scale_map[scale]
        
        if self.media_player_widget.scale_toggle_button.text() == "4x":
            self.media_player_widget.scale_toggle_button.setText("2x")
            self.current_sr_model_scale = '4x'
        else:
            self.media_player_widget.scale_toggle_button.setText("4x")
            self.current_sr_model_scale = '2x'
            
        self.update_session()
        self.media_player_widget.setModelName(model_scale_map[scale])
        self.media_player_widget.setScale(int(scale[0]))
        self.media_player_widget.run_still_execution()

    #Garbage collection when the code is exitted            
    def closeEvent(self, event):
        gc.collect()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    light_style = """
    QWidget {
        background-color: #ffffff;
        color: #000000;
    }
    QPushButton {
        background-color: #f0f0f0;
        color: #000000;
        border: 1px solid #cccccc;
        padding: 5px;
    }
    QPushButton::hover {
        background-color: #e0e0e0;
    }
    QPushButton::pressed {
        background-color: #d0d0d0;
    }
    """
    app.setStyleSheet(light_style)
    window = SuperResolutionGUI()
    window.showMaximized()
    sys.exit(app.exec())