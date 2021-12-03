#Importacion de módulos
import pygame, sys, os
from pygame.locals import *

#Constantes
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
IMG_DIR = "imagenes"
SONIDO_DIR = "sonidos"

#Clases y Funciones
def load_image(nombre, dir_imagen, alpha=False):
	#Funcion para cargar imagenes
	#Encontramos la ruta completa de la imagen
	ruta = os.path.join(dir_imagen, nombre)
	try:
		image = pygame.image.load(ruta)
	except:
		print("Error, no se puede cargar la imagen: " + ruta)
		sys.exit(1)
	#Comporbar si la imagen tiene "canal alpha" (como los png)
	if alpha is True:
		image = image.convert_alpha()
	else:
		image = image.convert()
	return image

def load_sonido(nombre, dir_sonido):
	#Funcion para cargar sonidos
	#Encontramos la ruta completa del sonido
	ruta = os.path.join(dir_sonido, nombre)
	try:
		sonido = pygame.mixer.Sound(ruta)
	except (pygame.error) as message:
		print("No se puede cargar el sonido: " + ruta)
		sonido = None
	return sonido


class Pelota(pygame.sprite.Sprite):
	#Clase Pelota
	def __init__(self, sonido_golpe, sonido_punto):
		pygame.sprite.Sprite.__init__(self)
		self.image = load_image("bola.png", IMG_DIR, alpha=True)			
		self.rect = self.image.get_rect()
		self.rect.centerx = int(SCREEN_WIDTH / 2)
		self.rect.centery = int(SCREEN_HEIGHT / 2)
		self.speed = [3, 3]
		self.sonido_golpe = sonido_golpe
		self.sonido_punto = sonido_punto

	def update(self, tablero):
		if self.rect.left < 0:
			self.speed[0] = -self.speed[0]
			self.sonido_punto.play() #Rreproducir el sonido de punto
			tablero.punt2 += 1
			self.rect.centerx = SCREEN_WIDTH / 2
			self.rect.centery = SCREEN_HEIGHT / 2
		elif self.rect.right > SCREEN_WIDTH:
			self.speed[0] = -self.speed[0]
			self.sonido_punto.play() #Rreproducir el sonido de punto
			tablero.punt1 += 1
			self.rect.centerx = SCREEN_WIDTH / 2
			self.rect.centery = SCREEN_HEIGHT / 2
		if self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT:
			self.speed[1] = -self.speed[1]
		self.rect.move_ip((self.speed[0], self.speed[1]))

	def colision(self, objetivo):
		if self.rect.colliderect(objetivo.rect):
			self.speed[0] = -self.speed[0]
			self.sonido_golpe.play()

class Paleta(pygame.sprite.Sprite):
	#Clase Paleta
	def __init__(self, x):
		pygame.sprite.Sprite.__init__(self)
		self.image = load_image("paleta.png", IMG_DIR, alpha=True)
		self.rect = self.image.get_rect()
		self.rect.centerx = x
		self.rect.centery = int(SCREEN_HEIGHT / 2)

	def humano(self):
		#Controlar Paleta
		if self.rect.bottom >= SCREEN_HEIGHT:
			self.rect.bottom = SCREEN_HEIGHT
		elif self.rect.top <= 0:
			self.rect.top = 0

	def cpu(self, pelota):
		#CPU
		self.speed = [0, 2.5]
		if pelota.speed[0] >= 0 and pelota.rect.centerx >= SCREEN_WIDTH / 2:
			if self.rect.centery > pelota.rect.centery:
				self.rect.centery -= self.speed[1]
			if self.rect.centery < pelota.rect.centery:
				self.rect.centery += self.speed[1]
			 
		if self.rect.bottom >= SCREEN_HEIGHT:
			self.rect.bottom = SCREEN_HEIGHT
		elif self.rect.top <= 0:
			self.rect.top = 0

class Puntaje():
	#El tablero con puntajes
	def __init__(self):
		self.punt1 = 0
		self.punt2 = 0
		self.fuente = pygame.font.Font(None, 50) #Se define la letra por defecto

	def update(self):
		self.texto = str(self.punt1) + "    " + str(self.punt2)	
		self.mensaje = self.fuente.render(self.texto, 1, (255, 255, 255))

#Función princiál del juego
def main():
	pygame.mixer.pre_init(44100, -16, 1, 512)
	pygame.init()
	pygame.mixer.init()
	#Creamos la ventana y le indicamos un título
	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
	pygame.display.set_caption("Pong")

	#Cargamos los objetos
	fondo = load_image("fondo.jpg", IMG_DIR, alpha=False)
	fondo = pygame.transform.scale(fondo, (SCREEN_WIDTH, SCREEN_HEIGHT))
	sonido_golpe = load_sonido("tennis.ogg", SONIDO_DIR)
	sonido_punto = load_sonido("aplausos.ogg", SONIDO_DIR)

	bola = Pelota(sonido_golpe, sonido_punto)
	jugador1 = Paleta(25)
	jugador2 = Paleta(SCREEN_WIDTH - 25)
	tablero = Puntaje()
	

	clock = pygame.time.Clock()
	#Activa la repetecion de la tecla al mantenerla pulsada
	pygame.key.set_repeat(1, 25)
	pygame.mouse.set_visible(False) 

	#Bucle principal del juego
	while True:
		clock.tick(60)
		
		#Obtenemos la posicion del mouse
		pos_mouse = pygame.mouse.get_pos()
		mov_mouse = pygame.mouse.get_rel()
	

		#Actualizamos los objetos en la pantalla
		bola.update(tablero)
		jugador1.humano()
		jugador2.cpu(bola)
		todos = pygame.sprite.Group(bola, jugador1, jugador2)
		tablero.update()

		#Comprobamos si colisionan los objetos
		bola.colision(jugador1)
		bola.colision(jugador2)
		
		#Posibles entradas de teclado/mouse
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				#La X de la ventana
				sys.exit(0)
			elif event.type == pygame.KEYDOWN:
				if event.key == K_UP:
					jugador1.rect.centery -= 5
				elif event.key == K_DOWN:
					jugador1.rect.centery += 5
				elif event.key == K_ESCAPE:
					sys.exit(0)
			elif event.type == pygame.KEYUP:
				if event.key == K_UP:
					jugador1.rect.centery +=  0
				elif event.key == K_DOWN:
					jugador1.rect.centery += 0
			#Si el mouse no esta quieto, mover la paleta
			elif mov_mouse[1] != 0:
				jugador1.rect.centery = pos_mouse[1]

	

		#Actualizamos la pantalla
		screen.blit(fondo, (0, 0))
		todos.draw(screen)
		screen.blit(tablero.mensaje, (int(SCREEN_WIDTH / 2) - 38, 5))
		"""
		screen.blit(bola.image, bola.rect)
		screen.blit(jugador1.image, jugador1.rect)
		screen.blit(jugador2.image, jugador2.rect)
		"""
		pygame.display.flip()


		

if __name__ == "__main__":
	main()