import random
import math

def should_bullet_spawn(percentage):
	return random.uniform(0, 1) < percentage

def get_distance(first_point, second_point):
	return math.sqrt((second_point[0] - first_point[0]) ** 2 + (second_point[1] - first_point[1]) ** 2)

def get_nearest_point(reference_point, points):
	nearest_point = [-1, -1]
	closest_distance = -1

	for point in points:
		distance = get_distance(point, reference_point)
		if closest_distance == - 1 or distance < closest_distance:
			closest_distance = distance
			nearest_point = point

		print(closest_distance)

	return nearest_point

