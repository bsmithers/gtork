from datetime import datetime
import unittest

from gtork.tests import get_test_parser
from gtork.garmin.parsers import GPXParser, TCXParser, GarminParseException


class TestParser(unittest.TestCase):
    def test_valid_gpx(self):
        parser = get_test_parser('sample.gpx', GPXParser)
        self.assertEqual(parser.type, 'running')
        self.assertEqual(parser.name, 'The title')
        self.assertEqual(parser.description, 'The description')
        self.assertEqual(parser.start_time, datetime(2017, 9, 23, 8, 5, 3))


        self.assertEqual(len(parser.gps_points), 280)

        self.assertEqual(parser.gps_points[0].timestamp, parser.start_time)

        self.assertEqual(len(parser.gps_points), len(parser.heartrate))

    def test_valid_tcx(self):
        parser = get_test_parser('sample.tcx', TCXParser)

        self.assertEqual(parser.type, 'running')
        self.assertEqual(parser.start_time, datetime(2017, 9, 23, 8, 5, 3))
        self.assertEqual(parser.heartrate[0].timestamp, parser.start_time)
        self.assertEqual(parser.calories, 348)
        self.assertEqual(parser.distance, 4844.74)
        self.assertEqual(parser.time, 2067.0)


    def test_compare_formats(self):
        """
        Check that the gpx and tcx parsers return the same values for the compatible fields
        """
        gpx_parser = get_test_parser('sample.gpx', GPXParser)
        tcx_parser = get_test_parser('sample.tcx', TCXParser)

        self.assertEqual(gpx_parser.start_time, tcx_parser.start_time)
        self.assertEqual(gpx_parser.heartrate, tcx_parser.heartrate)
        self.assertEqual(gpx_parser.type, tcx_parser.type)

    def test_treadmill(self):
        """
        Test a treadmill activity
        """
        parser = get_test_parser('treadmill.tcx', TCXParser)
        self.assertEqual(parser.type, 'running')
        self.assertEqual(parser.start_time, datetime(2017, 9, 8, 16, 21, 47))
        self.assertEqual(parser.heartrate[0].timestamp, parser.start_time)
        self.assertEqual(parser.calories, 360)
        self.assertEqual(parser.distance, 4744.08)
        self.assertEqual(parser.time, 2085.0)

    def test_no_heartrate(self):
        """
        Gpx file is valid with heartrates
        """
        parser = get_test_parser('nohr.gpx', GPXParser)
        self.assertEqual(parser.heartrate, [])

    def test_empty_gpx(self):
        with self.assertRaises(GarminParseException):
            gpx_parser = get_test_parser('empty.gpx', GPXParser)

    def test_invalid_tcx(self):
        with self.assertRaises(GarminParseException):
            gpx_parser = get_test_parser('error.tcx', TCXParser)

    def test_partial_heartrate(self):
        """
        Test a file with the 1st & 3rd hrs removed. Hrs should still be returned and should
        use the associated timestamps
        """
        parser = get_test_parser('partial_hr.gpx', GPXParser)
        self.assertEqual(len(parser.heartrate), len(parser.gps_points) - 2)
        self.assertNotEqual(parser.heartrate[0].timestamp, parser.start_time)
        self.assertEqual(parser.heartrate[-1].timestamp, parser.gps_points[-1].timestamp)


if __name__ == '__main__':
    unittest.main()
