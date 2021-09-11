from abc import ABC

import faust


# Here create a record that will hold kitti events as faust records.
class Kitti_Event(faust.Record, ABC, serializer='json'):
    frame_id: int  # The number of the current frame of the camera
    track_id: int  # The unique tracking id of an object
    type: str  # Type of the object(pedestrian)
    truncated: int
    occluded: int
    Alpha: int
    top_left_x: float  # The coordinates of the top-left and bottom right pixels of the bounding box around the object.
    top_left_y: float
    bottom_right_x: float
    bottom_right_y: float
    # The following fields are negative in the kitti files
    # ( This means that they currently don't exist in the kitti files.),
    # but I still assign them, so if in the future they are added they can be used.
    dimension_height_m: float
    dimension_width_m: float
    dimension_length_m: float
    location_x_m: float
    location_y_m: float
    location_z_m: float
    score: int
    obj_height_pix: float = 0
    obj_center_pix_x: float = 0
    obj_center_pix_y: float = 0


class center_point(faust.Record, ABC):
    x: float
    y: float


class position_3d(faust.Record, ABC):
    x: float
    y: float
    z: float


class violate_s_distance_holder(faust.Record, ABC):
    frame_id1: float
    frame_id2: float
    track_id1: float
    track_id2: float
    frame_distance: int
