import os
import tempfile
from typing import *

from datahold import OkayList

__all__ = ["Holder"]


class Holder(OkayList):
    @property
    def data(self) -> list[str]:
        "This property represents the lines of text."
        return list(self._data)

    @data.setter
    def data(self, value: Iterable, /):
        normed = list()
        for x in value:
            for y in str(x).split("\n"):
                normed.append(y)
        self._data = normed

    @data.deleter
    def data(self) -> None:
        self._data = list()

    def dump(self, stream: Any) -> None:
        "This method dumps the data into a byte stream."
        filename: str = "a.txt"
        with tempfile.TemporaryDirectory() as tmpDir:
            tmpFile: str = os.path.join(tmpDir, filename)
            self.dumpintofile(tmpFile)
            with open(tmpFile, "rb") as tmpRbStream:
                buffer: bytes = tmpRbStream.read()
        stream.write(buffer)

    def dumpintofile(self, file: str) -> None:
        "This method dumps the data into a file."
        with open(file, "w") as stream:
            for item in self:
                print(item, file=stream)

    def dumps(self) -> str:
        "This method dumps the data as a string."
        return "\n".join(self._data) + "\n"

    @classmethod
    def load(cls, stream: Any) -> Self:
        "This classmethod loads a new instance from a given byte stream."
        buffer: bytes = stream.read()
        filename: str = "a.txt"
        with tempfile.TemporaryDirectory() as tmpDir:
            tmpFile: str = os.path.join(tmpDir, filename)
            with open(tmpFile, "wb") as tmpWbStream:
                tmpWbStream.write(buffer)
            return cls.loadfromfile(tmpFile)

    @classmethod
    def loadfromfile(cls, file: str) -> Self:
        "This classmethod loads a new instance from a given file."
        with open(file, "r") as stream:
            return cls.loads(stream.read())

    @classmethod
    def loads(cls, string: str) -> Self:
        "This classmethod loads a new instance from a given string."
        if string.endswith("\n"):
            string = string[:-1]
        data = string.split("\n")
        return cls(data)
