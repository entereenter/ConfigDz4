import struct
import argparse
import json

class Assembler:
    def __init__(self, input_file, bin_out_file, log_file):
        self.input_file = input_file
        self.bin_out_file = bin_out_file
        self.log_file = log_file

    def create_command(self, A, B, C):
        # Загрузка константы (A = 10)
        if A == 10:
            return self.create_command_load_constant(B, C)
        # Чтение значения из памяти (A = 15)
        elif A == 15:
            return self.create_command_read_memory(B, C)
        # Запись значения в память (A = 3)
        elif A == 3:
            return self.create_command_write_memory(B, C)
        # Унарная операция sgn (A = 14)
        elif A == 14:
            return self.create_command_sgn(B, C)
        else:
            return None

    def main_assem(self):
        logs = []
        commands = []

        with open(self.input_file, 'r') as infile:
            for line in infile:
                elements = line.strip().split()
                if len(elements) == 3:
                    a, b, c = int(elements[0]), int(elements[1]), int(elements[2])
                    command = self.create_command(a, b, c)

                    commands.append(command)
                    line = self.create_for_log(a, b, c, command)
                    logs.append(line)

                elif len(elements) == 4:
                    a, b, c, d = int(elements[0]), int(elements[1]), int(elements[2]), int(elements[3])
                    command = self.create_command(a, b, c)

                    commands.append(command)
                    line = self.create_for_log(a, b, c, command)
                    logs.append(line)

        with open(self.bin_out_file, 'wb') as outfile:
            for command in commands:
                outfile.write(command)
            #print("Бинарный файл был успешно записан.")
            #print(f'Путь к файлу: {self.bin_out_file}')

        with open(self.log_file, 'w') as log_file:
            json.dump(logs, log_file, indent=2)
            #print(f"Файл-лог был успешно записан.")
            #print(f'Путь к файлу: {self.log_file}')

    def create_for_log(self, A, B, C, command):
        line = ""
        for i in range(0, 9, 2):

            line += "0x" + command.hex()[i:i + 2] + " "
        return f'Data: {A}, {B}, {C}; Commands: {line.strip()}'

    def create_command_load_constant(self, B, C):
        # Константа в C и адрес в B
        return struct.pack("BBBH", 10, B, C & 0xFF, (C >> 8) & 0xFF)

    def create_command_read_memory(self, B, C):
        # Чтение из памяти
        return struct.pack("BBB", 0x0F, B, C)

    def create_command_write_memory(self, B, C):
        # Запись в память
        return struct.pack("BBB", 0x03, B, C)

    def create_command_sgn(self, B, C):
        # Операция знака
        return struct.pack("BBB", 0x0E, B, C)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file")
    parser.add_argument("bin_out_file")
    parser.add_argument("log_file")

    args = parser.parse_args()
    assembler = Assembler(args.input_file, args.bin_out_file, args.log_file)
    assembler.main_assem()
