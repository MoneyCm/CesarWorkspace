import cv2
import pygame
import numpy as np
import sys
from tracker import HandTracker
from visuals import ArtEngine

def main():
    # Initialize PyGame
    pygame.init()
    WIDTH, HEIGHT = 1280, 720
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("HandArt Kinessis - Antigravity")
    clock = pygame.time.Clock()

    # Initialize Webcam
    cap = cv2.VideoCapture(0)
    cap.set(3, WIDTH)
    cap.set(4, HEIGHT)

    # Initialize Hand Tracker
    tracker = HandTracker(num_hands=2)
    
    # Initialize Art Engine
    art = ArtEngine(WIDTH, HEIGHT)

    running = True
    show_camera = True
    
    while running:
        # 1. PyGame Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    art.clear()
                if event.key == pygame.K_v:
                    show_camera = not show_camera

        # 2. Get Frame from Camera
        success, img = cap.read()
        if not success:
            print("Failed to get camera frame")
            break
            
        # Mirror image for natural feel
        img = cv2.flip(img, 1)
        
        # 3. Track Hands
        tracker.find_hands(img, draw=False) # Don't draw MP stickman on camera feed yet
        lm_list = tracker.find_position(img, draw=False)
        
        # 4. Interaction Logic
        if len(lm_list) != 0:
            # Index Finger Tip (ID 8)
            ix, iy = lm_list[8][1], lm_list[8][2]
            
            # Add particles at index finger
            art.add_particles(ix, iy, amount=5)
            
            # Check for "fist" or "open hand" to control visuals?
            # For now, just simple drawing.

        # 5. Render
        screen.fill((0, 0, 0)) # Clean screen
        
        if show_camera:
            # Convert OpenCV (BGR) to PyGame (RGB)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_rgb = np.rot90(img_rgb)
            img_rgb = np.flipud(img_rgb)
            frame_surface = pygame.surfarray.make_surface(img_rgb)
            # Fade out camera slightly so art pops
            frame_surface.set_alpha(100) 
            screen.blit(frame_surface, (0, 0))
            
        # Draw Art
        art.update_and_draw(screen)
        
        # UI Hints
        font = pygame.font.SysFont('Arial', 20)
        text = font.render(f"FPS: {int(clock.get_fps())} | 'C' to Clear | 'V' to Toggle Camera", True, (255, 255, 255))
        screen.blit(text, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
