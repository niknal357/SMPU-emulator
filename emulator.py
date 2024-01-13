DEBUG = False

class SMPU(object):
    def __init__(self):
        self.registers = {
            'a': 0,
            'b': 0,
            'q': 0,
            'h': 0,
            'l': 0,
            'p': 0,
            's': 255,
            'c': 0,
        }
        self.deviceManifold = None

    def get_value(self, register):
        if register in self.registers:
            return self.registers[register]
        else:
            if register == 'r':
                return self.get_value('h')*256 + self.get_value('l')
            elif register == 'z':
                return 1 if self.get_value('q') == 0 else 0

    def set_value(self, register, value):
        if register not in self.registers:
            raise Exception('Invalid register: ' + register)
        if register in ['a', 'b', 'q', 'h', 'l', 's']:
            self.registers[register] = value % 256
        elif register == 'p':
            self.registers[register] = value % 65536
        elif register == 'c':
            self.registers[register] = value % 2
        else:
            raise Exception('Invalid register: ' + register)

    def pull_at_program_counter(self):
        value = self.deviceManifold.read(self.get_value('p'))
        self.set_value('p', self.get_value('p') + 1)
        return value

    def mount(self, deviceManifold):
        self.deviceManifold = deviceManifold

    def clock(self):
        instruction = self.pull_at_program_counter()
        return self.execute(instruction)

    def execute(self, instruction):
        if instruction == 0: # HLT
            print('HALT') if DEBUG else None
            return False
        elif instruction == 1: # NOP
            print('NOP') if DEBUG else None
            return True
        elif instruction == 2: # ADR
            print('ADR') if DEBUG else None
            self.set_value('h', self.pull_at_program_counter())
            self.set_value('l', self.pull_at_program_counter())
            return True
        elif instruction == 3: # LDA
            print('LDA') if DEBUG else None
            self.set_value('a', self.deviceManifold.read(self.get_value('r')))
            return True
        elif instruction == 4: # STA
            print('STA') if DEBUG else None
            self.deviceManifold.write(self.get_value('r'), self.get_value('a'))
            return True
        elif instruction == 5: # LDB
            print('LDB') if DEBUG else None
            self.set_value('b', self.get_value('a'))
            return True
        elif instruction == 6: # SWP
            print('SWP') if DEBUG else None
            a = self.get_value('a')
            self.set_value('a', self.get_value('b'))
            self.set_value('b', a)
            return True
        elif instruction == 7: # LDH
            print('LDH') if DEBUG else None
            self.set_value('h', self.get_value('a'))
            return True
        elif instruction == 8: # LDL
            print('LDL') if DEBUG else None
            self.set_value('l', self.get_value('a'))
            return True
        elif instruction == 9: # STH
            print('STH') if DEBUG else None
            self.set_value('a', self.get_value('h'))
            return True
        elif instruction == 10: # STL
            print('STL') if DEBUG else None
            self.set_value('a', self.get_value('l'))
            return True
        elif instruction == 11: # LDQ
            print('LDQ') if DEBUG else None
            self.set_value('q', self.get_value('a'))
            return True
        elif instruction == 12: # STQ
            print('STQ') if DEBUG else None
            self.set_value('a', self.get_value('q'))
            return True
        elif instruction == 13: # CLA
            print('CLA') if DEBUG else None
            self.set_value('a', self.pull_at_program_counter())
            return True
        elif instruction == 14: # CLB
            print('CLB') if DEBUG else None
            self.set_value('b', self.pull_at_program_counter())
            return True
        elif instruction == 15: # CLQ
            print('CLQ') if DEBUG else None
            self.set_value('q', self.pull_at_program_counter())
            return True
        elif instruction == 20: # ADD
            print('ADD') if DEBUG else None
            result = self.get_value('a') + self.get_value('b')
            self.set_value('a', result)
            self.set_value('c', 1 if result > 255 else 0)
            return True
        elif instruction == 21: # ADDC
            print('ADDC') if DEBUG else None
            result = self.get_value('a') + self.get_value('b') + self.get_value('c')
            self.set_value('a', result)
            self.set_value('c', 1 if result > 255 else 0)
            return True
        elif instruction == 22: # SUB
            print('SUB') if DEBUG else None
            #Note that with subtraction, the carry out is the negative of the 9th bit of the outcome, because of how subtract works by overflwoing the add curcuit.
            result = self.get_value('a') + (self.get_value('b') ^ 0xFF) + 1
            self.set_value('a', result)
            self.set_value('c', 0 if result > 255 else 1)
            return True
        elif instruction == 23: # SUBC
            print('SUBC') if DEBUG else None
            result = self.get_value('a') + (self.get_value('b') ^ 0xFF) + 1 + self.get_value('c')
            self.set_value('a', result)
            self.set_value('c', 0 if result > 255 else 1)
            return True
        elif instruction == 24: # SHL
            print('SHL') if DEBUG else None
            result = self.get_value('a') << 1
            self.set_value('a', result)
            self.set_value('c', 1 if result > 255 else 0)
            return True
        elif instruction == 25: # SLHC
            print('SLHC') if DEBUG else None
            result = self.get_value('a') << 1 + self.get_value('c')
            self.set_value('a', result)
            self.set_value('c', 1 if result > 255 else 0)
            return True
        elif instruction == 26: # SHR
            print('SHR') if DEBUG else None
            result = self.get_value('a') >> 1
            self.set_value('a', result)
            self.set_value('c', 1 if result % 2 == 1 else 0)
            return True
        elif instruction == 27: # SHRC
            print('SHRC') if DEBUG else None
            result = self.get_value('a') >> 1 + self.get_value('c') * 128
            self.set_value('a', result)
            self.set_value('c', 1 if result % 2 == 1 else 0)
            return True
        elif instruction == 28: # AND
            print('AND') if DEBUG else None
            result = self.get_value('a') & self.get_value('b')
            self.set_value('a', result)
            return True
        elif instruction == 29: # OR
            print('OR') if DEBUG else None
            result = self.get_value('a') | self.get_value('b')
            self.set_value('a', result)
            return True
        elif instruction == 30: # XOR
            print('XOR') if DEBUG else None
            result = self.get_value('a') ^ self.get_value('b')
            self.set_value('a', result)
            return True
        elif instruction == 31: # NAND
            print('NAND') if DEBUG else None
            result = (self.get_value('a') & self.get_value('b')) ^ 0xFF
            self.set_value('a', result)
            return True
        elif instruction == 32: # NOR
            print('NOR') if DEBUG else None
            result = (self.get_value('a') | self.get_value('b')) ^ 0xFF
            self.set_value('a', result)
            return True
        elif instruction == 33: # XNOR
            print('XNOR') if DEBUG else None
            result = (self.get_value('a') ^ self.get_value('b')) ^ 0xFF
            self.set_value('a', result)
            return True
        elif instruction == 34: # CKSM
            print('CKSM') if DEBUG else None
            #xor all bits of A together and put it in the carry
            result = 0
            for i in range(8):
                result ^= (self.get_value('a') >> i) % 2
            self.set_value('c', result)
            return True
        elif instruction == 35: # CKSMC
            print('CKSMC') if DEBUG else None
            #xor all bits of A and the old carry together and put it in the new carry. Handy for getting the checksum of multiple bytes.
            result = 0
            for i in range(8):
                result ^= (self.get_value('a') >> i) % 2
            result ^= self.get_value('c')
            self.set_value('c', result)
            return True
        elif instruction == 36: # INCR
            print('INCR') if DEBUG else None
            self.set_value('q', self.get_value('q') + 1)
            return True
        elif instruction == 37: # DECR
            print('DECR') if DEBUG else None
            self.set_value('q', self.get_value('q') - 1)
            return True
        elif instruction == 38: # JMP
            print('JMP') if DEBUG else None
            self.set_value('p', self.get_value('r'))
            return True
        elif instruction == 39: # JMPC
            print('JMPC') if DEBUG else None
            if self.get_value('c') == 1:
                self.set_value('p', self.get_value('r'))
            return True
        elif instruction == 40: # JMPZ
            print('JMPZ') if DEBUG else None
            if self.get_value('z') == 1:
                self.set_value('p', self.get_value('r'))
            return True
        elif instruction == 41: # JMPQ
            print('JMPQ') if DEBUG else None
            if self.get_value('z') == 0:
                self.set_value('p', self.get_value('r'))
            return True
        elif instruction == 42: # PSH
            print('PSH') if DEBUG else None
            # add the value stored in A to the stack
            # the low byte of the stack pointer is stored, and 0xFF00 is added to it before it gets to the address bus. The stack works with the empty descending stack convention. Meanig that the outputted value starts as 0xFFFF and goes down to 0xFF00 if the stack is full. Good video: https://youtu.be/IWQ74f2ot7E
            self.deviceManifold.write(self.get_value('s') + 0xFF00, self.get_value('a'))
            self.set_value('s', self.get_value('s') - 1)
            return True
        elif instruction == 43: # POP
            print('POP') if DEBUG else None
            # pop a value from the stack and put it into A
            self.set_value('s', self.get_value('s') + 1)
            self.set_value('a', self.deviceManifold.read(self.get_value('s') + 0xFF00))
            return True
        elif instruction == 44: # SUBR
            print('SUBR') if DEBUG else None
            # start a subroutine by pushing the current program counter to the stack and then jumping to the address stored in the HL register pair, first H, then L is pushed
            self.deviceManifold.write(self.get_value('s') + 0xFF00, self.get_value('p') // 256)
            self.set_value('s', self.get_value('s') - 1)
            self.deviceManifold.write(self.get_value('s') + 0xFF00, self.get_value('p') % 256)
            self.set_value('s', self.get_value('s') - 1)
            self.set_value('p', self.get_value('r'))
            return True
        elif instruction == 45: # RET
            print('RET') if DEBUG else None
            #pops the address of the last subroutine instruction, first L, then H is popped (reverse from pushing, because its a stack)
            self.set_value('s', self.get_value('s') + 1)
            self.set_value('l', self.deviceManifold.read(self.get_value('s') + 0xFF00))
            self.set_value('s', self.get_value('s') + 1)
            self.set_value('h', self.deviceManifold.read(self.get_value('s') + 0xFF00))
            return True

        return False
class ReadWriteMemory(object):
    def __init__(self, nbits):
        self.nbits = nbits
        self.memory = [0] * (2**nbits)
    def read(self, address):
        return self.memory[address % (2**self.nbits)]
    def write(self, address, value):
        self.memory[address % (2**self.nbits)] = value % 8
    def setData(self, filename):
        with open(filename, 'r') as f:
            for i in range(len(self.memory)):
                line = f.readline().strip()
                if line == '':
                    continue
                self.memory[i] = int(line, 2)

memory = ReadWriteMemory(6)
memory.setData('memory.txt')

smpu = SMPU()
smpu.mount(memory)
while smpu.clock():
    print(
        smpu.get_value('a'),
        # smpu.get_value('b'),
        # smpu.get_value('q'),
        # smpu.get_value('p'),
        # smpu.get_value('r'),
        )