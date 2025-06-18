import sys
import time
import random
from ursina import *

# 1. Initialize Ursina Application
app = Ursina()

# 2. Global Variables for FPS Tracking and Duplication
fps_values = []
start_time = time.time()
test_duration = 10  # seconds
duplication_active = True
cube_count = 0

# NEW: Define how many cubes to spawn per frame
CUBES_PER_FRAME = 5 # Increase this number to spawn cubes even faster!

# 3. Create a Camera and Lighting
camera.position = (0, 0, -20) # Move camera back along the Z-axis to see more
camera.rotation_x = 0 # Look straight ahead

# Add some lighting
light = DirectionalLight(direction=(1, 1, 1), intensity=0.8)
AmbientLight(color=color.rgba(100, 100, 100, 10))

# 4. Create the FPS Counter Text Entity
fps_text = Text(text="FPS: 0", origin=(-0.85, 0.45), scale=2, color=color.white)

# 5. Removed custom Cube Counter Text Entity


# 6. `update` Function (Game Loop)
def update():
    global duplication_active, cube_count

    # Check if the test duration has passed
    if time.time() - start_time >= test_duration and duplication_active:
        duplication_active = False # Stop duplicating
        print_fps_statistics() # Print results
        application.quit() # Close the Ursina window

    if duplication_active:
        # Loop to create multiple cubes per frame
        for _ in range(CUBES_PER_FRAME):
            # We'll slightly offset each new cube to make them somewhat visible
            # This creates a "pile" of cubes.
            # Adding a small random offset can make the pile less uniform.
            new_cube_position = (
                random.uniform(-0.5, 0.5), # X-offset
                random.uniform(-0.5, 0.5), # Y-offset
                random.uniform(-0.5, 0.5)  # Z-offset
            )
            # Create the new cube with slightly smaller scale for better visibility of overlap
            new_cube = Entity(model='cube', texture='white_cube', color=color.white,
                              position=new_cube_position,
                              scale=0.5)
            # The Ursina engine automatically adds entities to the scene when created,
            # so we don't need a separate list like `all_cubes` for drawing.
            # We only increment a counter for statistics.
            cube_count += 1

        # Record the current FPS
        # Correctly calculate FPS using time.dt (delta time)
        if time.dt > 0: # Ensure time.dt is not zero to avoid division by zero
            current_fps = 1 / time.dt
            if current_fps > 0: # Avoid recording 0 FPS at the very start
                fps_values.append(current_fps)

    # Update the FPS display on screen
    display_fps = 0
    if time.dt > 0:
        display_fps = 1 / time.dt
    fps_text.text = f"FPS: {int(display_fps)}"

    # Removed custom cube count display update


# 7. Function to Print FPS Statistics
def print_fps_statistics():
    global fps_values, cube_count

    print("\n--- Ursina Performance Test Results ---")
    print(f"Test Duration: {test_duration} seconds")
    print(f"Total Cubes Generated: {cube_count}")

    if fps_values:
        filtered_fps_values = [f for f in fps_values if f > 0]

        if filtered_fps_values:
            min_fps = min(filtered_fps_values)
            max_fps = max(filtered_fps_values)
            avg_fps = sum(filtered_fps_values) / len(filtered_fps_values)

            print(f"Lowest FPS: {min_fps:.2f}")
            print(f"Highest FPS: {max_fps:.2f}")
            print(f"Average FPS: {avg_fps:.2f}")
        else:
            print("No valid FPS data collected during the test (ensure time.dt > 0).")
    else:
        print("No FPS data collected.")

# 8. Run the Ursina Application
app.run()

# 9. Exit System (after Ursina app closes)
sys.exit()
