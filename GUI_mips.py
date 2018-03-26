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
        self.form_widget = WindowFrame(Tabs)
        
        self.set_view()
        
#        self.setCentralWidget(self.form_widget)
        
        
    def set_view(self):
        self.setCentralWidget(self.form_widget)
        self.extractAction2.triggered.connect(self.print_text)
        
    #functionalities
    def print_text(self):
        #for testing, able to read text by line
        raw_code =  self.form_widget.layout.load_tab.layout.textEdit.toPlainText()
        self.code = raw_code.split('\n')
        
#        print(code)
        
        self.MIPS.start(self.code)
        self.opcodes = self.MIPS.opcodes
        self.output_to_gui()
        for i,line in enumerate(self.code):
            print('Line ' , i+1 , ' ' ,line)
            
            
    
    def output_to_gui(self):
        table = self.form_widget.layout.load_tab.layout.opcodes
        table.setRowCount(0)
        
        for i,line in enumerate(self.code):
            table.insertRow(table.rowCount())
            table.setItem(i, 0,QtWidgets.QTableWidgetItem(line))
            table.setItem(i, 7,QtWidgets.QTableWidgetItem(self.opcodes[i]))
        
        
    
#        self.ar_Table.setItem(self.ar_Table.rowCount()-1,0,QtWidgets.QTableWidgetItem(ar_row["Date"])



class WindowFrame(QtWidgets.QWidget):
    
    def __init__(self, layout):
        super().__init__()
        self.setWindowTitle("Window")
        self.layout = layout(self)
        self.setLayout(self.layout)


class loadview(QtWidgets.QVBoxLayout):
    def __init__(self, parent=None):
        super(QtWidgets.QVBoxLayout, self).__init__(parent)
        loadButton = QtWidgets.QPushButton('Load')
        
        label1 = QtWidgets.QLabel('Please Enter Code Here')
        
        self.textEdit = QtWidgets.QTextEdit()
        
        self.opcodes = QtWidgets.QTableWidget()
        self.opcodes.setColumnCount(8)
        self.opcodes.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.opcodes.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.opcodes.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.opcodes.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        self.opcodes.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
        self.opcodes.horizontalHeader().setSectionResizeMode(5, QtWidgets.QHeaderView.Stretch)
        self.opcodes.horizontalHeader().setSectionResizeMode(6, QtWidgets.QHeaderView.Stretch)
        self.opcodes.horizontalHeader().setSectionResizeMode(7, QtWidgets.QHeaderView.Stretch)
#        self.opcodes.setRowCount(10)
        self.opcodes.setHorizontalHeaderLabels(["Instruction", "B: 31-26", "B: 25-21", "B: 20-16", "B: 15-11", "B: 10-16", "B: 5-0", "Hex"])
#        self.opcodes.setColumnWidth(0,150)
#        self.opcodes.setColumnWidth(1,70)
#        self.opcodes.setColumnWidth(2,70)
#        self.opcodes.setColumnWidth(3,70)
#        self.opcodes.setColumnWidth(4,70)
#        self.opcodes.setColumnWidth(5,70)
#        self.opcodes.setColumnWidth(6,70)
#        self.opcodes.setColumnWidth(7,150)
        
        #opcodes.tableWidget.setRowCount(15)
        
        
        
        self.h_box = QtWidgets.QHBoxLayout()
        
        self.h_box.addWidget(self.textEdit)
        self.h_box.addWidget(self.opcodes)
        
        self.addWidget(label1)
        self.addLayout(self.h_box)

class mainview(QtWidgets.QVBoxLayout):
    def __init__(self, parent=None):
        super(QtWidgets.QVBoxLayout, self).__init__(parent)
        
        label2 = QtWidgets.QLabel('Pipeline')
        
        self.pipelineMap = QtWidgets.QTableWidget()
        self.pipelineMap.setColumnCount(4)
        self.pipelineMap.setRowCount(5)        
        self.pipelineMap.setHorizontalHeaderLabels(["Instruction","1","2","3"])
        self.pipelineMap.setColumnWidth(0,150)
        self.pipelineMap.setColumnWidth(1,50)
        self.pipelineMap.setColumnWidth(2,50)
        self.pipelineMap.setColumnWidth(3,50)
        
        
        self.registers = QtWidgets.QTableWidget()
        self.registers.setRowCount(32)        
        self.registers.setVerticalHeaderLabels(["R0","R1","R2","R3","R4","R5","R6","R7","R8","R9","R10","R11","R12","R13","R14","R15","R16","R17","R18","R19","R20","R21","R22","R23","R24","R25","R26","R27","R28","R29","R30","R31"])

        
        
        self.h_box = QtWidgets.QHBoxLayout()
        
        self.h_box.addWidget(self.pipelineMap)
        self.h_box.addWidget(self.registers)
        self.addWidget(label2)
        
        
        self.addLayout(self.h_box)        
       
        
        
        
class Tabs(QtWidgets.QGridLayout):

    def __init__(self, parent=None):   
        super(QtWidgets.QGridLayout, self).__init__(parent)
        #self.layout = QtWidgets.QGridLayout(self)
        self.tabs = QtWidgets.QTabWidget()
        
        self.load_tab = WindowFrame(loadview)
        self.main_tab = WindowFrame(mainview)
        
        self.tabs.addTab(self.load_tab,"Load")
        self.tabs.addTab(self.main_tab,"Main")
        #self.layout.addWidget(self.tabs)
        self.addWidget(self.tabs)
        
        
    
    
def run():        
    app = QtWidgets.QApplication(sys.argv)
    GUI = Window()
    GUI.show()
    sys.exit(app.exec())
    
run()       