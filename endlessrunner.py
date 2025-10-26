# Step 1: Basic Pygame window and main loop

import pygame
import sys
import random
import os
import math
import re

# Initialize Pygame
pygame.init()

# Set up display
# Increased resolution
WIDTH, HEIGHT = 1920, 1080
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

# Parallax background system (infinite scrolling)
class ParallaxLayer:
    def __init__(self, image_path, speed_factor):
        self.enabled = False
        self.speed_factor = speed_factor
        self.img = None
        self.positions = []
        self.y = 0
        if os.path.exists(image_path):
            try:
                img = pygame.image.load(image_path).convert_alpha()
                # Scale to screen height while keeping aspect ratio
                ih = img.get_height()
                iw = img.get_width()
                scale = HEIGHT / ih
                new_w = max(1, int(iw * scale))
                new_h = HEIGHT
                self.img = pygame.transform.smoothscale(img, (new_w, new_h))
                tile_w = self.img.get_width()
                # Create enough tiles to cover width plus buffer
                tile_count = max(3, math.ceil(WIDTH / tile_w) + 2)
                self.positions = [i * tile_w for i in range(tile_count)]
                self.y = 0  # align to top; adjust if your art needs bottom align
                self.enabled = True
            except Exception:
                self.enabled = False

    def update(self, dt):
        if not self.enabled:
            return
        dx = GROUND_SCROLL_PPS * self.speed_factor * (dt / 1000.0)
        # Move tiles left
        for i in range(len(self.positions)):
            self.positions[i] -= dx
        # Recycle tiles that moved off-screen
        w = self.img.get_width()
        while self.positions and self.positions[0] <= -w:
            _ = self.positions.pop(0)
            self.positions.append(self.positions[-1] + w)

    def draw(self, surface):
        if not self.enabled:
            return
        for x in self.positions:
            surface.blit(self.img, (int(x), int(self.y)))


class ParallaxBackground:
    def __init__(self, layers):
        self.layers = [l for l in layers if l and l.enabled]

    def update(self, dt):
        for l in self.layers:
            l.update(dt)

    def draw(self, surface):
        for l in self.layers:
            l.draw(surface)


def _find_new_background_path():
    """Find a user-added background image like 'background (1).png', 'background(1).png' or 'background（1）.png'."""
    bases = [
        os.path.dirname(__file__),
        os.getcwd(),
        os.path.join(os.path.dirname(__file__), "decoration"),
    ]
    # Match: background[optional space][( or （]1[) or ）].(png|jpg|jpeg), case-insensitive
    pat = re.compile(r"^background\s*[\(（]1[\)）]\.(png|jpg|jpeg)$", re.IGNORECASE)
    for base in bases:
        try:
            for fname in os.listdir(base):
                if pat.match(fname):
                    return os.path.join(base, fname)
        except Exception:
            continue
    # Fallback: recursive search under the script directory
    root = os.path.dirname(__file__)
    try:
        for dirpath, _dirs, files in os.walk(root):
            for fname in files:
                if pat.match(fname):
                    return os.path.join(dirpath, fname)
    except Exception:
        pass
    return None

def _find_generic_background_path():
    """Find 'background.png/jpg/jpeg' in root or decoration folders, case-insensitive (e.g., Background.png)."""
    exts = (".png", ".jpg", ".jpeg")
    bases = [os.path.dirname(__file__), os.path.join(os.path.dirname(__file__), "decoration")]
    for base in bases:
        try:
            for fname in os.listdir(base):
                lower = fname.lower()
                if lower.startswith("background") and lower.endswith(exts):
                    return os.path.join(base, fname)
        except Exception:
            continue
    return None


def create_background():
    # Prefer a newly added single background like 'background (1).png' if present
    nb = _find_new_background_path() or _find_generic_background_path()
    if nb:
        try:
            print(f"[background] Using: {nb}")
        except Exception:
            pass
        return ParallaxBackground([l for l in [ParallaxLayer(nb, 0.6)] if l and l.enabled])

    # Otherwise, try layered backgrounds
    names = ["bg_far.png", "bg_mid.png", "bg_near.png", "background.png"]
    candidates = []
    for nm, spd in zip(names, [0.2, 0.45, 0.75, 0.6]):
        # check both root and decoration folder, case-insensitive
        paths = [
            os.path.join(os.path.dirname(__file__), nm),
            os.path.join(os.path.dirname(__file__), "decoration", nm),
        ]
        found = None
        for p in paths:
            if os.path.exists(p):
                found = p
                break
            # try case-insensitive scan in the directory containing p
            d = os.path.dirname(p)
            try:
                for f in os.listdir(d):
                    if f.lower() == nm.lower():
                        found = os.path.join(d, f)
                        break
            except Exception:
                pass
            if found:
                break
        if found:
            candidates.append((found, spd))
    layers = []
    for path, spd in candidates:
        layer = ParallaxLayer(path, spd)
        if layer.enabled:
            layers.append(layer)
    return ParallaxBackground(layers)


background = create_background()

# Load and scale dungeon ground tile
def load_ground_tile():
    path = os.path.join("dungeonbackground", "Ground.png")
    if os.path.exists(path):
        try:
            img = pygame.image.load(path).convert_alpha()
            # Do not scale to preserve original appearance
            return img
        except Exception:
            return None
    return None

GROUND_TILE_IMG = load_ground_tile()

# Platform sprite size (scaled down proportionally to make platforms shorter)
PLATFORM_IMG = None
if GROUND_TILE_IMG is not None:
    _ow, _oh = GROUND_TILE_IMG.get_width(), GROUND_TILE_IMG.get_height()
    PLATFORM_TARGET_HEIGHT = 48  # shrink a bit; preserves aspect ratio
    _scale = PLATFORM_TARGET_HEIGHT / max(1, _oh)
    PLATFORM_W = max(16, int(_ow * _scale))
    PLATFORM_H = PLATFORM_TARGET_HEIGHT
    try:
        PLATFORM_IMG = pygame.transform.smoothscale(GROUND_TILE_IMG, (PLATFORM_W, PLATFORM_H))
    except Exception:
        PLATFORM_IMG = pygame.transform.scale(GROUND_TILE_IMG, (PLATFORM_W, PLATFORM_H))
else:
    PLATFORM_W = 120
    PLATFORM_H = 40

# Vertical band for floating platforms (lower overall)
PLATFORM_Y_MIN = int(HEIGHT * 0.66)
PLATFORM_Y_MAX = int(HEIGHT * 0.82)

# Short-platform policy using head/tail cropping
# We render short platforms by drawing the left "head" and right "tail" portions of the sprite
# and removing (skipping) the middle so the platform looks very short but still has both ends.
HEAD_CROP_FRAC = 0.35  # fraction of source sprite width used for the left head
TAIL_CROP_FRAC = 0.35  # fraction of source sprite width used for the right tail
SHORT_PLATFORM_MIN_FRAC = 0.25  # min width of a short platform as fraction of base sprite width
SHORT_PLATFORM_MAX_FRAC = 0.45  # max width of a short platform as fraction of base sprite width

# No around frame; keep platform vertical band as configured above

def draw_ground_tiled(surface, img, seg_x, seg_top, seg_w, seg_h):
    """Draw a platform using head/tail cropping for short widths; full blit for full width.
    - If seg_w >= sprite width: draw the whole sprite normally.
    - If seg_w < sprite width: draw left head and right tail parts, skipping the middle.
    """
    use_img = PLATFORM_IMG if PLATFORM_IMG is not None else img
    if use_img is not None:
        src_w = use_img.get_width()
        src_h = use_img.get_height()
        w = int(seg_w)
        if w >= src_w:
            surface.blit(use_img, (int(seg_x), int(seg_top)))
        else:
            # compute head/tail crop sizes in source space
            head_px = max(1, int(src_w * HEAD_CROP_FRAC))
            tail_px = max(1, int(src_w * TAIL_CROP_FRAC))
            sum_px = max(1, head_px + tail_px)
            # proportional allocation so head+tail exactly fill seg_w without overlap
            p_head = head_px / sum_px
            head_draw_w = max(1, int(round(w * p_head)))
            tail_draw_w = max(1, w - head_draw_w)
            # clamp to source caps and re-balance to exactly w
            if head_draw_w > head_px:
                head_draw_w = head_px
                tail_draw_w = max(1, w - head_draw_w)
            if tail_draw_w > tail_px:
                tail_draw_w = tail_px
                head_draw_w = max(1, w - tail_draw_w)
            # if still off due to rounding, adjust
            total = head_draw_w + tail_draw_w
            if total != w:
                diff = w - total
                # prefer adding to the side with remaining cap
                if diff > 0:
                    add_head = min(diff, max(0, head_px - head_draw_w))
                    head_draw_w += add_head
                    diff -= add_head
                    if diff > 0:
                        add_tail = min(diff, max(0, tail_px - tail_draw_w))
                        tail_draw_w += add_tail
                        diff -= add_tail
                    # if still diff > 0, distribute anyway
                    if diff > 0:
                        head_draw_w += diff
                else:
                    # need to shrink; reduce tail first
                    reduce_tail = min(-diff, max(0, tail_draw_w - 1))
                    tail_draw_w -= reduce_tail
                    diff += reduce_tail
                    if diff < 0:
                        reduce_head = min(-diff, max(0, head_draw_w - 1))
                        head_draw_w -= reduce_head
                        diff += reduce_head
            # ensure final non-overlapping coverage
            head_src = pygame.Rect(0, 0, head_draw_w, src_h)
            surface.blit(use_img, (int(seg_x), int(seg_top)), head_src)
            tail_src = pygame.Rect(src_w - tail_draw_w, 0, tail_draw_w, src_h)
            tail_dest_x = int(seg_x + w - tail_draw_w)
            surface.blit(use_img, (tail_dest_x, int(seg_top)), tail_src)
    else:
        pygame.draw.rect(surface, (50, 205, 50), (int(seg_x), int(seg_top), int(seg_w), int(seg_h)))

# Font for score
def get_font():
    return pygame.font.SysFont(None, 36)
font = get_font()

def draw_text_with_outline(surface, text, font, pos, color=(255,255,255), outline_color=(0,0,0), outline=2, bg_alpha=120):
    """Draw text with a subtle translucent background and an outline so it's always visible on any background."""
    if not text:
        return
    # render main and outline
    main = font.render(text, True, color)
    if outline > 0:
        out = font.render(text, True, outline_color)
    else:
        out = None
    x, y = pos
    # translucent bg behind text for contrast
    pad_x, pad_y = 8, 4
    bg = pygame.Surface((main.get_width() + pad_x*2, main.get_height() + pad_y*2), pygame.SRCALPHA)
    bg.fill((0,0,0,bg_alpha))
    surface.blit(bg, (x - pad_x, y - pad_y))
    # outline (simple 8-direction) then main
    if out:
        for ox, oy in [(-outline,0),(outline,0),(0,-outline),(0,outline),(-outline,-outline),(-outline,outline),(outline,-outline),(outline,outline)]:
            surface.blit(out, (x+ox, y+oy))
    surface.blit(main, (x, y))

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

# How high above the base ground line the double-jump pickup spawns (larger = higher on screen)
PICKUP_ABOVE_BASE = 300

# Ground segment properties
# Ground scroll speed in pixels per second (time-based)
GROUND_SCROLL_PPS = 360
# Make ground generally higher by raising the random height range
GROUND_MIN_HEIGHT = 60
GROUND_MAX_HEIGHT = 140
GROUND_WIDTH = 120
# Length (in pixels) of the very first ground platform (longer for easier start)
START_GROUND_PIXELS = max(GROUND_WIDTH * 3, int(WIDTH * 0.6))
GAP_MIN = 180  # Larger minimum gap for higher challenge
GAP_MAX = 360  # Larger maximum gap

# Level generation mode: finite vs endless
LEVEL_ENDLESS = True  # Enable infinite generation so platforms continue beyond early scores
# Total logical length of the finite level in pixels (from x=0)
LEVEL_LENGTH_PIXELS = int(WIDTH * 6)

# Score system
score = 0
score_timer = 0  # milliseconds

safe_area_segments = int(WIDTH // GROUND_WIDTH) + 1
GEN_BUFFER = WIDTH  # extra pixels to generate ahead to avoid popping

# Ground generation
def reset_ground():
    """Generate floating platforms using a fixed-size sprite (no tiling).
    Each platform is an individual sprite at a chosen (x, y), with width/height from the sprite.
    If LEVEL_ENDLESS is False, platforms are pre-generated up to LEVEL_LENGTH_PIXELS.
    Structure per segment: [x, y, w, h].
    """
    global ground_segments, ground_y_base
    ground_segments = []
    ground_y_base = HEIGHT

    # 1) Starting platform: a long strip made of multiple short sprites
    start_y = int((PLATFORM_Y_MIN + PLATFORM_Y_MAX) / 2)
    current_x = 0
    while current_x < START_GROUND_PIXELS:
        ground_segments.append([current_x, start_y, PLATFORM_W, PLATFORM_H])
        current_x += PLATFORM_W

    # 2) Generate the rest along X with gaps, Y within band (very short platforms via crop)
    limit_x = LEVEL_LENGTH_PIXELS if not LEVEL_ENDLESS else (WIDTH + PLATFORM_W + GEN_BUFFER)
    while current_x < limit_x:
        gap = random.randint(GAP_MIN, GAP_MAX)
        current_x += gap
        y = random.randint(PLATFORM_Y_MIN, PLATFORM_Y_MAX)
        # Choose a short platform width as a fraction of the base sprite width
        seg_w = max(8, int(PLATFORM_W * random.uniform(SHORT_PLATFORM_MIN_FRAC, SHORT_PLATFORM_MAX_FRAC)))
        ground_segments.append([current_x, y, seg_w, PLATFORM_H])
        current_x += seg_w

reset_ground()

# Align player start height to the first platform
if ground_segments:
    first_top = ground_segments[0][1]
    player_y = first_top - player_height + (player_sprites.ground_foot_offset() if hasattr(player_sprites, 'ground_foot_offset') else 0)

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

    # Add new segments if needed (only in endless mode)
    if LEVEL_ENDLESS:
        while ground_segments and ground_segments[-1][0] < WIDTH + GEN_BUFFER:
            gap = random.randint(GAP_MIN, GAP_MAX)
            new_x = ground_segments[-1][0] + ground_segments[-1][2] + gap
            new_y = random.randint(PLATFORM_Y_MIN, PLATFORM_Y_MAX)
            # Short platform width (single segment); head/tail drawn via cropping
            seg_w = max(8, int(PLATFORM_W * random.uniform(SHORT_PLATFORM_MIN_FRAC, SHORT_PLATFORM_MAX_FRAC)))
            ground_segments.append([new_x, new_y, seg_w, PLATFORM_H])

    # Find platform under the player (if any) - using smaller collision box
    collision_width = int(player_width * 0.7)
    collision_height = int(player_height * 0.8)
    collision_x = player_x + (player_width - collision_width) // 2
    collision_y = player_y + (player_height - collision_height)

    player_bottom = collision_y + collision_height
    player_on_ground = False
    if player_vel_y >= 0:  # Only check collision if falling
        for seg in ground_segments:
            seg_x, seg_y, seg_w, seg_h = seg
            seg_top = seg_y
            if collision_x + collision_width > seg_x and collision_x < seg_x + seg_w:
                # Player is above this platform
                if player_bottom >= seg_top and collision_y < seg_top:
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
            seg_x, seg_y, seg_w, seg_h = seg
            seg_top = seg_y
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
        pickup_y = HEIGHT - GROUND_BASE_HEIGHT - PICKUP_ABOVE_BASE

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
            if ground_segments:
                first_top = ground_segments[0][1]
                player_y = first_top - player_height + (player_sprites.ground_foot_offset() if hasattr(player_sprites, 'ground_foot_offset') else 0)
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
                if ground_segments:
                    first_top = ground_segments[0][1]
                    player_y = first_top - player_height + (player_sprites.ground_foot_offset() if hasattr(player_sprites, 'ground_foot_offset') else 0)
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

    # Draw background (fill if no layers present)
    if background and background.layers:
        # Update before drawing so it moves every frame
        background.update(dt)
        # Optional: base fill behind translucent images
        screen.fill((135, 206, 235))
        background.draw(screen)
    else:
        # Fallback sky color if no background image provided yet
        screen.fill((135, 206, 235))

    # Draw platforms (single-sprite floating platforms)
    for seg in ground_segments:
        seg_x, seg_y, seg_w, seg_h = seg
        if GROUND_TILE_IMG is not None or PLATFORM_IMG is not None:
            draw_ground_tiled(screen, GROUND_TILE_IMG, seg_x, seg_y, seg_w, seg_h)
        else:
            pygame.draw.rect(screen, (50, 205, 50), (int(seg_x), int(seg_y), seg_w, seg_h))

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

    # Draw score (top-right), on top of everything with outline and bg
    text_str = f"Score: {score}"
    # Measure to right-align
    tmp = font.render(text_str, True, (255,255,255))
    tx = WIDTH - tmp.get_width() - 20
    ty = 20
    draw_text_with_outline(screen, text_str, font, (tx, ty), color=(255,255,255), outline_color=(0,0,0), outline=2, bg_alpha=120)

    # No around frame overlay

    pygame.display.flip()

pygame.quit()
sys.exit()
