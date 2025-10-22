import pygame
import os

class Background:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.images = []
        self.current_bg_index = 0
        self.load_backgrounds()
        
    def load_backgrounds(self):
        #Load all background images from the assets/background folder
        background_path = "assets/background"
        
        if os.path.exists(background_path):
            # Get all image files 
            image_files = [f for f in os.listdir(background_path) 
                          if f.endswith(('.png', '.jpg', '.jpeg'))]
            image_files.sort()  # Sort to ensure consistent order
            
            for filename in image_files:
                try:
                    image_path = os.path.join(background_path, filename)
                    image = pygame.image.load(image_path).convert()
                    
                    # Scale image to fit screen if needed
                    if image.get_width() != self.screen_width or image.get_height() != self.screen_height:
                        image = pygame.transform.scale(image, (self.screen_width, self.screen_height))
                    
                    self.images.append(image)
                    print(f"Loaded background: {filename}")
                    
                except pygame.error as e:
                    print(f"Unable to load background image: {image_path}")
                    print(e)
        
        # If no backgrounds were loaded, create a fallback background
        if not self.images:
            print("No background images found. Creating fallback background.")
            fallback_bg = pygame.Surface((self.screen_width, self.screen_height))
            fallback_bg.fill((50, 50, 100))  # Dark blue color
            self.images.append(fallback_bg)
    
    def get_current_background(self):
        #Get the current background image
        if self.images:
            return self.images[self.current_bg_index]
        return None
    
    def next_background(self):
        # Switch to next background 
        if len(self.images) > 1:
            self.current_bg_index = (self.current_bg_index + 1) % len(self.images)
    
    def set_background(self, index):
        #Set specific background by index
        if 0 <= index < len(self.images):
            self.current_bg_index = index
    
    def draw(self, screen):
        #Draw the background to the screen
        current_bg = self.get_current_background()
        if current_bg:
            screen.blit(current_bg, (0, 0))
