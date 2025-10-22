import pygame
import sys
from player import Player
from enemy import Enemy
from background import Background

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
        
        # Load sounds
        self.load_sounds()
        
        # Game state
        self.current_round = 1
        self.max_rounds = 5
        self.player_wins = 0
        self.enemy_wins = 0
        self.round_over = False
        self.game_over = False
        self.round_transition_timer = 0
        self.round_transition_delay = 180  
        self.paused = False
        self.space_pressed = False  
        
        # Sound state
        self.player_running = False
        self.enemy_running = False
        
        # Create player and enemies
        self.reset_round()
    
    def load_sounds(self):
        # Load sound effects and music
        try:
            # Sound effects
            self.attack_sound = pygame.mixer.Sound("assets/audio/attack/slash.wav")
            self.jump_sound = pygame.mixer.Sound("assets/audio/jump/jump.wav")
            self.teleport_sound = pygame.mixer.Sound("assets/audio/teleport/teleport.wav")
            self.run_sound = pygame.mixer.Sound("assets/audio/run/run.wav")
            
            # Set volumes for sound effects 
            self.attack_sound.set_volume(0.7)
            self.jump_sound.set_volume(0.8)
            self.teleport_sound.set_volume(0.7)
            self.run_sound.set_volume(0.8)  
            
            # Background music
            pygame.mixer.music.load("assets/audio/music/music.wav")
            pygame.mixer.music.set_volume(0.6)  
            
        except pygame.error as e:
            print(f"Error loading sounds: {e}")
            # Create dummy sounds to prevent crashes
            self.attack_sound = None
            self.jump_sound = None
            self.teleport_sound = None
            self.run_sound = None
    
    def play_background_music(self):
        # Strt playing background music
        try:
            pygame.mixer.music.play(-1)  # loop
        except:
            print("Could not play background music")
    
    def handle_run_sounds(self):
        # Hndle playing running sounds fr player and enemy
        if self.paused or self.round_over or self.game_over:
            # Stop all running sounds if game is not active
            if self.player_running or self.enemy_running:
                self.run_sound.stop()
                self.player_running = False
                self.enemy_running = False
            return
        
        # Check if player is running
        player_is_running = (self.player.is_moving and 
                           not self.player.is_jumping and 
                           not self.player.is_teleporting and
                           self.player.health > 0)
        
        # Check if enemy is running
        enemy_is_running = False
        for enemy in self.enemies:
            if (enemy.health > 0 and 
                enemy.current_action in ["move_towards", "move_away"] and
                not enemy.is_jumping):
                enemy_is_running = True
                break
        
        # Player running sound
        if player_is_running and not self.player_running:
            # Start player running sound
            self.run_sound.play(-1)  # looop
            self.player_running = True
        elif not player_is_running and self.player_running:
            # Stop player running sound
            self.run_sound.stop()
            self.player_running = False
                
    def reset_round(self):
        # Reset player
        if hasattr(self, 'player'):
            # Reset existing player
            self.player.rect.x = 200
            self.player.rect.y = 400
            self.player.health = 100
            self.player.velocity_y = 0
            self.player.is_jumping = False
            self.player.attack_cooldown = 0
            self.player.is_moving = False
            self.player.health_regen_timer = 0
            self.player.set_state("idle")
        else:
            # Create player first time
            self.player = Player(200, 400, 62, 58, BLUE)
        
        # Create enemy
        self.enemies = []
        enemy = Enemy(800, 400, 62, 58, RED)
        self.enemies.append(enemy)
        
        self.round_over = False
        self.round_transition_timer = 0
        self.paused = False
        self.space_pressed = False
        
        # Stop running sounds when round resets
        if hasattr(self, 'run_sound') and self.run_sound:
            self.run_sound.stop()
        self.player_running = False
        self.enemy_running = False
        
        # Start music whn game starts
        if not hasattr(self, 'music_started'):
            self.play_background_music()
            self.music_started = True
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z and not self.game_over and not self.round_over and not self.paused:
                    # Teleport player
                    self.player.teleport()
                    # Play teleport sound
                    if hasattr(self, 'teleport_sound') and self.teleport_sound:
                        self.teleport_sound.play()
                        
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_SPACE and not self.game_over and not self.round_over:
                    # Toggle pause only when key is first pressed
                    if not self.space_pressed:
                        self.paused = not self.paused
                        self.space_pressed = True
                        # Pause/resume music when game is paused
                        if self.paused:
                            pygame.mixer.music.pause()
                            # Also stop running sounds when paused
                            if hasattr(self, 'run_sound') and self.run_sound:
                                self.run_sound.stop()
                        else:
                            pygame.mixer.music.unpause()
                            
                if event.key == pygame.K_UP and not self.game_over and not self.round_over and not self.paused:
                    self.player.jump()
                    # Play jump sound
                    if hasattr(self, 'jump_sound') and self.jump_sound:
                        self.jump_sound.play()
                        
                if event.key == pygame.K_x and not self.game_over and not self.round_over and not self.paused:
                    # Attack all enemies
                    for enemy in self.enemies:
                        if enemy.health > 0: 
                            self.player.attack(enemy)
                            # Play attack sound
                            if hasattr(self, 'attack_sound') and self.attack_sound:
                                self.attack_sound.play()
                                
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
            
            # Move player and check collisions with enemy
            if dx != 0:
                # Move player temporarily
                self.player.rect.x += dx
                
                # Check collision with enemy
                for enemy in self.enemies:
                    if (enemy.health > 0 and 
                        self.player.rect.colliderect(enemy.rect) and
                        abs(self.player.rect.centery - enemy.rect.centery) < 50):
                        
                        # Push player to the appropriate side of the enemy
                        if dx > 0:  # Moving right
                            self.player.rect.right = enemy.rect.left
                        else:  # Moving left
                            self.player.rect.left = enemy.rect.right
                        break 
                
            # Boundary checking 
            if self.player.rect.left < 0:
                self.player.rect.left = 0
            if self.player.rect.right > SCREEN_WIDTH:
                self.player.rect.right = SCREEN_WIDTH
        
        return True
    
    def next_round(self):
        self.current_round += 1
        if self.current_round > self.max_rounds:
            self.game_over = True
        else:
            self.reset_round()
    
    def check_round_winner(self):
        # Check if player died
        if self.player.health <= 0:
            self.enemy_wins += 1
            self.round_over = True
            self.round_transition_timer = self.round_transition_delay
            return
        
        # Check if the enemy is dead
        enemy_dead = self.enemies[0].health <= 0
        if enemy_dead:
            self.player_wins += 1
            self.round_over = True
            self.round_transition_timer = self.round_transition_delay
            # Check if this was the final round
            if self.current_round >= self.max_rounds:
                self.game_over = True
    
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
                
                # Update characters
                living_enemies = [enemy for enemy in self.enemies if enemy.health > 0]
                if living_enemies:
                    self.player.update(living_enemies[0])
                else:
                    self.player.update(None)
                
                # Update all enemy
                for enemy in self.enemies:
                    if enemy.health > 0:  
                        enemy.update(self.player)
                
                # Check for round winner
                self.check_round_winner()
        
        # Handle running sounds 
        self.handle_run_sounds()
    
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
        for enemy in self.enemies:
            if enemy.health > 0:  
                enemy.draw(self.screen)
        
        # Draw UI
        self.draw_ui()
        
        # Draw round over screen
        if self.round_over and not self.game_over:
            self.draw_round_over()
        
        # Draw game over screen
        if self.game_over:
            self.draw_game_over()
        
        # Draw pause screen
        if self.paused:
            self.draw_pause_screen()
        
        pygame.display.flip()
    
    def draw_ui(self):        
        # Draw health labels
        player_health_text = self.font.render(f"Player: {self.player.health}", True, BLUE)
        self.screen.blit(player_health_text, (10, 50))
        
        # Draw round info
        round_text = self.font.render(f"Round: {self.current_round}/{self.max_rounds}", True, WHITE)
        self.screen.blit(round_text, (SCREEN_WIDTH // 2 - round_text.get_width() // 2, 10))
        
        # Draw score
        score_text = self.font.render(f"Player: {self.player_wins} - Enemy: {self.enemy_wins}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH - 200, 10))
        
        # Draw enemy health
        if self.enemies[0].health > 0:
            enemy_health_text = self.small_font.render(f"Enemy: {self.enemies[0].health}", True, RED)
            self.screen.blit(enemy_health_text, (SCREEN_WIDTH - 200, 50))
    
    def draw_round_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        if self.player.health <= 0:
            winner = "ENEMY"
            color = RED
        else:
            winner = "PLAYER"
            color = GREEN
        
        round_over_text = self.font.render(f"ROUND OVER - {winner} WINS!", True, color)
        
        # Show countdown timer
        seconds_left = (self.round_transition_timer // 60) + 1
        countdown_text = self.font.render(f"Next round in: {seconds_left}", True, WHITE)
        score_text = self.font.render(f"Score: Player {self.player_wins} - {self.enemy_wins} Enemy", True, WHITE)
        
        self.screen.blit(round_over_text, (SCREEN_WIDTH // 2 - round_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(countdown_text, (SCREEN_WIDTH // 2 - countdown_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
    
    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        if self.player_wins > self.enemy_wins:
            winner = "PLAYER"
            color = GREEN
        else:
            winner = "ENEMY"
            color = RED
            
        game_over_text = self.font.render(f"GAME OVER - {winner} WINS THE MATCH!", True, color)
        final_score_text = self.font.render(f"Final Score: {self.player_wins} - {self.enemy_wins}", True, WHITE)
        restart_text = self.font.render("Press R to restart", True, WHITE)
        
        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
    
    def draw_pause_screen(self):
        # Create semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Draw pause text
        pause_text = self.font.render("GAME PAUSED", True, YELLOW)
        instruction_text = self.font.render("Press SPACE to resume", True, WHITE)
        controls_text = self.small_font.render("Controls: ARROWS to move, X to attack, Z to Teleport", True, WHITE)
        
        self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(controls_text, (SCREEN_WIDTH // 2 - controls_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
    
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
