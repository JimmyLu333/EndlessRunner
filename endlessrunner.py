# Step 1: Basic Pygame window and main loop

import pygame
import sys
import random
import os

# Initialize Pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Endless Runner")

# Set up clock
clock = pygame.time.Clock()
FPS = 60

# Font for score
def get_font():
    return pygame.font.SysFont(None, 36)
font = get_font()

# Menu / Dead menu fonts
title_font = pygame.font.SysFont(None, 48)
button_font = pygame.font.SysFont(None, 36)

# Player properties
def reset_player():
    global player_x, player_y, player_vel_y, player_vel_x, on_ground
    player_x = 100
    player_y = HEIGHT - player_height - 40  # 40px ground height
    player_vel_y = 0
    player_vel_x = 0
    on_ground = True

player_width, player_height = 50, 50
reset_player()
gravity = 1
jump_power = -18

# Ground segment properties
GROUND_SCROLL_SPEED = 6
GROUND_MIN_HEIGHT = 30
GROUND_MAX_HEIGHT = 80
GROUND_WIDTH = 120
GAP_MIN = 60
GAP_MAX = 180

# Score system
score = 0
score_timer = 0  # milliseconds

safe_area_segments = int(400 // GROUND_WIDTH) + 1

# Ground generation
def reset_ground():
    global ground_segments, ground_y_base
    ground_segments = []
    ground_y_base = HEIGHT
    current_x = 0
    for _ in range(safe_area_segments):
        ground_segments.append([current_x, 40, GROUND_WIDTH])
        current_x += GROUND_WIDTH
    while current_x < WIDTH + GROUND_WIDTH:
        gap = random.randint(GAP_MIN, GAP_MAX)
        current_x += gap
        height = random.randint(GROUND_MIN_HEIGHT, GROUND_MAX_HEIGHT)
        ground_segments.append([current_x, height, GROUND_WIDTH])
        current_x += GROUND_WIDTH

reset_ground()

BEST_SCORE_FILE = "best_score.txt"
def get_best_score():
    try:
        with open(BEST_SCORE_FILE, "r") as f:
            return int(f.read().strip())
    except Exception:
        return 0

def set_best_score(new_score):
    with open(BEST_SCORE_FILE, "w") as f:
        f.write(str(new_score))


def show_menu():
    """Show the start menu. Return True to start the game, False to quit."""
    button_width, button_height = 200, 60
    start_button_rect = pygame.Rect((WIDTH//2 - button_width//2, HEIGHT//2 - 80), (button_width, button_height))
    quit_button_rect = pygame.Rect((WIDTH//2 - button_width//2, HEIGHT//2 + 20), (button_width, button_height))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if start_button_rect.collidepoint(mouse_pos):
                    return True
                if quit_button_rect.collidepoint(mouse_pos):
                    return False

        screen.fill((135, 206, 235))
        title_text = title_font.render("Endless Runner", True, (0,0,0))
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 80))

        pygame.draw.rect(screen, (100, 200, 100), start_button_rect)
        start_text = button_font.render("Start", True, (0,0,0))
        screen.blit(start_text, (start_button_rect.centerx - start_text.get_width()//2, start_button_rect.centery - start_text.get_height()//2))

        pygame.draw.rect(screen, (200, 100, 100), quit_button_rect)
        quit_text = button_font.render("Quit", True, (0,0,0))
        screen.blit(quit_text, (quit_button_rect.centerx - quit_text.get_width()//2, quit_button_rect.centery - quit_text.get_height()//2))

        pygame.display.flip()
        clock.tick(FPS)


def show_dead_menu(current_score, best_score):
    """Show the dead menu. Return 'restart', 'menu', or 'quit'."""
    button_width, button_height = 200, 60
    restart_button_rect = pygame.Rect((WIDTH//2 - button_width//2, HEIGHT//2 + 10), (button_width, button_height))
    menu_button_rect = pygame.Rect((WIDTH//2 - button_width//2, HEIGHT//2 + 90), (button_width, button_height))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if restart_button_rect.collidepoint(mouse_pos):
                    return 'restart'
                if menu_button_rect.collidepoint(mouse_pos):
                    return 'menu'

        screen.fill((220, 80, 80))
        title_text = title_font.render("Game Over", True, (0,0,0))
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 60))

        score_text = button_font.render(f"Score: {current_score}", True, (0,0,0))
        best_text = button_font.render(f"Best: {best_score}", True, (0,0,0))
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 140))
        screen.blit(best_text, (WIDTH//2 - best_text.get_width()//2, 180))

        pygame.draw.rect(screen, (100, 200, 100), restart_button_rect)
        restart_text = button_font.render("Restart", True, (0,0,0))
        screen.blit(restart_text, (restart_button_rect.centerx - restart_text.get_width()//2, restart_button_rect.centery - restart_text.get_height()//2))

        pygame.draw.rect(screen, (100, 100, 200), menu_button_rect)
        menu_text = button_font.render("Menu", True, (0,0,0))
        screen.blit(menu_text, (menu_button_rect.centerx - menu_text.get_width()//2, menu_button_rect.centery - menu_text.get_height()//2))

        pygame.display.flip()
        clock.tick(FPS)

# Main game loop
# Show start menu first
start = show_menu()
if not start:
    pygame.quit()
    sys.exit()

running = True
while running:
    dt = clock.tick(FPS)  # milliseconds since last frame
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and on_ground:
                player_vel_y = jump_power
                on_ground = False

    # Get pressed keys
    keys = pygame.key.get_pressed()
    player_vel_x = 0
    if keys[pygame.K_a]:
        player_vel_x = -7
    if keys[pygame.K_d]:
        player_vel_x = 7

    # Apply horizontal movement
    player_x += player_vel_x
    # Keep player within screen bounds
    if player_x < 0:
        player_x = 0
    if player_x > WIDTH - player_width:
        player_x = WIDTH - player_width

    # Apply gravity
    player_vel_y += gravity
    player_y += player_vel_y

    # Scroll ground segments
    for seg in ground_segments:
        seg[0] -= GROUND_SCROLL_SPEED

    # Remove off-screen segments
    while ground_segments and ground_segments[0][0] + ground_segments[0][2] < 0:
        ground_segments.pop(0)

    # Add new segments if needed
    while ground_segments and ground_segments[-1][0] < WIDTH:
        gap = random.randint(GAP_MIN, GAP_MAX)
        new_x = ground_segments[-1][0] + ground_segments[-1][2] + gap
        new_height = random.randint(GROUND_MIN_HEIGHT, GROUND_MAX_HEIGHT)
        ground_segments.append([new_x, new_height, GROUND_WIDTH])

    # Find the ground height under the player (if any)
    player_bottom = player_y + player_height
    player_on_ground = False
    if player_vel_y >= 0:  # Only check collision if falling
        for i, seg in enumerate(ground_segments):
            seg_x, seg_h, seg_w = seg
            seg_top = ground_y_base - seg_h
            if player_x + player_width > seg_x and player_x < seg_x + seg_w:
                # Player is above this segment
                if player_bottom >= seg_top and player_y < seg_top:
                    player_y = seg_top - player_height
                    player_vel_y = 0
                    player_on_ground = True
                    break
    on_ground = player_on_ground

    # Score: add 1 point every second
    score_timer += dt
    if score_timer >= 1000:
        score += 1
        score_timer -= 1000

    # Restart game if player falls off (dead zone)
    if player_y > HEIGHT:
        best_score = get_best_score()
        if score > best_score:
            set_best_score(score)
            best_score = score
        # Show in-process dead menu and handle the player's choice
        choice = show_dead_menu(score, best_score)
        if choice == 'restart':
            # reset game state
            score = 0
            score_timer = 0
            reset_player()
            reset_ground()
            continue
        elif choice == 'menu':
            # go back to main menu
            go_start = show_menu()
            if go_start:
                score = 0
                score_timer = 0
                reset_player()
                reset_ground()
                continue
            else:
                running = False
                break
        else:
            running = False
            break

    screen.fill((135, 206, 235))  # Sky blue background

    # Draw ground segments
    for seg in ground_segments:
        seg_x, seg_h, seg_w = seg
        pygame.draw.rect(screen, (50, 205, 50), (seg_x, ground_y_base - seg_h, seg_w, seg_h))

    # Draw player
    pygame.draw.rect(screen, (255, 100, 100), (player_x, int(player_y), player_width, player_height))

    # Draw score (top right)
    score_text = font.render(f"Score: {score}", True, (0,0,0))
    screen.blit(score_text, (WIDTH - score_text.get_width() - 20, 20))

    pygame.display.flip()

pygame.quit()
sys.exit()
