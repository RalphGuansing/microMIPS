import re
from pprint import pprint
from GUI_mips import *
from threading import Thread
from excelwriter import *

test_string = """DADDIU R1, R0, #0000
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
DADDIU R3, R0, #0000
XORI R1, R2, #1000
"""
test_string1 = """DADDIU R1, R0, #1000
DADDIU R2, R0, #0000
BGTZC R1, L1
DADDU R3, R1, R1
DADDIU R3, R0, #0000
XORI R1, R2, #1000
L1: DADDIU R3, R0, #6969
"""

class MIPS:
    def __init__(self):
        self.ins_List = ["LD", "SD", "DADDIU", "XORI", "DADDU", "SLT", "BGTZC", "J"]
        self.regList = []

        self.reg_Phase = ({}, {}, {}, {}, {})

        for regNum in range(0, 32):
            reg = {}
            reg["regValue"] = hex(0).split('x')[-1].zfill(16)
            reg["regNum"] = bin(regNum).split('b')[-1].zfill(5)
            reg["in_use"] = False
            self.regList.append(reg)
        
        self.address_location = []
        self.clean_code = ""
        
    def DADDU_SLT_REGEX(self, expression):
        sanitized = expression.split(" ")
        del sanitized[0]
        sanitized = " ".join(sanitized)

        if re.match(r"^R([3][0-1]|[1-2][0-9]|[0-9]),(\sR|R)([3][0-1]|[1-2][0-9]|[0-9]),(\sR|R)([3][0-1]|[1-2][0-9]|[0-9])", sanitized):
            return False
        else:
            return True

    def LD_SD_REGEX(self, expression):
        sanitized = expression.split(" ")
        del sanitized[0]
        sanitized = " ".join(sanitized)
        if re.match(r"^R([3][0-1]|[1-2][0-9]|[0-9]),(\s1|1)[0-9A-F]{3}[(]R([3][0-1]|[1-2][0-9]|[0-9])[)]", sanitized):
            return False
        else:
            return True

    def DADDIU_XORI_REGEX(self, expression):
        sanitized = expression.split(" ")
        del sanitized[0]
        sanitized = " ".join(sanitized)

        if re.match(r"^R([3][0-1]|[1-2][0-9]|[0-9]),(\sR|R)([3][0-1]|[1-2][0-9]|[0-9]),(\s#|#)[0-9A-F]{4}", sanitized):
            return False
        else:
            return True

    #---------------------ralph---------------------------
    def BGTZC_REGEX(self, expression):
        sanitized = expression.split(" ")
        del sanitized[0]
    #    print(sanitized[len(sanitized)-2]) e.g. R1,
        sanitized = " ".join(sanitized)

        if re.match(r"^R([3][0-1]|[1-2][0-9]|[0-9]), \w+$", sanitized):
            return False
        else:
            return True

    def J_REGEX(self, expression):
        sanitized = expression.split(" ")
        del sanitized[0]
    #    print(sanitized[len(sanitized)-2]) e.g. R1,
        sanitized = " ".join(sanitized)

        if re.match(r"^\w+$", sanitized):
            return False
        else:
            return True
    #---------------------ralph---------------------------


    def DADDU_SLT_REFORMAT(self, expression):
        ins_Op = {4 : 0b101101, 5 : 0b101010}
        bin_Opcode = []
        bin_Opcode.append(bin(0).split('b')[-1].zfill(6))

        sanitized = expression.split(",")
        sanitized.insert(1, sanitized[0][-2:])
        del sanitized[0]

        rd = int(sanitized[0][-1:])
        rs = int(sanitized[1][-1:])
        rt = int(sanitized[2][-1:])

        bin_Opcode.append(self.regList[rs]["regNum"])
        bin_Opcode.append(self.regList[rt]["regNum"])
        bin_Opcode.append(self.regList[rd]["regNum"])

        bin_Opcode.append(bin(0).split('b')[-1].zfill(5))
        bin_Opcode.append(bin(ins_Op[self.ins_List.index(expression.split(" ")[0])]).split('b')[-1].zfill(6))

        hex_Opcode = hex(int("".join(bin_Opcode), 2)).split('x')[-1].zfill(8).upper()
        print(self, expression)
        print("OPCODE: ", hex_Opcode, "\n")

        return {"ins_rs": rs, "ins_rt": rt, "ins_rd": rd, "Opcode": hex_Opcode, "if_BCJ": False, "if_Imm": False, "if_LSD": False}


    def LD_SD_REFORMAT(self, expression):
        ins_Op = {0 : 0b110111, 1 : 0b111111}
        bin_Opcode = []
        bin_Opcode.append(bin(ins_Op[self.ins_List.index(expression.split(" ")[0])]).split('b')[-1].zfill(6))

        sanitized = expression.split(",")
        sanitized.insert(1, sanitized[0][-2:])
        del sanitized[0]

        base = int(sanitized[1].split('(')[-1][:2][1])
        rt = int(sanitized[0][-1:])
        offset = sanitized[1].split('(')[0][-4:]

        bin_Opcode.append(self.regList[base]["regNum"])
        bin_Opcode.append(self.regList[rt]["regNum"])

        for x in range(0, 4):
            bin_Opcode.append(bin(int(offset[x])).split('b')[-1].zfill(4))

        hex_Opcode = hex(int("".join(bin_Opcode), 2)).split('x')[-1].zfill(8).upper()
        print(self, expression)
        print("OPCODE: ", hex_Opcode, "\n")

        return {"ins_base": base, "ins_rt": rt, "ins_offset": offset, "Opcode": hex_Opcode, "if_BCJ": False, "if_Imm": False, "if_LSD": True}


    def DADDIU_XORI_REFORMAT(self, expression):
        ins_Op = {2 : 0b011001, 3 : 0b001110}
        bin_Opcode = []
        bin_Opcode.append(bin(ins_Op[self.ins_List.index(expression.split(" ")[0])]).split('b')[-1].zfill(6))

        sanitized = expression.split(",")
        sanitized.insert(1, sanitized[0][-2:])
        del sanitized[0]

        rt = int(sanitized[0][-1:])
        rs = int(sanitized[1][-1:])
        imm = sanitized[2][-4:]

        bin_Opcode.append(self.regList[rs]["regNum"])
        bin_Opcode.append(self.regList[rt]["regNum"])

        for x in range(0, 4):
            bin_Opcode.append(bin(int(imm[x])).split('b')[-1].zfill(4))

        hex_Opcode = hex(int("".join(bin_Opcode), 2)).split('x')[-1].zfill(8).upper()
        print(self, expression)
        print("OPCODE: ", hex_Opcode, "\n")

        return {"ins_rs": rs, "ins_rt": rt, "ins_imm": imm, "Opcode": hex_Opcode, "if_BCJ": False, "if_Imm": True, "if_LSD": False}

    #---------------------INC---------------------------
    def BGTZC_REFORMAT(self, expression, current_line):
        print("in BGTZC_REFORMAT")
        print(self, expression)
        ins_Op = {0: 0b010111, 1: 0b000010}
        bin_Opcode = []
        bin_Opcode.append(bin(ins_Op[0]).split('b')[-1].zfill(6))
        bin_Opcode.append(bin(0).split('b')[-1].zfill(5))

        sanitized = expression.split(" ")
        del sanitized[0]
        print(sanitized)

        rt = int(sanitized[0][:-1][-1:])

        bin_Opcode.append(self.regList[rt]["regNum"])

        # offset binary
        offset_line = self.get_line_address(sanitized[1])
        offset = abs(offset_line - current_line - 1)
        bin_Opcode.append(bin(offset).split('b')[-1].zfill(16))
        hex_Opcode = hex(int("".join(bin_Opcode), 2)).split('x')[-1].zfill(8).upper()

    #    print(offset)
    #    print(bin_Opcode)

        imm = hex_Opcode[-4:]
    #    print("THIS IS IMM ", imm)

        print("OPCODE: ", hex_Opcode, "\n")

        return {"ins_rt": rt, "ins_imm": imm, "Opcode": hex_Opcode, "if_BCJ": True, "if_Imm": False, "if_LSD": False}

    def J_REFORMAT(self, expression):
        print("in J_REFORMAT")
        print(self, expression)
        ins_Op ={0: 0b000010}
        bin_Opcode = []
        bin_Opcode.append(bin(ins_Op[0]).split('b')[-1].zfill(6))
        bin_Opcode.append(bin(0).split('b')[-1].zfill(5))
        bin_Opcode.append(bin(0).split('b')[-1].zfill(5))

        sanitized = expression.split(" ")
        del sanitized[0]

        offset_line = self.get_line_address(sanitized[0])
        bin_Opcode.append(bin(offset_line).split('b')[-1].zfill(16))
        hex_Opcode = hex(int("".join(bin_Opcode), 2)).split('x')[-1].zfill(8).upper()

        imm = hex_Opcode[-4:]

        print(bin_Opcode)
        print("OPCODE: ", hex_Opcode, "\n")


        rt = ""
        return {"ins_rt": rt, "ins_imm": imm, "Opcode": hex_Opcode, "if_BCJ": True, "if_Imm": False, "if_LSD": False}


    #---------------------INC---------------------------

    def LD_SD(self, instruction):
        # if instruction["ins_Num"] == 0:
        # 	#LD operation

        # else:
        # 	#SD operation
        pass

    def DADDIU_XORI(self, instruction):
        if instruction["ins_Num"] == 2:
            #DADDIU operation
            output = int(self.regList[instruction["ins_rs"]]["regValue"], 16) + int(instruction["ins_imm"], 16)
        else:
            #XORI operation
            output = int(self.regList[instruction["ins_rs"]]["regValue"], 16) ^ int(instruction["ins_imm"], 16)

        output = hex(output).split('x')[-1].zfill(16)
        cond = 0
        return {"ALUOUT": output, "cond": cond}

    def DADDU_SLT(self, instruction):
        if instruction["ins_Num"] == 4:
            #DADDU operation
            output = int(self.regList[instruction["ins_rs"]]["regValue"], 16) + int(self.regList[instruction["ins_rt"]]["regValue"], 16)
        else:
            #SLT operation
            if int(self.regList[instruction["ins_rs"]]["regValue"], 16) < int(self.regList[instruction["ins_rt"]]["regValue"], 16):
                output = int(self.regList[instruction["ins_rs"]]["regValue"], 16)
            else:
                output = 0
        output = hex(output).split('x')[-1].zfill(16)
        cond = 0
        return {"ALUOUT": output, "cond": cond}

    def BGTZC_J(self, instruction):
    #    pprint(self.reg_Phase)
        output = ""
        cond = 0
    #    print(int(self.regList[instruction["ins_rt"]]["regValue"], 16))
        if instruction["ins_Num"] == 6:
            #BGTZC operation
            NPC = int(self.reg_Phase[1]["ID/EX.NPC"], 16)
            IMM = int(self.reg_Phase[1]["ID/EX.IMM"], 16)
    #        print(NPC, " + ", IMM, " *4")
            output = NPC + IMM * 4
    #        print("ALUOUTPUT = ", hex(output))

            if int(self.regList[instruction["ins_rt"]]["regValue"], 16) > 0:
                cond = 1
            else:
                cond = 0

        elif instruction["ins_Num"] == 7:
            IMM = int(self.reg_Phase[1]["ID/EX.IMM"], 16)
            output = IMM * 4
            cond = 1

        output = hex(output).split('x')[-1].zfill(16)
    #    print("ALUOUTPUT = ", output)
    #    print("condition is ",cond)
        return {"ALUOUT": output, "cond": cond}


    def IF(self, ins_String):
        #if B or J


        self.reg_Phase[0]["IF/ID.IR"] = ins_String["ins_Opcode"]
        self.reg_Phase[0]["IF/ID.NPC"] = hex(int(ins_String["inst_add"], 16) + 4).split('x')[-1].zfill(4).upper()
        if ins_String["ins_type"] == 1:
            ins_String["if_BR_J"] = True

        print("IF")
    #    pprint(self.reg_Phase[0])
        return "IF"

    def ID(self, ins_String):
        #---------------------INC--------------------------- tweaked, maybe goods
        if ins_String["ins_type"] == 1: #BGTZC/J
    #        print("this is the rt", ins_String["ins_rt"])
            if ins_String["ins_rt"] == "":
                print("THIS IS J")
                self.reg_Phase[1]["ID/EX.IR"] = self.reg_Phase[0]["IF/ID.IR"]
                self.reg_Phase[1]["ID/EX.NPC"] = self.reg_Phase[0]["IF/ID.NPC"]
                self.reg_Phase[1]["ID/EX.IMM"] = ins_String["ins_imm"].zfill(16)
            else:
                if self.regList[ins_String["ins_rt"]]["in_use"]:
                    ins_String["if_Stall"] = True
                else:
                    ins_String["if_Stall"] = False
    #                self.regList[ins_String["ins_rt"]]["in_use"] = True
                    self.reg_Phase[1]["ID/EX.IR"] = self.reg_Phase[0]["IF/ID.IR"]
                    self.reg_Phase[1]["ID/EX.NPC"] = self.reg_Phase[0]["IF/ID.NPC"]
                    self.reg_Phase[1]["ID/EX.B"] = self.regList[ins_String["ins_rt"]]["regValue"]
                    self.reg_Phase[1]["ID/EX.IMM"] = ins_String["ins_imm"].zfill(16)
    #            pprint(self.reg_Phase[1])
                #get A, B and imm
            #---------------------INC---------------------------
        elif ins_String["ins_type"] == 2: #IMM
            if self.regList[ins_String["ins_rs"]]["in_use"]:
                ins_String["if_Stall"] = True
            else:
                ins_String["if_Stall"] = False
                self.regList[ins_String["ins_rt"]]["in_use"] = True
                self.reg_Phase[1]["ID/EX.IR"] = self.reg_Phase[0]["IF/ID.IR"]
                self.reg_Phase[1]["ID/EX.NPC"] = self.reg_Phase[0]["IF/ID.NPC"]
                self.reg_Phase[1]["ID/EX.A"] = self.regList[ins_String["ins_rs"]]["regValue"]
                self.reg_Phase[1]["ID/EX.B"] = self.regList[ins_String["ins_rt"]]["regValue"]
                self.reg_Phase[1]["ID/EX.IMM"] = ins_String["ins_imm"].zfill(16)
                #get A, B and imm
        elif ins_String["ins_type"] == 3: #SD/LD
            if self.regList[ins_String["ins_base"]]["in_use"]:
                ins_String["if_Stall"] = True
            else:
                ins_String["if_Stall"] = False
                self.regList[ins_String["ins_rt"]]["in_use"] = True
                self.reg_Phase[1]["ID/EX.IR"] = self.reg_Phase[0]["IF/ID.IR"]
                self.reg_Phase[1]["ID/EX.NPC"] = self.reg_Phase[0]["IF/ID.NPC"]
                self.reg_Phase[1]["ID/EX.A"] = self.regList[ins_String["ins_base"]]["regValue"]
                self.reg_Phase[1]["ID/EX.B"] = self.regList[ins_String["ins_rt"]]["regValue"]
                self.reg_Phase[1]["ID/EX.IMM"] =	ins_String["ins_offset"].zfill(16)
                #get A, B and imm
        else: #REGISTERS
            if self.regList[ins_String["ins_rt"]]["in_use"] or self.regList[ins_String["ins_rs"]]["in_use"]:
                ins_String["if_Stall"] = True
            else:
                ins_String["if_Stall"] = False
                self.regList[ins_String["ins_rd"]]["in_use"] = True
                self.reg_Phase[1]["ID/EX.IR"] = self.reg_Phase[0]["IF/ID.IR"]
                self.reg_Phase[1]["ID/EX.NPC"] = self.reg_Phase[0]["IF/ID.NPC"]
                self.reg_Phase[1]["ID/EX.A"] = self.regList[ins_String["ins_rs"]]["regValue"]
                self.reg_Phase[1]["ID/EX.B"] = self.regList[ins_String["ins_rt"]]["regValue"]
                self.reg_Phase[1]["ID/EX.IMM"] =	ins_String["ins_Opcode"][-4:].zfill(16)
                #get A, B and imm

        if not ins_String["if_Stall"]:
            self.reg_Phase[0].clear()
        print("ID")

        return "ID"

    def EX(self, ins_String):
        ALUOUT = {}
        type_Inst = {0 : self.LD_SD, 1 : self.LD_SD, 2 : self.DADDIU_XORI, 3 : self.DADDIU_XORI, 4 : self.DADDU_SLT, 5 : self.DADDU_SLT, 6 : self.BGTZC_J, 7 : self.BGTZC_J}
        ALUOUT = type_Inst[ins_String["ins_Num"]](ins_String)

        self.reg_Phase[2]["EX/MEM.IR"] = self.reg_Phase[1]["ID/EX.IR"]
        if ins_String["ins_Num"] != 7:
            self.reg_Phase[2]["EX/MEM.B"] = self.reg_Phase[1]["ID/EX.B"]
        self.reg_Phase[2]["EX/MEM.ALUOUTPUT"] = ALUOUT["ALUOUT"]
        self.reg_Phase[2]["EX/MEM.COND"] = ALUOUT["cond"]
        ins_String["cond"] = ALUOUT["cond"] 


    #    print(ins_String)
        self.reg_Phase[1].clear()

    #    if ins_String["ins_Num"] == 7 or ins_String["ins_Num"] == 6: #for debugging BGTZC/J
    #        pprint(self.reg_Phase[2])

        print("EX")

        return "EX"

    def MEM(self, ins_String):
        self.reg_Phase[3]["MEM/WB.IR"] = self.reg_Phase[2]["EX/MEM.IR"]
        self.reg_Phase[3]["MEM/WB.ALUOUTPUT"] = self.reg_Phase[2]["EX/MEM.ALUOUTPUT"]

        if ins_String["ins_type"] != 1:
            self.reg_Phase[3]["MEM/WB.RANGE"] = None
            self.reg_Phase[3]["MEM/WB.LMD"] = None

        else:
            #SD/LD stuff
            pass

        self.reg_Phase[2].clear()
        print("MEM")

        return "MEM"

    def WB(self, ins_String):
    #    pprint(ins_String)
        if ins_String["ins_type"] == 0:
            self.regList[ins_String["ins_rd"]]["in_use"] = False
            self.reg_Phase[4]["Rn"] = self.reg_Phase[3]["MEM/WB.ALUOUTPUT"]
            self.regList[ins_String["ins_rd"]]["regValue"] = self.reg_Phase[4]["Rn"]
        elif ins_String["ins_type"] == 2:
            self.regList[ins_String["ins_rt"]]["in_use"] = False
            self.reg_Phase[4]["Rn"] = self.reg_Phase[3]["MEM/WB.ALUOUTPUT"]
            self.regList[ins_String["ins_rt"]]["regValue"] = self.reg_Phase[4]["Rn"]
        elif ins_String["ins_type"] == 1:
            self.reg_Phase[4]["Rn"] = None
        else:
            self.regList[ins_String["ins_rt"]]["in_use"] = False
            self.reg_Phase[4]["Rn"] = None
            self.regList[ins_String["ins_rt"]]["regValue"] = self.reg_Phase[4]["Rn"]
        self.reg_Phase[3].clear()
        print("WB")

        return "WB"

    #TEST

    #EXTRA FUNCTIONS FOR BGTZC
    def find_address(self, code):
        """ This function gets the addresses in the code
            Populates   code_line,
                        code_line_splitted,
                        self.address_location,

        """
        self.clean_code = """"""
        print("in test_address")
        code_line = code.split("\n")
        print(code_line)

        code_line_splitted = []

        nCtr = 0
        while nCtr < len(code_line):
            code_line_splitted.append(code_line[nCtr].split(" "))
            nCtr_2 = 0
            while nCtr_2 < len(code_line_splitted[nCtr]):
                line_contents = code_line_splitted[nCtr]

                string = line_contents[nCtr_2]
                if string[-1:] == ':':
                    print("found an offset")
                    address_info = {}
                    address_info["line"] = nCtr
                    address_info["string"] = string[:-1]
                    self.address_location.append(address_info)
                    del(line_contents[nCtr_2])
                    nCtr_2 -=1
                else:
                    if (nCtr_2 == 0 or line_contents[0] == "BGTZC") and nCtr_2 != len(code_line_splitted[nCtr])-1: #only exception for BGTZC because it was made differently
                        self.clean_code += string + " "
                    else:
                        self.clean_code += string

                nCtr_2 += 1
            self.clean_code += "\n"

            nCtr += 1
        print(self.clean_code)
        # print(code_line_splitted)
        # print(self.address_location)
        print("returning clean code ...")
        return self.clean_code

    def get_line_address(self, offset):
        """ This function returns the offset of the label
            *should be executed only after the find_address function*
        """
        nCtr = 0
        while nCtr < len(self.address_location):
            if self.address_location[nCtr]["string"] == offset:
                return self.address_location[nCtr]["line"]
            nCtr += 1

        return 0

    #def run_UI():
    #    app = QtWidgets.QApplication(sys.argv)
    #    GUI = Window()
    #    GUI.show()
    #    app.exec()



    def start(self, dirty_code):

        #cleaning code.
        self.clean_code = self.find_address(dirty_code)

        ins_String = []
        input_Phase = True

        address_int = 0b0001000000000000

        address_hex = hex(address_int).split('x')[-1].zfill(4)

        #adjustment made.
        code_line = self.clean_code.split("\n")
        code_line = [x for x in code_line if x]
                
                
        nCtr = 0

        # OLD while input_Phase and int(address_hex, 16) < int("2000", 16):
        while nCtr < len(code_line):
            ins_Input = {}
            # OLD ins_Input["inst_String"] = input(address_hex + " ").upper()
            ins_Input["inst_String"] = code_line[nCtr]
            ins_Input["inst_add"] = address_hex
            address_int += 4
            address_hex = hex(address_int).split('x')[-1].zfill(4).upper()
            ins_Input["inst_Phase"] = 1
            ins_Input["if_Stall"] = False
            ins_Input["if_BR_J"] = False
            nCtr += 1
            if len(ins_Input["inst_String"]) != 0:
                ins_Input["ins_Num"] = self.ins_List.index(ins_Input["inst_String"].split(" ")[0])
                ins_String.append(ins_Input)
            else:
                input_Phase = False

        if_insError = False
        if_paramError = False
        count = 0

        while not if_insError and not if_paramError and count < len(ins_String):
            # Checks if Instruction is valid
            if ins_String[count]["inst_String"].split(" ")[0] in self.ins_List:
                type_Inst = {0 : self.LD_SD_REGEX, 1 : self.LD_SD_REGEX, 2 : self.DADDIU_XORI_REGEX, 3 : self.DADDIU_XORI_REGEX, 4 : self.DADDU_SLT_REGEX, 5 : self.DADDU_SLT_REGEX, 6 : self.BGTZC_REGEX, 7 : self.J_REGEX}
                # Checks if parameter is valid
                if_paramError = type_Inst[ins_String[count]["ins_Num"]](ins_String[count]["inst_String"])
                if if_paramError:
                    print("ERROR: Invalid Parameter @ Line", count + 1)
                else:
                    ins_Format = {}
                    type_Form = {0 : self.LD_SD_REFORMAT, 1 : self.LD_SD_REFORMAT, 2 : self.DADDIU_XORI_REFORMAT, 3 : self.DADDIU_XORI_REFORMAT, 4 : self.DADDU_SLT_REFORMAT, 5 : self.DADDU_SLT_REFORMAT, 6 : self.BGTZC_REFORMAT, 7 : self.J_REFORMAT}
                    typenum = self.ins_List.index(ins_String[count]["inst_String"].split(" ")[0])
                    if typenum == 6:
                        ins_Format = type_Form[self.ins_List.index(ins_String[count]["inst_String"].split(" ")[0])](ins_String[count]["inst_String"], count)
                    else:
                        ins_Format = type_Form[self.ins_List.index(ins_String[count]["inst_String"].split(" ")[0])](ins_String[count]["inst_String"])

                    ins_String[count]["ins_Opcode"] = ins_Format["Opcode"]
                    ins_String[count]["ins_rt"] = ins_Format["ins_rt"]

                    #---------------------INC---------------------------
                    if ins_Format["if_BCJ"]:
                        ins_String[count]["ins_type"] = 1
                        ins_String[count]["ins_imm"] = ins_Format["ins_imm"]
                        ins_String[count]["ins_rt"] = ins_Format["ins_rt"]
                        #---------------------INC---------------------------
                    elif ins_Format["if_Imm"]:
                        ins_String[count]["ins_imm"] = ins_Format["ins_imm"]
                        ins_String[count]["ins_rs"] = ins_Format["ins_rs"]
                        ins_String[count]["ins_type"] = 2
                    elif ins_Format["if_LSD"]:
                        ins_String[count]["ins_base"] = ins_Format["ins_base"]
                        ins_String[count]["ins_offset"] = ins_Format["ins_offset"]
                        ins_String[count]["ins_type"] = 3
                    else:
                        ins_String[count]["ins_rs"] = ins_Format["ins_rs"]
                        ins_String[count]["ins_rd"] = ins_Format["ins_rd"]
                        ins_String[count]["ins_type"] = 0


                    count += 1
            else:
                if_insError = True
                print("ERROR: Invalid Instruction @ Line", count + 1)

        done = count = max_Ins = 0
        phase_type = {1: self.IF, 2: self.ID, 3: self.EX, 4: self.MEM, 5: self.WB}
        if_Stall = False
        cycle_array=[]
        cycle_content={}
        while done != len(ins_String) and not if_insError and not if_paramError:
            print("-----------------Cycle ", count + 1, "-----------------")

            cycle_content={}

            inCount = done
            if_branch = False #--BGTZC/J--#
            if_jumped = False #--BGTZC/J--#
            maxCount = max_Ins + 1
            while inCount < max_Ins + 1:
                print("inst # ", inCount , max_Ins)

                phase = phase_type[ins_String[inCount]["inst_Phase"]](ins_String[inCount])

                print('current ',ins_String[inCount]["inst_String"])
    #            pprint(ins_String[inCount])

                #--BGTZC/J--#
                if ins_String[inCount]["if_BR_J"] and ins_String[inCount]["inst_Phase"] <= 4:


                    if ins_String[inCount]["inst_Phase"] < 4:
                        print("FLUSHING")
                        if_branch = True


                    if not ins_String[inCount]["if_Stall"]:
                        if inCount+1 < len(ins_String) and ins_String[inCount]["inst_Phase"] == 2:
                            print('current ',ins_String[inCount+1]["inst_String"])
                            cycle_content[inCount+1]= phase_type[1](ins_String[inCount+1])
                        if inCount+2 < len(ins_String)and ins_String[inCount]["inst_Phase"] == 3:
                            print('current ',ins_String[inCount+2]["inst_String"])
                            cycle_content[inCount+2]= phase_type[1](ins_String[inCount+2])
                        if inCount+3 < len(ins_String)and ins_String[inCount]["inst_Phase"] == 4:
                            print('current ',ins_String[inCount+3]["inst_String"])
                            cycle_content[inCount+3]= phase_type[1](ins_String[inCount+3])
                #--BGTZC/J--#


                if ins_String[inCount]["inst_Phase"] == 5:
                    done += 1
                    #--BGTZC/J--#
                    if ins_String[inCount]["if_BR_J"] and ins_String[inCount]["cond"]:
                        cycle_content[inCount]= phase #Store before jumping lines
                        if_jumped = True
                        sanitized = ins_String[inCount]["inst_String"].split(" ")
                        done = self.get_line_address(sanitized[len(sanitized)-1])
                        max_Ins = inCount = done 
                        inCount -=1
                    #--BGTZC/J--#

                if ins_String[inCount]["if_Stall"]:
                    if_Stall = True
                    print("STALLED")
                    cycle_content[inCount]= "*"
                    break

                else:
                    if not if_jumped:
                        cycle_content[inCount]= phase
                    if_jumped = False
                    if_Stall = False
                    ins_String[inCount]["inst_Phase"] += 1


                inCount+= 1


            cycle_array.append(cycle_content)
    #        pprint(cycle_array)
    #        a = input()
            count += 1
            #if br/j max = target offset; br/j = False
            if max_Ins + 1 < len(ins_String) and not if_Stall and not if_branch:
                #and not if_cond
                #if cond max = target offset
                #if_cond == true
                #if if_cond max += 1
                max_Ins += 1
            # else:
            # 	max = target offset $ one occurence only not looped
            # 	max += 1

            print("max: ", max_Ins)
        pprint(cycle_array)
        pprint(code_line)
        Print_to_xlsx(cycle_array,code_line)

if __name__ == "__main__":
    a = MIPS()
    a.start(test_string)