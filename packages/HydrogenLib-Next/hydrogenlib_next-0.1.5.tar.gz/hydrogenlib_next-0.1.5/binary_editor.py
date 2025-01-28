class BinaryEditor:
    def __init__(self, value=0):
        self.value = value

    def get_bit(self, position):
        """获取指定位置的位"""
        return (self.value >> position) & 1

    def set_bit(self, position):
        """设置指定位置的位为1"""
        self.value |= (1 << position)

    def clear_bit(self, position):
        """清除指定位置的位为0"""
        self.value &= ~(1 << position)

    def toggle_bit(self, position):
        """切换指定位置的位"""
        self.value ^= (1 << position)

    def get_bits(self, start, end):
        """获取指定范围内的位"""
        mask = ((1 << (end - start + 1)) - 1) << start
        return (self.value & mask) >> start

    def set_bits(self, start, end, value):
        """设置指定范围内的位"""
        mask = ((1 << (end - start + 1)) - 1) << start
        self.value &= ~mask
        self.value |= (value << start) & mask

    def clear_bits(self, start, end):
        """清除指定范围内的位"""
        mask = ~(((1 << (end - start + 1)) - 1) << start)
        self.value &= mask

    def add_bits_left(self, num_bits):
        """在二进制数的左边添加指定数量的位"""
        self.value <<= num_bits

    def add_bits_right(self, num_bits):
        """在二进制数的右边添加指定数量的位"""
        self.value |= (1 << num_bits) - 1

    def __str__(self):
        """返回当前二进制值的字符串表示"""
        return bin(self.value)[2:]

# 示例用法
if __name__ == "__main__":
    editor = BinaryEditor(0b101010)
    print(f"Original: {editor}")

    editor.set_bit(2)
    print(f"After setting bit 2: {editor}")

    editor.clear_bit(1)
    print(f"After clearing bit 1: {editor}")

    editor.toggle_bit(0)
    print(f"After toggling bit 0: {editor}")

    print(f"Bits from 1 to 3: {editor.get_bits(1, 3)}")

    editor.set_bits(1, 3, 0b111)
    print(f"After setting bits 1 to 3 to 111: {editor}")

    editor.clear_bits(1, 3)
    print(f"After clearing bits 1 to 3: {editor}")

    editor.add_bits_left(2)
    print(f"After adding 2 bits to the left: {editor}")

    editor.add_bits_right(2)
    print(f"After adding 2 bits to the right: {editor}")