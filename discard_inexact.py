import datetime
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


def is_too_inexact(point_a, point_b) -> bool:
    return geopy.distance.geodesic(point_a, point_b).m > 300


gpx_input_file = open('./out/2023-6.gpx', 'r')
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
        current_coordinates = (point.longitude, point.latitude)
        if has_point_to_save and is_too_inexact(current_coordinates, last_coordinates):
            save_segment(loop_segment)
            loop_segment = create_loop_segment()
            has_point_to_save = False
        else:
            has_point_to_save = True
            loop_segment.points.append(point)
        last_coordinates = (point.longitude, point.latitude)

    print("appending track {0}...".format(mode))
    track.type = mode
    new_gpx.tracks.append(track)

new_gpx.waypoints = old_gpx.waypoints
xml = new_gpx.to_xml()
gpx_output_file = open('output_file.gpx', 'w')
gpx_output_file.write(xml)
gpx_output_file.close()
