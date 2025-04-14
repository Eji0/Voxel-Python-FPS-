from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import socket
import threading

app = Ursina()

# Variables globales
game_started = False
is_zoomed = False
bullets = []
network_thread = None
sock = None
aide_text = None

def start_game():
    global player, gun

    camera.fov = 90
    mouse.visible = False

    player = FirstPersonController(speed=7, jump_height=3)
    player.collider = 'box'

    for x in range(-16, 16):
        for z in range(-16, 16):
            Entity(model="plane", texture="grass", collider="box", position=(x, 0, z), scale=(1, 1, 1))

    gun = Entity(
        parent=camera,
        model="cube",
        scale=(0.2, 0.1, 0.4),
        position=(0.4, -0.2, 0.5),
        rotation=(0, -90, 0),
        color=color.gray
    )

    def update():
        for bullet in bullets:
            bullet.position += bullet.velocity * time.dt
            if bullet.y < -5:
                destroy(bullet)
                bullets.remove(bullet)

    app.update = update

def shoot():
    global is_zoomed
    start_pos = camera.world_position + camera.forward * 0.5 if is_zoomed else gun.world_position + gun.forward * 0.5
    bullet = Entity(model='sphere', scale=0.05, color=color.red, position=start_pos, collider='box')
    bullet.velocity = camera.forward * 15
    bullets.append(bullet)
    destroy(bullet, delay=2)

def input(key):
    global is_zoomed
    if not game_started:
        return

    if key == "left mouse down":
        shoot()
    if key == "right mouse down":
        is_zoomed = True
        camera.fov = 40
        gun.position = (0, -0.2, 0.5)
    if key == "right mouse up":
        is_zoomed = False
        camera.fov = 90
        gun.position = (0.4, -0.2, 0.5)

def host_game():
    global sock, network_thread, game_started

    ip = input_field.text.strip()
    if not ip:
        ip = '0.0.0.0'

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, 12345))
    print("Serveur en écoute sur", ip)

    def server_loop():
        while True:
            try:
                data, addr = sock.recvfrom(1024)
                print("Reçu:", data, "de", addr)
            except:
                break

    network_thread = threading.Thread(target=server_loop, daemon=True)
    network_thread.start()

    destroy_all_buttons()
    start_game()
    global game_started
    game_started = True

def join_game():
    global sock, network_thread, game_started

    ip = input_field.text.strip()
    if not ip:
        print("IP non valide")
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def client_loop():
        while True:
            try:
                sock.sendto(b"Hello serveur", (ip, 12345))
                data, addr = sock.recvfrom(1024)
                print("Reçu:", data)
            except:
                break

    network_thread = threading.Thread(target=client_loop, daemon=True)
    network_thread.start()

    destroy_all_buttons()
    start_game()
    game_started = True

def afficher_aide():
    global aide_text
    if aide_text:
        aide_text.enabled = not aide_text.enabled
    else:
        aide_text = Text(
            text=(
                "Pour héberger :\n"
                "- Cliquez sur 'Héberger'\n"
                "- Donnez votre IP à vos amis\n"
                "- Autorisez la connexion dans le pare-feu\n\n"
                "Pour rejoindre :\n"
                "- Cliquez sur 'Rejoindre'\n"
                "- Entrez l'IP de l'hôte\n\n"
                "Si vous êtes sur le même réseau, utilisez l’IP locale\n"
                "Sinon, ouvrez le port 12345 sur la box de l'hôte."
            ),
            origin=(0,0),
            scale=1.2,
            x=-0.4,
            y=0.3,
            wordwrap=40,
            color=color.azure
        )

def destroy_all_buttons():
    for e in scene.entities:
        if isinstance(e, Button) or isinstance(e, InputField):
            destroy(e)

# Écran d'accueil
Text("Voxel Multijoueur", scale=2, origin=(0,0), y=0.4)
Button(text="Jouer", scale=(0.2, 0.1), y=0.1, on_click=lambda: afficher_menu_connexion())
Button(text="Quitter", scale=(0.2, 0.1), y=-0.1, on_click=application.quit)

# Menu de connexion (masqué au départ)
def afficher_menu_connexion():
    destroy_all_buttons()
    global input_field
    Text("Connexion au jeu", scale=1.5, origin=(0,0), y=0.4)
    input_field = InputField(default='127.0.0.1', y=0.2)
    Button(text="Héberger", y=0.05, on_click=host_game)
    Button(text="Rejoindre", y=-0.1, on_click=join_game)
    Button(text="Aide", y=-0.25, on_click=afficher_aide)
    Button(text="Retour", y=-0.4, on_click=lambda: restart_app())

def restart_app():
    destroy_all_buttons()
    if aide_text:
        aide_text.enabled = False
    Text("Voxel Multijoueur", scale=2, origin=(0,0), y=0.4)
    Button(text="Jouer", scale=(0.2, 0.1), y=0.1, on_click=lambda: afficher_menu_connexion())
    Button(text="Quitter", scale=(0.2, 0.1), y=-0.1, on_click=application.quit)

app.run()
