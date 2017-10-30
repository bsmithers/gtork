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


class GarminParser(object):
    """
    Abstract base class
    """

    def __init__(self, xml_string):
        self._heartrate = None
        self.xml = None

        try:
            # Not ideal, but stripping out the namespace makes our life easier. The extensions
            # are harder to deal with (as you also need to remove the prefix from each tag), so we'll leave them in.
            xml_string = re.sub(' xmlns="[^"]+"', '', xml_string, count=1)
            self.xml = xml.etree.ElementTree.fromstring(xml_string)
        except xml.etree.ElementTree.ParseError:
            raise GarminParseException("Could not extract XML namespaces")

    @staticmethod
    def parse_timestamp(ts):
        timestamp_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        return datetime.strptime(ts, timestamp_format)

    @property
    def type(self):
        raise NotImplementedError

    @property
    def start_time(self):
        raise NotImplementedError

    @property
    def heartrate(self):
        if self._heartrate is None:
            self._heartrate = self._parse_heartrate()
        return self._heartrate

    def _parse_heartrate(self):
        raise NotImplementedError


class GPXParser(GarminParser):
    # namespace extension
    ns3 = "http://www.garmin.com/xmlschemas/TrackPointExtension/v1"

    def __init__(self, xml_string):
        super().__init__(xml_string)
        self._gps_points = None

    @property
    def type(self):
        return self._simple_lookup('trk/type')

    @property
    def name(self):
        return self._simple_lookup('trk/name')

    @property
    def description(self):
        return self._simple_lookup('trk/desc')

    @property
    def start_time(self):
        return GarminParser.parse_timestamp(self._simple_lookup('metadata/time', required=True))

    @property
    def gps_points(self):
        if self._gps_points is None:

            self._gps_points = []

            try:
                for trkpt in self.xml.findall('trk//trkpt'):
                    latitude = float(trkpt.attrib['lat'])
                    longitude = float(trkpt.attrib['lon'])
                    elevation = float(trkpt.find('ele').text)
                    timestamp = GarminParser.parse_timestamp(trkpt.find('time').text)

                    self._gps_points.append(GPSpoint(latitude=latitude, longitude=longitude, elevation=elevation, timestamp=timestamp))

            except (AttributeError, KeyError):
                raise GPXException("Error extracting GPS datapoints")

        return self._gps_points

    def _parse_heartrate(self):

        hrs = []
        hr_path = "extensions/{%s}TrackPointExtension/{%s}hr" % (self.ns3, self.ns3)
        for trkpt in self.xml.findall('trk//trkpt'):
            hr_tag = trkpt.find(hr_path)
            if hr_tag is None:
                continue

            try:
                timestamp = GarminParser.parse_timestamp(trkpt.find('time').text)
                hr = int(hr_tag.text)
            except AttributeError:
                raise GPXException("Error extracting hr & timestamp data")
            except ValueError:
                raise GPXException('Could not convert heartrate to int in GPX data')

            hrs.append(HeartRate(hr=hr, timestamp=timestamp))

        return hrs

    def _simple_lookup(self, path, required=False, default=""):
        try:
            return self.xml.find(path).text
        except AttributeError:
            if required:
                raise GPXException("Could not find item at {}".format(path))
            return default


class TCXParser(GarminParser):

    @property
    def type(self):
        try:
            return self.xml.find('Activities/Activity').attrib['Sport'].lower()
        except AttributeError:
            raise TCXException("Acitivity type not found in TCX data")

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
        if not laps:
            raise TCXException("No laps found in TCX data")

        first_lap = laps[0]

        try:
            return GarminParser.parse_timestamp(first_lap.attrib['StartTime'])
        except AttributeError:
            raise TCXException("StartTime not found in lap")

    def _parse_heartrate(self):
        try:
            timestamps = [GarminParser.parse_timestamp(e.text) for e in self.xml.findall('.//Lap/Track/Trackpoint/Time')]
            hrs = [int(e.text) for e in self.xml.findall('.//Lap/Track/Trackpoint/HeartRateBpm/Value')]
        except TypeError:
            raise TCXException("Error extracting timestamps and heartrates in TCX data")
        except ValueError:
            raise TCXException('Could not convert heartrate to int in TCX data')

        return [HeartRate(hr=h, timestamp=t) for (h, t) in zip(hrs, timestamps)]

    @functools.lru_cache()
    def _lap_summation(self, field, type_=float):
        try:
            values = [type_(l.find(field).text) for l in self._get_laps()]
            return sum(values)
        except AttributeError:
            raise TCXException('Could not find {} in TCX data'.format(field))
        except ValueError:
            raise TCXException('Could not convert {} to {} in TCX data'.format(field, type_))

    def _get_laps(self):
        return self.xml.findall('.//Lap')
