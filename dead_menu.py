import pygame
import sys
import os

def dead_menu(current_score, best_score):
    pygame.init()
    WIDTH, HEIGHT = 800, 400
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Game Over - Endless Runner")
    clock = pygame.time.Clock()
    FPS = 60
    font = pygame.font.SysFont(None, 48)
    button_font = pygame.font.SysFont(None, 36)

    # Button properties
    button_width, button_height = 200, 60
    restart_button_rect = pygame.Rect((WIDTH//2 - button_width//2, HEIGHT//2 + 10), (button_width, button_height))
    menu_button_rect = pygame.Rect((WIDTH//2 - button_width//2, HEIGHT//2 + 90), (button_width, button_height))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if restart_button_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    os.system(f'"{sys.executable}" endlessrunner.py')
                    sys.exit()
                if menu_button_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    os.system(f'"{sys.executable}" menu.py')
                    sys.exit()

        screen.fill((220, 80, 80))
        title_text = font.render("Game Over", True, (0,0,0))
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 60))

        score_text = button_font.render(f"Score: {current_score}", True, (0,0,0))
        best_text = button_font.render(f"Best: {best_score}", True, (0,0,0))
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 140))
        screen.blit(best_text, (WIDTH//2 - best_text.get_width()//2, 180))

        # Draw Restart button
        pygame.draw.rect(screen, (100, 200, 100), restart_button_rect)
        restart_text = button_font.render("Restart", True, (0,0,0))
        screen.blit(restart_text, (restart_button_rect.centerx - restart_text.get_width()//2, restart_button_rect.centery - restart_text.get_height()//2))

        # Draw Menu button
        pygame.draw.rect(screen, (100, 100, 200), menu_button_rect)
        menu_text = button_font.render("Menu", True, (0,0,0))
        screen.blit(menu_text, (menu_button_rect.centerx - menu_text.get_width()//2, menu_button_rect.centery - menu_text.get_height()//2))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        current_score = int(sys.argv[1])
        best_score = int(sys.argv[2])
    else:
        current_score = 0
        best_score = 0
    dead_menu(current_score, best_score)
