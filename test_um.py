#!/usr/bin/env python
import ctypes
import unittest
from StringIO import StringIO

from um import UM


__author__ = 'Thang Pham <thang.g.pham@gmail.com>'


class TestUM(unittest.TestCase):
    def setUp(self):
        self.file_path = './codex.umz'

    def test_init(self):
        test_um = UM(self.file_path)
        self.assertEqual([0] * 8, test_um.registers)
        self.assertEqual(self.file_path, test_um.file_path)
        self.assertEqual(0, test_um.exec_finger)
        self.assertEqual(0, len(test_um.arrays))

    def test_op_code0(self):
        test_um = UM(self.file_path)

        # op_code: 0 - Conditional move
        op_code = 0
        test_um.registers[0] = 1
        test_um.registers[1] = 2
        test_um.registers[2] = 3
        test_um.operate(op_code, 0, 1, 2)
        self.assertEqual(test_um.registers[0], 2)
        test_um.registers[0] = 1
        test_um.registers[1] = 2
        test_um.registers[2] = 0
        # No change because registers[c] = 0
        self.assertEqual(1, test_um.registers[0])
        self.assertEqual(2, test_um.registers[1])
        self.assertEqual(0, test_um.registers[2])

    def test_op_code1(self):
        test_um = UM(self.file_path)
        test_um.arrays.append([1, 2, 3])
        test_um.arrays.append([4, 5, 6])
        self.assertEqual([[1, 2, 3], [4, 5, 6]], test_um.arrays)

        # op_code: 1 - Array index
        op_code = 1
        test_um.registers[0] = 0
        test_um.registers[1] = 1
        test_um.registers[2] = 2
        test_um.operate(op_code, 0, 1, 2)
        self.assertEqual(6, test_um.registers[0])
        self.assertEqual(1, test_um.registers[1])
        self.assertEqual(2, test_um.registers[2])

    def test_op_code2(self):
        test_um = UM(self.file_path)
        test_um.arrays.append([1, 2, 3])

        # op_code: 2 - Array Amendment
        op_code = 2
        test_um.registers[0] = 0
        test_um.registers[1] = 1
        test_um.registers[2] = 123
        test_um.operate(op_code, 0, 1, 2)
        self.assertEqual([[1, 123, 3]], test_um.arrays)

    def test_op_code3(self):
        test_um = UM(self.file_path)

        # op_code: 3 - Array Amendment
        op_code = 3
        test_um.registers[0] = 0
        test_um.registers[1] = 1
        test_um.registers[2] = 2
        test_um.operate(op_code, 0, 1, 2)
        self.assertEqual(3, test_um.registers[0])  # (1 + 2) % 2^32 = 3
        test_um.registers[0] = 0
        test_um.registers[1] = 0
        test_um.registers[2] = 2**32
        test_um.operate(op_code, 0, 1, 2)
        self.assertEqual(0, test_um.registers[0])  # (0 + 2^32) % 2^32 = 0

    def test_op_code4(self):
        test_um = UM(self.file_path)

        # op_code: 4 - Multiplication
        op_code = 4
        test_um.registers[0] = 0
        test_um.registers[1] = 1
        test_um.registers[2] = 2
        test_um.operate(op_code, 0, 1, 2)
        self.assertEqual(2, test_um.registers[0])  # (1 * 2) % 2^32 = 3
        test_um.registers[0] = 0
        test_um.registers[1] = 1
        test_um.registers[2] = 2 ** 32
        test_um.operate(op_code, 0, 1, 2)
        self.assertEqual(0, test_um.registers[0])  # (1 * 2^32) % 2^32 = 0

    def test_op_code5(self):
        test_um = UM(self.file_path)

        # op_code: 5 - Division
        op_code = 5
        test_um.registers[0] = 0
        test_um.registers[1] = 3
        test_um.registers[2] = 2
        test_um.operate(op_code, 0, 1, 2)
        self.assertEqual(1, test_um.registers[0])  # 3 // 2 = 1
        test_um.registers[0] = 0
        test_um.registers[1] = 6
        test_um.registers[2] = 2
        test_um.operate(op_code, 0, 1, 2)
        self.assertEqual(3, test_um.registers[0])  # 6 // 2 = 3

    def test_op_code6(self):
        test_um = UM(self.file_path)

        # op_code: 6 - Not-And
        op_code = 6
        test_um.registers[0] = 0
        test_um.registers[1] = 1
        test_um.registers[2] = 7
        test_um.operate(op_code, 0, 1, 2)
        expected_val = ctypes.c_uint32(~(1 & 7)).value
        self.assertEqual(expected_val, test_um.registers[0])

    def test_halt(self):
        test_um = UM(self.file_path)

        # op_code: 7 - Halt
        with self.assertRaises(SystemExit):
            test_um.halt()

    def test_op_code8(self):
        test_um = UM(self.file_path)
        test_um.arrays.append([1, 2, 3])

        # op_code: 8 - Allocation
        op_code = 8
        test_um.registers[0] = 0
        test_um.registers[1] = 1
        test_um.registers[2] = 2
        test_um.operate(op_code, 0, 1, 2)
        self.assertEqual([[1, 2, 3], [0, 0]], test_um.arrays)
        self.assertEqual(1, test_um.registers[1])

    def test_op_code9(self):
        test_um = UM(self.file_path)
        test_um.arrays.append([1, 2, 3])
        test_um.arrays.append([4, 5, 6])

        # op_code: 9 - Abandonment
        op_code = 9
        test_um.registers[0] = 0
        test_um.registers[1] = 1
        test_um.registers[2] = 1  # Clears arrays[1]
        test_um.operate(op_code, 0, 1, 2)
        self.assertEqual([[1, 2, 3], []], test_um.arrays)

        test_um.registers.pop(2)
        self.assertRaises(Exception, test_um.operate, op_code, 0, 1, 2)

    def test_op_code10(self):
        stdout = StringIO()
        test_um = UM(self.file_path, stdout=stdout)

        # op_code: 10 - Output
        op_code = 10
        test_um.registers[0] = 0
        test_um.registers[1] = 1
        test_um.registers[2] = 97
        test_um.operate(op_code, 0, 1, 2)

        output = stdout.getvalue()
        self.assertEqual(chr(97), output)

    def test_op_code11(self):
        stdin = StringIO(chr(97))
        test_um = UM(self.file_path, stdin=stdin)

        # op_code: 11 - Input
        op_code = 11
        test_um.operate(op_code, 0, 1, 2)
        self.assertEqual(97, test_um.registers[2])

    def test_op_code12(self):
        test_um = UM(self.file_path)
        test_um.arrays.append([1, 2, 3])
        test_um.arrays.append([4, 5, 6])
        test_um.arrays.append([7, 8, 9])

        # op_code: 12 - Load Program
        op_code = 12

        # register[b] is undef
        test_um.registers[0] = 0
        test_um.registers[1] = 1
        test_um.registers[2] = 2
        test_um.operate(op_code, 0, 1, 2)
        self.assertEqual([4, 5, 6], test_um.arrays[0])
        self.assertEqual(2, test_um.exec_finger)

    def test_op_code13(self):
        test_um = UM(self.file_path)

        # op_code: 13 - Orthography
        test_um.registers[0] = 0
        test_um.orthography(0, 1234)
        self.assertEqual(1234, test_um.registers[0])

    def test_op_code_undef(self):
        test_um = UM(self.file_path)

        # op_code: 123 - Undefined
        op_code = 123
        self.assertRaises(Exception, test_um.operate, op_code, 0, 1, 2)

    def test_get_op_code(self):
        self.assertEqual(0, UM.get_op_code(int('0x00000000', base=16)))
        self.assertEqual(1, UM.get_op_code(int('0x10000000', base=16)))
        self.assertEqual(2, UM.get_op_code(int('0x20000000', base=16)))
        self.assertEqual(3, UM.get_op_code(int('0x30000000', base=16)))
        self.assertEqual(4, UM.get_op_code(int('0x40000000', base=16)))
        self.assertEqual(5, UM.get_op_code(int('0x50000000', base=16)))
        self.assertEqual(6, UM.get_op_code(int('0x60000000', base=16)))
        self.assertEqual(7, UM.get_op_code(int('0x70000000', base=16)))
        self.assertEqual(8, UM.get_op_code(int('0x80000000', base=16)))
        self.assertEqual(9, UM.get_op_code(int('0x90000000', base=16)))
        self.assertEqual(10, UM.get_op_code(int('0xA0000000', base=16)))
        self.assertEqual(11, UM.get_op_code(int('0xB0000000', base=16)))
        self.assertEqual(12, UM.get_op_code(int('0xC0000000', base=16)))
        self.assertEqual(13, UM.get_op_code(int('0xD0000000', base=16)))

    def test_get_c(self):
        #                               A     C
        #                               |     |
        #                               vvv   vvv
        #       .--------------------------------.
        #       |VUTSRQPONMLKJIHGFEDCBA9876543210|
        #       `--------------------------------'
        #        ^^^^                      ^^^
        #        |                         |
        #        operator number           B
        self.assertEqual(7, UM.get_c(int('0x00000007', base=16)))
        self.assertEqual(6, UM.get_c(int('0x00000006', base=16)))
        self.assertEqual(5, UM.get_c(int('0x00000005', base=16)))

    def test_get_b(self):
        self.assertEqual(1, UM.get_b(int('0x00000008', base=16)))
        self.assertEqual(2, UM.get_b(int('0x00000010', base=16)))
        self.assertEqual(3, UM.get_b(int('0x00000018', base=16)))

    def test_get_a(self):
        self.assertEqual(1, UM.get_a(int('0x00000040', base=16)))
        self.assertEqual(2, UM.get_a(int('0x00000080', base=16)))
        self.assertEqual(3, UM.get_a(int('0x000000C0', base=16)))

    def test_get_ortho_a(self):
        #            A
        #            |
        #            vvv
        #       .--------------------------------.
        #       |VUTSRQPONMLKJIHGFEDCBA9876543210|
        #       `--------------------------------'
        #        ^^^^   ^^^^^^^^^^^^^^^^^^^^^^^^^
        #        |      |
        #        |      value
        #        |
        #        operator number
        self.assertEqual(1, UM.get_ortho_a(int('0x02000000', base=16)))
        self.assertEqual(2, UM.get_ortho_a(int('0x04000000', base=16)))
        self.assertEqual(3, UM.get_ortho_a(int('0x06000000', base=16)))

    def test_get_ortho_value(self):
        self.assertEqual(1, UM.get_ortho_value(int('0x00000001', base=16)))
        self.assertEqual(2, UM.get_ortho_value(int('0x00000002', base=16)))
        self.assertEqual(3, UM.get_ortho_value(int('0x00000003', base=16)))


if __name__ == '__main__':
    unittest.main()
