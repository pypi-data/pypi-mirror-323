import unittest
from flask_secure_keygen import generate_secret_key

class TestKeyGen(unittest.TestCase):
    def test_key_length(self):
        key = generate_secret_key(64)
        self.assertEqual(len(key), 64)

    def test_invalid_length(self):
        with self.assertRaises(ValueError):
            generate_secret_key(16)

if __name__ == "__main__":
    unittest.main()
