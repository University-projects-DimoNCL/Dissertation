# The dictionary below is used to store the last objects within an appropriate frame distance.
# This is a basically a windowed table.
# How tables are supposed to work.
# events = app.Table('table_topic', default=int, key_type=int, value_type=Kitti_Event, partitions=1)
dictionary_ev = {}
# The next variable is a counter starting from zero and keeps track overall headcounts found by the algorithm.
overall_headcounts: int = 0
# The next variable holds the maximum difference in frames between two objects that allows a social distance check
# to be performed
violated_social_distance_count: int = 0
measure_social_distance_count: int = 0
frame_Distance = 4
# These values are used for the position estimation
camera_focal_length_m = 3.6
camera_focal_length_pix = 0
sensor_width = 8.3
image_width = 520
# This is the average human height in meters
height_Y_meters = 1.76
