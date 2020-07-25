"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.register = [0] * 8
        self.pc = 0
        self.sp = 7
        self.halt = False
        self.fl = 0b00000000

        self.LDI = 0b10000010
        self.PRN = 0b01000111
        self.HLT = 0b00000001
        self.MUL = 0b10100010
        self.ADD = 0b10100000
        self.POP = 0b01000110
        self.PUSH = 0b01000101

        self.CMP = 0b10100111
        self.JEQ = 0b01010101
        self.JNE = 0b01010110
        self.JMP = 0b01010100
        
    def push(self):
        self.register[self.sp] -= 1

        address = self.ram[self.pc + 1]
        value = self.register[address]

        top_loc = self.register[self.sp]
        self.ram[top_loc] = value
        self.pc += 2

    def pop(self):
        top_stack_val = self.register[self.sp]
        reg_addr = self.ram[self.pc + 1]
        self.register[reg_addr] = self.ram[top_stack_val]
        self.register[self.sp] += 1
        self.pc += 2
 
    def ram_read(self, mdr):
        return self.ram[mdr]

    def ram_write(self, value, address):
        self.ram[address] = value

    def load(self, file):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:
        with open(file, "r") as program_data:

            # remove whitespaces and comments and store in a new list
            program = []

            for line in program_data:

                code_and_comments = line.split("#")
                code = code_and_comments[0]
                code = code.strip()

                if len(code) > 0:
                    program.append(int(code, 2))
        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def hlt(self):
        self.pc += 1
        self.halt = True

    def mult(self):
        self.alu("MUL", 0, 1)
        self.pc += 3

    def add(self):
        self.alu("ADD", 0, 0)
        self.pc += 3

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.register[reg_a] += self.register[reg_b]
        elif op == "MUL":
            self.register[reg_a] *= self.register[reg_b]
        elif op == "CMP":
            if self.register[reg_a] > self.register[reg_b]:
                self.fl = 0b00000010
            elif self.register[reg_a] == self.register[reg_b]:
                self.fl = 0b00000001
            elif self.register[reg_a] < self.register[reg_b]:
                self.fl = 0b00000100
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.register[i], end='')

        print()
    def ldi(self):
        address = self.ram[self.pc + 1]
        value = self.ram[self.pc + 2]
        self.register[address] = value
        self.pc += 3

    def prn(self):
        address = self.ram[self.pc + 1]
        value = self.register[address]
        print(value)
        self.pc += 2

    def comp(self):
        self.alu("CMP", 0, 1)
        self.pc += 3

    def jeq(self):
        flag = str(self.fl)[-1]
        address = self.ram[self.pc + 1]
        if int(flag) == 1:
            self.pc = self.register[address]
        else:
            self.pc += 2

    def jne(self):
        flag = str(self.fl)[-1]
        address = self.ram[self.pc + 1]
        if int(flag) != 1:
            self.pc = self.register[address]
        else:
            self.pc += 2

    def jmp(self):
        address = self.ram[self.pc + 1]
        self.pc = self.register[address]

    def run(self):
        """Run the CPU."""
        # while self.halt is False:
        #     cmd = self.ram[self.pc]
        #     if cmd == 0b10000010:
        #         reg = self.ram[self.pc + 1]
        #         value = self.ram[self.pc + 2]
        #         self.register[reg] = value
        #         self.pc += 3
        #     elif cmd == 0b01000111:
        #         reg = self.ram[self.pc + 1]
        #         print(self.register[reg])
        #         self.pc += 2
        #     elif cmd == 0b00000001:
        #         self.halt = True
        #     elif cmd == 0b10100010:
        #         regA = self.ram[self.pc + 1]
        #         regB = self.ram[self.pc + 2]
        #         self.alu("MUL", regA, regB)
        #         self.pc += 3
        #     elif cmd == 0b01000110: #pop
        #         self.pop()
        #     elif cmd == 0b01000101: #push
        #         self.push()
        branch_table = {
            self.LDI : self.ldi,
            self.PRN : self.prn,
            self.MUL : self.mult,
            self.ADD : self.add,
            self.HLT : self.hlt,
            self.PUSH : self.push,
            self.POP : self.pop,
            self.CMP : self.comp,
            self.JEQ : self.jeq,
            self.JNE : self.jne,
            self.JMP : self.jmp
        }
        self.register[self.sp] = 0xF4
        
        self.halt = False
        while self.halt is False:
            ir = self.ram[self.pc]
            if ir in branch_table:
            
                branch_table[ir]()
            elif ir not in branch_table:
                print(f"Wrong instruction {ir} at address {self.pc}")
                sys.exit(1)

            