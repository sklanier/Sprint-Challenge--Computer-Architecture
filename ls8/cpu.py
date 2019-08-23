"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""

        # 8 GP Registers with counters and mem allocations
        self.GEN_REG = [0] * 8
        self.CPU_RUNNING = False
        self.RAM = [0] * 256
        self.PC = 0
        self.SP = 7
        self.E_FLAG = 0b00000000
        self.LT_FLAG = 0b00000000
        self.GT_FLAG = 0b00000000

    def RAM_READ(self, MAR):
        """Read the RAM. MAR = memory ADDRESS register"""
        try:
            return self.RAM[MAR] # return allocated array of Memory ADDRESS Register
        except IndexError:
            print("Error: index not within range")

    def RAM_WRITE(self, MDR, MAR):
        """write to the RAM. MDR = Memory Data Register"""
        try:
            self.RAM[MAR] = MDR
        except IndexError:
            print("Error: index not within range")

    def INCREMENT_PC(self, OP_CODE):
        PC_ADD = (OP_CODE >> 6) + 1
        self.PC += PC_ADD

    def load(self, FILE):
        """Load file into memory."""
        
        print("loading:", FILE)
        ADDRESS = 0
        try:
            with open(FILE) as f:
                for line in f:
                    num = line.split("#", 1)[0]

                    if num.strip() == '':
                        continue

                    self.RAM[ADDRESS] = int(num, 2)
                    ADDRESS += 1
        except FileNotFoundError:
            print(f"ERROR: {FILE} not found")
            sys.exit(2)
        except IsADirectoryError:
            print(f"ERROR: {FILE} is a directory")
            sys.exit(3)

    def ALU(self, OP, REG_A, REG_B):
        """ALU operations."""

        # ADD operation
        if OP == "ADD": 
            self.GEN_REG[REG_A] += self.GEN_REG[REG_B]

        # MUL operation
        elif OP == "MUL":
            self.GEN_REG[REG_A] = self.GEN_REG[REG_A] * self.GEN_REG[REG_B]

        # CMP operation
        elif OP == "CMP":
            if self.GEN_REG[REG_A] == self.GEN_REG[REG_B]:
                self.FLAG = 0b00000001
            elif self.GEN_REG[REG_A] != self.GEN_REG[REG_B]: 
                self.FLAG = 0b00000000 
            elif self.GEN_REG[REG_A] < self.GEN_REG[REG_B]:
                self.LT_FLAG = 0b00000001
                self.GT_FLAG = 0b00000000
            elif self.GEN_REG[REG_A] > self.GEN_REG[REG_B]:
                self.GT_FLAG = 0b00000001
                self.LT_FLAG = 0b00000000
        else:
            raise Exception("ALU operation not supported")

    def TRACE(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from RUN() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.PC,
            self.RAM_READ(self.PC),
            self.RAM_READ(self.PC + 1),
            self.RAM_READ(self.PC + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        self.CPU_RUNNING = True
        while self.CPU_RUNNING:
            OP_CODE = self.RAM_READ(self.PC)  

            # HLT instruction
            if OP_CODE == 0b00000001:
                self.CPU_RUNNING = False
                sys.exit(1)

            # LDI instruction
            elif OP_CODE == 0b10000010:
                ADDRESS = self.RAM_READ(self.PC + 1)
                data = self.RAM_READ(self.PC + 2)
                self.GEN_REG[ADDRESS] = data
                self.INCREMENT_PC(OP_CODE)

            # PRN instruction
            elif OP_CODE == 0b01000111:
                ADDRESS_A = self.RAM_READ(self.PC + 1)
                print(self.GEN_REG[ADDRESS_A])
                self.INCREMENT_PC(OP_CODE)
                pass
            
            # CMP instruction
            elif OP_CODE == 0b10100111:
                ADDRESS_A = self.RAM_READ(self.PC + 1)
                ADDRESS_B = self.RAM_READ(self.PC + 2)
                self.ALU('CMP', ADDRESS_A, ADDRESS_B)
                self.INCREMENT_PC(OP_CODE)

            # ADD instruction
            elif OP_CODE == 0b10100000:
                ADDRESS_A = self.RAM_READ(self.PC + 1)
                ADDRESS_B = self.RAM_READ(self.PC + 2)
                self.ALU('ADD', ADDRESS_A, ADDRESS_B)
                self.INCREMENT_PC(OP_CODE)

            # MUL instruction
            elif OP_CODE == 0b10100010:
                ADDRESS_A = self.RAM_READ(self.PC + 1)
                ADDRESS_B = self.RAM_READ(self.PC + 2)
                self.ALU('MUL', ADDRESS_A, ADDRESS_B)
                self.INCREMENT_PC(OP_CODE)

            # JMP instruction
            elif OP_CODE == 0b01010100:
                REG = self.RAM_READ(self.PC + 1)
                self.PC = self.GEN_REG[REG]

            # JEQ instruction
            elif OP_CODE == 0b01010101:
                REG = self.RAM_READ(self.PC + 1)
                if self.FLAG == 0b00000001:
                    self.PC = self.GEN_REG[REG]
                else:
                    self.INCREMENT_PC(OP_CODE)

            # JNE instruction
            elif OP_CODE == 0b01010110:
                REG = self.RAM_READ(self.PC + 1)
                if self.FLAG != 0b00000001:
                    self.PC = self.GEN_REG[REG]
                else:
                    self.INCREMENT_PC(OP_CODE)

            # PUSH instruction
            elif OP_CODE == 0b01000101:
                REG = self.RAM_READ(self.PC + 1)
                VALUE = self.GEN_REG[REG]
                self.GEN_REG[self.SP] -= 1
                self.RAM[self.GEN_REG[self.SP]] = VALUE
                self.INCREMENT_PC(OP_CODE)

            # POP instruction
            elif OP_CODE == 0b01000110:
                REG = self.RAM_READ(self.PC + 1)
                VALUE = self.RAM[self.GEN_REG[self.SP]]
                self.GEN_REG[REG] = VALUE
                self.GEN_REG[self.SP] += 1
                self.INCREMENT_PC(OP_CODE)

            # CALL instruction
            elif OP_CODE == 0b01010000:
                self.GEN_REG[self.SP] -= 1
                self.RAM[self.GEN_REG[self.SP]] = self.PC + 2
                ADDRESS_of_subroutine = self.RAM[self.PC + 1]
                self.PC = self.GEN_REG[ADDRESS_of_subroutine]

            # RET instruction
            elif OP_CODE == 0b00010001:
                self.PC = self.RAM[self.GEN_REG[self.SP]]
                self.GEN_REG[self.SP] += 1
            else:
                print('CPU instruction not supported')