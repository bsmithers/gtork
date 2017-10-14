import os
import unittest

from gtork.tests import TEST_DATA_DIR
from gtork.garmin.parsers import GPXParser, TCXParser, GarminParseException

class TestParser(unittest.TestCase):
    def test_valid_gpx(self):
        parser = self._get_parser('sample.gpx', GPXParser)
        self.assertEqual(parser.type, 'running')
        self.assertEqual(parser.name, 'The title')
        self.assertEqual(parser.desciption, 'The description')
        self.assertEqual(parser.start_time, '2017-09-23T08:05:03.000Z')

        self.assertEqual(len(parser.gps_points), 280)

        self.assertEqual(parser.gps_points[0].timestamp, parser.start_time)

        self.assertEqual(len(parser.gps_points), len(parser.heartrate))

    def test_valid_tcx(self):
        parser = self._get_parser('sample.tcx', TCXParser)

        self.assertEqual(parser.type, 'running')
        self.assertEqual(parser.start_time, '2017-09-23T08:05:03.000Z')
        self.assertEqual(parser.heartrate[0].timestamp, parser.start_time)
        self.assertEqual(parser.calories, 348)
        self.assertEqual(parser.distance, 4844.74)
        self.assertEqual(parser.time, 2067.0)


    def test_compare_formats(self):
        """
        Check that the gpx and tcx parsers return the same values for the compatible fields
        """
        gpx_parser = self._get_parser('sample.gpx', GPXParser)
        tcx_parser = self._get_parser('sample.tcx', TCXParser)

        self.assertEqual(gpx_parser.start_time, tcx_parser.start_time)
        self.assertEqual(gpx_parser.heartrate, tcx_parser.heartrate)
        self.assertEqual(gpx_parser.type, tcx_parser.type)

    def test_treadmill(self):
        """
        Test a treadmill activity
        """
        parser = self._get_parser('treadmill.tcx', TCXParser)
        self.assertEqual(parser.type, 'running')
        self.assertEqual(parser.start_time, '2017-09-08T16:21:47.000Z')
        self.assertEqual(parser.heartrate[0].timestamp, parser.start_time)
        self.assertEqual(parser.calories, 360)
        self.assertEqual(parser.distance, 4744.08)
        self.assertEqual(parser.time, 2085.0)\

    def test_no_heartrate(self):
        """
        Gpx file is valid with heartrates
        """
        parser = self._get_parser('nohr.gpx', GPXParser)
        self.assertEqual(parser.heartrate, [])

    def test_empty_gpx(self):
        with self.assertRaises(GarminParseException):
            gpx_parser = self._get_parser('empty.gpx', GPXParser)

    def test_invalid_tcx(self):
        with self.assertRaises(GarminParseException):
            gpx_parser = self._get_parser('error.tcx', TCXParser)

    def _get_parser(self, filename, parser_class):
        data_file = os.path.join(TEST_DATA_DIR, filename)
        with open(data_file) as h:
            return parser_class(h.read())


if __name__ == '__main__':
    unittest.main()
