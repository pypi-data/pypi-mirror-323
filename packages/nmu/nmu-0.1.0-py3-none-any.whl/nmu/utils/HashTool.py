import math

class HashTool:
    def __init__(self):
        self.constants = [0x5A827999, 0x6ED9EBA1, 0x8F1BBCDC, 0xCA62C1D6]

    def hash(self, t):
        # 将字符串编码为 UTF-8 字节序列
        t = t.encode('utf-8')

        # 按 SHA-1 规范补位
        bit_len = len(t) * 8
        t += b'\x80'  # 添加 1 位的 '1'
        while (len(t) % 64) != 56:  # 补 0，直到长度为 64 的倍数 - 8
            t += b'\x00'

        # 添加原始长度的 64 位（以大端序存储）
        t += (bit_len >> 32).to_bytes(4, 'big')  # 高 32 位
        t += (bit_len & 0xFFFFFFFF).to_bytes(4, 'big')  # 低 32 位

        # 初始化哈希变量
        h = [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0]

        # 分块处理
        for i in range(0, len(t), 64):
            block = t[i:i+64]
            w = [0] * 80

            # 将前 16 个字初始化为当前块
            for j in range(16):
                w[j] = int.from_bytes(block[j*4:(j+1)*4], 'big')

            # 扩展到 80 个字
            for j in range(16, 80):
                w[j] = self.ROTL(w[j-3] ^ w[j-8] ^ w[j-14] ^ w[j-16], 1)

            # 初始化当前块的哈希值
            a, b, c, d, e = h

            # 80 步的主循环
            for j in range(80):
                f = self.f(j, b, c, d)
                k = self.constants[j // 20]
                temp = (self.ROTL(a, 5) + f + e + k + w[j]) & 0xFFFFFFFF
                e = d
                d = c
                c = self.ROTL(b, 30)
                b = a
                a = temp

            # 将当前块的哈希值加到结果中
            h[0] = (h[0] + a) & 0xFFFFFFFF
            h[1] = (h[1] + b) & 0xFFFFFFFF
            h[2] = (h[2] + c) & 0xFFFFFFFF
            h[3] = (h[3] + d) & 0xFFFFFFFF
            h[4] = (h[4] + e) & 0xFFFFFFFF

        # 拼接最终的哈希值（十六进制格式）
        return ''.join(f'{x:08x}' for x in h)

    def f(self, t, b, c, d):
        if t // 20 == 0:
            return (b & c) | (~b & d)
        elif t // 20 == 1:
            return b ^ c ^ d
        elif t // 20 == 2:
            return (b & c) | (b & d) | (c & d)
        elif t // 20 == 3:
            return b ^ c ^ d

    def ROTL(self, x, n):
        return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF




# 示例调用
if __name__ == "__main__":
    # 测试
    hash_function = HashTool()
    result = hash_function.hash("Hello, World!")
    print(f"Hash result: {result}")
