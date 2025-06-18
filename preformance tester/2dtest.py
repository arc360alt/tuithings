import pygame
import sys
import random
import time # Import the time module for the timer

# 1. Initialize Pygame
pygame.init()

# 2. Screen Dimensions and Setup
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Sprite Duplicator - Faster Spawn & FPS Counter")

# 3. Define Colors (RGB tuples)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# 4. Sprite Properties
SPRITE_SIZE = 50
# Define how many duplicates to create per frame
DUPLICATES_PER_FRAME = 5 # You can increase this number to spawn even more cubes rapidly!
# Define the maximum random offset for duplicated sprites
MAX_DUPLICATE_OFFSET = 20 # Adjust this value to make the duplicates more spread out

# 5. Timer Variables
start_time = time.time() # Record the time when the application starts
test_duration = 20 # seconds - the application will run for this duration

# 6. Sprite Class
class Sprite:
    def __init__(self, x, y, color):
        """
        Initializes a new Sprite object.
        Args:
            x (int): The initial x-coordinate (top-left) of the sprite.
            y (int): The initial y-coordinate (top-left) of the sprite.
            color (tuple): The RGB color of the sprite.
        """
        self.image = pygame.Surface((SPRITE_SIZE, SPRITE_SIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, surface):
        """
        Draws the sprite onto the given surface.
        Args:
            surface (pygame.Surface): The surface to draw the sprite on.
        """
        surface.blit(self.image, self.rect)

# 7. Initial Game State Setup
main_sprite_color = RED
# Start the main sprite at a random initial position.
initial_x = random.randint(0, WIDTH - SPRITE_SIZE)
initial_y = random.randint(0, HEIGHT - SPRITE_SIZE)
main_sprite = Sprite(initial_x, initial_y, main_sprite_color)
all_sprites = [main_sprite]

# 8. FPS Counter and Tracking Setup
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
fps_values = []

# 9. Game Loop
running = True
while running:
    # --- Check for Timer Expiration ---
    if time.time() - start_time >= test_duration:
        running = False # Exit the loop if the test duration is over

    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Sprite Movement Logic (Automatic Random Movement) ---
    # Store the main sprite's position *before* potential movement for duplication.
    old_rect_pos = main_sprite.rect.topleft

    # Generate new random coordinates for the main sprite.
    # Ensure the new position keeps the entire sprite within the screen boundaries.
    new_x = random.randint(0, WIDTH - SPRITE_SIZE)
    new_y = random.randint(0, HEIGHT - SPRITE_SIZE)

    # Move the main sprite to the new random position.
    main_sprite.rect.topleft = (new_x, new_y)

    # --- Sprite Duplication Logic (Spawning Multiple Duplicates) ---
    # We always consider the main sprite "moved" since it teleports every frame.
    # Now, we duplicate it multiple times per frame based on DUPLICATES_PER_FRAME.
    for _ in range(DUPLICATES_PER_FRAME):
        # Generate a slightly different color for each duplicate.
        duplicate_color = (
            (main_sprite_color[0] + random.randint(-50, 50)) % 256,
            (main_sprite_color[1] + random.randint(-50, 50)) % 256,
            (main_sprite_color[2] + random.randint(-50, 50)) % 256
        )
        # Calculate a random offset for the new duplicate
        offset_x = random.randint(-MAX_DUPLICATE_OFFSET, MAX_DUPLICATE_OFFSET)
        offset_y = random.randint(-MAX_DUPLICATE_OFFSET, MAX_DUPLICATE_OFFSET)

        # Create the new sprite at the OLD position of the main sprite PLUS the offset
        new_sprite = Sprite(old_rect_pos[0] + offset_x, old_rect_pos[1] + offset_y, duplicate_color)
        all_sprites.append(new_sprite)

        # Optional: Limit the number of sprites if performance becomes too low.
        # This removes the oldest duplicate when a certain number is exceeded.
        # if len(all_sprites) > 2000: # Example limit
        #     all_sprites.pop(1) # Index 0 is the main sprite, so remove from index 1 onwards


    # --- Drawing ---
    SCREEN.fill(BLACK) # Clear the screen

    # Draw all sprites
    for sprite in all_sprites:
        sprite.draw(SCREEN)

    # --- FPS Counter Display ---
    current_fps = clock.get_fps()
    if current_fps > 0: # Only record valid FPS values
        fps_values.append(current_fps)
    fps_text = font.render(f"FPS: {int(current_fps)}", True, WHITE)
    SCREEN.blit(fps_text, (10, 10))

    # --- Sprite Counter Display ---
    # Render the current number of sprites on the screen
    sprite_count_text = font.render(f"Sprites: {len(all_sprites)}", True, WHITE)
    SCREEN.blit(sprite_count_text, (10, 50)) # Position it below the FPS counter

    # --- Update Display ---
    pygame.display.flip()

    # --- Frame Rate Cap ---
    clock.tick(1000) # Cap the frame rate to 60 FPS

# 10. End of Game Loop - Quit Pygame
pygame.quit()

# 11. FPS Statistics Calculation and Printing
if fps_values:
    filtered_fps_values = [fps for fps in fps_values if fps > 0]
    if filtered_fps_values:
        min_fps = min(filtered_fps_values)
        max_fps = max(filtered_fps_values)
        avg_fps = sum(filtered_fps_values) / len(filtered_fps_values)

        print("\n--- FPS Statistics ---")
        print(f"Total Sprites Generated: {len(all_sprites)}")
        print(f"Lowest FPS: {min_fps:.2f}")
        print(f"Highest FPS: {max_fps:.2f}")
        print(f"Average FPS: {avg_fps:.2f}")
    else:
        print("\nNo valid FPS data collected (the application might have closed too quickly).")
else:
    print("\nNo FPS data collected.")

# 12. Exit System
sys.exit()
