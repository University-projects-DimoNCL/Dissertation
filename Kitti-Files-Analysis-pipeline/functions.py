from Records import Records
import math
import config


# Gets the top-left and bottom-right  pixel of the bounding box
# and finds the coordinates that are in the  center of the bbox
def find_object_center_pixels(x1, y1, x2, y2):
    dif_x = abs(x1 - x2)
    dif_y = abs(y1 - y2)
    x: float
    y: float
    if x1 > x2:
        x = x1 - (dif_x / 2)
    else:
        x = x2 - (dif_x / 2)
    if y1 > y2:
        y = y1 - (dif_y / 2)
    else:
        y = y2 - (dif_y / 2)
    return Records.center_point(x, y)


def find_object_center_meters(x_center_pix, y_center_pix, focal_length_pixels, obj_depth):
    x_m = x_center_pix * obj_depth / focal_length_pixels
    y_m = y_center_pix * obj_depth / focal_length_pixels

    return Records.position_3d(x_m, y_m, obj_depth)


# returns an absolute value of the height of an object in pixels
def obj_height_pixels(y1, y2):
    return abs(y1 - y2)


# Returns Z or the object depth of an object

def object_depth_Z(obj_height_meters, obj_height_pix, focal_length_pixels):
    return focal_length_pixels * obj_height_meters / obj_height_pix


# Convert the focal length from mm to pixels in order to be used in formulas

def convert_focal_length_mm_to_pixels(image_width_pix, focal_length_mm, sensor_width_mm):
    return image_width_pix * focal_length_mm / sensor_width_mm


def distance_between_2points_in_3d_space(x1, y1, z1, x2, y2, z2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)


def headcounts():
    print(f" \r\n The headcounts for the last {config.frame_Distance} frames: \n\t {len(list(config.dictionary_ev))}"
          f" \n And the overall headcounts since the consumer is running are: \n\t {config.overall_headcounts}"
          )
