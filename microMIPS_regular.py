import re
from pprint import pprint
from GUI_mips import *
from threading import Thread


ins_List = ["LD", "SD", "DADDIU", "XORI", "DADDU", "SLT", "BGTZC", "J"]
regList = []

reg_Phase = ({}, {}, {}, {}, {})

for regNum in range(0, 32):
    reg = {}
    reg["regValue"] = hex(0).split('x')[-1].zfill(16)
    reg["regNum"] = bin(regNum).split('b')[-1].zfill(5)
    reg["in_use"] = False
    regList.append(reg)


def DADDU_SLT_REGEX(expression):
    sanitized = expression.split(" ")
    del sanitized[0]
    sanitized = " ".join(sanitized)

    if re.match(r"^R([3][0-1]|[1-2][0-9]|[0-9]),(\sR|R)([3][0-1]|[1-2][0-9]|[0-9]),(\sR|R)([3][0-1]|[1-2][0-9]|[0-9])", sanitized):
        return False
    else:
        return True

def LD_SD_REGEX(expression):
    sanitized = expression.split(" ")
    del sanitized[0]
    sanitized = " ".join(sanitized)
    if re.match(r"^R([3][0-1]|[1-2][0-9]|[0-9]),(\s1|1)[0-9A-F]{3}[(]R([3][0-1]|[1-2][0-9]|[0-9])[)]", sanitized):
        return False
    else:
        return True

def DADDIU_XORI_REGEX(expression):
    sanitized = expression.split(" ")
    del sanitized[0]
    sanitized = " ".join(sanitized)

    if re.match(r"^R([3][0-1]|[1-2][0-9]|[0-9]),(\sR|R)([3][0-1]|[1-2][0-9]|[0-9]),(\s#|#)[0-9A-F]{4}", sanitized):
        return False
    else:
        return True

#---------------------ralph---------------------------
def BGTZC_REGEX(expression):
    sanitized = expression.split(" ")
    del sanitized[0]
#    print(sanitized[len(sanitized)-2]) e.g. R1,
    sanitized = " ".join(sanitized)

    if re.match(r"^R([3][0-1]|[1-2][0-9]|[0-9]), \w+$", sanitized):
        return False
    else:
        return True
    
def J_REGEX(expression):
    sanitized = expression.split(" ")
    del sanitized[0]
#    print(sanitized[len(sanitized)-2]) e.g. R1,
    sanitized = " ".join(sanitized)

    if re.match(r"^\w+$", sanitized):
        return False
    else:
        return True
#---------------------ralph---------------------------


def DADDU_SLT_REFORMAT(expression):
    ins_Op = {4 : 0b101101, 5 : 0b101010}
    bin_Opcode = []
    bin_Opcode.append(bin(0).split('b')[-1].zfill(6))

    sanitized = expression.split(",")
    sanitized.insert(1, sanitized[0][-2:])
    del sanitized[0]

    rd = int(sanitized[0][-1:])
    rs = int(sanitized[1][-1:])
    rt = int(sanitized[2][-1:])

    bin_Opcode.append(regList[rs]["regNum"])
    bin_Opcode.append(regList[rt]["regNum"])
    bin_Opcode.append(regList[rd]["regNum"])

    bin_Opcode.append(bin(0).split('b')[-1].zfill(5))
    bin_Opcode.append(bin(ins_Op[ins_List.index(expression.split(" ")[0])]).split('b')[-1].zfill(6))

    hex_Opcode = hex(int("".join(bin_Opcode), 2)).split('x')[-1].zfill(8).upper()
    print(expression)
    print("OPCODE: ", hex_Opcode, "\n")

    return {"ins_rs": rs, "ins_rt": rt, "ins_rd": rd, "Opcode": hex_Opcode, "if_BCJ": False, "if_Imm": False, "if_LSD": False}


def LD_SD_REFORMAT(expression):
    ins_Op = {0 : 0b110111, 1 : 0b111111}
    bin_Opcode = []
    bin_Opcode.append(bin(ins_Op[ins_List.index(expression.split(" ")[0])]).split('b')[-1].zfill(6))

    sanitized = expression.split(",")
    sanitized.insert(1, sanitized[0][-2:])
    del sanitized[0]

    base = int(sanitized[1].split('(')[-1][:2][1])
    rt = int(sanitized[0][-1:])
    offset = sanitized[1].split('(')[0][-4:]

    bin_Opcode.append(regList[base]["regNum"])
    bin_Opcode.append(regList[rt]["regNum"])

    for x in range(0, 4):
        bin_Opcode.append(bin(int(offset[x])).split('b')[-1].zfill(4))

    hex_Opcode = hex(int("".join(bin_Opcode), 2)).split('x')[-1].zfill(8).upper()
    print(expression)
    print("OPCODE: ", hex_Opcode, "\n")

    return {"ins_base": base, "ins_rt": rt, "ins_offset": offset, "Opcode": hex_Opcode, "if_BCJ": False, "if_Imm": False, "if_LSD": True}


def DADDIU_XORI_REFORMAT(expression):
    ins_Op = {2 : 0b011001, 3 : 0b001110}
    bin_Opcode = []
    bin_Opcode.append(bin(ins_Op[ins_List.index(expression.split(" ")[0])]).split('b')[-1].zfill(6))

    sanitized = expression.split(",")
    sanitized.insert(1, sanitized[0][-2:])
    del sanitized[0]

    rt = int(sanitized[0][-1:])
    rs = int(sanitized[1][-1:])
    imm = sanitized[2][-4:]

    bin_Opcode.append(regList[rs]["regNum"])
    bin_Opcode.append(regList[rt]["regNum"])

    for x in range(0, 4):
        bin_Opcode.append(bin(int(imm[x])).split('b')[-1].zfill(4))

    hex_Opcode = hex(int("".join(bin_Opcode), 2)).split('x')[-1].zfill(8).upper()
    print(expression)
    print("OPCODE: ", hex_Opcode, "\n")

    return {"ins_rs": rs, "ins_rt": rt, "ins_imm": imm, "Opcode": hex_Opcode, "if_BCJ": False, "if_Imm": True, "if_LSD": False}

#---------------------INC---------------------------
def BGTZC_REFORMAT(expression, current_line):
    print("in BGTZC_REFORMAT")
    print(expression)
    ins_Op = {0: 0b010111, 1: 0b000010}
    bin_Opcode = []
    bin_Opcode.append(bin(ins_Op[0]).split('b')[-1].zfill(6))
    bin_Opcode.append(bin(0).split('b')[-1].zfill(5))

    sanitized = expression.split(" ")
    del sanitized[0]
    print(sanitized)

    rt = int(sanitized[0][:-1][-1:])

    bin_Opcode.append(regList[rt]["regNum"])

    # offset binary
    offset_line = get_line_address(sanitized[1])
    offset = abs(offset_line - current_line - 1)
    bin_Opcode.append(bin(offset).split('b')[-1].zfill(16))
    hex_Opcode = hex(int("".join(bin_Opcode), 2)).split('x')[-1].zfill(8).upper()

#    print(offset)
#    print(bin_Opcode)

    imm = hex_Opcode[-4:]
#    print("THIS IS IMM ", imm)

    print("OPCODE: ", hex_Opcode, "\n")

    return {"ins_rt": rt, "ins_imm": imm, "Opcode": hex_Opcode, "if_BCJ": True, "if_Imm": False, "if_LSD": False}

def J_REFORMAT(expression):
    print("in J_REFORMAT")
    print(expression)
    ins_Op ={0: 0b000010}
    bin_Opcode = []
    bin_Opcode.append(bin(ins_Op[0]).split('b')[-1].zfill(6))
    bin_Opcode.append(bin(0).split('b')[-1].zfill(5))
    bin_Opcode.append(bin(0).split('b')[-1].zfill(5))
    
    sanitized = expression.split(" ")
    del sanitized[0]
    
    offset_line = get_line_address(sanitized[0])
    bin_Opcode.append(bin(offset_line).split('b')[-1].zfill(16))
    hex_Opcode = hex(int("".join(bin_Opcode), 2)).split('x')[-1].zfill(8).upper()
    
    imm = hex_Opcode[-4:]
    
    print(bin_Opcode)
    print("OPCODE: ", hex_Opcode, "\n")
    
    
    rt = ""
    return {"ins_rt": rt, "ins_imm": imm, "Opcode": hex_Opcode, "if_BCJ": True, "if_Imm": False, "if_LSD": False}
    
    
#---------------------INC---------------------------

def LD_SD(instruction):
    # if instruction["ins_Num"] == 0:
    # 	#LD operation

    # else:
    # 	#SD operation
    pass

def DADDIU_XORI(instruction):
    if instruction["ins_Num"] == 2:
        #DADDIU operation
        output = int(regList[instruction["ins_rs"]]["regValue"], 16) + int(instruction["ins_imm"], 16)
    else:
        #XORI operation
        output = int(regList[instruction["ins_rs"]]["regValue"], 16) ^ int(instruction["ins_imm"], 16)

    output = hex(output).split('x')[-1].zfill(16)
    cond = 0
    return {"ALUOUT": output, "cond": cond}

def DADDU_SLT(instruction):
    if instruction["ins_Num"] == 4:
        #DADDU operation
        output = int(regList[instruction["ins_rs"]]["regValue"], 16) + int(regList[instruction["ins_rt"]]["regValue"], 16)
    else:
        #SLT operation
        if int(regList[instruction["ins_rs"]]["regValue"], 16) < int(regList[instruction["ins_rt"]]["regValue"], 16):
            output = int(regList[instruction["ins_rs"]]["regValue"], 16)
        else:
            output = 0
    output = hex(output).split('x')[-1].zfill(16)
    cond = 0
    return {"ALUOUT": output, "cond": cond}

def BGTZC_J(instruction):
#    pprint(reg_Phase)
    output = ""
    cond = 0
#    print(int(regList[instruction["ins_rt"]]["regValue"], 16))
    if instruction["ins_Num"] == 6:
        #BGTZC operation
        NPC = int(reg_Phase[1]["ID/EX.NPC"], 16)
        IMM = int(reg_Phase[1]["ID/EX.IMM"], 16)
#        print(NPC, " + ", IMM, " *4")
        output = NPC + IMM * 4
#        print("ALUOUTPUT = ", hex(output))

        if int(regList[instruction["ins_rt"]]["regValue"], 16) > 0:
            cond = 1
        else:
            cond = 0

    else:
        IMM = int(reg_Phase[1]["ID/EX.IMM"], 16)
        output = IMM * 4
        cond = 1
        
    output = hex(output).split('x')[-1].zfill(16)
#    print("ALUOUTPUT = ", output)
#    print("condition is ",cond)
    return {"ALUOUT": output, "cond": cond}


def IF(ins_String):
    #if br/j if_br_j = True
    reg_Phase[0]["IF/ID.IR"] = ins_String["ins_Opcode"]
    reg_Phase[0]["IF/ID.NPC"] = hex(int(ins_String["inst_add"], 16) + 4).split('x')[-1].zfill(4).upper()

    print("IF")

def ID(ins_String):
    #---------------------INC--------------------------- tweaked, maybe goods
    if ins_String["ins_type"] == 1: #BGTZC/J
#        print("this is the rt", ins_String["ins_rt"])
        if ins_String["ins_rt"] == "":
            print("THIS IS J")
            reg_Phase[1]["ID/EX.IR"] = reg_Phase[0]["IF/ID.IR"]
            reg_Phase[1]["ID/EX.NPC"] = reg_Phase[0]["IF/ID.NPC"]
            reg_Phase[1]["ID/EX.IMM"] = ins_String["ins_imm"].zfill(16)
        else:
            if regList[ins_String["ins_rt"]]["in_use"]:
                ins_String["if_Stall"] = True
            else:
                ins_String["if_Stall"] = False
                regList[ins_String["ins_rt"]]["in_use"] = True
                reg_Phase[1]["ID/EX.IR"] = reg_Phase[0]["IF/ID.IR"]
                reg_Phase[1]["ID/EX.NPC"] = reg_Phase[0]["IF/ID.NPC"]
                reg_Phase[1]["ID/EX.B"] = regList[ins_String["ins_rt"]]["regValue"]
                reg_Phase[1]["ID/EX.IMM"] = ins_String["ins_imm"].zfill(16)
#            pprint(reg_Phase[1])
            #get A, B and imm
        #---------------------INC---------------------------
    elif ins_String["ins_type"] == 2: #IMM
        if regList[ins_String["ins_rs"]]["in_use"]:
            ins_String["if_Stall"] = True
        else:
            ins_String["if_Stall"] = False
            regList[ins_String["ins_rt"]]["in_use"] = True
            reg_Phase[1]["ID/EX.IR"] = reg_Phase[0]["IF/ID.IR"]
            reg_Phase[1]["ID/EX.NPC"] = reg_Phase[0]["IF/ID.NPC"]
            reg_Phase[1]["ID/EX.A"] = regList[ins_String["ins_rs"]]["regValue"]
            reg_Phase[1]["ID/EX.B"] = regList[ins_String["ins_rt"]]["regValue"]
            reg_Phase[1]["ID/EX.IMM"] = ins_String["ins_imm"].zfill(16)
            #get A, B and imm
    elif ins_String["ins_type"] == 3: #SD/LD
        if regList[ins_String["ins_base"]]["in_use"]:
            ins_String["if_Stall"] = True
        else:
            ins_String["if_Stall"] = False
            regList[ins_String["ins_rt"]]["in_use"] = True
            reg_Phase[1]["ID/EX.IR"] = reg_Phase[0]["IF/ID.IR"]
            reg_Phase[1]["ID/EX.NPC"] = reg_Phase[0]["IF/ID.NPC"]
            reg_Phase[1]["ID/EX.A"] = regList[ins_String["ins_base"]]["regValue"]
            reg_Phase[1]["ID/EX.B"] = regList[ins_String["ins_rt"]]["regValue"]
            reg_Phase[1]["ID/EX.IMM"] =	ins_String["ins_offset"].zfill(16)
            #get A, B and imm
    else: #REGISTERS
        if regList[ins_String["ins_rt"]]["in_use"] or regList[ins_String["ins_rs"]]["in_use"]:
            ins_String["if_Stall"] = True
        else:
            ins_String["if_Stall"] = False
            regList[ins_String["ins_rd"]]["in_use"] = True
            reg_Phase[1]["ID/EX.IR"] = reg_Phase[0]["IF/ID.IR"]
            reg_Phase[1]["ID/EX.NPC"] = reg_Phase[0]["IF/ID.NPC"]
            reg_Phase[1]["ID/EX.A"] = regList[ins_String["ins_rs"]]["regValue"]
            reg_Phase[1]["ID/EX.B"] = regList[ins_String["ins_rt"]]["regValue"]
            reg_Phase[1]["ID/EX.IMM"] =	ins_String["ins_Opcode"][-4:].zfill(16)
            #get A, B and imm

    if not ins_String["if_Stall"]:
        reg_Phase[0].clear()
    print("ID")

def EX(ins_String):
    ALUOUT = {}
    type_Inst = {0 : LD_SD, 1 : LD_SD, 2 : DADDIU_XORI, 3 : DADDIU_XORI, 4 : DADDU_SLT, 5 : DADDU_SLT, 6 : BGTZC_J, 7 : BGTZC_J}
    ALUOUT = type_Inst[ins_String["ins_Num"]](ins_String)

    reg_Phase[2]["EX/MEM.IR"] = reg_Phase[1]["ID/EX.IR"]
    if ins_String["ins_Num"] != 7:
        reg_Phase[2]["EX/MEM.B"] = reg_Phase[1]["ID/EX.B"]
    reg_Phase[2]["EX/MEM.ALUOUTPUT"] = ALUOUT["ALUOUT"]
    reg_Phase[2]["EX/MEM.COND"] = ALUOUT["cond"]
    reg_Phase[1].clear()
    print("EX")

def MEM(ins_String):
    reg_Phase[3]["MEM/WB.IR"] = reg_Phase[2]["EX/MEM.IR"]
    reg_Phase[3]["MEM/WB.ALUOUTPUT"] = reg_Phase[2]["EX/MEM.ALUOUTPUT"]

    if ins_String["ins_type"] != 1:
        reg_Phase[3]["MEM/WB.RANGE"] = None
        reg_Phase[3]["MEM/WB.LMD"] = None

    else:
        #SD/LD stuff
        pass

    reg_Phase[2].clear()
    print("MEM")

def WB(ins_String):
#    pprint(ins_String)
    if ins_String["ins_type"] == 0:
        regList[ins_String["ins_rd"]]["in_use"] = False
        reg_Phase[4]["Rn"] = reg_Phase[3]["MEM/WB.ALUOUTPUT"]
        regList[ins_String["ins_rd"]]["regValue"] = reg_Phase[4]["Rn"]
    elif ins_String["ins_type"] == 2:
        regList[ins_String["ins_rt"]]["in_use"] = False
        reg_Phase[4]["Rn"] = reg_Phase[3]["MEM/WB.ALUOUTPUT"]
        regList[ins_String["ins_rt"]]["regValue"] = reg_Phase[4]["Rn"]
    elif ins_String["ins_type"] == 1:
        reg_Phase[4]["Rn"] = None
    else:
        regList[ins_String["ins_rt"]]["in_use"] = False
        reg_Phase[4]["Rn"] = None
        regList[ins_String["ins_rt"]]["regValue"] = reg_Phase[4]["Rn"]
    reg_Phase[3].clear()
    print("WB")

#TEST
test_string = """DADDIU R1, R0, #1000
DADDIU R2, R0, #0000
DADDU R3, R1, R2
J L1
DADDU R3, R1, R1
DADDIU R3, R0, #0000
XORI R1, R2, #1000
L1: DADDIU R3, R0, #6969
"""

address_location = []
clean_code = ""
#EXTRA FUNCTIONS FOR BGTZC
def find_address(code):
    """ This function gets the addresses in the code
        Populates   code_line,
                    code_line_splitted,
                    address_location,

    """
    clean_code = """"""
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
                address_location.append(address_info)
                del(line_contents[nCtr_2])
                nCtr_2 -=1
            else:
                if (nCtr_2 == 0 or line_contents[0] == "BGTZC") and nCtr_2 != len(code_line_splitted[nCtr])-1: #only exception for BGTZC because it was made differently
                    clean_code += string + " "
                else:
                    clean_code += string

            nCtr_2 += 1
        clean_code += "\n"

        nCtr += 1
    print(clean_code)
    # print(code_line_splitted)
    # print(address_location)
    print("returning clean code ...")
    return clean_code

def get_line_address(offset):
    """ This function returns the offset of the label
        *should be executed only after the find_address function*
    """
    nCtr = 0
    while nCtr < len(address_location):
        if address_location[nCtr]["string"] == offset:
            return address_location[nCtr]["line"]
        nCtr += 1

    return 0

#def run_UI():
#    app = QtWidgets.QApplication(sys.argv)
#    GUI = Window()
#    GUI.show()
#    app.exec()


if __name__ == '__main__':

    #cleaning code.
    clean_code = find_address(test_string)

    ins_String = []
    input_Phase = True

    address_int = 0b0001000000000000

    address_hex = hex(address_int).split('x')[-1].zfill(4)

    #adjustment made.
    code_line = clean_code.split("\n")
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
            ins_Input["ins_Num"] = ins_List.index(ins_Input["inst_String"].split(" ")[0])
            ins_String.append(ins_Input)
        else:
            input_Phase = False

    if_insError = False
    if_paramError = False
    count = 0

    while not if_insError and not if_paramError and count < len(ins_String):
        # Checks if Instruction is valid
        if ins_String[count]["inst_String"].split(" ")[0] in ins_List:
            type_Inst = {0 : LD_SD_REGEX, 1 : LD_SD_REGEX, 2 : DADDIU_XORI_REGEX, 3 : DADDIU_XORI_REGEX, 4 : DADDU_SLT_REGEX, 5 : DADDU_SLT_REGEX, 6 : BGTZC_REGEX, 7 : J_REGEX}
            # Checks if parameter is valid
            if_paramError = type_Inst[ins_String[count]["ins_Num"]](ins_String[count]["inst_String"])
            if if_paramError:
                print("ERROR: Invalid Parameter @ Line", count + 1)
            else:
                ins_Format = {}
                type_Form = {0 : LD_SD_REFORMAT, 1 : LD_SD_REFORMAT, 2 : DADDIU_XORI_REFORMAT, 3 : DADDIU_XORI_REFORMAT, 4 : DADDU_SLT_REFORMAT, 5 : DADDU_SLT_REFORMAT, 6 : BGTZC_REFORMAT, 7 : J_REFORMAT}
                typenum = ins_List.index(ins_String[count]["inst_String"].split(" ")[0])
                if typenum == 6:
                    ins_Format = type_Form[ins_List.index(ins_String[count]["inst_String"].split(" ")[0])](ins_String[count]["inst_String"], count)
                else:
                    ins_Format = type_Form[ins_List.index(ins_String[count]["inst_String"].split(" ")[0])](ins_String[count]["inst_String"])

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
    phase_type = {1: IF, 2: ID, 3: EX, 4: MEM, 5: WB}
    if_Stall = False
    while done != len(ins_String) and not if_insError and not if_paramError:
        print("-----------------Cycle ", count + 1, "-----------------")


        for inCount in range(done, max_Ins + 1):
            print("inst # ", inCount , max_Ins)

#            print('inst_Phase',ins_String[inCount]["inst_Phase"])
            phase_type[ins_String[inCount]["inst_Phase"]](ins_String[inCount])
            print(ins_String[inCount]["inst_String"])
            if ins_String[inCount]["inst_Phase"] == 5:
                done += 1


            #if branch
            #if_br = True

            if ins_String[inCount]["if_Stall"]:
                if_Stall = True
                print("STALLED")
                break

            else:
                if_Stall = False
                ins_String[inCount]["inst_Phase"] += 1


        # print(reg_Phase)
        # print(regList[0])
        # print(regList[1])
        # print(regList[2])
        # print(regList[3])
        # print(regList[4])
        # print(regList[5])


        a = input()
        count += 1
        #if br/j max = target offset; br/j = False
        if max_Ins + 1 < len(ins_String) and not if_Stall:
            #and not if_cond
            #if cond max = target offset
            #if_cond == true
            #if if_cond max += 1
            max_Ins += 1
        # else:
        # 	max = target offset $ one occurence only not looped
        # 	max += 1

        print("max: ", max_Ins)


#if COND == 1 
#done = get target offset
#