"""环境准备"""
import re

X_VER = 0x7fff_ffff

class Version():
    def __init__(self, ver_str):
        if not re.match("^([0-9]|([1-9][0-9]*))\\.(x|[0-9]|([1-9][0-9]*))$", ver_str):
            raise Exception("Version string {ver_str} not match with regex ^([0-9]|([1-9][0-9]*))\\.([0-9]|([1-9][0-9]*))$")
        chunks = ver_str.split(".")
        self.major = int(chunks[0])
        if chunks[1] == "x":
            self.minor = X_VER
        else:
            self.minor = int(chunks[1])
        self.str = ver_str

    def bt(self, next_ver):
        next = Version(next_ver)
        if self.major > next.major or (self.major == next.major and (self.minor > next.minor and self.minor != X_VER)):
            return True
        return False

    def be(self, next_ver):
        next = Version(next_ver)
        if self.major > next.major or (self.major == next.major and self.minor >= next.minor):
            return True
        return False

    def lt(self, next_ver):
        next = Version(next_ver)
        if self.major < next.major or (self.major == next.major and (self.minor < next.minor and next.minor != X_VER and next.minor != X_VER)):
            return True
        return False

    def le(self, next_ver):
        next = Version(next_ver)
        if self.major < next.major or (self.major == next.major and (self.minor <= next.minor or self.minor == X_VER)):
            return True
        return False

