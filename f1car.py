import numpy as np
import pygame
import math


class Car:
	def __init__(self, starting_point: tuple[int, int], game_map, border_color, screen):
		# Setting Values
		self.min_speed = 5
		self.max_speed = 40

		# Car
		self.image = r"Images\F1Car_2.png"
		self.xsize = 57
		self.ysize = 20
		self.half_xsize = self.xsize // 2
		self.half_ysize = self.ysize // 2

		# Map
		self.game_map = game_map
		self.map_xsize = self.game_map.get_size()[0]
		self.map_ysize = self.game_map.get_size()[1]
		self.game_border_color = border_color
		self.game_screen = screen

		# Car World Position
		self.screen_position = starting_point  # From the center
		self.angle = 0

		# Image
		image = pygame.image.load(self.image).convert_alpha()
		self.original_sprite = pygame.transform.scale(image, (self.xsize, self.ysize))
		self.sprite = self.original_sprite

		# Car Points
		self.center = [0, 0]  # Center Point
		self.corners = []  # Corners Points
		self.borders = []  # Middle Borders Points

		# Radar Points
		self.radars = []  # Radar Points
		self.radar_length = 100

		# IA Variables
		self.is_alive = True
		self.speed = self.min_speed

		# Rewards
		self.medium_speed = 0  # (medium - max_speed) * 2 => [-70, 0] (is keep alive at the end this is 0 -> good reward)
		self.angles_taked = 0  # Lower == Better
		self.distance_traveled = 0  # Higher == Better
		self.ticks_alive = 0  # Higher == Better

		# Calculations
		self.radians = math.radians(self.angle)
		self.cos = math.cos(self.radians)
		self.sin = math.sin(self.radians)

		# Post Init
		self.center = self.get_center_point()
		self.corners = self.get_corners_points()
		self.borders = self.get_borders_points()
		self.radars = self.get_5_points_radars()

	def __str__(self):
		return (
			f"F1Car:\n"
			f"  - Starting Point: {self.screen_position}\n"
			f"  - Speed Range: {self.min_speed} to {self.max_speed}\n"
			f"  - Car Image: {self.image}\n"
			f"  - Car Size: {self.xsize}x{self.ysize}\n"
			f"  - Half Car Size: {self.half_xsize}x{self.half_ysize}\n"
			f"  - Map Size: {self.map_xsize}x{self.map_ysize}\n"
			f"  - Game Border Color: {self.game_border_color}\n"
			f"  - Game Screen: {self.game_screen}\n"
			f"  - Angle: {self.angle}\n"
			f"  - Original Sprite: {self.original_sprite}\n"
			f"  - Sprite: {self.sprite}\n"
			f"  - Center Point: {self.center}\n"
			f"  - Corners Points: {self.corners}\n"
			f"  - Borders Points: {self.borders}\n"
			f"  - Radars: {self.radars}\n"
			f"  - Radar Length: {self.radar_length}\n"
			f"  - Is Alive: {self.is_alive}\n"
			f"  - Speed: {self.speed}\n"
			f"  - Medium Speed: {self.medium_speed}\n"
			f"  - Angles Taked: {self.angles_taked}\n"
			f"  - Distance Traveled: {self.distance_traveled}\n"
			f"  - Ticks Alive: {self.ticks_alive}\n"
			f"  - Radians: {self.radians}\n"
			f"  - Cosine: {self.cos}\n"
			f"  - Sine: {self.sin}\n"
		)

	def update(self):
		# AI Functions have been executed (accelerate, deccelerate, turn) so speed, angle may have changed

		if not self.is_alive: return  # If not alive -> Do nothing

		self.distance_traveled += self.speed
		self.ticks_alive += 1

		# Recalculate for the new positions
		self.screen_position = int(self.screen_position[0] + self.cos * self.speed), int(self.screen_position[1] - self.sin * self.speed)

		self.center = self.get_center_point()
		self.corners = self.get_corners_points()
		self.borders = self.get_borders_points()
		self.radars = self.get_5_points_radars()

		self.draw()
		self.check_is_alive()

	def update_angle(self, angle):
		self.angle += angle
		self.radians = math.radians(self.angle)
		self.cos = math.cos(self.radians)
		self.sin = math.sin(self.radians)
		self.angles_taked += abs(angle)

	# AI Funtions
	def get_reward(self):
		return (self.distance_traveled + self.medium_speed - (self.angles_taked // 2)) // 32

	def accelerate(self):
		self.speed = max(self.min_speed, min(self.speed, self.max_speed))
		if 5 <= self.speed < 15: self.speed += 4
		elif 15 <= self.speed < 22: self.speed += 3
		elif 22 <= self.speed < 32: self.speed += 2
		elif 32 <= self.speed < 40: self.speed += 1

	def deccelerate(self):
		self.speed = max(self.min_speed, self.speed - 5)  # Remove 5 in speed but min speed is 5

	def turn(self, left: bool, big: bool):
		speeds = [0, 15, 25, 35, 41]
		angles = [8, 6, 4, 2]

		for i in range(len(speeds) - 2):
			if speeds[i] <= self.speed < speeds[i + 1]:
				angle = angles[i]

				if not left: angle = -angle
				if not big: angle //= 2

				self.update_angle(angle)
				return

	# Car Points
	def get_center_point(self):
		return int(max(0, min(self.half_xsize + self.screen_position[0], self.map_xsize - 1))), int(max(0, min(self.half_ysize + self.screen_position[1], self.map_ysize - 1)))

	def get_corners_points(self):
		hx, hy = self.half_xsize, self.half_ysize
		return self.__get_points_positions([(-hx, -hy), (hx, -hy), (hx, hy), (-hx, hy)])

	def get_borders_points(self):
		hx, hy = self.half_xsize, self.half_ysize
		return self.__get_points_positions([(-hx, 0), (0, -hy), (hx, 0), (0, hy)])

	def __get_points_positions(self, reference_point_position: list[tuple[int, int]]):
		points_without_rotations = np.array(reference_point_position)

		rotation_matrix = np.array([[self.cos, -self.sin], [self.sin, self.cos]])

		# Apply rotation to each corner and add center coordinates
		points_with_rotations = np.dot(points_without_rotations, rotation_matrix) + np.array(self.center)

		# Limit values to map size to avoid errors
		return [(int(max(0, min(x, self.map_xsize - 1))), int(max(0, min(y, self.map_ysize - 1)))) for x, y in points_with_rotations]

	# Radar Points
	def get_5_points_radars(self):
		radars_values = [
			(self.borders[1], self.radar_length, 80),  # Border Left
			(self.corners[1], self.radar_length, 45),  # Corner Top Left
			(self.borders[2], self.radar_length, 0),  # Border Top
			(self.corners[2], self.radar_length, -45),  # Corner Top Right
			(self.borders[3], self.radar_length, -80)  # Border Right
		]
		return self.__get_radars(radars_values)

	def __get_radars(self, values):
		"""
		Get Radars values - Simple and not Optimize Way
		:param values: Tuple[ StartPoint: Tuple[int, int], max_length: int, angle: int ]
		:return: List[ StartPoint: Tuple[int, int], EndPoint: Tuple[int, int], DistanceToBorder: int ]
		"""

		radars = []
		for start, max_length, angle in values:
			radians = math.radians(self.angle + angle)
			cos, sin = math.cos(radians), math.sin(radians)

			x, y, length = 0, 0, 1
			while length < max_length:
				x, y = max(0, min(int(start[0] + cos * length), self.map_xsize - 1)), max(0, min(int(start[1] - sin * length), self.map_ysize - 1))

				if self.game_map.get_at((x, y)) == self.game_border_color: break

				length += 1

			radars.append((start, (x, y), length))
		return radars

	def get_radars_distances(self):
		return [radar[2] for radar in self.radars]

	# Draw on Screen
	def draw(self, _center: bool = True, _corners: bool = True, _borders: bool = True, _radars: bool = True):
		center_color = (0, 0, 255)
		corners_color = (255, 0, 0)
		borders_color = (0, 255, 0)
		radars_color = (100, 100, 255)

		# Show image in screen
		self.game_screen.blit(self.sprite, (int(self.center[0] - self.sprite.get_width() / 2), int(self.center[1] - self.sprite.get_height() / 2)))
		# Rotate the image
		self.sprite = self.original_sprite
		self.sprite = pygame.transform.rotate(self.sprite, self.angle)

		if _center: pygame.draw.circle(self.game_screen, center_color, self.center, 3)
		if _corners: [pygame.draw.circle(self.game_screen, corners_color, corner, 3) for corner in self.corners]
		if _borders: [pygame.draw.circle(self.game_screen, borders_color, border, 3) for border in self.borders]
		if _radars:
			for start, end, distance in self.radars:
				pygame.draw.line(self.game_screen, radars_color, start, end, 1)
				pygame.draw.circle(self.game_screen, radars_color, end, 3)

	# Other Functions
	def selfkill(self):
		self.is_alive = False
		if self.distance_traveled != 0: self.medium_speed = self.distance_traveled // self.ticks_alive; return
		print("Error - Distance Traveled equals 0")
		print(self)

	def check_is_alive(self):
		for point in self.corners:
			if self.game_map.get_at(point) == self.game_border_color: self.selfkill()
			if point[0] == self.map_xsize - 1 or point[1] == self.map_ysize - 1: self.selfkill()
