import pygame
import random
import sys
import time
import cv2
import numpy as np

# Initialize Pygame
pygame.init()

# Ensure pygame.mixer is initialized
pygame.mixer.init()

# Screen dimensions
WIDTH, HEIGHT = 600, 800

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fighter Jet Game")
clock = pygame.time.Clock()

# Load images
plane_image = pygame.image.load(r"GAME\jet2.png.crdownload")
bullet_image = pygame.image.load(r"GAME\ullet1.png")
obstacle_image = pygame.image.load(r"GAME\obstacle2.png")
power_image = pygame.image.load(r"GAME\power.png")

# Load collision sound
collision_sound = pygame.mixer.Sound(r"GAME\voice.mp3")

# Scale images
new_width = 150
plane_width, plane_height = plane_image.get_size()
new_height = int((new_width / plane_width) * plane_height)
plane_image = pygame.transform.scale(plane_image, (new_width, new_height))
bullet_image = pygame.transform.scale(bullet_image, (20, 40))
obstacle_image = pygame.transform.scale(obstacle_image, (50, 50))
power_image = pygame.transform.scale(power_image, (40, 40))

# Plane settings
plane_x, plane_y = WIDTH // 2, HEIGHT - 150
plane_speed = 10
plane_angle = 0

# Bullet settings
bullets = []
last_fired_time = 0
fire_rate = 0.3

# Missile settings
missiles = []
missile_speed = 15
can_launch_missiles = False
missile_launch_time = 0
missile_cooldown = 1

# Obstacle settings
obstacles = []
obstacle_speed = 2
spawn_rate = 25

# Power-up settings
power_x, power_y = random.randint(0, WIDTH - 40), random.randint(-100, -40)
power_speed = 3

# Score and health
score = 0
health = 3
font = pygame.font.Font(None, 36)

# Game loop flag
running = True

# Video background setup using OpenCV
video_path = r"C:\Users\khanf\OneDrive\Desktop\python\GAME\trimmed.mp4"
cap = cv2.VideoCapture(video_path)

# Check if video opened successfully
if not cap.isOpened():
    print("Error: Unable to open video file.")
    pygame.quit()
    sys.exit()

def get_video_frame():
    ret, frame = cap.read()
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Restart video from the beginning
        ret, frame = cap.read()

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert frame to RGB
    frame = cv2.resize(frame, (WIDTH, HEIGHT))  # Resize frame to fill the screen
    frame = np.rot90(frame)  # Rotate the frame 90 degrees if needed
    frame = pygame.surfarray.make_surface(frame)
    return frame

def draw_plane(x, y, angle):
    rotated_plane = pygame.transform.rotate(plane_image, angle)
    plane_rect = rotated_plane.get_rect(center=(x + new_width // 2, y + new_height // 2))
    screen.blit(rotated_plane, plane_rect.topleft)

def draw_bullet(bullets):
    for bullet in bullets:
        screen.blit(bullet_image, (bullet[0], bullet[1]))

def draw_missiles(missiles):
    for missile in missiles:
        screen.blit(bullet_image, (missile[0], missile[1]))

def draw_obstacles(obstacles):
    for obstacle in obstacles:
        screen.blit(obstacle_image, (obstacle[0], obstacle[1]))

def draw_power(power_x, power_y):
    screen.blit(power_image, (power_x, power_y))

def check_collision(bullets, obstacles):
    global score
    for bullet in bullets[:]:
        for obstacle in obstacles[:]:
            if (
                bullet[0] < obstacle[0] + 50 and
                bullet[0] + 20 > obstacle[0] and
                bullet[1] < obstacle[1] + 50 and
                bullet[1] + 40 > obstacle[1]
            ):
                bullets.remove(bullet)
                obstacles.remove(obstacle)
                score += 1

def check_missile_collision(missiles, obstacles):
    for missile in missiles[:]:
        for obstacle in obstacles[:]:
            if (
                missile[0] < obstacle[0] + 50 and
                missile[0] + 20 > obstacle[0] and
                missile[1] < obstacle[1] + 50 and
                missile[1] + 40 > obstacle[1]
            ):
                missiles.remove(missile)
                obstacles.remove(obstacle)

                # Play collision sound, loop if needed
                if not collision_sound.get_busy():  # Check if sound is not already playing
                    collision_sound.play(loops=0, maxtime=1000)  # Play for 1 second or adjust

def plane_collision(plane_x, plane_y, obstacles):
    global can_launch_missiles, health
    plane_rect = pygame.Rect(plane_x, plane_y, new_width, new_height)
    for obstacle in obstacles[:]:
        obstacle_rect = pygame.Rect(obstacle[0], obstacle[1], 50, 50)
        if plane_rect.colliderect(obstacle_rect):
            obstacles.remove(obstacle)
            if can_launch_missiles:
                can_launch_missiles = False  # Remove power-up effect
                return False
            else:
                health -= 1
                if health <= 0:
                    return True
    return False

# Game loop
frame_count = 0
while running:
    screen.fill((0, 0, 0))

    # Get the next video frame and draw it
    background_frame = get_video_frame()
    screen.blit(background_frame, (0, 0))

    draw_power(power_x, power_y)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Plane movement
    keys = pygame.key.get_pressed()
    plane_angle = 0

    if keys[pygame.K_LEFT] and plane_x > 0:
        plane_x -= plane_speed
        plane_angle = 15
    if keys[pygame.K_RIGHT] and plane_x < WIDTH - new_width:
        plane_x += plane_speed
        plane_angle = -15
    if keys[pygame.K_UP] and plane_y > 0:
        plane_y -= plane_speed
    if keys[pygame.K_DOWN] and plane_y < HEIGHT - new_height:
        plane_y += plane_speed

    # Shooting bullets
    current_time = time.time()
    if keys[pygame.K_SPACE] and current_time - last_fired_time > fire_rate:
        # Adjust bullet positions for better spacing
        bullets.append([plane_x + new_width // 2 - 10, plane_y])  # Middle bullet

        if can_launch_missiles:
            # Left bullet a little farther from the center
            bullets.append([plane_x + new_width // 4 - 10, plane_y + 10])  # Left bullet a little farther
            # Right bullet equally spaced from the center
            bullets.append([plane_x + new_width * 3 // 4 - 10, plane_y + 10])  # Right bullet equally spaced

        last_fired_time = current_time

    # Moving bullets
    for bullet in bullets[:]:
        bullet[1] -= 10
        if bullet[1] < 0:
            bullets.remove(bullet)

    # Spawn obstacles
    if frame_count % spawn_rate == 0:
        obstacle_x = random.randint(0, WIDTH - 50)
        obstacles.append([obstacle_x, -50])

    # Move obstacles
    for obstacle in obstacles[:]:
        obstacle[1] += obstacle_speed
        if obstacle[1] > HEIGHT:
            obstacles.remove(obstacle)

    # Move power-up
    power_y += power_speed
    if power_y > HEIGHT:
        power_x, power_y = random.randint(0, WIDTH - 40), random.randint(-100, -40)

    # Check collisions
    check_collision(bullets, obstacles)
    check_missile_collision(missiles, obstacles)
    if plane_collision(plane_x, plane_y, obstacles):
        print("Game Over! Your score:", score)
        pygame.quit()
        sys.exit()

    # Power-up collection
    if (plane_x < power_x + 40 and
        plane_x + new_width > power_x and
        plane_y < power_y + 40 and
        plane_y + new_height > power_y):
        can_launch_missiles = True
        power_x, power_y = random.randint(0, WIDTH - 40), random.randint(-100, -40)

    # Draw everything
    draw_plane(plane_x, plane_y, plane_angle)
    draw_bullet(bullets)
    draw_obstacles(obstacles)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    health_text = font.render(f"Health: {health}", True, (255, 0, 0))
    screen.blit(score_text, (10, 10))
    screen.blit(health_text, (10, 50))

    frame_count += 1
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
cap.release()
