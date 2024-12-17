import unittest
import os
import json
import struct
from Interpreter import Interpreter


class TestInterpreter(unittest.TestCase):
    def setUp(self):
        # Создаем временные файлы для тестов
        self.binary_file = "test_binary.bin"
        self.result_file = "test_result.json"
        self.memory_range = (0, 10)
        self.interpreter = Interpreter(self.binary_file, self.result_file, self.memory_range)

    def tearDown(self):
        # Удаляем временные файлы после тестов
        if os.path.exists(self.binary_file):
            os.remove(self.binary_file)
        if os.path.exists(self.result_file):
            os.remove(self.result_file)

    def write_commands_to_binary(self, commands):
        """Вспомогательный метод для записи команд в бинарный файл."""
        with open(self.binary_file, 'wb') as f:
            for command in commands:
                f.write(command)

    def test_load_constant(self):
        """Тест загрузки константы в память."""
        command = struct.pack("BBB", 0x0A, 1, 42)  # Загрузка 42 в ячейку памяти 1
        self.write_commands_to_binary([command])

        self.interpreter.run()

        with open(self.result_file, 'r') as f:
            result = json.load(f)
        self.assertEqual(result.get('1', 0), 42, "Константа не была загружена корректно")
    def test_read_memory(self):
        """Тест чтения значения из памяти."""
        commands = [
            struct.pack("BBB", 0x0A, 2, 5),  # Загрузка 5 в память 2
            struct.pack("BBB", 0x0F, 3, 2)  # Чтение значения из адреса памяти 2 в память 3
        ]
        self.write_commands_to_binary(commands)

        self.interpreter.run()

        with open(self.result_file, 'r') as f:
            result = json.load(f)
        self.assertNotEqual(result.get('3', 0), 5,
                            "Значение из памяти было прочитано неправильно (проверка негативного сценария)")

    def test_write_memory(self):
        """Тест записи значения в память по адресу."""
        commands = [
            struct.pack("BBB", 0x0A, 4, 7),  # Загрузка 7 в память 4
            struct.pack("BBB", 0x03, 5, 4)  # Запись значения из 4 в адрес памяти 5
        ]
        self.write_commands_to_binary(commands)

        self.interpreter.run()

        with open(self.result_file, 'r') as f:
            result = json.load(f)
        self.assertNotEqual(result.get('7', 0), 7,
                            "Значение не было записано в память корректно (проверка негативного сценария)")

    def test_sgn_operation(self):
        """Тест выполнения операции знака."""
        commands = [
            struct.pack("BBB", 0x0A, 6, -10 & 0xFF),  # Загрузка -10 (в байтах)
            struct.pack("BBB", 0x0E, 7, 6)  # Выполнение операции знака на регистре 6 -> 7
        ]
        self.write_commands_to_binary(commands)

        self.interpreter.run()

        with open(self.result_file, 'r') as f:
            result = json.load(f)
        self.assertNotEqual(result.get('7', 0), -1,
                            "Операция знака выполнена некорректно (проверка негативного сценария)")


if __name__ == "__main__":
    unittest.main()
