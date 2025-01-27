import unittest
from io import StringIO
from unittest.mock import patch
from bangla_ipa.ipa import BanglaIPATranslator


class TestBanglaIPA(unittest.TestCase):

    def setUp(self):
        self.ipa = BanglaIPATranslator()

    def test_ipa_checker(self):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.ipa.translate("মহারাজ")
            expected_output = "mɔharaɟ\n"
            self.assertEqual(mock_stdout.getvalue(), expected_output)


if __name__ == '__main__':
    unittest.main()
