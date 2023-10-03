import datetime

import gpxpy
import gpxpy.gpx
from shapely import wkb
import csv
import dateutil.parser.isoparser

gpx_file = gpxpy.gpx.GPX()


def add_track_to_gpx(mode: str, track_datetime: datetime.datetime, coordinate_str: str):
    try:
        points = wkb.loads(coordinate_str, hex=True).coords
        gpx_track = gpxpy.gpx.GPXTrack()
        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        for point in points:
            gpx_tp = gpxpy.gpx.GPXTrackPoint(latitude=point[1], longitude=point[0],
                                             time=track_datetime)
            gpx_segment.points.append(gpx_tp)
        gpx_track.segments.append(gpx_segment)
        gpx_file.tracks.append(gpx_track)
        print('appended track', track_datetime)
    except:
        print('error', mode, track_datetime, coordinate_str)


def add_stay_to_gpx(point_datetime: datetime.datetime, coordinate_str: str):
    point = wkb.loads(coordinate_str, hex=True)
    gpx_wp = gpxpy.gpx.GPXWaypoint(latitude=point.y, longitude=point.x, time=point_datetime)
    gpx_file.waypoints.append(gpx_wp)
    print('appended waypoint', point_datetime)


def export(month: str):
    global gpx_file
    file = "out/" + str(month) + ".gpx"
    xml = gpx_file.to_xml()
    print('saving file to', file)
    out_file = open(file, "w")
    out_file.write(xml)
    out_file.close()
    gpx_file = gpxpy.gpx.GPX()


with open('cmd-export.csv', 'r') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
    # Skip the header
    next(spamreader)

    for row in spamreader:
        # 2: Track or Stay
        transport_mode = row[2]
        # 9: Trip mode (Mode::Walk)
        mode = row[9]
        # 11: coordinates
        coordinates_hex = row[11]
        # 18: date time localized
        print(row[18])
        datetime = dateutil.parser.isoparse(row[18])
        current_month = str(datetime.year) + "-" + str(datetime.month)

        if 'last_month' not in locals():
            print('creating var')
            last_month = current_month

        if last_month != current_month:
            export(last_month)
            last_month = current_month

        if transport_mode == 'Track':
            add_track_to_gpx(mode=mode, track_datetime=datetime, coordinate_str=coordinates_hex)
        elif transport_mode == 'Stay':
            add_stay_to_gpx(point_datetime=datetime, coordinate_str=coordinates_hex)

export(current_month)
exit(1)
