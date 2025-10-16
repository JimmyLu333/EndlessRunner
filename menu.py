import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Endless Runner - Menu")

clock = pygame.time.Clock()
FPS = 60

font = pygame.font.SysFont(None, 48)
button_font = pygame.font.SysFont(None, 36)

# Button properties
button_width, button_height = 200, 60
start_button_rect = pygame.Rect((WIDTH//2 - button_width//2, HEIGHT//2 - 80), (button_width, button_height))
quit_button_rect = pygame.Rect((WIDTH//2 - button_width//2, HEIGHT//2 + 20), (button_width, button_height))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if start_button_rect.collidepoint(mouse_pos):
                # Start the game
                import endlessrunner
                sys.exit()
            if quit_button_rect.collidepoint(mouse_pos):
                running = False

    screen.fill((135, 206, 235))
    title_text = font.render("Endless Runner", True, (0,0,0))
    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 80))

    # Draw Start button
    pygame.draw.rect(screen, (100, 200, 100), start_button_rect)
    start_text = button_font.render("Start", True, (0,0,0))
    screen.blit(start_text, (start_button_rect.centerx - start_text.get_width()//2, start_button_rect.centery - start_text.get_height()//2))

    # Draw Quit button
    pygame.draw.rect(screen, (200, 100, 100), quit_button_rect)
    quit_text = button_font.render("Quit", True, (0,0,0))
    screen.blit(quit_text, (quit_button_rect.centerx - quit_text.get_width()//2, quit_button_rect.centery - quit_text.get_height()//2))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
