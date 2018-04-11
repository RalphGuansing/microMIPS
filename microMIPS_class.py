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
        
        #-----KIEF-----
        self.memList= []
        self.address_mem = 0b0000000000000000
        self.address_mem_hex = hex(self.address_mem).split('x')[-1].zfill(4)

        #Memory	
        while int(self.address_mem_hex, 16) < int("1000" , 16):
            self.mem = {}
            self.mem["memValue"] = hex(0).split('x')[-1].zfill(2)
            self.mem["memAddress"] = self.address_mem_hex
            self.address_mem += 1
            self.address_mem_hex = hex(self.address_mem).split('x')[-1].zfill(4)
            self.memList.append(self.mem)
        
        #-----KIEF-----
        

        for regNum in range(0, 32):
            reg = {}
            reg["regValue"] = hex(0).split('x')[-1].zfill(16)
            reg["regNum"] = bin(regNum).split('b')[-1].zfill(5)
            reg["in_use"] = False
            self.regList.append(reg)
        
        self.address_location = []
        self.clean_code = ""
        self.loops = 0
        
    def DADDU_SLT_REGEX(self, expression):
        sanitized = expression.split(" ")
        del sanitized[0]
        sanitized = " ".join(sanitized)

        if re.match(r"^R([3][0-1]|[1-2][0-9]|[0-9]),(\sR|R)([3][0-1]|[1-2][0-9]|[0-9]),(\sR|R)([3][0-1]|[1-2][0-9]|[0-9])$", sanitized):
            return False
        else:
            return True

    def LD_SD_REGEX(self, expression):
        sanitized = expression.split(" ")
        del sanitized[0]
        sanitized = " ".join(sanitized)
#        if re.match(r"^R([3][0-1]|[1-2][0-9]|[0-9]),(\s1|1)[0-9A-F]{3}[(]R([3][0-1]|[1-2][0-9]|[0-9])[)]", sanitized): OLD
        if re.match(r"^R([3][0-1]|[1-2][0-9]|[0-9]),(\s0|0)[0-9A-Fa-f]{3}[(]R([3][0-1]|[1-2][0-9]|[0-9])[)]$", sanitized):
            return False
        else:
            return True

    def DADDIU_XORI_REGEX(self, expression):
        sanitized = expression.split(" ")
        del sanitized[0]
        sanitized = " ".join(sanitized)

        if re.match(r"^R([3][0-1]|[1-2][0-9]|[0-9]),(\sR|R)([3][0-1]|[1-2][0-9]|[0-9]),(\s#|#)[0-9A-F]{4}$", sanitized):
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
            sanitized = sanitized.split(" ")
            if sanitized[0][-2:][:-1] == "0" or self.get_line_address(sanitized[1]) == 0:
                return True
            else:
                return False
        else:
            return True

    def J_REGEX(self, expression):
        sanitized = expression.split(" ")
        del sanitized[0]
    #    print(sanitized[len(sanitized)-2]) e.g. R1,
        sanitized = " ".join(sanitized)

        if re.match(r"^\w+$", sanitized):
            if self.get_line_address(sanitized) == 0:
                return True
            else:
                return False
        else:
            return True
    #---------------------ralph---------------------------


    def DADDU_SLT_REFORMAT(self, expression):
        ins_Op = {4 : 0b101101, 5 : 0b101010}
        bin_Opcode = []
        bin_Opcode.append(bin(0).split('b')[-1].zfill(6))
        
        sanitized = expression.split(",")
        sanitized_array = sanitized[0].split(" ")
        del sanitized_array[0]
        sanitized[0] = sanitized_array[0]
#        print("sanitized = ", sanitized)
        
        rd = int(sanitized[0][1:])
        rs = int(sanitized[1][1:])
        rt = int(sanitized[2][1:])
#        print("rd = ",rd,"rs = ",rs,"rt = ",rt)
        
        
        bin_Opcode.append(self.regList[rs]["regNum"])
        bin_Opcode.append(self.regList[rt]["regNum"])
        bin_Opcode.append(self.regList[rd]["regNum"])

        bin_Opcode.append(bin(0).split('b')[-1].zfill(5))
        bin_Opcode.append(bin(ins_Op[self.ins_List.index(expression.split(" ")[0])]).split('b')[-1].zfill(6))

        hex_Opcode = hex(int("".join(bin_Opcode), 2)).split('x')[-1].zfill(8).upper()
        print(expression)
        print("OPCODE: ", hex_Opcode, "\n")

        return {"ins_rs": rs, "ins_rt": rt, "ins_rd": rd, "Opcode": hex_Opcode, "if_BCJ": False, "if_Imm": False, "if_LSD": False}


    def LD_SD_REFORMAT(self, expression):
        ins_Op = {0 : 0b110111, 1 : 0b111111}
        bin_Opcode = []
        bin_Opcode.append(bin(ins_Op[self.ins_List.index(expression.split(" ")[0])]).split('b')[-1].zfill(6))

        sanitized = expression.split(",")
        sanitized_array = sanitized[0].split(" ")
        del sanitized_array[0]
        sanitized[0] = sanitized_array[0]
        
        print("IN LD")
        print(sanitized)
        
        base = int(sanitized[1].split('(')[1][1:-1])
        rt = int(sanitized[0][1:])
        offset = sanitized[1].split('(')[0][-4:]
        print("base = ",base, "\nrt = ",rt, "\noffset = ",offset )
        
        
        bin_Opcode.append(self.regList[base]["regNum"])
        bin_Opcode.append(self.regList[rt]["regNum"])

        for x in range(0, 4):
#            bin_Opcode.append(bin(int(offset[x])).split('b')[-1].zfill(4)) old
            bin_Opcode.append(bin(int(offset[x], 16)).split('b')[-1].zfill(4))

        hex_Opcode = hex(int("".join(bin_Opcode), 2)).split('x')[-1].zfill(8).upper()
        print(expression)
        print("OPCODE: ", hex_Opcode, "\n")

        return {"ins_base": base, "ins_rt": rt, "ins_offset": offset, "Opcode": hex_Opcode, "if_BCJ": False, "if_Imm": False, "if_LSD": True}


    def DADDIU_XORI_REFORMAT(self, expression):
        ins_Op = {2 : 0b011001, 3 : 0b001110}
        bin_Opcode = []
        bin_Opcode.append(bin(ins_Op[self.ins_List.index(expression.split(" ")[0])]).split('b')[-1].zfill(6))

        sanitized = expression.split(",")
        sanitized_array = sanitized[0].split(" ")
        del sanitized_array[0]
        sanitized[0] = sanitized_array[0]
        
        
        print("sanitized = ", sanitized)
#        sanitized.insert(1, sanitized[0][-2:])
#        print("sanitized = ", sanitized)
        
        
        print("rt = ", sanitized[0][1:])
        print("rs = ", sanitized[1][1:])
        rt = int(sanitized[0][1:])
        rs = int(sanitized[1][1:])
        imm = sanitized[2][-4:]

        bin_Opcode.append(self.regList[rs]["regNum"])
        bin_Opcode.append(self.regList[rt]["regNum"])

        for x in range(0, 4):
            bin_Opcode.append(bin(int(imm[x], 16)).split('b')[-1].zfill(4))

        hex_Opcode = hex(int("".join(bin_Opcode), 2)).split('x')[-1].zfill(8).upper()
        print(expression)
        print("OPCODE: ", hex_Opcode, "\n")
#        a = input()
        return {"ins_rs": rs, "ins_rt": rt, "ins_imm": imm, "Opcode": hex_Opcode, "if_BCJ": False, "if_Imm": True, "if_LSD": False}

    def BGTZC_REFORMAT(self, expression, current_line):
        print("in BGTZC_REFORMAT")
        print(expression)
        ins_Op = {0: 0b010111, 1: 0b000010}
        bin_Opcode = []
        bin_Opcode.append(bin(ins_Op[0]).split('b')[-1].zfill(6))
        bin_Opcode.append(bin(0).split('b')[-1].zfill(5))

        sanitized = expression.split(" ")
        del sanitized[0]
#        print(sanitized)
#        print("sanitized in BGTZC ", sanitized[0], sanitized[0][1:-1])
        rt = int(sanitized[0][1:-1])
        
        bin_Opcode.append(self.regList[rt]["regNum"])

        # offset binary
        offset_line = self.get_line_address(sanitized[1])
        offset = offset_line - current_line - 1
        if offset >= 0:
            bin_Opcode.append(bin(offset).split('b')[-1].zfill(16))
        else:
            offset = ((offset * -1) - 1) ^ int("FFFF", 16)
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
        print(expression)
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

    def LD_SD(self, instruction):
        if instruction["ins_Num"] == 0:
            #LD operation
            output = int(self.regList[instruction["ins_base"]]["regValue"], 16) + int(instruction["ins_offset"], 16)
        else:
            #SD operation
            output = int(self.regList[instruction["ins_base"]]["regValue"], 16) + int(instruction["ins_offset"], 16)

        output = hex(output).split('x')[-1].zfill(4)
        cond = 0   

        return {"ALUOUT": output, "cond": cond}

        

    def DADDIU_XORI(self, instruction):
        if instruction["ins_Num"] == 2:
            #DADDIU operation
            output = self.Two_Compliment(self.regList[instruction["ins_rs"]]["regValue"]) + self.Two_Compliment(self.reg_Phase[1]["ID/EX.IMM"])

            if output < 0:
                print("output before", hex(output))
                output = ((output * -1) - 1) ^ int("FFFFFFFFFFFFFFFF", 16)
                print("output after", hex(output))
            # if len(hex(output)) > 16:
            # 	output = hex(output).split('x')[-1].upper()[1:]
            # else:
            # 	output = hex(output).split('x')[-1].upper()
            #changed
            # output = int(self.regList[instruction["ins_rs"]]["regValue"], 16) + int(instruction["ins_imm"], 16)
        else:
            #XORI operation
            
            output = int(self.regList[instruction["ins_rs"]]["regValue"], 16) ^ int(instruction["ins_imm"], 16)

        output = hex(output).split('x')[-1].zfill(16).upper()
        cond = 0
        return {"ALUOUT": output, "cond": cond}

    def DADDU_SLT(self, instruction):
        if instruction["ins_Num"] == 4:
            #DADDU operation
            # output = self.Two_Compliment(self.regList[instruction["ins_rs"]]["regValue"]) + self.Two_Compliment(self.regList[instruction["ins_rt"]]["regValue"])
            #changed
#            print("RS = ", int(self.regList[instruction["ins_rs"]]["regValue"], 16))
#            print("RT = ", int(self.regList[instruction["ins_rt"]]["regValue"], 16))
            
            output = int(self.regList[instruction["ins_rs"]]["regValue"], 16) + int(self.regList[instruction["ins_rt"]]["regValue"], 16)
        else:
            #SLT operation
            if int(self.regList[instruction["ins_rs"]]["regValue"], 16) < int(self.regList[instruction["ins_rt"]]["regValue"], 16):
                output = int(self.regList[instruction["ins_rs"]]["regValue"], 16)
            else:
                output = 0
        if len(hex(output)) > 16:
        	output = hex(output).split('x')[-1].zfill(16).upper()[1:]
        else:
        	output = hex(output).split('x')[-1].zfill(16).upper()
        cond = 0
        return {"ALUOUT": output, "cond": cond}
    
    
    def twos_comp(self, binVal):
#        for i in bin(IMM).split('b')[-1]:
        bin_String = ""
        for i in binVal:
            bin_String += str(1-int(i))
            
        bin_String = bin(int(bin_String, 2) + 1).split('b')[-1]
            
#        print(bin_String.zfill(64))
        return bin_String.zfill(64)
        
    def BGTZC_J(self, instruction):
    #    pprint(self.reg_Phase)
        output = ""
        cond = 0
        bin_String = ""
    #    print(int(self.regList[instruction["ins_rt"]]["regValue"], 16))
        if instruction["ins_Num"] == 6:
            #BGTZC operation
            
            
            NPC = int(self.reg_Phase[1]["ID/EX.NPC"], 16)
            
            sign_bit = self.Sign_Bit(self.reg_Phase[1]["ID/EX.IMM"][0])#changed

            if sign_bit == '1':#changed
                IMM = int(self.reg_Phase[1]["ID/EX.IMM"], 16)
                bin_IMM = bin(IMM).split('b')[-1]
                bin_Complement = self.twos_comp(bin_IMM)
                IMM = int(self.twos_comp(bin_IMM),2)*-1
            else:
                IMM = int(self.reg_Phase[1]["ID/EX.IMM"], 16)
                
            print("NPC = ",NPC)
            print("IMM = ",IMM)
            
            
    #        print(NPC, " + ", IMM, " *4")
            output = NPC + IMM * 4
    #        print("ALUOUTPUT = ", hex(output))

            if int(self.regList[instruction["ins_rt"]]["regValue"], 16) > 0:
                cond = 1
            else:
                cond = 0

        elif instruction["ins_Num"] == 7:
            IMM = int(self.reg_Phase[1]["ID/EX.IMM"], 16)
            output = (IMM * 4) + int("1000",16)
            cond = 1

        output = hex(output).split('x')[-1].zfill(16)
    #    print("ALUOUTPUT = ", output)
    #    print("condition is ",cond)
        return {"ALUOUT": output, "cond": cond}


    def IF(self, ins_String):

        self.reg_Phase[0]["IF/ID.IR"] = ins_String["ins_Opcode"]
        self.reg_Phase[0]["IF/ID.NPC"] = hex(int(ins_String["inst_add"], 16) + 4).split('x')[-1].zfill(16).upper()
        if ins_String["ins_type"] == 1:
            ins_String["if_BR_J"] = True

        print("IF")
        content = dict(self.reg_Phase[0]) 

        return {"phase":"IF", "content":content}

    def ID(self, ins_String):
        #---------------------INC--------------------------- tweaked, maybe goods
        if ins_String["ins_type"] == 1: #BGTZC/J
            if ins_String["ins_rt"] == "":
                print("THIS IS J")
                self.reg_Phase[1]["ID/EX.IR"] = self.reg_Phase[0]["IF/ID.IR"]
                self.reg_Phase[1]["ID/EX.NPC"] = self.reg_Phase[0]["IF/ID.NPC"]
                self.reg_Phase[1]["ID/EX.IMM"] = ins_String["ins_imm"].zfill(16)
                self.reg_Phase[1]["ID/EX.A"] = None
                self.reg_Phase[1]["ID/EX.B"] = None
            else:
                if self.regList[ins_String["ins_rt"]]["in_use"]:
                    ins_String["if_Stall"] = True
                else:
                    ins_String["if_Stall"] = False
                    #self.regList[self.ins_String["ins_rt"]]["in_use"] = True
                    self.reg_Phase[1]["ID/EX.IR"] = self.reg_Phase[0]["IF/ID.IR"]
                    self.reg_Phase[1]["ID/EX.NPC"] = self.reg_Phase[0]["IF/ID.NPC"]
                    self.reg_Phase[1]["ID/EX.B"] = self.regList[ins_String["ins_rt"]]["regValue"]
                    self.reg_Phase[1]["ID/EX.A"] = None
                    sign_bit = self.Sign_Bit(ins_String["ins_imm"][0])
                    if sign_bit == '1':#changed
                        self.reg_Phase[1]["ID/EX.IMM"] = 12*'F' + ins_String["ins_imm"]
                    else:
                        self.reg_Phase[1]["ID/EX.IMM"] = ins_String["ins_imm"].zfill(16)
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
                sign_bit = self.Sign_Bit(ins_String["ins_imm"][0])#changed

                if sign_bit == '1':#changed
                    self.reg_Phase[1]["ID/EX.IMM"] = 12*'F' + ins_String["ins_imm"]
                else:
                    self.reg_Phase[1]["ID/EX.IMM"] = ins_String["ins_imm"].zfill(16)
                #get A, B and imm
        elif ins_String["ins_type"] == 3: #SD/LD
            if self.regList[ins_String["ins_base"]]["in_use"]:
                ins_String["if_Stall"] = True
            else:
                ins_String["if_Stall"] = False
                if ins_String["ins_Num"] == 0: 
                    self.regList[ins_String["ins_rt"]]["in_use"] = True
                self.reg_Phase[1]["ID/EX.IR"] = self.reg_Phase[0]["IF/ID.IR"]
                self.reg_Phase[1]["ID/EX.NPC"] = self.reg_Phase[0]["IF/ID.NPC"]
                self.reg_Phase[1]["ID/EX.A"] = self.regList[ins_String["ins_base"]]["regValue"]
                self.reg_Phase[1]["ID/EX.B"] = self.regList[ins_String["ins_rt"]]["regValue"]
                sign_bit = self.Sign_Bit(ins_String["ins_offset"][0])#changed

                if sign_bit == '1':#changed
                    self.reg_Phase[1]["ID/EX.IMM"] = 12*'F' + ins_String["ins_offset"]
                else:
                    self.reg_Phase[1]["ID/EX.IMM"] = ins_String["ins_offset"].zfill(16)
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
                sign_bit = self.Sign_Bit(ins_String["ins_Opcode"][-4:][0])#changed

                if sign_bit == '1':#changed
                    self.reg_Phase[1]["ID/EX.IMM"] = 12*'F' + ins_String["ins_Opcode"][-4:]
                else:
                    self.reg_Phase[1]["ID/EX.IMM"] = ins_String["ins_Opcode"][-4:].zfill(16)
                #get A, B and imm

        if not ins_String["if_Stall"]:
            self.reg_Phase[0].clear()
        print("ID")
        content = dict(self.reg_Phase[1])
        return {"phase":"ID", "content":content}

    def EX(self, ins_String):
        ALUOUT = {}
        type_Inst = {0 : self.LD_SD, 1 : self.LD_SD, 2 : self.DADDIU_XORI, 3 : self.DADDIU_XORI, 4 : self.DADDU_SLT, 5 : self.DADDU_SLT, 6 : self.BGTZC_J, 7 : self.BGTZC_J}
        ALUOUT = type_Inst[ins_String["ins_Num"]](ins_String)

        self.reg_Phase[2]["EX/MEM.IR"] = self.reg_Phase[1]["ID/EX.IR"]
        if ins_String["ins_Num"] != 7:
            self.reg_Phase[2]["EX/MEM.B"] = self.reg_Phase[1]["ID/EX.B"]
        else:
            self.reg_Phase[2]["EX/MEM.B"] = None
        self.reg_Phase[2]["EX/MEM.ALUOUTPUT"] = ALUOUT["ALUOUT"]
        self.reg_Phase[2]["EX/MEM.COND"] = ALUOUT["cond"]
        ins_String["cond"] = ALUOUT["cond"] 

        self.reg_Phase[1].clear()

        print("EX")
        content = dict(self.reg_Phase[2])
        return {"phase":"EX", "content":content}

    def MEM(self, ins_String):
        self.reg_Phase[3]["MEM/WB.IR"] = self.reg_Phase[2]["EX/MEM.IR"]
        self.reg_Phase[3]["MEM/WB.ALUOUTPUT"] = self.reg_Phase[2]["EX/MEM.ALUOUTPUT"]

#        if ins_String["ins_type"] != 1:
        self.reg_Phase[3]["MEM/WB.LMD"] = ""
        self.reg_Phase[3]["MEM/WB.B"] = self.reg_Phase[2]["EX/MEM.B"]
        if ins_String["ins_type"] != 3:
            self.reg_Phase[3]["MEM/WB.RANGE"] = None
            self.reg_Phase[3]["MEM/WB.LMD"] = None

        else:
            if ins_String["ins_Num"] == 0:
                #LD operation

                mem = self.reg_Phase[3]["MEM/WB.ALUOUTPUT"]
                print(mem)

                for i in range (len(self.memList)):
                    if(self.memList[i]["memAddress"] == mem):

                        byte1= self.memList[i]["memValue"]
#                        print(self.memList[i]["memValue"],self.memList[i]["memAddress"])

                        byte2= self.memList[i+1]["memValue"]
#                        print(self.memList[i+1]["memValue"],self.memList[i+1]["memAddress"])

                        byte3= self.memList[i+2]["memValue"]
#                        print(self.memList[i+2]["memValue"],self.memList[i+2]["memAddress"])

                        byte4= self.memList[i+3]["memValue"]
#                        print(self.memList[i+3]["memValue"],self.memList[i+3]["memAddress"])

                        byte5= self.memList[i+4]["memValue"]
#                        print(self.memList[i+4]["memValue"],self.memList[i+4]["memAddress"])

                        byte6= self.memList[i+5]["memValue"]
#                        print(self.memList[i+5]["memValue"],self.memList[i+5]["memAddress"])

                        byte7= self.memList[i+6]["memValue"]
#                        print(self.memList[i+6]["memValue"],self.memList[i+6]["memAddress"])

                        byte8= self.memList[i+7]["memValue"]
#                        print(self.memList[i+7]["memValue"],self.memList[i+7]["memAddress"])

                self.reg_Phase[3]["MEM/WB.LMD"] = "".join((byte8,byte7,byte6,byte5,byte4,byte3,byte2,byte1))
                self.reg_Phase[3]["MEM/WB.RANGE"] = None
#                print(reg_Phase[3]["MEM/WB.LMD"])
            
            else:
                #SD operation

                reg= str(self.reg_Phase[3]["MEM/WB.B"])
                print(reg)
                mem = self.reg_Phase[3]["MEM/WB.ALUOUTPUT"]
                print(mem)

                byte1 = reg[14:16]
                print(byte1)
                byte2 = reg[12:14]
                print(byte2)
                byte3 = reg[10:12]
                print(byte3)
                byte4 = reg[8:10]
                print(byte3)
                byte5 = reg[6:8]
                print(byte4)
                byte6 = reg[4:6]
                print(byte5)
                byte7 = reg[2:4]
                print(byte6)
                byte8 = reg[0:2]
                print(byte7)

                for i in range (len(self.memList)):
                    if(self.memList[i]["memAddress"] == mem):
                        self.memList[i]["memValue"]=byte1
                        self.memList[i+1]["memValue"]=byte2
                        self.memList[i+2]["memValue"]=byte3
                        self.memList[i+3]["memValue"]=byte4
                        self.memList[i+4]["memValue"]=byte5
                        self.memList[i+5]["memValue"]=byte6
                        self.memList[i+6]["memValue"]=byte7
                        self.memList[i+7]["memValue"]=byte8

#                        print(self.memList[i]["memValue"],self.memList[i]["memAddress"])
#                        print(self.memList[i+1]["memValue"],self.memList[i+1]["memAddress"])
#                        print(self.memList[i+2]["memValue"],self.memList[i+2]["memAddress"])
#                        print(self.memList[i+3]["memValue"],self.memList[i+3]["memAddress"])
#                        print(self.memList[i+4]["memValue"],self.memList[i+4]["memAddress"])
#                        print(self.memList[i+5]["memValue"],self.memList[i+5]["memAddress"])
#                        print(self.memList[i+6]["memValue"],self.memList[i+6]["memAddress"])
#                        print(self.memList[i+7]["memValue"],self.memList[i+7]["memAddress"])
                
                self.reg_Phase[3]["MEM/WB.LMD"] = "".join((byte8,byte7,byte6,byte5,byte4,byte3,byte2,byte1))
                
                
                
                
                self.reg_Phase[3]["MEM/WB.RANGE"] = mem.upper() + " - " + str(hex(int(mem, 16)+7).split('x')[-1].zfill(4).upper())
                
        self.reg_Phase[2].clear()
        print("MEM")
        content = dict(self.reg_Phase[3])
        return {"phase":"MEM", "content":content}

    def WB(self, ins_String):
        
        if ins_String["ins_type"] == 0:
            # self.regList[ins_String["ins_rd"]]["in_use"] = False
            self.reg_Phase[4]["Rn"] = self.reg_Phase[3]["MEM/WB.ALUOUTPUT"]
            self.regList[ins_String["ins_rd"]]["regValue"] = self.reg_Phase[4]["Rn"]
            self.reg_Phase[4]["Register affected"] = "R"+str(ins_String["ins_rd"])
        elif ins_String["ins_type"] == 2:
            # self.regList[ins_String["ins_rt"]]["in_use"] = False
            self.reg_Phase[4]["Rn"] = self.reg_Phase[3]["MEM/WB.ALUOUTPUT"]
            self.regList[ins_String["ins_rt"]]["regValue"] = self.reg_Phase[4]["Rn"]
            self.reg_Phase[4]["Register affected"] = "R"+str(ins_String["ins_rt"])
            print("register ", ins_String["ins_rt"])
        elif ins_String["ins_type"] == 1:
            self.reg_Phase[4]["Rn"] = None
            self.reg_Phase[4]["Register affected"] = None
        else:
            if ins_String["ins_Num"] == 0:
                # self.regList[ins_String["ins_rt"]]["in_use"] = False
                self.reg_Phase[4]["Rn"] = self.reg_Phase[3]["MEM/WB.LMD"]
                self.reg_Phase[4]["Register affected"] = "R"+str(ins_String["ins_rt"])
                self.regList[ins_String["ins_rt"]]["regValue"] = self.reg_Phase[4]["Rn"]
            else:
                self.reg_Phase[4]["Rn"] = None
                self.reg_Phase[4]["Register affected"] = None
            
        self.reg_Phase[3].clear()
        print("WB")
        
        content = dict(self.reg_Phase[4])
        return {"phase":"WB", "content":content}

    def BUFFER(self,ins_String):
        if ins_String["ins_type"] == 0:
            self.regList[ins_String["ins_rd"]]["in_use"] = False

        elif ins_String["ins_type"] == 2:
            self.regList[ins_String["ins_rt"]]["in_use"] = False

        else:
            if ins_String["ins_rt"] != "": 
                self.regList[ins_String["ins_rt"]]["in_use"] = False
        content = ""
        return {"phase":"","content":content}

    def Sign_Bit(self, hex_String):#changed
#        print("this is the hex_String ", hex_String)
        sBit = bin(int(hex_String, 16)).split('b')[-1].zfill(4)[0]
#        print("This is SBit ",sBit)
        return sBit
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
        
    def Two_Compliment(self, hex_value):#changed
    	mask = "FFFFFFFFFFFFFFFF"
    	sBit = self.Sign_Bit(hex_value[0])

    	if sBit == '1':
    		value = int(mask, 16) ^ int(hex_value, 16)
    		return -1 * (value + 1)
    	else:
    		return int(hex_value, 16)


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


    def start_opcode(self, dirty_code):
        self.if_Error = False
        self.Error_Line = 0
        self.opcode = []
        
        #cleaning code.
        self.clean_code = self.find_address(dirty_code)

        self.ins_String = []
        self.input_Phase = True

        self.address_int = 0b0001000000000000

        self.address_hex = hex(self.address_int).split('x')[-1].zfill(4)

        #adjustment made.
        code_line = self.clean_code.split("\n")
        code_line = [x for x in code_line if x]
        self.code_line = code_line
                
                
        nCtr = 0
        print("in initialize")
        # OLD while self.input_Phase and int(self.address_hex, 16) < int("2000", 16):
        while nCtr < len(code_line):
            ins_Input = {}
            # OLD ins_Input["inst_String"] = input(self.address_hex + " ").upper()
            ins_Input["inst_String"] = code_line[nCtr].upper()
            ins_Input["inst_add"] = self.address_hex
            self.address_int += 4
            self.address_hex = hex(self.address_int).split('x')[-1].zfill(4).upper()
            ins_Input["inst_Phase"] = 1
            ins_Input["if_Stall"] = False
            ins_Input["if_BR_J"] = False
            nCtr += 1
            if len(ins_Input["inst_String"]) != 0:
                
                if ins_Input["inst_String"].split(" ")[0] in self.ins_List:
                    ins_Input["ins_Num"] = self.ins_List.index(ins_Input["inst_String"].split(" ")[0])
                    self.ins_String.append(ins_Input)
                else:
                    print("Instruction Error asdasd")
                    print("Instruction Does not exist")
#                    pprint()
                    
                    self.if_Error = True
                    self.Error_Line = nCtr 
                    break
                    
            else:
                self.input_Phase = False

        self.if_insError = False
        self.if_paramError = False
        count = 0
        
        if not self.if_Error:
        
            while not self.if_insError and not self.if_paramError and count < len(self.ins_String):
                # Checks if Instruction is valid
                if self.ins_String[count]["inst_String"].split(" ")[0] in self.ins_List:
                    type_Inst = {0 : self.LD_SD_REGEX, 1 : self.LD_SD_REGEX, 2 : self.DADDIU_XORI_REGEX, 3 : self.DADDIU_XORI_REGEX, 4 : self.DADDU_SLT_REGEX, 5 : self.DADDU_SLT_REGEX, 6 : self.BGTZC_REGEX, 7 : self.J_REGEX}
                    # Checks if parameter is valid
                    self.if_paramError = type_Inst[self.ins_String[count]["ins_Num"]](self.ins_String[count]["inst_String"])
                    if self.if_paramError:
                        print("ERROR: Invalid Parameter @ Line", count + 1)
                        self.Error_Line = count+1
                        break
                    else:
                        ins_Format = {}
                        type_Form = {0 : self.LD_SD_REFORMAT, 1 : self.LD_SD_REFORMAT, 2 : self.DADDIU_XORI_REFORMAT, 3 : self.DADDIU_XORI_REFORMAT, 4 : self.DADDU_SLT_REFORMAT, 5 : self.DADDU_SLT_REFORMAT, 6 : self.BGTZC_REFORMAT, 7 : self.J_REFORMAT}
                        typenum = self.ins_List.index(self.ins_String[count]["inst_String"].split(" ")[0])
                        if typenum == 6:
                            ins_Format = type_Form[self.ins_List.index(self.ins_String[count]["inst_String"].split(" ")[0])](self.ins_String[count]["inst_String"], count)
                        else:
                            ins_Format = type_Form[self.ins_List.index(self.ins_String[count]["inst_String"].split(" ")[0])](self.ins_String[count]["inst_String"])

                        self.opcode.append(ins_Format["Opcode"])
                        self.ins_String[count]["ins_Opcode"] = ins_Format["Opcode"]
                        self.ins_String[count]["ins_rt"] = ins_Format["ins_rt"]

                        #---------------------INC---------------------------
                        if ins_Format["if_BCJ"]:
                            self.ins_String[count]["ins_type"] = 1
                            self.ins_String[count]["ins_imm"] = ins_Format["ins_imm"]
                            self.ins_String[count]["ins_rt"] = ins_Format["ins_rt"]
                            #---------------------INC---------------------------
                        elif ins_Format["if_Imm"]:
                            self.ins_String[count]["ins_imm"] = ins_Format["ins_imm"]
                            self.ins_String[count]["ins_rs"] = ins_Format["ins_rs"]
                            self.ins_String[count]["ins_type"] = 2
                        elif ins_Format["if_LSD"]:
                            self.ins_String[count]["ins_base"] = ins_Format["ins_base"]
                            self.ins_String[count]["ins_offset"] = ins_Format["ins_offset"]
                            self.ins_String[count]["ins_type"] = 3
                        else:
                            self.ins_String[count]["ins_rs"] = ins_Format["ins_rs"]
                            self.ins_String[count]["ins_rd"] = ins_Format["ins_rd"]
                            self.ins_String[count]["ins_type"] = 0


                        count += 1
                else:
                    self.if_insError = True
                    print("ERROR: Invalid Instruction @ Line", count + 1)
            self.init_cycle()
        
#        self.start_cycle(True)
    def init_cycle(self):
        self.if_updated_ui = False
        self.done = self.count = self.max_Ins = 0
        self.cycle_array=[]
        self.cycle_content_array=[]
        self.cycle_content={}
        self.is_Done_cycle = False
        self.loops = 0
    def Update_ui(self,main_layout,cycle_array):
        pipeline_map = main_layout.pipelineMap
#        pipeline_map.setColumnCount(1)
#        pprint(self.cycle_content_array[7][3])    
    
        if not self.if_updated_ui:
            pipeline_map.setRowCount(0)
            pipeline_map.setColumnCount(0)
            print("is updating")
            for nCtr, code in enumerate(self.code_line):
                pipeline_map.insertRow(pipeline_map.rowCount())
#                pipeline_map.setItem(nCtr, 0,QtWidgets.QTableWidgetItem(code))
                pipeline_map.setVerticalHeaderLabels(self.code_line)

        for nCtr, cycle in enumerate(cycle_array):
            if not self.is_Done_cycle:
                if(pipeline_map.columnCount() < len(cycle_array)):
                    pipeline_map.insertColumn(pipeline_map.columnCount())
            else:
                if(pipeline_map.columnCount() < len(cycle_array)-1):
                    pipeline_map.insertColumn(pipeline_map.columnCount())
                
#            pprint(cycle)
#            print("phase in Cycle", nCtr +1,)
            for nCtr_2 in range(0, len(self.code_line)):
                if nCtr_2 in cycle:
                    pipeline_map.setItem(nCtr_2,nCtr, QtWidgets.QTableWidgetItem(cycle[nCtr_2]))  
                    pipeline_map.selectColumn(pipeline_map.columnCount() -1) 
        
#        pprint(cycle_array)
        print("in update ui")
#        print(self.cycle_array)
        
        self.if_updated_ui = True


    
    def start_cycle(self, if_Single, main_layout):
#        pprint(self.ins_String)
#        print(string)
        
        phase_type = {1: self.IF, 2: self.ID, 3: self.EX, 4: self.MEM, 5: self.WB, 6: self.BUFFER}
        if_Stall = False
        
        
        highest = len(self.ins_String)
        
        
        if_Done_Single = False
        
        while self.done != highest and not self.if_insError and not self.if_paramError and not if_Done_Single:
            print("-----------------Cycle ", self.count + 1, "-----------------")

            self.cycle_content={}
            cycle_phase={}

            inCount = self.done
            if_branch = False #--BGTZC/J--#
            if_jumped = False #--BGTZC/J--#
            maxCount = self.max_Ins + 1
            while inCount < self.max_Ins + 1:
                print("inst # ", inCount , self.max_Ins)
#                pprint(self.ins_String[inCount])
                print("PHASE", self.ins_String[inCount]["inst_Phase"])
#                pprint(self.ins_String[inCount])
                phase = phase_type[self.ins_String[inCount]["inst_Phase"]](self.ins_String[inCount])
#                pprint(phase)
#                print('current ',self.ins_String[inCount]["inst_String"])
    #            pprint(self.ins_String[inCount])

                #--BGTZC/J--#
                if self.ins_String[inCount]["if_BR_J"] and self.ins_String[inCount]["inst_Phase"] <= 4:


                    if self.ins_String[inCount]["inst_Phase"] < 4:
                        print("FLUSHING")
                        if_branch = True


                    if not self.ins_String[inCount]["if_Stall"]:
                        if inCount+1 < len(self.ins_String) and self.ins_String[inCount]["inst_Phase"] == 2:
                            print("---I AM FLUSHING---")
                            print('current ',self.ins_String[inCount+1]["inst_String"])
                            flush_phase = phase_type[1](self.ins_String[inCount+1])
                            cycle_phase[inCount+1] = flush_phase["phase"]
                            self.cycle_content[inCount+1] = flush_phase["content"]
                        if inCount+2 < len(self.ins_String)and self.ins_String[inCount]["inst_Phase"] == 3:
                            print("---I AM FLUSHING---")
                            print('current ',self.ins_String[inCount+2]["inst_String"])
                            flush_phase = phase_type[1](self.ins_String[inCount+2])
                            cycle_phase[inCount+2] = flush_phase["phase"]
                            self.cycle_content[inCount+2] = flush_phase["content"]
                        if inCount+3 < len(self.ins_String)and self.ins_String[inCount]["inst_Phase"] == 4:
                            print("---I AM FLUSHING---")
                            print('current ',self.ins_String[inCount+3]["inst_String"])
                            flush_phase = phase_type[1](self.ins_String[inCount+3])
                            cycle_phase[inCount+3] = flush_phase["phase"]
                            self.cycle_content[inCount+3] = flush_phase["content"]
                #--BGTZC/J--#


                if self.ins_String[inCount]["inst_Phase"] == 6:
                    self.done += 1
                    self.ins_String[inCount]["inst_Phase"] = 0
                    #--BGTZC/J--#
#                    if self.ins_String[inCount]["if_BR_J"] and self.ins_String[inCount]["cond"]:
#                        cycle_phase[inCount]= phase["phase"] #Store before jumping lines
#                        self.cycle_content[inCount]= phase["content"] #Store before jumping lines
#                        if_jumped = True
#                        sanitized = self.ins_String[inCount]["inst_String"].split(" ")
#                        self.done = self.get_line_address(sanitized[len(sanitized)-1])-1
#                        self.max_Ins = inCount = self.done 
#                        inCount -=1
                if self.ins_String[inCount]["inst_Phase"] == 5: 
                    
                    if self.ins_String[inCount]["if_BR_J"] and self.loops == 20:
                        self.ins_String[inCount]["cond"] = 0
                        self.showMessage("Infinite Loop","An infinite loop was detected.","Branch condition is now set to 0",1)
                        
                    if self.ins_String[inCount]["if_BR_J"] and self.ins_String[inCount]["cond"]:
                            self.loops += 1
                            cycle_phase[inCount]= phase["phase"] #Store before jumping lines
                            self.cycle_content[inCount]= phase["content"] #Store before jumping lines
                            if_jumped = True
                            sanitized = self.ins_String[inCount]["inst_String"].split(" ")
                            
                            int_address = self.get_line_address(sanitized[len(sanitized)-1])
                            print("this is the address ", int_address)
                            self.ins_String[inCount]["inst_Phase"] = 1
                            
                            self.done = int_address
                            self.max_Ins = inCount = self.done 
                            inCount -=1
                            
                            
                        #--BGTZC/J--#

                if self.ins_String[inCount]["if_Stall"]:
                    if_Stall = True
                    print("STALLED")
                    cycle_phase[inCount]= "*"
                    break

                else:
                    if not if_jumped:
                        cycle_phase[inCount]= phase["phase"]
                        self.cycle_content[inCount]= phase["content"]
                    if_jumped = False
                    if_Stall = False
                    self.ins_String[inCount]["inst_Phase"] += 1

                
                inCount+= 1
            if if_Single:
                if_Done_Single = True


            self.cycle_array.append(cycle_phase)
            self.cycle_content_array.append(self.cycle_content)
            self.count += 1

            if self.max_Ins + 1 < len(self.ins_String) and not if_Stall and not if_branch:

                self.max_Ins += 1


            print("max: ", self.max_Ins)
            
        if self.done == highest:
            self.is_Done_cycle = True
        
        self.Update_ui(main_layout,self.cycle_array)
#        Print_to_xlsx(self.cycle_array,self.code_line)
#        pprint(len(self.cycle_array))
#        pprint(self.cycle_content_array)
#        pprint(code_line)
#        pprint(self.opcode)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
#    a = MIPS()
    GUI = Window()
    GUI.show()
    sys.exit(app.exec())
    
    
    
#    a = MIPS()
#    a.start(test_string)