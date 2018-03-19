import sys
from PyQt5 import QtWidgets
from microMIPS import *


class Window(QtWidgets.QMainWindow):
    
    def __init__(self, parent= None):
        super(Window, self).__init__()
        
        self.setGeometry(8,50,1500,500)
        self.setWindowTitle("microMIPS")
        
        self.extractAction1 = QtWidgets.QAction("Run Single Cycle", self)
        self.extractAction1.setShortcut('F5')
        self.extractAction2 = QtWidgets.QAction("Run Continuously", self)
        self.extractAction2.setShortcut('F7')
        
        self.statusBar()
        
        self.MIPS = MIPS()
        
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&Run')
        fileMenu.addAction(self.extractAction1)
        fileMenu.addAction(self.extractAction2)
        self.form_widget = FormWidget(self)
        
        self.set_view()
        
#        self.setCentralWidget(self.form_widget)
        
        
    def set_view(self):
        self.setCentralWidget(self.form_widget)
        self.extractAction2.triggered.connect(self.print_text)
        
    #functionalities
    def print_text(self):
        #for testing, able to read text by line
        raw_code =  self.form_widget.textEdit.toPlainText()
        self.code = raw_code.split('\n')
        
#        print(code)
        
        self.MIPS.start(self.code)
        self.opcodes = self.MIPS.opcodes
        self.output_to_gui()
        for i,line in enumerate(self.code):
            print('Line ' , i+1 , ' ' ,line)
            
            
    
    def output_to_gui(self):
        table = self.form_widget.pipelineMap
        
        for i,line in enumerate(self.code):
            table.setItem(i, 0,QtWidgets.QTableWidgetItem(line))
            table.setItem(i, 7,QtWidgets.QTableWidgetItem(self.opcodes[i]))
        
        
    
#        self.ar_Table.setItem(self.ar_Table.rowCount()-1,0,QtWidgets.QTableWidgetItem(ar_row["Date"]))

    
class FormWidget(QtWidgets.QWidget):
    
    def __init__(self, parent):
        super(FormWidget,self).__init__(parent)
        
        loadButton = QtWidgets.QPushButton('Load')
        
        label1 = QtWidgets.QLabel('Please Enter Code Here')
        label2 = QtWidgets.QLabel('OpCodes')
        
        self.textEdit = QtWidgets.QTextEdit()
        
        self.pipelineMap = QtWidgets.QTableWidget()
        self.pipelineMap.setColumnCount(8)
        self.pipelineMap.setRowCount(10)
        self.pipelineMap.setHorizontalHeaderLabels(["Instruction", "B: 31-26", "B: 25-21", "B: 20-16", "B: 15-11", "B: 10-16", "B: 5-0", "Hex"])
        self.pipelineMap.setColumnWidth(0,150)
        self.pipelineMap.setColumnWidth(1,70)
        self.pipelineMap.setColumnWidth(2,70)
        self.pipelineMap.setColumnWidth(3,70)
        self.pipelineMap.setColumnWidth(4,70)
        self.pipelineMap.setColumnWidth(5,70)
        self.pipelineMap.setColumnWidth(6,70)
        self.pipelineMap.setColumnWidth(7,150)
        
        #pipelineMap.tableWidget.setRowCount(15)
        
        
        
        h_box = QtWidgets.QHBoxLayout()
        
        h_box.addWidget(self.textEdit)
        h_box.addWidget(self.pipelineMap)
        
        
        v_box = QtWidgets.QVBoxLayout()
        v_box.addWidget(label1)
        v_box.addLayout(h_box)
        
        
        
        self.setLayout(v_box)
        
        
    

    
    
def run():        
    app = QtWidgets.QApplication(sys.argv)
    GUI = Window()
    GUI.show()
    sys.exit(app.exec())
    
run()       