from os import listdir
import gpxpy
import gpxpy.gpx
from gpxpy.gpx import GPXTrackSegment
import geopy.distance


def track_segments_to_single_segment(track: gpxpy.gpx.GPXTrack) -> GPXTrackSegment:
    print("creating unified segments...")
    return_segment = gpxpy.gpx.GPXTrackSegment()
    for unify_segment in track.segments:
        for unify_point in unify_segment.points:
            return_segment.points.append(unify_point)

    return return_segment


def is_exact(point_a, point_b) -> bool:
    return geopy.distance.geodesic(point_a, point_b).m < 50


for file_name in listdir('./arc/'):
    print(file_name)
    if not file_name.endswith(".gpx"):
        print("skipping since file {0} does not end with .gpx".format(file_name))
        # Skip loop and iterate over next item
        continue

    gpx_input_file = open('./arc/{0}'.format(file_name), 'r')
    old_gpx = gpxpy.parse(gpx_input_file)
    new_gpx = gpxpy.gpx.GPX()

    for old_track in old_gpx.tracks:
        total_segment = track_segments_to_single_segment(old_track)
        new_segments = []


        def create_loop_segment() -> GPXTrackSegment:
            return GPXTrackSegment()


        loop_segment = create_loop_segment()
        for index, point in enumerate(total_segment.points):
            current_coordinates = (point.latitude, point.longitude)
            # check if point is last
            if len(total_segment.points) == (index + 1):
                last_point = total_segment.points[index - 1]
                last_coordinates = (last_point.latitude, last_point.longitude)
                if is_exact(current_coordinates, last_coordinates):
                    loop_segment.points.append(point)
                    new_segments.append(loop_segment)
                break
            next_point = total_segment.points[index + 1]
            next_coordinates = (next_point.latitude, next_point.longitude)

            if is_exact(current_coordinates, next_coordinates):
                print("appending current and next point to segment")
                loop_segment.points.append(point)
                loop_segment.points.append(next_point)
            else:
                print("current point too far from next, discarding point")

                new_segments.append(loop_segment)
                loop_segment = create_loop_segment()

        print("appending track {0}...".format(old_track.type))
        old_track.segments = new_segments
        new_gpx.tracks.append(old_track)

    new_gpx.waypoints = old_gpx.waypoints
    xml = new_gpx.to_xml()
    gpx_output_file = open('./out/exact/{0}'.format(file_name), 'w')
    gpx_output_file.write(xml)
    gpx_output_file.close()
