import re

class MIPS:
    def initialize(self):
        self.ins_List = ["LD", "SD", "DADDIU", "XORI", "DADDU", "SLT", "BGTZC", "J"]
        self.regList = []
        self.opcodes = []
        for regNum in range(0, 32):
            reg = {}
            reg["regValue"] = hex(0).split('x')[-1].zfill(8)
            reg["regNum"] = bin(regNum).split('b')[-1].zfill(5)
            reg["in_use"] = False
            self.regList.append(reg)


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

    def BGTZC_J_REGEX(self, expression):
        pass
        # sanitized = expression.split(" ")
        # del sanitized[0]
        # sanitized = " ".join(sanitized)

        # if re.match(r"^R([3][0-1]|[1-2][0-9]|[0-9]),(\sR|R)([3][0-1]|[1-2][0-9]|[0-9]),(\sR|R)([3][0-1]|[1-2][0-9]|[0-9])", sanitized):
        # 	return False
        # else:
        # 	return True

        # re.match(r"^R([3][0-1]|[1-2][0-9]|[0-9]),(\sR|R)([3][0-1]|[1-2][0-9]|[0-9]),(\sR|R)([3][0-1]|[1-2][0-9]|[0-9])", sanitized)
        # print(sanitized)

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
        print(expression)
        print("OPCODE: ", hex_Opcode, "\n")
        self.opcodes.append(hex_Opcode)
        # print({"ins_rs": rs, "ins_rt": rt, "ins_rd": rd, "Opcode": hex_Opcode, "if_BCJ": False, "if_Imm": False})

        # return {"ins_rs": rs, "ins_rt": rt, "ins_rd": rd, "Opcode": hex_Opcode, "if_BCJ": False, "if_Imm": False, "if_LSD": False}


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
        print(expression)
        print("OPCODE: ", hex_Opcode, "\n")
        self.opcodes.append(hex_Opcode)
        # return {"ins_base": base, "ins_rt": rt, "ins_offset": offset, "Opcode": hex_Opcode, "if_BCJ": False, "if_Imm": False, "if_LSD": True}


    def DADDIU_XORI_REFORMAT(self, expression):
        ins_Op = {2 : 0b011001, 3 : 0b001110}
        bin_Opcode = []
        bin_Opcode.append(bin(ins_Op[self.ins_List.index(expression.split(" ")[0])]).split('b')[-1].zfill(6))

        sanitized = expression.split(",")
        sanitized.insert(1, sanitized[0][-2:])
        del sanitized[0]

        rs = int(sanitized[0][-1:])
        rt = int(sanitized[1][-1:])
        imm = sanitized[2][-4:]

        bin_Opcode.append(self.regList[rs]["regNum"])
        bin_Opcode.append(self.regList[rt]["regNum"])

        for x in range(0, 4):
            bin_Opcode.append(bin(int(imm[x])).split('b')[-1].zfill(4))

        hex_Opcode = hex(int("".join(bin_Opcode), 2)).split('x')[-1].zfill(8).upper()
        print(expression)
        print("OPCODE: ", hex_Opcode, "\n")
        self.opcodes.append(hex_Opcode)
        # print({"ins_rs": rs, "ins_rt": rt, "ins_imm": imm, "Opcode": hex_Opcode, "if_BCJ": False, "if_Imm": True})
        # return {"ins_rs": rs, "ins_rt": rt, "ins_imm": imm, "Opcode": hex_Opcode, "if_BCJ": False, "if_Imm": True, "if_LSD": False}

    def BGTZC_J_REFORMAT(self, expression):
        pass
        # sanitized = expression.split(" ")
        # del sanitized[0]
        # sanitized = " ".join(sanitized)




    def start(self, ins_String):
        self.initialize()
        if_insError = False
        if_paramError = False   
        count = 0   
        while count < len(ins_String):# Checks if Instruction is valid
            if ins_String[count].split(" ")[0] in self.ins_List:
                type_Inst = {0 : self.LD_SD_REGEX, 
                             1 : self.LD_SD_REGEX, 
                             2 : self.DADDIU_XORI_REGEX, 
                             3 : self.DADDIU_XORI_REGEX, 
                             4 : self.DADDU_SLT_REGEX, 
                             5 : self.DADDU_SLT_REGEX, 
                             6 : self.BGTZC_J_REGEX, 
                             7 : self.BGTZC_J_REGEX}
                # Checks if parameter is valid
                if_paramError = type_Inst[self.ins_List.index(ins_String[count].split(" ")[0])](ins_String[count])
                if if_paramError:
                    print("ERROR: Invalid Parameter @ Line", count + 1)
                else:
                    type_Form = {0 : self.LD_SD_REFORMAT, 
                                 1 : self.LD_SD_REFORMAT, 
                                 2 : self.DADDIU_XORI_REFORMAT, 
                                 3 : self.DADDIU_XORI_REFORMAT, 
                                 4 : self.DADDU_SLT_REFORMAT, 
                                 5 : self.DADDU_SLT_REFORMAT, 
                                 6 : self.BGTZC_J_REFORMAT, 
                                 7 : self.BGTZC_J_REFORMAT}
                    type_Form[self.ins_List.index(ins_String[count].split(" ")[0])](ins_String[count])

                    # ins_String[count]["ins_Opcode"]
                    count += 1			
            else:
                if_insError = True
                print("ERROR: Invalid Instruction @ Line", count + 1)
            
