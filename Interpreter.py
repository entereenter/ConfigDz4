import struct
import argparse
import json

class Interpreter:
    def __init__(self, binary_file, result_file, memory_range):
        self.binary_file = binary_file
        self.result_file = result_file
        self.memory_range = memory_range
        # Инициализация памяти с учетом диапазона от memory_range[0] до memory_range[1]
        self.memory = [0] * (memory_range[1] + 1)  # +1, так как индекс может быть равен memory_range[1]

    def run(self):
        with open(self.binary_file, 'rb') as file:
            while command := file.read(3):  # Чтение 3 байт для команды
                if len(command) < 3:
                    break  # если команда неполная, выходим
                args = struct.unpack("BBB", command)
                #print(f"Распакованные аргументы: {args}")
                self.execute_command(args)

        result = {}  # Запись результатов

        # Проверяем диапазон памяти и записываем в JSON только допустимые ячейки
        for i in range(self.memory_range[0], self.memory_range[1] + 1):
            result[i] = self.memory[i]

        with open(self.result_file, 'w') as json_file:
            json.dump(result, json_file, indent=2)
            #print(f"Результат с диапазоном памяти УВМ был успешно записан в файл.")
            #print(f'Путь к файлу: {self.result_file}')

    def execute_command(self, args):
        a, b, c = args

        if a == 0x0A:  # Загрузка константы
            constant = c
            self.memory[b] = constant
            #print(f"Загружена константа {constant} в регистр {b}")

        elif a == 0x0F:  # Чтение значения из памяти
            if c < self.memory_range[0] or c > self.memory_range[1]:
                print(f"Ошибка: адрес {c} выходит за допустимые границы памяти.")
                return
            address = self.memory[c]
            if address < len(self.memory):
                self.memory[b] = self.memory[address]
                #print(f"Прочитано значение из памяти по адресу {address}, загружено в регистр {b}")
            else:
                print(f"Ошибка: адрес {address} выходит за пределы памяти.")

        elif a == 0x03:  # Запись значения в память
            if b < self.memory_range[0] or b > self.memory_range[1]:
                print(f"Ошибка: адрес {b} выходит за допустимые границы памяти.")
                return
            address = self.memory[b]
            if address < len(self.memory):
                self.memory[address] = self.memory[c]
                #print(f"Записано значение {self.memory[c]} в память по адресу {address}")
            else:
                print(f"Ошибка: адрес {address} выходит за пределы памяти.")

        elif a == 0x0E:  # Операция знака
            value = self.memory[c]
            self.memory[b] = 1 if value > 0 else -1 if value < 0 else 0
            #print(f"Результат операции знака: {self.memory[b]} в регистр {b}")

        #else:
            #print(f"Неизвестная команда с опкодом {a}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file")
    parser.add_argument("output_file")
    parser.add_argument("memory_range", nargs=2, type=int)

    args = parser.parse_args()

    interpreter = Interpreter(args.input_file, args.output_file, tuple(args.memory_range))
    interpreter.run()
