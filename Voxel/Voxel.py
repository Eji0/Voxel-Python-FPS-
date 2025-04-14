from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# Cacher le curseur
mouse.visible = False

# Joueur en première personne
player = FirstPersonController(speed=5)

# Sol pour repère visuel
class Ground(Entity):
    def __init__(self, position = (0, 0, 0)):
        super().__init__(
            model="plane", 
            texture="grass", 
            collider="box", 
            position = position, 
        )

# Pistolet 3D
gun = Entity(
    parent=camera,
    model="cube",  # Remplace par un vrai modèle si dispo
    scale=(0.2, 0.1, 0.4),
    position=(0.4, -0.2, 0.5),  # Position en bas à droite
    rotation=(0, -90, 0),  # Pointe vers le centre
    color=color.gray
)

# Paramètres de caméra
normal_fov = 90
zoom_fov = 40
is_zoomed = False

# Fonction pour tirer un projectile
def shoot():
    # Déterminer le point de départ du tir
    if is_zoomed:
        bullet_start_pos = camera.world_position + camera.forward * 0.5  # Centre écran en zoom
    else:
        bullet_start_pos = gun.world_position + gun.forward * 0.5  # Bout du pistolet

    # Créer le projectile
    bullet = Entity(
        model="sphere",
        scale=0.05,
        color=color.red,
        position=bullet_start_pos,
        collider="box"
    )

    # La balle se déplace dans la direction où regarde la caméra
    bullet.velocity = camera.forward * 15  # Vitesse vers l'avant

    # Mise à jour du mouvement des balles
    def update_bullet():
        bullet.position += bullet.velocity * time.dt  # Déplacement en fonction du temps
        if bullet.world_position.y < -5:  # Supprimer si trop bas (évite fuite mémoire)
            destroy(bullet)

    bullet.update = update_bullet  # Assigner la fonction à la balle
    destroy(bullet, delay=2)  # Auto-destruction après 2s

# Gestion des entrées clavier / souris
def input(key):
    global is_zoomed
    if key == "left mouse down":
        shoot()

    if key == "right mouse down":
        is_zoomed = True
        camera.fov = zoom_fov
        gun.position = (0, -0.2, 0.5)  # Recentre l'arme sur Y

    if key == "right mouse up":
        is_zoomed = False
        camera.fov = normal_fov
        gun.position = (0.4, -0.2, 0.5)  # Remet l'arme en bas à droite

for x in range(-16, 16):
    for z in range(-16, 16):
        ground = Ground(position=(x, 0, z))

app.run()
