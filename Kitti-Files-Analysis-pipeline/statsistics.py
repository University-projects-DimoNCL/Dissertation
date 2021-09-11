import config


# Returns the floating point percentage of how many violations of social distancing are happening compared to the
# number of measuring
def how_often_violated():
    violated_measure: int = config.violated_social_distance_count
    overall_measure: int = config.measure_social_distance_count
    if overall_measure == 0:
        return 0
    return violated_measure / overall_measure
