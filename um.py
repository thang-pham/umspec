#!/usr/bin/env python
import ctypes
import struct
import sys

__author__ = 'Thang Pham <thang.g.pham@gmail.com>'

# Operation codes
HALT = 7
LOAD = 12
ORTHOGRAPHY = 13


class UM(object):
    """ UM-32 Universal Machine """

    def __init__(self, file_path, stdout=sys.stdout, stdin=sys.stdin):
        self.stdout = stdout
        self.stdin = stdin
        self.file_path = file_path

        # Eight distinct general-purpose registers
        self.registers = [0, 0, 0, 0, 0, 0, 0, 0]

        # Operator shall be retrieved from the platter that is indicated by the execution finger
        self.exec_finger = 0

        # A collection of arrays of platters
        self.arrays = []

    def read_in_platters(self):
        program_scroll = []
        with open(self.file_path, 'rb') as c:
            while True:
                _bytes = c.read(4)  # Read in unsigned 32-bit/4-byte number
                if not _bytes:
                    break

                program_scroll.append(struct.unpack('>L', _bytes)[0])

        self.arrays.append(program_scroll)

    def operate(self, op_code, a, b, c):
        if op_code == 0:
            # 0. Conditional Move.
            # The register A receives the value in register B, unless the register C contains 0.
            if self.registers[c] != 0:
                self.registers[a] = self.registers[b]

        elif op_code == 1:
            # 1. Array Index.
            # The register A receives the value stored at offset in register C in the array identified by B.
            offset = self.registers[c]
            self.registers[a] = self.arrays[self.registers[b]][offset]

        elif op_code == 2:
            # 2. Array Amendment.
            # The array identified by A is amended at the offset in register B to store the value in register C.
            offset = self.registers[b]
            self.arrays[self.registers[a]][offset] = self.registers[c]  # Raises IndexError if index does not exist

        elif op_code == 3:
            # 3. Addition.
            # The register A receives the value in register B plus the value in register C, modulo 2^32.
            self.registers[a] = (self.registers[b] + self.registers[c]) % 2**32

        elif op_code == 4:
            # 4. Multiplication.
            # The register A receives the value in register B times the value in register C, modulo 2^32.
            self.registers[a] = (self.registers[b] * self.registers[c]) % 2**32

        elif op_code == 5:
            # 5. Division.
            # The register A receives the value in register B divided by the value in register C, if any, where
            # each quantity is treated treated as an unsigned 32 bit number.
            self.registers[a] = self.registers[b] // self.registers[c]  # Raises ZeroDivisionError if divide by zero

        elif op_code == 6:
            # 6. Not-And.
            # Each bit in the register A receives the 1 bit if either register B or register C has a 0 bit in that
            # position.  Otherwise the bit in register A receives the 0 bit.
            self.registers[a] = ctypes.c_uint32(~(self.registers[b] & self.registers[c])).value

        elif op_code == 8:
            # 8. Allocation.
            # A new array is created with a capacity of platters commensurate to the value in the register C. This
            # new array is initialized entirely with platters holding the value 0. A bit pattern not consisting of
            # exclusively the 0 bit, and that identifies no other active allocated array, is placed in the B register.
            new_array = [0 for n in range(self.registers[c])]
            self.arrays.append(new_array)
            self.registers[b] = len(self.arrays) - 1

        elif op_code == 9:
            # 9. Abandonment.
            # The array identified by the register C is abandoned. Future allocations may then reuse that identifier.
            if self.registers[c]:
                self.arrays[self.registers[c]] = []
            else:
                # If the program decides to abandon the '0' array, or to abandon an array that is not active,
                # then the machine may Fail.
                raise Exception()

        elif op_code == 10:
            # 10. Output.
            # The value in the register C is displayed on the console immediately. Only values between and
            # including 0 and 255 are allowed.
            self.stdout.write(chr(self.registers[c]))  # The argument must be in the range [0..255], inclusive.

        elif op_code == 11:
            # 11. Input.
            # The universal machine waits for input on the console. When input arrives, the register C is loaded with
            # the input, which must be between and including 0 and 255. If the end of input has been signaled, then the
            # register C is endowed with a uniform value pattern where every place is pregnant with the 1 bit.
            try:
                self.registers[c] = ord(self.stdin.read(1))  # char > int
            except EOFError:
                self.registers[c] = 0xFFFFFFFF

        elif op_code == 12:
            # 12. Load Program.
            # The array identified by the B register is duplicated and the duplicate shall replace the '0' array,
            # regardless of size. The execution finger is placed to indicate the platter of this array that is
            # described by the offset given in C, where the value 0 denotes the first platter, 1 the second, et cetera.
            #
            # The '0' array shall be the most sublime choice for loading, and shall be handled with the utmost velocity.
            if self.registers[b]:  # Do not reload array[0] with itself
                duplicate = list(self.arrays[self.registers[b]])
                self.arrays[0] = duplicate
            self.exec_finger = self.registers[c]

        else:
            raise Exception('Not a valid instruction')

    def halt(self):
        # 7. Halt.
        # The universal machine stops computation.
        exit(0)

    def orthography(self, a, value):
        # 13. Orthography.
        # The value indicated is loaded into the register A forthwith.
        self.registers[a] = value

    @staticmethod
    def get_op_code(platter):
        return platter >> 28

    @staticmethod
    def get_a(platter):
        return platter >> 6 & 0x00000007

    @staticmethod
    def get_b(platter):
        return platter >> 3 & 0x00000007

    @staticmethod
    def get_c(platter):
        return platter & 0x00000007

    @staticmethod
    def get_ortho_a(platter):
        return (platter & 0x0E000000) >> 25  # 1110 = E

    @staticmethod
    def get_ortho_value(platter):
        return platter & 0x01FFFFFF

    def run(self):
        # Collection of arrays of platters, each referenced by a distinct 32-bit identifier.
        self.read_in_platters()

        while True:
            platter = self.arrays[0][self.exec_finger]

            op_code = UM.get_op_code(platter)
            # print 'op_code: %d' % op_code
            if op_code == HALT:
                # print '%d: HALT' % platter
                self.halt()
            elif op_code == ORTHOGRAPHY:
                a = UM.get_ortho_a(platter)
                value = UM.get_ortho_value(platter)
                # print '  %d| a:%d value:%d' % (platter, a, value)
                self.orthography(a, value)
            else:
                # Registers a, b, and c
                c = UM.get_c(platter)
                b = UM.get_b(platter)
                a = UM.get_a(platter)

                # print '  %d| a:%d b:%d c:%d' % (platter, a, b, c)
                self.operate(op_code, a, b, c)

            # Before this operator is discharged, the execution finger shall be advanced to the next platter, if any.
            if op_code != LOAD:
                self.exec_finger += 1


if __name__ == '__main__':
    um_32 = UM(sys.argv[1])
    um_32.run()
