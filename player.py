import pygame
import os
from animation import Animation

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

class Player:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.velocity_y = 0
        self.jump_power = -21
        self.gravity = 0.8
        self.is_jumping = False
        self.health = 100
        self.max_health = 100
        self.facing_right = True
        self.attack_cooldown = 0
        self.is_moving = False  # Track movement state
        
        
        # Animation states
        self.current_state = "idle"
        self.states = {}
        self.load_animations()
        
    def load_animations(self):
        #Load all animations for the player
        base_path = "assets/player/"
        
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
        #Load all PNG images from a folder and return as list of surfaces
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
                    print(f"Unable to load image: {os.path.join(folder_path, filename)}")
                    print(e)
        
        if not frames:
            print(f"No frames loaded from {folder_path}")
            
        return frames
    
    def set_state(self, new_state):
        #Change the current animation state
        if new_state != self.current_state and new_state in self.states:
            self.current_state = new_state
            self.current_animation = self.states[new_state]
            self.current_animation.reset()
    
    def jump(self):
        if not self.is_jumping:
            self.velocity_y = self.jump_power
            self.is_jumping = True
            self.set_state("jump")
    
            
            # Set new position
            self.rect.x = new_x
            
            # Set cooldown
            self.teleport_cooldown = self.teleport_cooldown_time
    
    def take_damage(self, amount):
        self.health -= amount
        self.health_regen_timer = 0  # Reset regen timer when taking damage
    
    
    def attack(self, enemy):
        if self.attack_cooldown <= 0 and "attack" in self.states:
            self.set_state("attack")
            attack_range = 50
            attack_height = 40
            
            if self.facing_right:
                attack_rect = pygame.Rect(
                    self.rect.right, 
                    self.rect.centery - attack_height//2, 
                    attack_range, 
                    attack_height
                )
            else:
                attack_rect = pygame.Rect(
                    self.rect.left - attack_range, 
                    self.rect.centery - attack_height//2, 
                    attack_range, 
                    attack_height
                )
            
            # Check if attack hits specific enemy
            if attack_rect.colliderect(enemy.rect):
                if hasattr(enemy, 'take_damage'):
                    enemy.take_damage(5)
                else:
                    enemy.health -= 5            
            self.attack_cooldown = 30
    
    def update(self, enemy):
        # Update cooldowns
        if self.teleport_cooldown > 0:
            self.teleport_cooldown -= 1
        
        # Update teleport effect
        if self.is_teleporting:
            self.teleport_timer -= 1
            if self.teleport_timer <= 0:
                self.is_teleporting = False
        
        # Health regeneration
        self.regenerate_health()
        
        # Update animation state based on current conditions
        if not self.is_jumping and self.current_state != "attack" and not self.is_teleporting:
            if self.is_moving:
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
                elif self.is_moving:
                    self.set_state("run")
                else:
                    self.set_state("idle")
            
            # Return to appropriate state after jump animation finish
            if self.current_state == "jump" and self.current_animation.is_finished() and not self.is_jumping:
                if self.is_moving:
                    self.set_state("run")
                else:
                    self.set_state("idle")
        
        # Ground collision
        if self.rect.bottom >= 720 - 20:  # SCREEN_HEIGHT - ground height
            self.rect.bottom = 720 - 20
            self.velocity_y = 0
            self.is_jumping = False
        
        # Update cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
    
    def draw(self, screen):
        # Only draw if not teleporting 
        if not self.is_teleporting or (self.is_teleporting and self.teleport_timer % 3 == 0):  # Blink effect
            if self.current_animation and self.current_animation.get_current_frame():
                current_frame = self.current_animation.get_current_frame()
                
                # Flip the frame if facing left
                if not self.facing_right:
                    current_frame = pygame.transform.flip(current_frame, True, False)
                
                # Draw the sprite centered on the rectangle
                sprite_rect = current_frame.get_rect()
                sprite_rect.center = self.rect.center
                
                # Add transparency effect during teleport
                if self.is_teleporting:
                    # Create a copy with alpha modulation for teleport effect
                    teleport_frame = current_frame.copy()
                    alpha = 128 + (self.teleport_timer * 12)  # Fade in from transparent
                    teleport_frame.set_alpha(min(255, alpha))
                    screen.blit(teleport_frame, sprite_rect)
                else:
                    screen.blit(current_frame, sprite_rect)
            else:
                # Fallback: draw rectangle if no sprites loaded
                if self.is_teleporting:
                    s = pygame.Surface((self.rect.width, self.rect.height))
                    s.set_alpha(128)
                    s.fill(self.color)
                    screen.blit(s, self.rect)
                else:
                    pygame.draw.rect(screen, self.color, self.rect)
        
        # Draw facing direction indicator
        if not self.is_teleporting:
            direction_x = self.rect.centerx + (20 if self.facing_right else -20)
            pygame.draw.circle(screen, GREEN, (direction_x, self.rect.centery), 5)
        
        
      
