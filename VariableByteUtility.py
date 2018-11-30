class VariableByteUtility:
    @staticmethod
    def encode(number: int) -> bytes:  # Up to 28 bit positive integers supported
        temp = number

        parts = []

        first_non_zero_part = 0
        for i in range(4):
            parts.append(temp & int.from_bytes(b'\x7F', 'big'))
            if parts[i] != 0:
                first_non_zero_part = i
            temp >>= 7

        result = []

        for i in range(first_non_zero_part, -1, -1):
            if i > 0:
                result.append(parts[i].to_bytes(1, 'big'))
            else:
                result.append((parts[i] | int.from_bytes(b'\x80', 'big')).to_bytes(1, 'big'))

        return b''.join(result)

    @staticmethod
    def decode(inp: bytes) -> int:
        result = 0
        for b in inp:
            if b >= 128:
                result = (result << 7) + b - 128
            else:
                result = (result << 7) + b
        return result

