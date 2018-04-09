import sys
import re
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import Qt
from pprint import pprint
from functools import partial
from microMIPS_class import *

class Window(QtWidgets.QMainWindow):
    
    def __init__(self, parent= None ):
        super(Window, self).__init__()
        
#        self.setGeometry(8,50,1500,500)
        self.resize(1366,768)
        self.setWindowTitle("microMIPS")
        
        self.extractAction1 = QtWidgets.QAction("Run Single Cycle", self)
        self.extractAction1.setShortcut('F5')
        self.extractAction2 = QtWidgets.QAction("Run Continuously", self)
        self.extractAction2.setShortcut('F7')
        self.extractAction3 = QtWidgets.QAction("Go To Memory", self)
        self.extractAction3.setShortcut('F1')
        
        self.statusBar()

        
        mainMenu = self.menuBar()        
        fileMenu = mainMenu.addMenu('&Run')
        fileMenu.addAction(self.extractAction1)
        fileMenu.addAction(self.extractAction2)
        
        self.Go_To = mainMenu.addMenu('&Go To')
        self.Go_To.addAction(self.extractAction3)
        
        self.form_widget = WindowFrame(Tabs)
        
        self.set_view()
        
#        self.setCentralWidget(self.form_widget)
        
        
    def set_view(self):
        self.setCentralWidget(self.form_widget)
        self.form_widget.layout.load_tab.layout.bLoad.clicked.connect(self.print_text)
        self.form_widget.layout.main_tab.layout.bEdit.clicked.connect(self.set_reg)
        self.extractAction3.triggered.connect(self.Go_To_func)
        
        #test only
#        self.form_widget.layout.load_tab.layout.bStart.clicked.connect(self.show_inner_pipeline)
        
        
        self.extractAction1.triggered.connect(partial(self.start_cycle,True,self.form_widget.layout.main_tab.layout))
        self.extractAction2.triggered.connect(partial(self.start_cycle,False,self.form_widget.layout.main_tab.layout))
        self.form_widget.layout.main_tab.layout.pipelineMap.itemDoubleClicked.connect(self.show_inner_pipeline)
    
    def set_reg(self):
        if hasattr(self,"MIPS"):
            if not self.MIPS.if_Error and not self.MIPS.if_paramError:
                pprint(self.MIPS.regList)
                reg_table = self.form_widget.layout.main_tab.layout.registers
                for i in range(reg_table.rowCount()):
#                    print(i ,reg_table.item(i, 0).text())
                    self.MIPS.regList[i]["regValue"] = reg_table.item(i, 0).text()
                
                pprint(self.MIPS.regList)
                    
                
            else:
                if self.MIPS.if_Error:
                    self.showMessage("Instruction Error","ERROR: Invalid Instruction @ Line "+str(self.MIPS.Error_Line),None,0)
                if self.MIPS.if_paramError:
                    self.showMessage("Parameter Error","ERROR: Invalid Parameter @ Line "+str(self.MIPS.Error_Line),None,0)
            
        else:
            self.showMessage("Error","YOU NEED TO LOAD FIRST",None,0)
    
    
    def start_cycle(self, if_Single, main_layout):
        if hasattr(self,"MIPS"):
            if not self.MIPS.if_Error and not self.MIPS.if_paramError:
                self.MIPS.start_cycle(if_Single,main_layout)
                self.output_to_gui()
            else:
                if self.MIPS.if_Error:
                    self.showMessage("Instruction Error","ERROR: Invalid Instruction @ Line "+str(self.MIPS.Error_Line),None,0)
                if self.MIPS.if_paramError:
                    self.showMessage("Parameter Error","ERROR: Invalid Parameter @ Line "+str(self.MIPS.Error_Line),None,0)
                
        else:
            self.showMessage("Error","YOU NEED TO LOAD FIRST",None,0)
        
        
#        main_layout.pipelineMap.itemActivated.connect(self.show_inner_pipeline)
    
    
    
        
    #functionalities
    def Go_To_func(self):
        print("in Go To Function")
        title = "Go To Memory"
        label = "Address"
        
        text_address = QtWidgets.QInputDialog.getText(self, title, label)
#        print(text_address)
        
        if text_address[1] and text_address[0] != "":
            mem_table = self.form_widget.layout.main_tab.layout.data
            if mem_table.rowCount() > 0:
                
                if re.match(r"^[0-9A-F]{4}$", text_address[0]) and int(text_address[0],16)< int("1000", 16):
                    
                    
                    current_address  = int(text_address[0],16)
                    
                    while current_address % 8 != 0:
                        current_address -= 1
                    
                    hex_address = hex(current_address).split('x')[-1].zfill(4).upper()
                    
                    
                    
                    
                    mem_item = mem_table.findItems(hex_address, QtCore.Qt.MatchExactly)
#                    print(mem_item)
                    
                    #change tab
                    self.form_widget.layout.tabs.setCurrentIndex(1)
                    
                    mem_table.selectRow(mem_item[0].row())
                else:
                    self.showMessage("Error Input","Input needs to be 4 hex characters","Input should only be from 0000 - 0FFF")
            else:
                print("YOU NEED TO LOAD FIRST")    
                self.showMessage("Error","YOU NEED TO LOAD FIRST",None,1)
            
            
        
        

    
    def showMessage(self, title,message, info=None, messageType=0):
        
        """ This Method is responsible for Showing Dialogs if there is an error """
                    
        infoBox = QtWidgets.QMessageBox()
        if messageType == 0:
            infoBox.setIcon(QtWidgets.QMessageBox.Warning)
        else:
            infoBox.setIcon(QtWidgets.QMessageBox.Information)
        infoBox.setText(message)
        if info is not None:
            infoBox.setInformativeText(info)
        infoBox.setWindowTitle(title)
        infoBox.setEscapeButton(QtWidgets.QMessageBox.Close) 
        infoBox.exec_()

        infoBox.close()
    
    
    
    def show_inner_pipeline(self, table_item):
        print("table_item ", table_item.row(), table_item.column(), table_item.text())
        
        try:
            self.pipeline_Window.close()
        except:
            pass
        
        cycle_content ={}
        cycle_content["phase"] = table_item.text()
        print("THIS IS THE PHASE ", cycle_content["phase"])
        print("THIS IS THE LENGTH OF PHASE ", len(cycle_content["phase"]))
        #---only for testing---#
        #---only for testing---#
        
        
        if len(cycle_content["phase"]) != 0 and len(cycle_content["phase"]) != 1:
            cycle_content["data"] = self.MIPS.cycle_content_array[table_item.column()][table_item.row()]
            self.pipeline_Window = SubWindow(cycle_content,self)
            self.pipeline_Window.subwidgetFrame.layout.bExit.clicked.connect(self.pipeline_Window.close)
            self.pipeline_Window.show()
            print("showing inner pipeline")
            
    
    def print_text(self):
        self.MIPS = MIPS()
        #for testing, able to read text by line
        raw_code =  self.form_widget.layout.load_tab.layout.textEdit.toPlainText()
        
#        print(code)
#        pprint(raw_code)
        self.MIPS.start_opcode(raw_code)
    
        if not self.MIPS.if_Error and not self.MIPS.if_paramError:
            self.opcodes = self.MIPS.opcode
            self.code_line = self.MIPS.code_line
            self.output_to_gui()
            for i,line in enumerate(self.code_line):
                print('Line ' , i+1 , ' ' ,line)
        else:
            if self.MIPS.if_Error:
                self.showMessage("Instruction Error","ERROR: Invalid Instruction @ Line "+str(self.MIPS.Error_Line),None,0)
            if self.MIPS.if_paramError:
                self.showMessage("Parameter Error","ERROR: Invalid Parameter @ Line "+str(self.MIPS.Error_Line),None,0)
            
    
    def assemble_mem(self, memList):
        memValue = ""
        mem_container_array = []
        mem_container ={}
        

        #IMPORTANT TO CREATE A SEPARATE MEMORY LIST
        
#        for nCtr,mem in enumerate(memList):
        nCtr = 0
        while nCtr <= len(memList):
            if nCtr != len(memList):
                mem = memList[nCtr]
        
            if nCtr == len(memList):
                mem_container["Value"] = memValue.upper()
                mem_container_array.append(mem_container)
                mem_container={}
    
            elif int(mem["memAddress"], 16)% 8 == 0:  
                if nCtr != 0:
                    mem_container["Value"] = memValue.upper()
                    memValue = ""
                    mem_container_array.append(mem_container)
                    mem_container={}
                    
                mem_container["Address"] = mem["memAddress"].upper()
#                print(mem["memAddress"])
                
#                if nCtr == len(memList)-1:
#                    mem_container_array.append(mem_container)
            if nCtr != len(memList):
                memValue = mem["memValue"]+ str(memValue)
            nCtr += 1
        
        return mem_container_array
        
        
    
    
    def output_to_gui(self):
        if not self.MIPS.if_Error:
        
            table = self.form_widget.layout.load_tab.layout.opcodes
            table.setRowCount(0)

            for i,line in enumerate(self.code_line):
                table.insertRow(table.rowCount())
                table.setItem(i, 0,QtWidgets.QTableWidgetItem(line))
                table.setItem(i, 7,QtWidgets.QTableWidgetItem(self.opcodes[i]))

            reg_table = self.form_widget.layout.main_tab.layout.registers
            reg_table.setColumnCount(0)
            reg_table.setColumnCount(1)
            reg_table.setHorizontalHeaderLabels(["Value"])
            reg_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

            regList = list(self.MIPS.regList)        

            for nCtr, reg in enumerate(regList):
                reg_table.setItem(nCtr, 0,QtWidgets.QTableWidgetItem(reg["regValue"]))



            mem_table = self.form_widget.layout.main_tab.layout.data
            mem_table.setRowCount(0)
            mem_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
            mem_table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

            memList = list(self.MIPS.memList)
            memList = self.assemble_mem(memList)

            for nCtr, mem in enumerate(memList):
                mem_table.insertRow(mem_table.rowCount())
                mem_table.setItem(nCtr,0, QtWidgets.QTableWidgetItem(mem["Address"]))
                mem_table.setItem(nCtr,1, QtWidgets.QTableWidgetItem(mem["Value"]))
            
#        pprint(memList)
            
        
        
            
class SubWindow(QtWidgets.QMainWindow):
    
    def __init__(self, cycle_content,parent=None):
        super(SubWindow, self).__init__(parent)
#        print(table_item)
        self.resize(600,300)
        self.setWindowTitle("Inner Pipeline")
        self.setWindowFlag(QtCore.Qt.SubWindow)
        self.pipeline_tab(cycle_content)
        
    def pipeline_tab(self, cycle_content):
        self.subwidgetFrame = SubWindowFrame(PipelineView, cycle_content)
        self.setCentralWidget(self.subwidgetFrame)

class SubWindowFrame(QtWidgets.QWidget):
    
    def __init__(self, layout, extra=None):
        super().__init__()
        
        if extra is None:
            self.layout = layout(self)
        else:
            self.layout = layout(extra, self)
        
        self.setLayout(self.layout)
        
class PipelineView(QtWidgets.QGridLayout):
    
    def __init__(self, cycle_content, parent=None ):
        super().__init__()
        self.cycle_content = cycle_content
        self.init_ui()

    
    def init_ui(self):
        self.pipelineContent = QtWidgets.QTableWidget()
        self.pipelineContent.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.pipelineContent.setColumnCount(1)
        self.pipelineContent.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.pipelineContent.setHorizontalHeaderLabels(["Data"])
        self.bExit = QtWidgets.QPushButton("EXIT")
        self.bExit.setFixedWidth(100)
        self.bExit.setStyleSheet("""QPushButton { font-size: 14pt; padding: 10px; color: #fff; background-color: #ffc107; border-color: #4cae4c;
                                                    border-radius: 5px;
                                                    margin-top: 10px;
                                                    }
                                        QPushButton:hover {background-color: #fdcb35; border-color: #fdcb35;}""")
        
        
#        print(self.table_item)
        
        self.addWidget(self.pipelineContent,1,1,2,2)
        self.addWidget(self.bExit,3,2,1,1)
#        pprint(self.cycle_content)
        
        content_title =[]
        
        if self.cycle_content["phase"] == "IF":
            content_title = ["IF/ID.IR", "IF/ID.NPC"]
        if self.cycle_content["phase"] == "ID":
            content_title = ["ID/EX.A", "ID/EX.B", "ID/EX.IMM", "ID/EX.IR", "ID/EX.NPC"]
        if self.cycle_content["phase"] == "EX":
            content_title = ["EX/MEM.ALUOUTPUT", "EX/MEM.COND", "EX/MEM.IR", "EX/MEM.B"]
        if self.cycle_content["phase"] == "MEM":
            content_title = ["MEM/WB.LMD","MEM/WB.IR","MEM/WB.ALUOUTPUT","MEM/WB.B",'MEM/WB.RANGE']
        if self.cycle_content["phase"] == "WB":
            content_title = ["Rn"]
            
        if len(content_title) != 0:
        
            self.pipelineContent.setRowCount(len(content_title))
            self.pipelineContent.setVerticalHeaderLabels(content_title)

            for nCtr, title in enumerate(content_title):
                self.pipelineContent.setItem(nCtr,0, QtWidgets.QTableWidgetItem(str(self.cycle_content["data"][title])))
            
        
        

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
        self.textEdit.setText("""DADDIU R1, R0, #0000
DADDIU R2, R0, #0000
DADDU R3, R1, R2
BGTZC R1, L1
DADDU R3, R1, R1
DADDIU R3, R0, #0000
DADDIU R3, R0, #0000
DADDIU R3, R0, #0000
L1: DADDIU R3, R0, #6969
DADDIU R3, R0, #0000
DADDIU R3, R0, #0000
SD R2, 0F00(R0)
DADDIU R3, R2, #0000
XORI R1, R2, #1000
""")
        
        self.opcodes = QtWidgets.QTableWidget()
        self.opcodes.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.opcodes.setColumnCount(8)
        self.opcodes.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
#        self.opcodes.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
#        self.opcodes.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
#        self.opcodes.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
#        self.opcodes.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
#        self.opcodes.horizontalHeader().setSectionResizeMode(5, QtWidgets.QHeaderView.Stretch)
#        self.opcodes.horizontalHeader().setSectionResizeMode(6, QtWidgets.QHeaderView.Stretch)
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
        
        
        
        self.h_box = QtWidgets.QGridLayout()
        
        self.h_box.setColumnStretch(1,1)
        self.h_box.addWidget(self.textEdit,0,1)
        self.h_box.addWidget(self.opcodes,0,2)
        self.h_box.setColumnStretch(2,2)
        
        self.bLoad = QtWidgets.QPushButton("LOAD")
        self.bLoad.setFixedWidth(100)
        self.bLoad.setStyleSheet("""QPushButton { font-size: 14pt; padding: 10px; color: #fff; background-color: #ffc107; border-color: #4cae4c;
                                                    border-radius: 5px;
                                                    margin-top: 10px;
                                                    }
                                        QPushButton:hover {background-color: #fdcb35; border-color: #fdcb35;}""")
        
        self.bStart = QtWidgets.QPushButton("START")
        self.bStart.setFixedWidth(100)
        self.bStart.setStyleSheet("""QPushButton { font-size: 14pt; padding: 10px; color: #fff; background-color: #5cb85c; border-color: #4cae4c;
                                                    border-radius: 5px;
                                                    margin-top: 10px;
                                                    }
                                        QPushButton:hover {background-color: #4baa4b; border-color: #409140;}""")
        self.grid_layout = QtWidgets.QGridLayout()
#        self.h_box_2.setSpacing(0)
        self.grid_layout.setColumnStretch(0,1)
        self.grid_layout.addWidget(self.bLoad,0,1)
#        self.grid_layout.addWidget(self.bStart,0,2)
        self.grid_layout.setColumnStretch(2,1)
        
        self.addWidget(label1)
        self.addLayout(self.h_box)
        self.addLayout(self.grid_layout)

class mainview(QtWidgets.QGridLayout):
    def __init__(self, parent=None):
        super(QtWidgets.QGridLayout, self).__init__(parent)
        
        label2 = QtWidgets.QLabel('Pipeline')
        
        self.pipelineMap = QtWidgets.QTableWidget()
        self.pipelineMap.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.registers = QtWidgets.QTableWidget()
        self.registers.setRowCount(32)
        self.bEdit = QtWidgets.QPushButton("Edit")
        self.registers.setVerticalHeaderLabels(["R0","R1","R2","R3","R4","R5","R6","R7","R8","R9","R10","R11","R12","R13","R14","R15","R16","R17","R18","R19","R20","R21","R22","R23","R24","R25","R26","R27","R28","R29","R30","R31"])
        
        self.data = QtWidgets.QTableWidget()
        self.data.setColumnCount(2)
        self.data.setHorizontalHeaderLabels(["Address", "Representation"])
        

        
        Pipeline_Group = QtWidgets.QGroupBox("Pipeline")
        Pipeline_Layout = QtWidgets.QGridLayout()
        Pipeline_Layout.addWidget(self.pipelineMap,1,1)
        Pipeline_Group.setLayout(Pipeline_Layout)
        
        Register_Group = QtWidgets.QGroupBox("Registers")
        Register_Layout = QtWidgets.QGridLayout()
        Register_Layout.addWidget(self.registers,1,1)
        Register_Layout.addWidget(self.bEdit,2,1)
        Register_Group.setLayout(Register_Layout)
        
        Data_Group = QtWidgets.QGroupBox("Data")
        Data_Layout = QtWidgets.QGridLayout()
        Data_Layout.addWidget(self.data,1,1)
        Data_Group.setLayout(Data_Layout)
        
        self.addWidget(Pipeline_Group,1,1,2,1)
        self.addWidget(Register_Group,1,2,1,1)
        self.addWidget(Data_Group,2,2,1,1)
        
        
        self.setColumnStretch(1,2)
        self.setColumnStretch(2,1)
        
        
#        self.addWidget(label2)
        
        
#        self.addLayout(self.h_box)
        
    def make_navbar(self):
        self.navbar = QtWidgets.QGroupBox("Registers")
        #self.navbar.setFlat(True)
        
        navGrid = QtWidgets.QGridLayout()
        
        navGrid.setColumnStretch(5,1)
        navGrid.addWidget(self.bLogo, 1,1)
        navGrid.addWidget(self.bInvoice, 1,2)
        navGrid.addWidget(self.bInventory,1,3)
        navGrid.addWidget(self.bAccounting,1,4)
        #navGrid.addWidget(self.bAdmin,1,6)
        navGrid.addWidget(self.bLogout,1,7)
        
        self.navbar.setLayout(navGrid)
        
       
        
        
        
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
        
        
    
    
#def run():
#    app = QtWidgets.QApplication(sys.argv)
#    GUI = Window()
#    GUI.show()
#    sys.exit(app.exec())
#
#run()       