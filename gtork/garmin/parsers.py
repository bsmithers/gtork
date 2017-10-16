import collections
from datetime import datetime
import functools
import re
import xml.etree.ElementTree


class GarminParseException(Exception):
    pass


class GPXException(GarminParseException):
    pass


class TCXException(GarminParseException):
    pass


GPSpoint = collections.namedtuple('GPSpoint', ['latitude', 'longitude', 'elevation', 'timestamp'])
HeartRate = collections.namedtuple('HeartRate', ['hr', 'timestamp'])


def get_garmin_xml(xml_string):
    try:
        # Not ideal, but stripping out the namespace makes our life easier. The extensions
        # are harder to deal with (as you also need to remove the prefix from each tag), so we'll leave them in.
        xml_string = re.sub(' xmlns="[^"]+"', '', xml_string, count=1)
        return xml.etree.ElementTree.fromstring(xml_string)
    except xml.etree.ElementTree.ParseError:
        raise GarminParseException


def parse_timestamp(ts):
    timestamp_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    return datetime.strptime(ts, timestamp_format)


class GPXParser(object):
    # namespace extension
    ns3 = "http://www.garmin.com/xmlschemas/TrackPointExtension/v1"

    def __init__(self, gpx_string):
        self._gps_points = None
        self._heartrate = None
        self.gpx = get_garmin_xml(gpx_string)

    @property
    def type(self):
        return self._simple_lookup('trk/type')

    @property
    def name(self):
        return self._simple_lookup('trk/name')

    @property
    def desciption(self):
        return self._simple_lookup('trk/desc')

    @property
    def start_time(self):
        return parse_timestamp(self._simple_lookup('metadata/time', required=True))

    @property
    def gps_points(self):
        if self._gps_points is None:
            self._gps_points = []

            try:
                for trkpt in self.gpx.findall('trk//trkpt'):
                    latitude = trkpt.attrib['lat']
                    longitude = trkpt.attrib['lon']
                    elevation = trkpt.find('ele').text
                    timestamp = parse_timestamp(trkpt.find('time').text)

                    self._gps_points.append(GPSpoint(latitude=latitude, longitude=longitude, elevation=elevation, timestamp=timestamp))

            except (AttributeError, KeyError):
                raise GPXException

        return self._gps_points

    @property
    def heartrate(self):
        if self._heartrate is None:
            search = "trk//trkpt/extensions/{%s}TrackPointExtension/{%s}hr" % (self.ns3, self.ns3)

            try:
                hrs = [int(e.text) for e in self.gpx.findall(search)]
            except AttributeError:
                raise GPXException

            if len(hrs) == 0:
                return hrs

            timestamps = [p.timestamp for p in self.gps_points]
            if len(hrs) != len(timestamps):
                raise GPXException

            self._heartrate = [HeartRate(hr=h, timestamp=t) for (h, t) in zip(hrs, timestamps)]

        return self._heartrate

    def _simple_lookup(self, path, required=False, default=""):
        try:
            return self.gpx.find(path).text
        except AttributeError:
            if required:
                raise GPXException
            return default


class TCXParser(object):
    def __init__(self, tcx_string):
        self.tcx = get_garmin_xml(tcx_string)
        self._heartrate = None

    @property
    def type(self):
        try:
            return self.tcx.find('Activities/Activity').attrib['Sport'].lower()
        except AttributeError:
            raise TCXException

    @property
    def distance(self):
        return self._lap_summation('DistanceMeters')

    @property
    def calories(self):
        return self._lap_summation('Calories', type_=int)

    @property
    def time(self):
        return self._lap_summation('TotalTimeSeconds')

    @property
    def start_time(self):
        laps = self._get_laps()
        first_lap = laps[0]

        try:
            return parse_timestamp(first_lap.attrib['StartTime'])
        except AttributeError:
            raise TCXException

    @property
    def heartrate(self):
        timestamps = [parse_timestamp(e.text) for e in self.tcx.findall('.//Lap/Track/Trackpoint/Time')]
        hrs = [int(e.text) for e in self.tcx.findall('.//Lap/Track/Trackpoint/HeartRateBpm/Value')]

        return [HeartRate(hr=h, timestamp=t) for (h, t) in zip(hrs, timestamps)]

    @functools.lru_cache()
    def _lap_summation(self, field, type_=float):
        try:
            values = [type_(l.find(field).text) for l in self._get_laps()]
            return sum(values)
        except AttributeError:
            raise TCXException

    def _get_laps(self):
        return self.tcx.findall('.//Lap')
