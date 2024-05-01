from track import get_track_infos
from f1car import Car
import pygame
import neat

WIDTH = 1280
HEIGHT = 720

generation = 0
track_path = r"Images\Track_1.png"
start_position = (0, 0)
border_color = (0, 0, 0, 0)


def simulation(genomes, config):
	global generation

	nets, cars = [], []  # Empty Collections For Nets and Cars

	pygame.init()
	game_map = pygame.transform.scale(pygame.image.load(track_path), (WIDTH, HEIGHT))
	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	clock = pygame.time.Clock()
	font = pygame.font.SysFont("OCR A", 20)

	for i, g in genomes:
		cars.append(Car(start_position, game_map, border_color, screen))
		nets.append(neat.nn.FeedForwardNetwork.create(g, config))
		g.fitness = 0

	generation += 1

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT: break
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE: break
				if event.key == pygame.K_SPACE:
					for car in cars:
						if car.is_alive:
							car.selfkill()

		screen.blit(game_map, (0, 0))

		for i, car in enumerate(cars):
			output = nets[i].activate(car.get_radars_distances())
			# Choices
			match (output.index(max(output))):
				case 0: car.turn(True, True)
				case 1: car.turn(True, False)
				case 2: car.turn(False, True)
				case 3: car.turn(False, False)
				case 4: car.accelerate()
				case 5: car.deccelerate()

		still_alive = 0

		for i, car in enumerate(cars):
			if not car.is_alive: continue
			still_alive += 1
			car.update()
			genomes[i][1].fitness += car.get_reward()

		if still_alive == 0: break

		text = font.render(f"Alive: {still_alive:2} | Generation: {generation:3}", True, (255, 255, 255))
		screen.blit(text, (200, 600))

		pygame.display.flip()
		clock.tick(60)


def main():
	global track_path, start_position, border_color

	track_path = r"Images\Track_1.png"
	start_position, border_color = get_track_infos(track_path, WIDTH, HEIGHT)

	# Load Config
	config_path = "neat_config.txt"
	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

	# Create Population And Add Reporters
	population = neat.Population(config)
	population.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	population.add_reporter(stats)

	# Run Simulation For A Maximum of 1000 Generations
	population.run(simulation, 1000)


if __name__ == '__main__':
	main()
