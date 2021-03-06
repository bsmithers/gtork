import unittest

from gtork.gtork import Garmin2Runkeeper, Activity, ConversionException
from gtork.tests import get_test_xml


class BasicGPSTest(unittest.TestCase):
    a_name = 'the name'
    a_description = 'some description'
    a_local_start_time = '2017-10-13 13:50:35'
    a_type = 'running'

    e_type = 'Running'
    e_start_time = 'Fri, 13 Oct 2017 13:50:35'
    e_notes = 'the name: some description'
    options={}

    def get_expected(self):
        return {
            'type': self.e_type,
            'start_time': self.e_start_time,
            'notes': self.e_notes,
        }

    def get_activity(self):
        return Activity(name=self.a_name, description=self.a_description, local_start_time=self.a_local_start_time,
                        type=self.a_type)

    def get_gpx(self):
        return get_test_xml('sample.gpx')

    def get_tcx(self):
        return get_test_xml('sample.tcx')

    def complex_checks(self, result):
        self.assertEqual(len(result['heart_rate']), len(result['path']))
        self.check_hr(result)
        self.check_gps(result)

    def check_hr(self, result):
        self.assertIn('heart_rate', result)
        last_timestamp = -1
        for hr in result['heart_rate']:
            self.assertIn('timestamp', hr)
            self.assertIn('heart_rate', hr)
            self.assertIsInstance(hr['timestamp'], int)
            self.assertIsInstance(hr['heart_rate'], int)
            self.assertGreater(hr['timestamp'], last_timestamp)
            last_timestamp = hr['timestamp']

        # The first point is at t=0
        self.assertEqual(result['heart_rate'][0]["timestamp"], 0)

    def check_gps(self, result):
        self.assertIn('path', result)
        last_timestamp = -1
        for i, p in enumerate(result['path']):
            expected_fields = ['timestamp', 'latitude', 'longitude', 'altitude', 'type']
            for f in expected_fields:
                self.assertIn(f, p)

            expected_type = 'gps'
            if i == 0:
                expected_type = 'start'
            if i == len(result['path']) - 1:
                expected_type = 'end'

            self.assertEqual(p['type'], expected_type)

            self.assertIsInstance(p['timestamp'], int)
            self.assertIsInstance(p['latitude'], float)
            self.assertIsInstance(p['longitude'], float)
            self.assertIsInstance(p['altitude'], float)
            self.assertGreater(p['timestamp'], last_timestamp)
            last_timestamp = p['timestamp']

    def test_conversion(self):
        converter = Garmin2Runkeeper(self.get_activity(), self.get_gpx(), self.get_tcx(), options=self.options)
        result = converter.as_rk_dict()

        # Check the simple fields are present & correct
        for k, v in self.get_expected().items():
            self.assertIn(k, result)
            self.assertEqual(v, result[k])

        # Now do the more complex checks
        self.complex_checks(result)


class RunningOverrideGPS(BasicGPSTest):

    options={"override_gps": True}

    def get_expected(self):
        d = super().get_expected()
        d['total_distance'] = 4844.74
        return d

    def complex_checks(self, result):
        self.assertNotIn('path', result)


class CycleGPSTest(BasicGPSTest):
    a_type = 'cycling'
    e_type = 'Cycling'


class WalkingGPSTest(BasicGPSTest):
    a_type = 'walking'
    e_type = 'Walking'


class RunningNonGPSTest(BasicGPSTest):
    a_type = 'treadmill_running'

    e_equipment = 'Treadmill'
    e_total_distance = 4744.08
    e_duration = 2085.0

    def get_expected(self):
        e = super().get_expected()
        e.update({
            'equipment': self.e_equipment,
            'total_distance': self.e_total_distance,
            'duration': self.e_duration
        })
        return e

    def get_gpx(self):
        return ''

    def get_tcx(self):
        return get_test_xml('treadmill.tcx')

    def complex_checks(self, result):
        self.check_hr(result)

    def test_gpx_raises_exception(self):
        with self.assertRaises(ConversionException):
            converter = Garmin2Runkeeper(self.get_activity(), 'non-empty', self.get_tcx())


class PartialHRTest(BasicGPSTest):
    """
    Test a file with the 1st & 3rd hrs removed. hr timestamps should be calculated relative to
    the activity start time
    """

    def get_gpx(self):
        return get_test_xml('partial_hr.gpx')

    def complex_checks(self, result):
        self.assertEqual(len(result['heart_rate']), len(result['path']) - 2)
        self.check_hr(result)
        self.check_gps(result)

        # Check the timetamps agree taking into account the missing hrs
        self.assertEqual(result['heart_rate'][0]['timestamp'], result['path'][1]['timestamp'])
        for i in range(1, len(result['heart_rate'])):
            self.assertEqual(result['heart_rate'][i]['timestamp'], result['path'][i+2]['timestamp'])

    def check_hr(self, result):

        # Compare the timestamps (in seconds since activity start) for the first few HRs against
        # manual calculations
        self.assertEqual(result['heart_rate'][0]["timestamp"], 1)
        self.assertEqual(result['heart_rate'][1]["timestamp"], 7)
        self.assertEqual(result['heart_rate'][2]["timestamp"], 10)




if __name__ == '__main__':
    unittest.main()
