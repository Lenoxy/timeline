import datetime

import gpxpy
import gpxpy.gpx
from shapely import wkb
import csv
import dateutil.parser.isoparser
import geopy.distance


gpx_file = gpxpy.gpx.GPX()


def add_track_to_gpx(mode: str, track_datetime: datetime.datetime, coordinate_str: str):
    try:
        points = wkb.loads(coordinate_str, hex=True).coords
        gpx_track = gpxpy.gpx.GPXTrack()
        gpx_segment = gpxpy.gpx.GPXTrackSegment()

        last_coords = (0,0)
        skip_append = False
        for point in points:
            gpx_tp = gpxpy.gpx.GPXTrackPoint(latitude=point[1], longitude=point[0],
                                             time=track_datetime)
            gpx_segment.points.append(gpx_tp)
            # only save the track to file if points are closer than 100m apart. Ignore tracks far apart
            current_coords = (point[1], point[0])
            if last_coords != (0,0) and geopy.distance.geodesic(last_coords, current_coords).km > 5:
                skip_append = True
                break

            last_coords = current_coords
        if skip_append == False:
            gpx_track.type = mode
            gpx_track.segments.append(gpx_segment)
            gpx_file.tracks.append(gpx_track)
            print('appended track', track_datetime)
        else:
            print("skip_append has been set, skipping this track.")

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
    print('saving file to', file)
    xml = gpx_file.to_xml()
    out_file = open(file, "w")
    out_file.write(xml)
    out_file.close()
    gpx_file = gpxpy.gpx.GPX()


def map_mode(cmd_mode: str):
    if cmd_mode == "Mode::Walk":
        return "walking"
    elif cmd_mode == "Mode::Bicycle" or cmd_mode == "Mode::Ebicycle":
        return "cycling"
    elif cmd_mode == "Mode::Bus":
        return "bus"
    elif cmd_mode == "Mode::Tram" or cmd_mode == "Mode::LightRail":
        return "tram"
    elif cmd_mode == "Mode::Train" or cmd_mode == "Mode::Subway" or cmd_mode == "Mode::RegionalTrain":
        return "train"
    elif cmd_mode == "Mode::Car" or cmd_mode == "Mode::TaxiUber" or cmd_mode == "Mode::CarsharingMobility":
        return "car"
    elif cmd_mode == "Mode::Motorbike":
        return "motorcycle"
    elif cmd_mode == "Mode::Airplane":
        return "airplane"
    elif cmd_mode == "Mode::Boat":
        return "boat"
    else:
        print(cmd_mode, "not able to map.")
        exit(1)


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
            add_track_to_gpx(mode=map_mode(mode), track_datetime=datetime, coordinate_str=coordinates_hex)
        elif transport_mode == 'Stay':
            add_stay_to_gpx(point_datetime=datetime, coordinate_str=coordinates_hex)

export(current_month)
exit(1)



