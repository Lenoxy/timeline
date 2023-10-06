import datetime
from os import walk, listdir
from typing import Type

import gpxpy
import gpxpy.gpx
from gpxpy.gpx import GPXTrackSegment
from shapely import wkb
import csv
import dateutil.parser.isoparser
import geopy.distance


def track_segments_to_single_segment(track: gpxpy.gpx.GPXTrack) -> GPXTrackSegment:
    print("creating unified segments...")
    return_segment = gpxpy.gpx.GPXTrackSegment()
    for unify_segment in track.segments:
        for unify_point in unify_segment.points:
            return_segment.points.append(unify_point)

    return return_segment


def is_exact(point_a, point_b) -> bool:
    return geopy.distance.geodesic(point_a, point_b).m < 300



for file_name in listdir('./out/'):
    print(file_name)
    if not file_name.endswith(".gpx"):
        print("skipping since file {0} does not end with .gpx".format(file_name))
        continue

    gpx_input_file = open('./out/{0}'.format(file_name), 'r')
    old_gpx = gpxpy.parse(gpx_input_file)
    new_gpx = gpxpy.gpx.GPX()

    for track in old_gpx.tracks:
        mode = track.type
        single_segment = track_segments_to_single_segment(track)


        def save_segment(segment):
            track.segments.append(segment)


        def create_loop_segment() -> GPXTrackSegment:
            return GPXTrackSegment()


        loop_segment = create_loop_segment()
        has_point_to_save = False
        for point in single_segment.points:
            try:
                current_coordinates = (point.longitude, point.latitude)
                if has_point_to_save and not is_exact(current_coordinates, last_coordinates):
                    save_segment(loop_segment)
                    loop_segment = create_loop_segment()
                    has_point_to_save = False
                else:
                    has_point_to_save = True
                    loop_segment.points.append(point)
                last_coordinates = (point.longitude, point.latitude)
            except:
                print("warning")
                continue
        print("appending track {0}...".format(mode))
        track.type = mode
        new_gpx.tracks.append(track)

    new_gpx.waypoints = old_gpx.waypoints
    xml = new_gpx.to_xml()
    gpx_output_file = open('./out/exact/{0}'.format(file_name), 'w')
    gpx_output_file.write(xml)
    gpx_output_file.close()
