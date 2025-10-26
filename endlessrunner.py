# Step 1: Basic Pygame window and main loop

import pygame
import sys
import random
import os

# Initialize Pygame
pygame.init()

# Set up display
# Increased resolution
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Endless Runner")

# Set up clock
clock = pygame.time.Clock()
FPS = 60

# Sprite Animation System
class PlayerSprites:
    def __init__(self):
        self.animations = {}
        self.current_animation = 'idle'
        self.frame_index = 0
        self.animation_speed = 0.15
        # Per-frame foot baseline storage (transparent pixels below feet)
        self.frame_foot = {}
        # Baseline used when standing on ground (stable across frames)
        self.run_foot_baseline = None
        # Small base adjustment if needed
        self.foot_offset_base = 1
        # A tiny visual nudge to draw the sprite a few pixels lower (downwards)
        self.draw_offset_down = 0
        self.load_sprites()
    
    def load_sprites(self):
        # Load idle animation - Increase character size further
        self.animations['idle'] = []
        self.frame_foot['idle'] = []
        for i in range(1, 25):  # idle_00001.png to idle_00024.png
            try:
                img = pygame.image.load(f"cloaked char/idle/idle_{i:05d}.png").convert_alpha()
                img = pygame.transform.scale(img, (150, 200))  # Larger size
                # Compute bottom transparent pixels to estimate foot baseline
                bbox = img.get_bounding_rect(min_alpha=1)
                bottom_transparent = img.get_height() - (bbox.y + bbox.height)
                self.animations['idle'].append(img)
                self.frame_foot['idle'].append(bottom_transparent)
            except:
                pass
        
        # Load run animation
        self.animations['run'] = []
        self.frame_foot['run'] = []
        for i in range(6, 19):  # run_00006.png to run_00018.png
            try:
                img = pygame.image.load(f"cloaked char/run/runloop/run_{i:05d}.png").convert_alpha()
                img = pygame.transform.scale(img, (150, 200))  # Larger size
                bbox = img.get_bounding_rect(min_alpha=1)
                bottom_transparent = img.get_height() - (bbox.y + bbox.height)
                self.animations['run'].append(img)
                self.frame_foot['run'].append(bottom_transparent)
            except:
                pass
        # Establish a stable ground baseline using the max across run frames
        if self.frame_foot.get('run'):
            self.run_foot_baseline = max(self.frame_foot['run'])
        else:
            self.run_foot_baseline = 14
        
        # Load jump animation
        self.animations['jump'] = []
        self.frame_foot['jump'] = []
        for i in range(1, 13):  # jump_00001.png to jump_00012.png
            try:
                img = pygame.image.load(f"cloaked char/jump/jump_{i:05d}.png").convert_alpha()
                img = pygame.transform.scale(img, (150, 200))  # Larger size
                bbox = img.get_bounding_rect(min_alpha=1)
                bottom_transparent = img.get_height() - (bbox.y + bbox.height)
                self.animations['jump'].append(img)
                self.frame_foot['jump'].append(bottom_transparent)
            except:
                pass
        
        # Load fall animation
        self.animations['fall'] = []
        self.frame_foot['fall'] = []
        for i in range(12, 25):  # fall_00012.png to fall_00024.png
            try:
                img = pygame.image.load(f"cloaked char/fall/fall_{i:05d}.png").convert_alpha()
                img = pygame.transform.scale(img, (150, 200))  # Larger size
                bbox = img.get_bounding_rect(min_alpha=1)
                bottom_transparent = img.get_height() - (bbox.y + bbox.height)
                self.animations['fall'].append(img)
                self.frame_foot['fall'].append(bottom_transparent)
            except:
                pass

    def ground_foot_offset(self):
        # Use a stable baseline (run animation) plus a small base tweak
        base = self.run_foot_baseline if self.run_foot_baseline is not None else 14
        return int(base + self.foot_offset_base)
    
    def set_animation(self, animation_name):
        if animation_name != self.current_animation and animation_name in self.animations:
            self.current_animation = animation_name
            self.frame_index = 0
    
    def update(self):
        if self.current_animation in self.animations and len(self.animations[self.current_animation]) > 0:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.animations[self.current_animation]):
                self.frame_index = 0
    
    def get_current_sprite(self):
        if self.current_animation in self.animations and len(self.animations[self.current_animation]) > 0:
            return self.animations[self.current_animation][int(self.frame_index)]
        return None

# Initialize player sprites
player_sprites = PlayerSprites()

# Font for score
def get_font():
    return pygame.font.SysFont(None, 36)
font = get_font()

# Menu / Dead menu fonts
title_font = pygame.font.SysFont(None, 48)
button_font = pygame.font.SysFont(None, 36)

# Base safe-ground height (used for player start and safe area)
GROUND_BASE_HEIGHT = 80

# Player properties
def reset_player():
    global player_x, player_y, player_vel_y, player_vel_x, on_ground
    player_x = 100
    player_y = HEIGHT - player_height - GROUND_BASE_HEIGHT
    player_vel_y = 0
    player_vel_x = 0
    on_ground = True

player_width, player_height = 150, 200  # Updated to match larger sprite size
reset_player()
gravity = 1
jump_power = -18
# Double-jump pickup state
double_jump_available = False   # player has pickup and can double-jump
double_jump_used = False        # whether double jump used during current airtime
pickup_spawned = False
pickup_x = 0.0
pickup_y = 0.0
pickup_radius = 18
next_spawn_score = 10  # spawn first at score 10; if missed, set to 20

# Ground segment properties
# Ground scroll speed in pixels per second (time-based)
GROUND_SCROLL_PPS = 360
# Make ground generally higher by raising the random height range
GROUND_MIN_HEIGHT = 60
GROUND_MAX_HEIGHT = 140
GROUND_WIDTH = 120
GAP_MIN = 100  # Increased minimum gap
GAP_MAX = 250  # Increased maximum gap

# Score system
score = 0
score_timer = 0  # milliseconds

safe_area_segments = int(WIDTH // GROUND_WIDTH) + 1
GEN_BUFFER = WIDTH  # extra pixels to generate ahead to avoid popping

# Ground generation
def reset_ground():
    global ground_segments, ground_y_base
    ground_segments = []
    ground_y_base = HEIGHT
    current_x = 0
    for _ in range(safe_area_segments):
        ground_segments.append([current_x, GROUND_BASE_HEIGHT, GROUND_WIDTH])
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
            if event.key == pygame.K_SPACE:
                # Normal jump
                if on_ground:
                    player_vel_y = jump_power
                    on_ground = False
                    double_jump_used = False
                # Double jump if pickup available and not yet used in this airtime
                elif double_jump_available and not double_jump_used:
                    player_vel_y = jump_power
                    double_jump_used = True

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

    # Scroll ground segments (time-based)
    for seg in ground_segments:
        seg[0] -= GROUND_SCROLL_PPS * (dt / 1000.0)

    # Remove off-screen segments (with buffer)
    while ground_segments and ground_segments[0][0] + ground_segments[0][2] < -GEN_BUFFER:
        ground_segments.pop(0)

    # Add new segments if needed (generate ahead by GEN_BUFFER)
    while ground_segments and ground_segments[-1][0] < WIDTH + GEN_BUFFER:
        gap = random.randint(GAP_MIN, GAP_MAX)
        new_x = ground_segments[-1][0] + ground_segments[-1][2] + gap
        new_height = random.randint(GROUND_MIN_HEIGHT, GROUND_MAX_HEIGHT)
        ground_segments.append([new_x, new_height, GROUND_WIDTH])

    # Find the ground height under the player (if any) - Using smaller collision box
    collision_width = int(player_width * 0.7)  # 70% of visual width for collision
    collision_height = int(player_height * 0.8)  # 80% of visual height for collision
    collision_x = player_x + (player_width - collision_width) // 2  # Center the collision box
    collision_y = player_y + (player_height - collision_height)  # Bottom-align collision box
    
    player_bottom = collision_y + collision_height
    player_on_ground = False
    if player_vel_y >= 0:  # Only check collision if falling
        for i, seg in enumerate(ground_segments):
            seg_x, seg_h, seg_w = seg
            seg_top = ground_y_base - seg_h
            if collision_x + collision_width > seg_x and collision_x < seg_x + seg_w:
                # Player is above this segment
                if player_bottom >= seg_top and collision_y < seg_top:
                    # Place the sprite so that its feet touch the ground consistently
                    player_y = seg_top - player_height + player_sprites.ground_foot_offset()
                    player_vel_y = 0
                    player_on_ground = True
                    break
    on_ground = player_on_ground
    # Reset double-jump usage when player lands
    if on_ground:
        double_jump_used = False
        # Snap feet to ground each frame to avoid any tiny air gap due to rounding
        for seg in ground_segments:
            seg_x, seg_h, seg_w = seg
            seg_top = ground_y_base - seg_h
            if collision_x + collision_width > seg_x and collision_x < seg_x + seg_w:
                player_y = seg_top - player_height + player_sprites.ground_foot_offset()
                break
    
    # Update player animation based on state
    if player_vel_y < -2:  # Jumping up
        player_sprites.set_animation('jump')
    elif player_vel_y > 2:  # Falling down
        player_sprites.set_animation('fall')
    elif on_ground:  # On ground - running
        player_sprites.set_animation('run')
    else:  # Default to idle
        player_sprites.set_animation('idle')
    
    # Update sprite animation
    player_sprites.update()

    # Score: add 1 point every second
    score_timer += dt
    if score_timer >= 1000:
        score += 1
        score_timer -= 1000

    # Spawn pickup logic: spawn when score reaches next_spawn_score if not already spawned
    if not pickup_spawned and not double_jump_available and score >= next_spawn_score:
        # spawn pickup ahead of player
        pickup_spawned = True
        # place pickup somewhere ahead (e.g., middle-right area)
        pickup_x = WIDTH + 200
        pickup_y = HEIGHT - GROUND_BASE_HEIGHT - 150

    # Move pickup with world (same rate as ground)
    if pickup_spawned:
        pickup_x -= GROUND_SCROLL_PPS * (dt / 1000.0)

        # If pickup goes off-screen without being collected, schedule next spawn at +10 score
        if pickup_x + pickup_radius < -GEN_BUFFER:
            pickup_spawned = False
            next_spawn_score += 10

        # Collision with player (simple circle-rect overlap)
        if pickup_spawned:
            px = int(player_x + player_width/2)
            py = int(player_y + player_height/2)
            dx = px - int(pickup_x)
            dy = py - int(pickup_y)
            if dx*dx + dy*dy <= (pickup_radius + max(player_width, player_height)/2)**2:
                double_jump_available = True
                pickup_spawned = False

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
            # reset pickup/double-jump state for new run
            double_jump_available = False
            double_jump_used = False
            pickup_spawned = False
            next_spawn_score = 10
            continue
        elif choice == 'menu':
            # go back to main menu
            go_start = show_menu()
            if go_start:
                score = 0
                score_timer = 0
                reset_player()
                reset_ground()
                # reset pickup/double-jump state for new run
                double_jump_available = False
                double_jump_used = False
                pickup_spawned = False
                next_spawn_score = 10
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
        pygame.draw.rect(screen, (50, 205, 50), (int(seg_x), ground_y_base - seg_h, seg_w, seg_h))

    # Draw pickup if spawned
    if pickup_spawned:
        pygame.draw.circle(screen, (255, 215, 0), (int(pickup_x), int(pickup_y)), pickup_radius)

    # Draw indicator if player has double-jump available
    if double_jump_available:
        pygame.draw.circle(screen, (30, 144, 255), (20, 60), 12)

    # Draw player sprite
    current_sprite = player_sprites.get_current_sprite()
    if current_sprite:
        # Draw a couple pixels lower to visually close any tiny residual gap
        screen.blit(current_sprite, (player_x, int(player_y + player_sprites.draw_offset_down)))
    else:
        # Fallback to rectangle if sprites fail to load
        pygame.draw.rect(screen, (255, 100, 100), (player_x, int(player_y), player_width, player_height))

    # Draw score (top right)
    score_text = font.render(f"Score: {score}", True, (0,0,0))
    screen.blit(score_text, (WIDTH - score_text.get_width() - 20, 20))

    pygame.display.flip()

pygame.quit()
sys.exit()
