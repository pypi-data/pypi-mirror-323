import os
import tempfile
import unittest
from io import BytesIO

from texthold.core import Holder


class TestHolder(unittest.TestCase):

    def test_data_property(self):
        holder = Holder(["line1", "line2"])
        self.assertEqual(holder.data, ["line1", "line2"])

        holder.data = ["new line1\nnew line2", "line3"]
        self.assertEqual(holder.data, ["new line1", "new line2", "line3"])

        del holder.data
        self.assertEqual(holder.data, [])

    def test_dumps(self):
        holder = Holder(["line1", "line2"])
        result = holder.dumps()
        self.assertEqual(result, "line1\nline2\n")

    def test_dump(self):
        holder = Holder(["line1", "line2"])
        stream = BytesIO()
        holder.dump(stream)

        # Check the content of the byte stream
        stream.seek(0)
        self.assertEqual(stream.read().decode("utf-8"), "line1\nline2\n")

    def test_load(self):
        stream = BytesIO(b"line1\nline2\n")
        holder = Holder.load(stream)
        self.assertEqual(holder.data, ["line1", "line2"])

    def test_dumpintofile_and_loadfromfile(self):
        holder = Holder(["line1", "line2"])

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.close()
            holder.dumpintofile(temp_file.name)

            with open(temp_file.name, "r") as f:
                content = f.read()
                self.assertEqual(content, "line1\nline2\n")

            loaded_holder = Holder.loadfromfile(temp_file.name)
            self.assertEqual(loaded_holder.data, ["line1", "line2"])

            os.unlink(temp_file.name)

    def test_loads(self):
        string = "line1\nline2\n"
        holder = Holder.loads(string)
        self.assertEqual(holder.data, ["line1", "line2"])


if __name__ == "__main__":
    unittest.main()
