import unittest
import struct
import os
import json
from Assembler import Assembler

class TestAssembler(unittest.TestCase):
    def setUp(self):
        # Создаем временные файлы для тестов
        self.input_file = "test_input.txt"
        self.bin_out_file = "test_output.bin"
        self.log_file = "test_log.json"

        # Пример входных данных
        with open(self.input_file, "w") as f:
            f.write("10 1 255\n")   # Загрузка константы
            f.write("15 2 3\n")    # Чтение из памяти
            f.write("3 4 5\n")     # Запись в память
            f.write("14 6 7\n")    # Унарная операция sgn

        self.assembler = Assembler(self.input_file, self.bin_out_file, self.log_file)

    def tearDown(self):
        # Удаляем временные файлы после тестов
        for file in [self.input_file, self.bin_out_file, self.log_file]:
            if os.path.exists(file):
                os.remove(file)

    def test_create_command_load_constant(self):
        command = self.assembler.create_command_load_constant(1, 255)
        expected = struct.pack("BBBH", 10, 1, 255 & 0xFF, (255 >> 8) & 0xFF)
        self.assertEqual(command, expected)

    def test_create_command_read_memory(self):
        command = self.assembler.create_command_read_memory(2, 3)
        expected = struct.pack("BBB", 0x0F, 2, 3)
        self.assertEqual(command, expected)

    def test_create_command_write_memory(self):
        command = self.assembler.create_command_write_memory(4, 5)
        expected = struct.pack("BBB", 0x03, 4, 5)
        self.assertEqual(command, expected)

    def test_create_command_sgn(self):
        command = self.assembler.create_command_sgn(6, 7)
        expected = struct.pack("BBB", 0x0E, 6, 7)
        self.assertEqual(command, expected)

    def test_create_command_invalid(self):
        command = self.assembler.create_command(99, 1, 2)
        self.assertIsNone(command)

    def test_create_for_log(self):
        # Проверяем строку лога
        command = struct.pack("BBB", 0x0A, 1, 2)
        log_line = self.assembler.create_for_log(10, 1, 2, command)


        expected = "Data: 10, 1, 2; Commands: 0x0a 0x01 0x02 0x 0x"
        self.assertEqual(log_line.strip(), expected)

    def test_main_assem(self):
        # Проверяем основной метод main_assem
        self.assembler.main_assem()

        # Проверяем бинарный выходной файл
        with open(self.bin_out_file, "rb") as f:
            content = f.read()
        expected_content = (
            struct.pack("BBBH", 10, 1, 255 & 0xFF, (255 >> 8) & 0xFF) +  # load constant
            struct.pack("BBB", 0x0F, 2, 3) +                            # read memory
            struct.pack("BBB", 0x03, 4, 5) +                            # write memory
            struct.pack("BBB", 0x0E, 6, 7)                              # sgn
        )
        self.assertEqual(content, expected_content)

        # Проверяем файл логов
        with open(self.log_file, "r") as f:
            logs = json.load(f)


        self.assertEqual(len(logs), 4)
        self.assertIn("Data: 10, 1, 255", logs[0])
        self.assertIn("Commands: 0x0a 0x01 0xff 0x00", logs[0])

if __name__ == "__main__":
    unittest.main()
#python -m unittest test_Assembler.py