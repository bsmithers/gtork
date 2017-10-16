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
            "equipment": "treadmill"
        }
    }

    def __init__(self, activity, gpx_data, tcx_data):
        self.rk_object = {}
        self.activity = activity

        if not self.is_gps_type and not self.is_non_gps_type:
            raise ConversionException("Activity type {} not supported".format(activity.type))

        if self.is_non_gps_type:
            if not len(gpx_data) == 0:
                raise ConversionException(
                    'Non GPS type {} supplied, but Garmin provided non-zero gpx file'.format(activity.type))

        if self.is_gps_type:
            self.parser = GPXParser(gpx_data)
        else:
            self.parser = TCXParser(tcx_data)

    def as_json(self):
        rk_object = {}
        rk_object['type'] = self.type
        rk_object['equipment'] = self.equipment
        rk_object['start_time'] = self.start_time
        rk_object['notes'] = self.notes
        return rk_object

    @property
    def type(self):
        t = self.activity.type
        if self.is_non_gps_type:
            t = Garmin2Runkeeper.nongps_types[t]['basetype']

        return t.capitalize()

    @property
    def equipment(self):
        if self.is_non_gps_type:
            return Garmin2Runkeeper.nongps_types[self.activity.type]['equipment']
        return "None"

    @property
    def start_time(self):
        garmin_format = "%Y-%m-%d %H:%M:%S"
        rk_format = "%a, %d %b %Y %H:%M:%S"
        return datetime.strptime(self.activity.local_start_time, garmin_format).strftime(rk_format)

    @property
    def notes(self):
        return "{}: {}".format(self.activity.name, self.activity.description)

    @property
    def is_gps_type(self):
        return self.activity.type in Garmin2Runkeeper.gps_types

    @property
    def is_non_gps_type(self):
        return self.activity.type in Garmin2Runkeeper.nongps_types
