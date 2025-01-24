import unittest
from MyPkgAuto2.hello import auto2_say_hello
from MyPkgAuto2.hello import auto2_say_hello2

class TestHello(unittest.TestCase):
    def test_default(self):
        self.assertEqual(auto2_say_hello(), "Hello, World!")

    def test_custom_name(self):
        self.assertEqual(auto2_say_hello("Python"), "Hello, Python!")

    def test_default2(self):
        self.assertEqual(auto2_say_hello2(), "World, World, Hello!")

    def test_custom_name2(self):
        self.assertEqual(auto2_say_hello2("Python"), "Python, Python, Hello!")

if __name__ == "__main__":
    unittest.main()
