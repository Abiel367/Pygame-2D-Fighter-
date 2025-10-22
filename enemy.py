import pygame
import os
import random
from animation import Animation

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

class Enemy:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.velocity_y = 0
        self.jump_power = -15
        self.gravity = 0.8
        self.is_jumping = False
        self.health = 100
        self.max_health = 100
        self.facing_right = False
        self.attack_cooldown = 0
        self.move_timer = 0
        self.current_action = "idle"
        self.aggression_level = "normal"  
        self.health_regen_timer = 0
        self.health_regen_delay = 180  
        
        # Animation states
        self.current_state = "idle"
        self.states = {}
        self.load_animations()
        
        # Sound
        self.attack_sound = None
        self.load_sounds()
    
    def load_sounds(self):
        # Lod enemy sounds
        try:
            self.attack_sound = pygame.mixer.Sound("assets/audio/attack/slash.wav")
            self.attack_sound.set_volume(0.7)  
        except:
            print("Could not load enemy attack sound")
    
    def load_animations(self):
        # Load all animations for the enemy
        base_path = "assets/enemy/"
        
        # Load idle animation
        idle_frames = self.load_frames_from_folder(os.path.join(base_path, "idle"))
        if idle_frames:
            self.states["idle"] = Animation(idle_frames, speed=10)
        
        # Load run animation
        run_frames = self.load_frames_from_folder(os.path.join(base_path, "run"))
        if run_frames:
            self.states["run"] = Animation(run_frames, speed=5)  
        
        # Load jump animation
        jump_frames = self.load_frames_from_folder(os.path.join(base_path, "jump"))
        if jump_frames:
            self.states["jump"] = Animation(jump_frames, speed=10, loop=False)
        
        # Load attack animation
        attack_frames = self.load_frames_from_folder(os.path.join(base_path, "attack"))
        if attack_frames:
            self.states["attack"] = Animation(attack_frames, speed=5, loop=False)
        
        # Set default state
        self.current_animation = self.states.get("idle", None)
    
    def load_frames_from_folder(self, folder_path):
        # Load all PNG images from a folder and return as list of surfaces
        frames = []
        if os.path.exists(folder_path):
            # Get all PNG files and sort them
            png_files = [f for f in os.listdir(folder_path) if f.endswith('.png')]
            png_files.sort()  # Sort to ensure correct order
            
            for filename in png_files:
                try:
                    frame = pygame.image.load(os.path.join(folder_path, filename)).convert_alpha()
                    frames.append(frame)
                except pygame.error as e:
                    print(f"Unable to load enemy image: {os.path.join(folder_path, filename)}")
                    print(e)
        
        if not frames:
            print(f"No enemy frames loaded from {folder_path}")
            
        return frames
    
    def set_state(self, new_state):
        # Change the current animation state
        if new_state != self.current_state and new_state in self.states:
            self.current_state = new_state
            self.current_animation = self.states[new_state]
            self.current_animation.reset()
    
    def move(self, dx, player):
        self.rect.x += dx
        
        # Boundary checking
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > 1280:  # SCREEN_WIDTH
            self.rect.right = 1280
            
        # Collision with player
        if self.rect.colliderect(player.rect):
            if dx > 0:  # Moving right
                self.rect.right = player.rect.left
            elif dx < 0:  # Moving left
                self.rect.left = player.rect.right
        
        # Update facing direction
        if dx > 0:
            self.facing_right = True
        elif dx < 0:
            self.facing_right = False
    
    def jump(self):
        if not self.is_jumping:
            self.velocity_y = self.jump_power
            self.is_jumping = True
            self.set_state("jump")
    
    def attack(self, player):
        if self.attack_cooldown <= 0 and "attack" in self.states:
            self.set_state("attack")
            
            attack_range = 50  
            attack_height = 40  
            
            if self.facing_right:
                attack_rect = pygame.Rect(self.rect.right, self.rect.centery - attack_height//2, attack_range, attack_height)
            else:
                attack_rect = pygame.Rect(self.rect.left - attack_range, self.rect.centery - attack_height//2, attack_range, attack_height)
            
            # Check if attack hits player
            if attack_rect.colliderect(player.rect):
                damage = 8 if self.aggression_level == "aggressive" else 5
                player.health -= damage
            
            # Play enemy attack sound
            if self.attack_sound:
                self.attack_sound.play()
            
            # Reduced cooldown for faster attacks
            self.attack_cooldown = 15 if self.aggression_level == "aggressive" else 25
            self.health_regen_timer = 0
    
    def take_damage(self, amount):
        self.health -= amount
        self.health_regen_timer = 0  # Reset regen timer when taking damage
    
    def regenerate_health(self):
        # Only regenerate if not at full health and not recently damaged
        if self.health < self.max_health and self.health_regen_timer >= self.health_regen_delay:
            # Regenerate health every 10 frames (6 HP per second)
            if self.health_regen_timer % 10 == 0:
                self.health = min(self.max_health, self.health + 1)
        
        if self.health < self.max_health:
            self.health_regen_timer += 1
    
    def update_aggression_level(self):
        # Change behavior based on health
        if self.health <= 45:
            self.aggression_level = "defensive"  
        elif self.health <= 70:
            self.aggression_level = "aggressive" 
        else:
            self.aggression_level = "aggressive"  
    
    def ai_think(self, player):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        self.move_timer -= 1
        
        # Update aggression based on health
        self.update_aggression_level()
        
        # Health regeneration
        self.regenerate_health()
        
        # Calculate distance to player
        distance_x = player.rect.centerx - self.rect.centerx
        distance_y = abs(player.rect.centery - self.rect.centery)
        
        # Face the player
        self.facing_right = distance_x > 0
        
        # AI decision making based on aggression level
        if self.move_timer <= 0:
            if self.aggression_level == "aggressive":
                # Very aggressive - mostly attack and chase
                actions = ["move_towards", "attack", "attack", "jump", "move_towards"]
                weights = [30, 40, 40, 10, 30]
                self.move_timer = random.randint(20, 60)  # Faster decisions
                
            elif self.aggression_level == "defensive":
                # Defensive - hit and run tactics
                actions = ["move_away", "attack", "move_towards", "jump", "move_away"]
                weights = [40, 25, 15, 10, 40]
                self.move_timer = random.randint(40, 80)  # Slower, more cautious decisions
                
            else:  # normal
                actions = ["move_towards", "move_away", "jump", "attack", "idle"]
                weights = [40, 10, 15, 30, 5]
                self.move_timer = random.randint(30, 90)
            
            self.current_action = random.choices(actions, weights=weights)[0]
        
        # Execute current action with aggression-based parameters
        move_speed = 4 if self.aggression_level == "aggressive" else 3
        
        if self.current_action == "move_towards":
            if self.aggression_level == "defensive":
                # Only move towards if player is far enough and we're healthy enough to risk it
                if abs(distance_x) > 150 and self.health > 20:
                    if distance_x > 0:
                        self.move(move_speed, player)
                    else:
                        self.move(-move_speed, player)
            else:
                # Normal/aggressive movement towards player
                if abs(distance_x) > (80 if self.aggression_level == "aggressive" else 100):
                    if distance_x > 0:
                        self.move(move_speed, player)
                    else:
                        self.move(-move_speed, player)
        
        elif self.current_action == "move_away":
            if self.aggression_level == "defensive":
                # More likely to move away when defensive
                if abs(distance_x) < 250:
                    if distance_x > 0:
                        self.move(-move_speed, player)
                    else:
                        self.move(move_speed, player)
            else:
                # Only move away if too close (normal/aggressive)
                if abs(distance_x) < 150:
                    if distance_x > 0:
                        self.move(-move_speed, player)
                    else:
                        self.move(move_speed, player)
        
        elif self.current_action == "jump" and not self.is_jumping:
            # More likely to jump when aggressive to close distance
            if self.aggression_level == "aggressive" or (self.aggression_level == "defensive" and random.random() < 0.3):
                self.jump()
        
        elif self.current_action == "attack":
        # Reduced attack ranges based on aggression
            if self.aggression_level == "aggressive":
                attack_range = 120  
            elif self.aggression_level == "defensive":
                attack_range = 80   
            else:
                attack_range = 100  
            
            # Make enemy more likely to attack when close
            if abs(distance_x) < attack_range and distance_y < 40:  # Reduced vertical tolerance
                self.attack(player)
                
                # After attacking when defensive, immediately consider moving away
                if self.aggression_level == "defensive" and random.random() < 0.7:
                    self.current_action = "move_away"
                    self.move_timer = 20  
    
    def update(self, player):
        # Apply gravity
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y
        
        # Ground collision
        if self.rect.bottom >= 720 - 20:  # SCREEN_HEIGHT - ground height
            self.rect.bottom = 720 - 20
            self.is_jumping = False
            self.velocity_y = 0
        
        # Update animation state based on current conditions
        if not self.is_jumping and self.current_state != "attack":
            if self.current_action in ["move_towards", "move_away"]:
                # Use run animation for movement
                self.set_state("run")
            else:
                self.set_state("idle")
        
        # Update animation
        if self.current_animation:
            self.current_animation.update()
            
            # Return to appropriate state after attack animation finishes
            if self.current_state == "attack" and self.current_animation.is_finished():
                if self.is_jumping:
                    self.set_state("jump")
                elif self.current_action in ["move_towards", "move_away"]:
                    self.set_state("run")
                else:
                    self.set_state("idle")
            
            # Return to appropriate state after jump animation finishes (if on ground)
            if self.current_state == "jump" and self.current_animation.is_finished() and not self.is_jumping:
                if self.current_action in ["move_towards", "move_away"]:
                    self.set_state("run")
                else:
                    self.set_state("idle")
        
        # AI behavior
        self.ai_think(player)
    
    def draw(self, screen):
        if self.current_animation and self.current_animation.get_current_frame():
            current_frame = self.current_animation.get_current_frame()
            
            # Flip the frame if facing left (enemies face opposite direction)
            if not self.facing_right:
                current_frame = pygame.transform.flip(current_frame, True, False)
            
            # Draw the sprite centered on the rectangle
            sprite_rect = current_frame.get_rect()
            sprite_rect.center = self.rect.center
            screen.blit(current_frame, sprite_rect)
        else:
            # Fallback: draw rectangle if no sprites loaded
            pygame.draw.rect(screen, self.color, self.rect)
        
        # Draw facing direction indicator with color based on aggression
        direction_color = RED if self.aggression_level == "aggressive" else YELLOW if self.aggression_level == "defensive" else GREEN
        direction_x = self.rect.centerx + (20 if self.facing_right else -20)
        pygame.draw.circle(screen, direction_color, (direction_x, self.rect.centery), 5)
        
        # Draw health bar
        health_width = (self.rect.width * self.health) // 100
        health_color = GREEN if self.health > 50 else RED
        health_bar = pygame.Rect(self.rect.x, self.rect.y - 25, health_width, 10)
        pygame.draw.rect(screen, health_color, health_bar)
        
        # Draw health bar background
        health_bg = pygame.Rect(self.rect.x, self.rect.y - 25, self.rect.width, 10)
        pygame.draw.rect(screen, WHITE, health_bg, 1)
        
        # Draw regen indicator (pulsing green circle when regenerating)
        if self.health_regen_timer >= self.health_regen_delay and self.health < self.max_health:
            regen_x = self.rect.centerx
            regen_y = self.rect.y - 40
            pulse = (pygame.time.get_ticks() // 200) % 2  # Pulsing effect
            size = 5 if pulse else 3
            pygame.draw.circle(screen, GREEN, (regen_x, regen_y), size)
