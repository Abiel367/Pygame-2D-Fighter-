import pygame
import sys

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()  
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("2D Fighter")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.background = Background(SCREEN_WIDTH, SCREEN_HEIGHT)
        
      
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False            
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_SPACE and not self.game_over and not self.round_over:
                    # Toggle pause only when key is first pressed
                    if not self.space_pressed:
                        self.paused = not self.paused
                        self.space_pressed = True
                            
                if event.key == pygame.K_UP and not self.game_over and not self.round_over and not self.paused:
                    self.player.jump()
                        
                if event.key == pygame.K_x and not self.game_over and not self.round_over and not self.paused:
                    # Attack all enemies
                    for enemy in self.enemies:
                        if enemy.health > 0: 
                            self.player.attack(enemy)
                                
                if event.key == pygame.K_r and self.game_over:
                    self.__init__()  # Reset the entire game
        
        # Reset space pressed flag when spacebar is released
        keys = pygame.key.get_pressed()
        if not keys[pygame.K_SPACE]:
            self.space_pressed = False
        
        # Update player movement state
        if not self.game_over and not self.round_over and not self.paused:
            keys = pygame.key.get_pressed()
            
            # Reset movement state
            self.player.is_moving = False
            
            # Player controls 
            dx = 0
            if keys[pygame.K_LEFT]:
                dx = -5
                self.player.is_moving = True
                self.player.facing_right = False
            elif keys[pygame.K_RIGHT]:
                dx = 5
                self.player.is_moving = True
                self.player.facing_right = True 
                
            # Boundary checking 
            if self.player.rect.left < 0:
                self.player.rect.left = 0
            if self.player.rect.right > SCREEN_WIDTH:
                self.player.rect.right = SCREEN_WIDTH
        
        return True
    
        
    
    def update(self):
        if not self.game_over and not self.paused:
            if self.round_over:
                # Handle round transition
                self.round_transition_timer -= 1
                if self.round_transition_timer <= 0:
                    self.next_round()
            else:
                # Update cooldowns
                if self.player.attack_cooldown > 0:
                    self.player.attack_cooldown -= 1
    
    def draw(self):
        # Draw background instead of black screen
        self.background.draw(self.screen)
        
        # Draw ground 
        ground_surface = pygame.Surface((SCREEN_WIDTH, 50))
        ground_surface.set_alpha(200)  
        ground_surface.fill(WHITE)
        self.screen.blit(ground_surface, (0, SCREEN_HEIGHT - 50))
        
        # Draw characters
        self.player.draw(self.screen)
        
        # Draw UI
        self.draw_ui()
        
        # Draw pause screen
        if self.paused:
            self.draw_pause_screen()
        
        pygame.display.flip()
    
    def draw_ui(self):        
        # Draw health labels
        player_health_text = self.font.render(f"Player: {self.player.health}", True, BLUE)
        self.screen.blit(player_health_text, (10, 50))
        
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    Game().run()
