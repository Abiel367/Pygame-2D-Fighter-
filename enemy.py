import pygame
import os
import random

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
        
        # Animation states
        self.current_state = "idle"
        self.states = {}
        self.load_animations()
    
    
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
    
    def update_aggression_level(self):
        # Change behavior based on health
        if self.health <= 45:
            self.aggression_level = "defensive"  
        elif self.health <= 70:
            self.aggression_level = "aggressive" 
        else:
            self.aggression_level = "aggressive"  
    
    
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
        
        
