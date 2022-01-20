class SymbolTable:
    def __init__(self):
        self.st = {}

        for i in range(16):
            self.st['R' + str(i)] = i
        self.variable_count = 16

        self.st['SCREEN'] = 16384
        self.st['KBD'] = 24576
        self.st['SP'] = 0
        self.st['LCL'] = 1
        self.st['ARG'] = 2
        self.st['THIS'] = 3
        self.st['THAT'] = 4

    def add_label(self, label, line_number):
        self.st[label] = line_number

    def get_value(self, symbol):
        if symbol not in self.st:
            self.st[symbol] = self.variable_count
            self.variable_count += 1
        return self.st[symbol]


def to_binary(value, length):
    bits = []
    for i in range(length):
        bits.append(str(value % 2))
        value //= 2
    return ''.join(reversed(bits))


def encode_a_instruction(instruction, symbol_table):
    value = instruction[1:]
    if value.isdigit():
        value = to_binary(int(value), 16)
    else:
        value = to_binary(symbol_table.get_value(value), 16)
    return value


def encode_dest(dest):
    bits = []
    for register in 'ADM':
        bits.append('1' if register in dest else '0')
    return ''.join(bits)


def encode_comp(comp):
    bits = ['1' if 'M' in comp else '0']
    comp = comp.replace('M', 'A')

    command_sets = '''0 1 -1 A !A -A A+1 A-1
    1 -1 A !A -A D+1 A+1 A-1 D-A D|A
    0 1 -1 D !D -D D+1 D-1
    1 D !D -D D+1 A+1 D-1 A-D D|A
    0 1 -1 -D -A D+1 A+1 D-1 A-1 D+A D-A A-D
    1 !D !A -D -A D+1 A+1 D-A A-D D|A'''.split('\n')
    for command_set in command_sets:
        bits.append('1' if comp in command_set.split() else '0')

    return ''.join(bits)


def encode_jmp(jmp):
    jmp_types = ' JGT JEQ JGE JLT JNE JLE JMP'.split(' ')
    return to_binary(jmp_types.index(jmp), 3)


def encode_c_instruction(instruction):
    if '=' not in instruction:
        instruction = '=' + instruction
    if ';' not in instruction:
        instruction += ';'
    dest, instruction = instruction.split('=')
    comp, jmp = instruction.split(';')
    return '111' + encode_comp(comp) + encode_dest(dest) + encode_jmp(jmp)


def encode_program(program):
    symbol_table = SymbolTable()
    instructions = []
    line_number = 0

    for line in program:
        line = line.split('//')[0].strip()
        if line.startswith('('):
            symbol_table.add_label(line[1:-1], line_number)
        elif len(line):
            instructions.append(line)
            line_number += 1

    codes = []

    for line in instructions:
        if line.startswith('@'):
            codes.append(encode_a_instruction(line, symbol_table))
        else:
            codes.append(encode_c_instruction(line))

    return codes


from sys import stdin
with open('program.hack', 'w') as file:
    print('\n'.join(encode_program(stdin.readlines())), file=file)
