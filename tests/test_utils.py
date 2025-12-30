import unittest
import os
import tempfile
from src.utils import read_paper_text

class TestUtils(unittest.TestCase):
    def test_read_paper_truncation(self):
        # Create a temp file
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
            # Write 100 chars
            f.write("a" * 100)
            temp_path = f.name
            
        try:
            # Read with max_tokens corresponding to < 100 chars
            # utils uses max_tokens * 4 chars. So max_tokens=10 -> 40 chars.
            text = read_paper_text(temp_path, max_tokens=10)
            self.assertTrue(len(text) < 100)
            self.assertTrue("TRUNCATED" in text)
            
            # Read with ample space
            text_full = read_paper_text(temp_path, max_tokens=50)
            self.assertEqual(len(text_full), 100)
            self.assertFalse("TRUNCATED" in text_full)
            
        finally:
            os.remove(temp_path)

if __name__ == '__main__':
    unittest.main()
