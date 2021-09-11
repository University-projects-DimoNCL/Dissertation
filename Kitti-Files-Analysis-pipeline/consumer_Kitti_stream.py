import functions
import statsistics
from Records import Records

import faust
import config

app = faust.App('faust_consumer', broker='kafka:\\localhost:9092')

consume_topic = app.topic('kitti_files', value_serializer='raw', partitions=1)
json_event_values_topic = app.topic('kitti_json', value_serializer='json', partitions=1, value_type=Records.Kitti_Event)
processed_events_json_topic = app.topic('processed_kitti_json', value_serializer='json', partitions=1,
                                        value_type=Records.Kitti_Event)
social_distancing_violated_topic = app.topic('social_distance', value_serializer='json')


# This agent consumes the raw kitti file values
# and turns them into a custom Kitti_Events that are in json format and are easier to work with.
@app.agent(consume_topic)
async def convert_json_kitti(stream):
    async for kitti in stream:
        # print(kitti.decode('utf-8'))
        split_list = (kitti.decode('utf-8')).split()
        '''
        This prints the kitti event before it is sent to its topic (Used for testing if the values are correct) 
        
        kit_prt = Records.Kitti_Event(split_list[0], split_list[1], split_list[2], split_list[3], split_list[4], 
        split_list[5], split_list[6], split_list[7], split_list[8], split_list[9], split_list[10], split_list[11], 
        split_list[12], split_list[13], split_list[14], split_list[15], split_list[16]) print(kit_prt) '''
        await json_event_values_topic.send(
            value=Records.Kitti_Event(split_list[0], split_list[1], split_list[2], split_list[3], split_list[4],
                                      split_list[5],
                                      split_list[6], split_list[7], split_list[8], split_list[9], split_list[10],
                                      split_list[11],
                                      split_list[12], split_list[13], split_list[14], split_list[15], split_list[16]),
            value_serializer='json')


# In here some values are updated or added to the objects
@app.agent(json_event_values_topic)
async def process_json_kitti(stream):
    async for event in stream:
        # The center point of the bbox object is found in X,Y pixel coordinates.
        center = functions.find_object_center_pixels(float(event.top_left_x), float(event.top_left_y),
                                                     float(event.bottom_right_x),
                                                     float(event.bottom_right_y))
        # Height of the bbox object is calculated
        height = functions.obj_height_pixels(float(event.top_left_y), float(event.bottom_right_y))
        # The focal length of the camera is converted to pixels using the width of the image in pixels,focal length
        # in mm and the sensor width in mm
        focal_pix = functions.convert_focal_length_mm_to_pixels(config.image_width, config.camera_focal_length_m,
                                                                config.sensor_width)
        '''Next two comments are used for troubleshooting
        print(event)
        print(height)
        print(center)
        '''
        # All The values found above are updated in the kitti object
        event.obj_height_pix = height
        event.obj_center_pix_x = center.x
        event.obj_center_pix_y = center.y
        event.dimension_height = config.height_Y_meters
        # By having those values and an estimation of pedestrian height we can find Z in Meters
        z = functions.object_depth_Z(float(event.dimension_height), float(event.obj_height_pix), float(focal_pix))
        # Knowing Z we can substituted and find the exact location of the object in the real world (relative to the
        # image)
        location = functions.find_object_center_meters(float(event.obj_center_pix_x), float(event.obj_center_pix_y),
                                                       float(focal_pix), z)
        # print(event)
        # print(z)
        # print(location)
        # We assign this location to the object parameters
        event.location_x_m = location.x
        event.location_y_m = location.y
        event.location_z_m = location.z
        '''Next two comments are used for troubleshooting'''
        # print(event)
        # print(f"The x center pix {event.obj_center_pix_x} and the y {event.obj_center_pix_y} ")

        # We send the processed object to a new topic.
        await processed_events_json_topic.send(value=event, value_serializer='json')


@app.agent(processed_events_json_topic)
async def process_kitti_events_in_table(stream):
    async for event in stream.group_by(Records.Kitti_Event.frame_id):
        # if an entry with that key does not exist in the dictionary
        if event.track_id not in list(config.dictionary_ev):
            config.overall_headcounts += 1  # Increments the counter of the overall distinct object headcounts
            for key in list(config.dictionary_ev):
                if abs(int(config.dictionary_ev[key].frame_id) - int(event.frame_id)) <= config.frame_Distance:
                    config.measure_social_distance_count += 1
                    # print('VinIF Social Distancing will be measured and the item will be added to the dictionary')
                    distance = functions.distance_between_2points_in_3d_space(float(event.location_x_m),
                                                                              float(event.location_y_m),
                                                                              float(event.location_z_m),
                                                                              float(config.dictionary_ev[
                                                                                        key].location_x_m),
                                                                              float(config.dictionary_ev[
                                                                                        key].location_y_m),
                                                                              float(config.dictionary_ev[
                                                                                        key].location_z_m))
                    if distance >= 1:
                        print(f'There is social distancing in frame {event.frame_id}')
                    else:
                        config.violated_social_distance_count += 1
                        print(f'\n\t'
                              f'Social Distancing Violated in frame {event.frame_id},\n\t'
                              f'No social distancing between object id{event.track_id}'
                              f'and object id {config.dictionary_ev[key].track_id}')
                        holder = Records.violate_s_distance_holder(event.frame_id, config.dictionary_ev[key].frame_id,
                                                                   event.track_id, config.dictionary_ev[key].track_id,
                                                                   config.frame_Distance
                                                                   )

                        await social_distancing_violated_topic.send(value=holder, value_serializer='json')
                else:
                    config.dictionary_ev.pop(key)
                    # print('1 Item was removed from the dict 1')
        else:  # If even.track_id is a key in events
            for key in list(config.dictionary_ev):
                if abs(int(config.dictionary_ev[key].frame_id) - int(
                        event.frame_id)) <= config.frame_Distance and key != event.track_id:
                    # print('VinEl Social distancing will be measured')
                    distance = functions.distance_between_2points_in_3d_space(float(event.location_x_m),
                                                                              float(event.location_y_m),
                                                                              float(event.location_z_m),
                                                                              float(config.dictionary_ev[
                                                                                        key].location_x_m),
                                                                              float(config.dictionary_ev[
                                                                                        key].location_y_m),
                                                                              float(config.dictionary_ev[
                                                                                        key].location_z_m))
                    if distance >= 1:
                        print(
                            f'There is social distancing in frame {event.frame_id} and there are '
                            f' {len(list(config.dictionary_ev))} '
                            f' headcounts detected in the last {config.frame_Distance}')
                    else:
                        print(f'\n\t'
                              f'Social Distancing Violated in frame {event.frame_id},\n\t'
                              f'No social distancing between object id {event.track_id} \t'
                              f' and object id {config.dictionary_ev[key].track_id}'
                              f'there are  {len(list(config.dictionary_ev))}'
                              f' headcounts detected in the last {config.frame_Distance}'
                              )
                        holder = Records.violate_s_distance_holder(event.frame_id, config.dictionary_ev[key].frame_id,
                                                                   event.track_id, config.dictionary_ev[key].track_id,
                                                                   config.frame_Distance
                                                                   )

                        await social_distancing_violated_topic.send(value=holder, value_serializer='json')
                else:
                    config.dictionary_ev.pop(key)
                    # print('2 Item was removed from the dict 2')
        config.dictionary_ev[event.track_id] = event
        # print(dictionary_ev)


'''A Function that prints the headcounts found by the program in a certain range and at all.
It works at a set interval of time.
'''


# @app.agent(social_distancing_violated_topic)
# async def write_to_csv(stream):
#     async for event in stream:
#         async with open('violated.csv', 'w', newline='') as file:
#             writer = csv.writer(file)
#             writer.writerow(event.frame_id1, event.frame_id2, event.track_id1, event.track_id2, event.frame_distance)


@app.timer(interval=10)
async def print_headcounts():
    functions.headcounts()


@app.timer(interval=30)
async def print_stats():
    print(f'Social distancing is violated {statsistics.how_often_violated() * 100} % of the time! ')


if __name__ == '__main__':
    app.main()
