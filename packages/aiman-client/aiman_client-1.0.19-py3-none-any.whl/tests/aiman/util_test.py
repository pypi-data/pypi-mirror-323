"""client test module"""
from pathlib import Path
import unittest
import aiman


class UtilTest(unittest.TestCase):
    """_summary_

    Args:
        unittest (_type_): _description_
    """
    current_directory = Path(__file__)
    def test_validate_url(self):
        """_summary_"""
        is_url = aiman.Util.validate_url(url ="C:/MyWindowsPath/myFile.jpg", check_only=True)
        self.assertFalse(is_url)

        is_url = aiman.Util.validate_url(url ="www.myUrl.com", check_only=True)
        self.assertTrue(is_url)
        parsed_url = aiman.Util.validate_url(url ="www.myUrl.com", check_only=False)
        self.assertEqual(parsed_url, "https://www.myUrl.com")

        is_url = aiman.Util.validate_url(url ="https://www.myUrl.com", check_only=True)
        self.assertTrue(is_url)

        is_url = aiman.Util.validate_url(url ="http://www.myUrl.com", check_only=True)
        self.assertTrue(is_url)

        parsed_url = aiman.Util.validate_url(url ="http://www.myUrl.com", check_only=False)
        self.assertEqual(parsed_url, "https://www.myUrl.com")

    def test_parse_filename(self):
        """_summary_"""
        test_path = f"{self.current_directory}/service_client_test.py"
        name = aiman.Util.get_file_name(test_path)
        self.assertEqual(name,"service_client_test.py")

        file_name, ext = aiman.Util.get_file_name_and_ext(f"{self.current_directory}/service_client_test.py")
        self.assertEqual(file_name,"service_client_test.py")
        self.assertEqual(ext,"py")

    def test_parse_mimetype(self):
        """_summary_"""
        mimetype = aiman.Util.get_mimetype_by_ext("pdf")
        self.assertEqual(mimetype, "application/pdf")

        mimetype = aiman.Util.get_mimetype_by_ext("csv")
        self.assertEqual(mimetype, "application/csv")

        mimetype = aiman.Util.get_mimetype_by_ext("xlsx")
        self.assertEqual(mimetype, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        mimetype = aiman.Util.get_mimetype_by_ext("png")
        self.assertEqual(mimetype, "image/png")

        mimetype = aiman.Util.get_mimetype_by_ext("jpeg")
        self.assertEqual(mimetype, "image/jpeg")

        mimetype = aiman.Util.get_mimetype_by_ext("tif")
        self.assertEqual(mimetype, "image/tif")
