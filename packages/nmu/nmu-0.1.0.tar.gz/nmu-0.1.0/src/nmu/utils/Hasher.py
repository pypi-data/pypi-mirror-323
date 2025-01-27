import hashlib

class Hasher:
    def __init__(self):
        self._buffer = bytearray()
        self._state = hashlib.md5()  # 使用 MD5 哈希算法
        self._data_length = 0

    def start(self):
        self._buffer.clear()
        self._state = hashlib.md5()
        self._data_length = 0
        return self

    def appendStr(self, t):
        s = 0
        while s < len(t):
            char_code = ord(t[s])
            if char_code < 128:
                self._buffer.append(char_code)
            elif char_code < 2048:
                self._buffer.append(192 + (char_code >> 6))
                self._buffer.append(128 + (char_code & 63))
            elif char_code < 55296 or char_code > 56319:
                self._buffer.append(224 + (char_code >> 12))
                self._buffer.append(128 + ((char_code >> 6) & 63))
                self._buffer.append(128 + (char_code & 63))
            else:
                if s + 1 < len(t):
                    next_char_code = ord(t[s + 1])
                    char_code = 1024 * (char_code - 55296) + (next_char_code - 56320) + 65536
                    self._buffer.append(240 + (char_code >> 18))
                    self._buffer.append(128 + ((char_code >> 12) & 63))
                    self._buffer.append(128 + ((char_code >> 6) & 63))
                    self._buffer.append(128 + (char_code & 63))
                    s += 1
                else:
                    raise ValueError("Invalid UTF-16 surrogate pair")

            if len(self._buffer) >= 64:
                self._state.update(self._buffer[:64])
                self._buffer = self._buffer[64:]
            s += 1
        return self

    def end(self):
        self._data_length += len(self._buffer)
        self._state.update(self._buffer)
        return self._state.hexdigest()


# 测试代码
if __name__ == "__main__":
    hasher = Hasher()
    print("MD5 Hash:", hasher.start().appendStr("hello").end())