from PIL import Image

START_POINT_COLOR = (255, 0, 0, 255)



def __get_star_position(image, xsize, ysize):
	for y in range(ysize):
		for x in range(xsize):
			if image.getpixel((x, y)) != START_POINT_COLOR: continue
			return x, y


def get_track_infos(image_path, width, height):
	image = Image.open(image_path)

	xsize, ysize = image.size

	image = image.convert("RGBA")

	border_color = image.getpixel((0, 0))

	x, y = __get_star_position(image, xsize, ysize)

	start_point = int(x * width / xsize), int(y * height / ysize)

	return start_point, border_color


def main():
	track_path = r"Images\Track_1.png"
	print(get_track_infos(track_path, 1280, 720))


if __name__ == '__main__':
	main()
