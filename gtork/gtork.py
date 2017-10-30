import collections
from datetime import datetime

from gtork.garmin.parsers import GPXParser, TCXParser

Activity = collections.namedtuple("Activity", ["name", "description", "type", "local_start_time"])


class ConversionException(Exception):
    pass


class Garmin2Runkeeper(object):

    gps_types = {"running", "cycling", "walking"}
    nongps_types = {
        "treadmill_running": {
            "basetype": "running",
            "equipment": "Treadmill"
        }
    }

    def __init__(self, activity, gpx_data, tcx_data):
        self.rk_object = {}
        self.activity = activity

        if not (self.is_gps_type() or self.activity.type in Garmin2Runkeeper.nongps_types):
            raise ConversionException("Activity type {} not supported".format(activity.type))

        if not self.is_gps_type():
            if not len(gpx_data) == 0:
                raise ConversionException(
                    'Non GPS type {} supplied, but Garmin provided non-zero gpx file'.format(activity.type))

        if self.is_gps_type():
            self.parser = GPXParser(gpx_data)
        else:
            self.parser = TCXParser(tcx_data)

    def as_rk_dict(self):
        rk_object = {}
        rk_object['type'] = self._format_type()
        rk_object['start_time'] = self._format_start_time()
        rk_object['notes'] = self._format_notes()
        hr = self._format_heartrate()
        if hr:
            rk_object['heart_rate'] = hr

        if self.is_gps_type():
            rk_object['path'] = self._format_path()
        else:
            rk_object['total_distance'] = self.parser.distance
            rk_object['duration'] = self.parser.time
            rk_object['equipment'] = Garmin2Runkeeper.nongps_types[self.activity.type]['equipment']

        return rk_object

    def is_gps_type(self):
        return self.activity.type in Garmin2Runkeeper.gps_types

    def _format_type(self):
        t = self.activity.type
        if not self.is_gps_type():
            t = Garmin2Runkeeper.nongps_types[t]['basetype']

        return t.capitalize()

    def _format_start_time(self):
        garmin_format = "%Y-%m-%d %H:%M:%S"
        rk_format = "%a, %d %b %Y %H:%M:%S"
        return datetime.strptime(self.activity.local_start_time, garmin_format).strftime(rk_format)

    def _format_notes(self):
        return "{}: {}".format(self.activity.name, self.activity.description)

    def _format_heartrate(self):
        if not self.parser.heartrate:
            return None

        datapoints = []
        for hr in self.parser.heartrate:
            delta = hr.timestamp - self.parser.start_time
            datapoint = {
                'timestamp': delta.seconds,
                'heart_rate': hr.hr
            }
            datapoints.append(datapoint)

        return datapoints

    def _format_path(self):
        if not self.is_gps_type():
            return None

        datapoints = []
        for gps in self.parser.gps_points:
            delta = gps.timestamp - self.parser.start_time
            datapoint = {
                'timestamp': delta.seconds,
                'latitude': gps.latitude,
                'longitude': gps.longitude,
                'altitude': gps.elevation,
                'type': 'gps'
            }
            datapoints.append(datapoint)

        # Now set first & last types to start/end
        datapoints[0]["type"] = "start"
        datapoints[-1]["type"] = "end"

        return datapoints
