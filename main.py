from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
import sys

# Game state variables
player_pos = [0, 0, 0]  # Player position
body_angle = 0  # Body rotation angle
enemies = []  # List of enemies
player_life = 5  # Player lives
game_score = 0  # Game score
cheat_mode = False  # Cheat mode flag
auto_follow = False  # Auto follow flag
camera_mode = "third_person"  # Camera mode
game_over = False  # Game over flag
exit_pos = None  # Will store the exit position
game_start_time = 0  # When the game started
game_completed = False  # Whether player reached the exit
completion_time = 0  # Time taken to complete
star_rating = 0  # Star rating (0-3)
reward_collected = False  # Track if reward was collected
quiones = []  # List of quiones (time-decreasing objects)
last_quione_spawn_time = 0  # When last quione was spawned
QUIONE_SPAWN_INTERVAL = 10  # Seconds between quione spawns

# Camera-related variables
camera_pos = [0, 500, 500]  # Default camera position
camera_angle_x = 45  # Camera rotation around X axis
camera_angle_y = 45  # Camera rotation around Y axis
camera_distance = 500  # Camera distance from player

# Game constants
GRID_SIZE = 950  # Size of the game grid
ENEMY_COUNT = 2  # Number of enemies
ENEMY_SPEED = 0.5  # Enemy speed
PLAYER_SPEED = 30  # Player movement speed
ENEMY_SIZE = 30  # Base enemy size
ENEMY_PULSE_SPEED = 0.05  # Enemy pulsing speed
PLAYER_RADIUS = 15  # Player collision radius
ENEMY_RADIUS = 15  # Enemy collision radius
QUIONE_RADIUS = 20  
TIME_PENALTY = 5  

# Maze configuration
WALL_HEIGHT = 130
WALL_THICKNESS = 50
COLLISION_MARGIN = 6

maze = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,0,1,0,1,0,1,1,1,0,1,0,1,0,1,0,1],
    [1,0,1,0,0,1,0,0,0,0,0,1,0,0,0,1,0,0,0,1],
    [1,0,1,0,1,1,0,0,1,1,0,1,1,1,0,1,1,1,0,1],
    [1,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,0,1],
    [1,0,1,0,1,1,0,1,1,0,1,1,0,1,1,1,0,1,0,1],
    [1,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,0,0,0,1],
    [1,0,1,1,0,1,0,0,1,1,0,1,1,1,0,1,0,1,0,1],
    [1,0,1,0,0,0,0,0,0,1,1,0,1,1,0,0,0,1,0,1],
    [1,0,1,0,1,1,1,1,0,1,0,1,0,1,1,1,0,1,0,1],
    [1,0,0,0,0,0,0,1,0,0,1,0,0,1,0,1,0,1,0,1],
    [1,1,0,0,1,1,1,1,1,1,0,1,0,1,0,1,1,1,0,1],
    [1,0,1,0,1,1,0,0,0,0,0,1,0,1,0,1,1,0,0,1],
    [1,0,1,1,0,1,1,0,0,1,0,1,1,0,0,1,1,1,0,1],
    [1,0,1,0,0,0,1,0,0,1,0,0,1,1,0,0,0,1,0,1],
    [1,0,1,0,1,0,1,1,0,1,0,1,0,1,0,1,0,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1],
]

# Maze dimensions
maze_width = 0
maze_height = 0
maze_offset_x = 0
maze_offset_y = 0
wall_boundaries = []  # For collision detection

def init_maze():
    
    global maze_width, maze_height, maze_offset_x, maze_offset_y, wall_boundaries, exit_pos
    
    rows = len(maze)
    cols = len(maze[0])
    cell_size = WALL_THICKNESS * 2
    
    maze_offset_x = -cols * WALL_THICKNESS
    maze_offset_y = -rows * WALL_THICKNESS
    maze_width = cols * cell_size
    maze_height = rows * cell_size
    
    wall_boundaries = []
    
    for i in range(rows):
        for j in range(cols):
            if maze[i][j] == 1:
                x = maze_offset_x + j * cell_size
                y = maze_offset_y + i * cell_size
                wall_boundaries.append((
                    x - COLLISION_MARGIN,
                    y - COLLISION_MARGIN, 
                    x + cell_size + COLLISION_MARGIN, 
                    y + cell_size + COLLISION_MARGIN,
                    False
                ))
    
    # Set exit position (the single 0 in the last row)
    for j in range(cols):
        if maze[rows-1][j] == 0:
            exit_pos = [
                maze_offset_x + j * cell_size + cell_size/2,
                maze_offset_y + (rows-1) * cell_size + cell_size/2,
                0
            ]
            break

def is_point_in_wall(x, y, radius=0):
  
    for min_x, min_y, max_x, max_y, _ in wall_boundaries:
        if (x + radius > min_x and 
            x - radius < max_x and 
            y + radius > min_y and 
            y - radius < max_y):
            return True
    return False

def check_wall_collision(new_x, new_y, current_x, current_y, radius):
  
    if is_point_in_wall(new_x, new_y, radius):
        # Try moving only in X direction
        if not is_point_in_wall(new_x, current_y, radius):
            return new_x, current_y, True
        
        # Try moving only in Y direction
        if not is_point_in_wall(current_x, new_y, radius):
            return current_x, new_y, True
        
        # If both axes collide, stay in place
        return current_x, current_y, False
    
    # No collision
    return new_x, new_y, True

def movement_with_collision_detection(dx, dy, entity_pos, radius):
    """Move entity with collision detection"""
    current_x, current_y = entity_pos[0], entity_pos[1]
    new_x = current_x + dx
    new_y = current_y + dy
    
    final_x, final_y, moved = check_wall_collision(new_x, new_y, current_x, current_y, radius)
    
    entity_pos[0] = final_x
    entity_pos[1] = final_y
    
    return moved

def draw_maze():
   
    rows = len(maze)
    cols = len(maze[0])
    cell_size = WALL_THICKNESS * 2
    
    offset_x = maze_offset_x
    offset_y = maze_offset_y
    
    for i in range(rows):
        for j in range(cols):
            if maze[i][j] == 1:
                x = offset_x + j * cell_size
                y = offset_y + i * cell_size
                z = 0
                
                glPushMatrix()
                glTranslatef(x + WALL_THICKNESS/2, y + WALL_THICKNESS/2, z + WALL_HEIGHT/2)
                glColor3f(0, 0.5, 0)  # Green walls
                glScalef(cell_size, cell_size, WALL_HEIGHT)
                glutSolidCube(1.0)
                
                glDisable(GL_LIGHTING)
                glColor3f(0, 0, 0)  # Black borders
                glutWireCube(1.01)
                glEnable(GL_LIGHTING)
                glPopMatrix()
    
    # Draw exit position (last row's 0) as a red cube
    if exit_pos:
        x, y, z = exit_pos
        glPushMatrix()
        glTranslatef(x, y, z + 50)  # Position the cube above ground
        glColor3f(1.0, 0.0, 0.0)  # Bright red
        glutSolidCube(50)  # Draw a cube of size 50
        glPopMatrix()

def init_game():
    global player_pos, body_angle, enemies, player_life, game_score, game_over
    global exit_pos, game_start_time, game_completed, completion_time, star_rating, reward_collected
    global quiones, last_quione_spawn_time
    
    player_pos = [0, 0, 0]
    body_angle = 0
    enemies = []
    quiones = []
    player_life = 5
    game_score = 0
    game_over = False
    game_completed = False
    completion_time = 0
    star_rating = 0
    reward_collected = False
    last_quione_spawn_time = 0
    
    # Initialize maze
    init_maze()
    
    # Place player in a valid starting position
    place_player_in_maze()
    
    # Initialize enemies at random positions
    for _ in range(ENEMY_COUNT):
        spawn_enemy()
    
    # Record start time (in seconds)
    game_start_time = glutGet(GLUT_ELAPSED_TIME) / 1000.0

def place_player_in_maze():

    global player_pos
    
    rows = len(maze)
    cols = len(maze[0])
    cell_size = WALL_THICKNESS * 2
    
    # Find first open position (not the exit)
    for i in range(rows-1):  # Skip last row where exit is
        for j in range(cols):
            if maze[i][j] == 0:
                player_pos[0] = maze_offset_x + j * cell_size + cell_size/2
                player_pos[1] = maze_offset_y + i * cell_size + cell_size/2
                player_pos[2] = 0
                return
    
    # Default position if no open space found (shouldn't happen with this maze)
    player_pos = [0, 0, 0]

def spawn_enemy():
   
    rows = len(maze)
    cols = len(maze[0])
    cell_size = WALL_THICKNESS * 2
    
    # Find all open positions (not the exit)
    open_positions = []
    for i in range(rows-1):  # Skip last row where exit is
        for j in range(cols):
            if maze[i][j] == 0:
                x = maze_offset_x + j * cell_size + cell_size/2
                y = maze_offset_y + i * cell_size + cell_size/2
                open_positions.append((x, y))
    
    # Place enemy if open positions exist
    if open_positions:
        x, y = random.choice(open_positions)
        enemies.append({
            'pos': [x, y, 0],
            'size': ENEMY_SIZE,
            'pulse': 0,
            'speed': random.uniform(ENEMY_SPEED * 0.5, ENEMY_SPEED * 1.5)
        })

def spawn_quione():
    """Spawn a time-decreasing quione at random position"""
    rows = len(maze)
    cols = len(maze[0])
    cell_size = WALL_THICKNESS * 2
    
    # Find all open positions (not the exit)
    open_positions = []
    for i in range(rows-1):  # Skip last row where exit is
        for j in range(cols):
            if maze[i][j] == 0:
                x = maze_offset_x + j * cell_size + cell_size/2
                y = maze_offset_y + i * cell_size + cell_size/2
                open_positions.append((x, y))
    
    # Place quione if open positions exist
    if open_positions:
        x, y = random.choice(open_positions)
        quiones.append({
            'pos': [x, y, 0],
            'size': QUIONE_RADIUS,
            'rotation': 0,
            'rotation_speed': random.uniform(0.5, 2.0)
        })

def check_quione_collision():
   
    global game_start_time, quiones
    
    current_time = glutGet(GLUT_ELAPSED_TIME) / 1000.0
    
    for quione in quiones[:]:  # Create a copy for iteration
        dx = player_pos[0] - quione['pos'][0]
        dy = player_pos[1] - quione['pos'][1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < PLAYER_RADIUS + QUIONE_RADIUS:
            # Player touched quione - decrease time by penalty
            game_start_time += TIME_PENALTY
            quiones.remove(quione)
            
            # Play a sound (if sound was enabled)
            # glutPostRedisplay()

def check_exit_reached():
    global game_completed, completion_time, star_rating, game_over, reward_collected, game_score
    
    if exit_pos is None or game_completed:
        return
    
    # Calculate current game time
    current_time = (glutGet(GLUT_ELAPSED_TIME) / 1000.0) - game_start_time
    
    # Game automatically ends after 2 minutes (120 seconds)
    if current_time >= 120:
        game_completed = False  # Player didn't reach exit in time
        game_over = True
        completion_time = current_time
        star_rating = 0  # No stars for timeout
        return
    
    # Calculate distance to exit
    dx = player_pos[0] - exit_pos[0]
    dy = player_pos[1] - exit_pos[1]
    distance = math.sqrt(dx*dx + dy*dy)
    
    # Check if player is close enough to exit (using cube size)
    if distance < PLAYER_RADIUS + 25:  # 25 is half of cube size (50/2)
        if not reward_collected:
            reward_collected = True
            game_score += 1000  # Big reward for reaching exit
        
        game_completed = True
        game_over = True
        completion_time = current_time
        
        # Calculate star rating based on completion time
        if completion_time <= 60:    # Under 1 minute = 3 stars
            star_rating = 3
        elif completion_time <= 75:   # Under 1.15 minutes = 2 stars
            star_rating = 2
        elif completion_time <= 99:   # Under 1.59 minutes = 1 star
            star_rating = 1
        else:                         # Over 1.59 minutes = 0 stars
            star_rating = 0

def draw_player():
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    glRotatef(body_angle, 0, 0, 1)  # Rotate entire body
    
    # Torso (main cuboid) - Dark Green
    glPushMatrix()
    glColor3f(0.0, 0.4, 0.0)  # Dark green
    glTranslatef(0, 0, 50)  # Center of body
    glScalef(40, 30, 100)  # Width, Depth, Height
    glutSolidCube(1)
    glPopMatrix()

    # Head (sphere) - Black
    glPushMatrix()
    glColor3f(0.0, 0.0, 0.0)  # Black
    glTranslatef(0, 0, 100)  # On top of torso
    glutSolidSphere(25, 20, 20)
    glPopMatrix()

    # Arms (cylinders) - Skin color, stretched forward horizontally
    glPushMatrix()
    glColor3f(0.9, 0.7, 0.6)  # Skin color
    # Left arm (stretched forward)
    glPushMatrix()
    glTranslatef(-15, 30, 70)  # Moved closer to center
    glRotatef(90, 1, 0, 0)  # Rotate to point forward (horizontal)
    gluCylinder(gluNewQuadric(), 12, 12, 60, 10, 10)  # Arm length 60 forward
    glPopMatrix()
    # Right arm (stretched forward)
    glPushMatrix()
    glTranslatef(15, 30, 70)  # Moved closer to center
    glRotatef(90, 1, 0, 0)  # Rotate to point forward (horizontal)
    gluCylinder(gluNewQuadric(), 12, 12, 60, 10, 10)  # Arm length 60 forward
    glPopMatrix()
    glPopMatrix()

    # Legs (cuboids) - Blue (increased size)
    glPushMatrix()
    glColor3f(0.0, 0.0, 0.8)  # Blue
    # Left leg (larger)
    glPushMatrix()
    glTranslatef(-20, 0, 0)  # Wider stance
    glScalef(20, 20, 60)  # Increased size (was 15,15,50)
    glutSolidCube(1)
    glPopMatrix()
    # Right leg (larger)
    glPushMatrix()
    glTranslatef(20, 0, 0)  # Wider stance
    glScalef(20, 20, 60)  # Increased size (was 15,15,50)
    glutSolidCube(1)
    glPopMatrix()
    glPopMatrix()

    glPopMatrix()  # End player

def draw_enemies():
    for enemy in enemies:
        glPushMatrix()
        glTranslatef(enemy['pos'][0], enemy['pos'][1], enemy['pos'][2])
        
        # Enemy pulsing effect
        pulse_factor = 1 + math.sin(enemy['pulse']) * 0.2
        enemy['pulse'] += ENEMY_PULSE_SPEED
        
        # Main enemy body (larger sphere)
        glColor3f(0.8, 0.2, 0.2)  # Red color for enemies
        glutSolidSphere(ENEMY_SIZE * pulse_factor, 20, 20)
        
        # Enemy eye (smaller sphere)
        glPushMatrix()
        glTranslatef(20 * pulse_factor, 20 * pulse_factor, 20 * pulse_factor)
        glColor3f(1, 1, 1)  # White eye
        glutSolidSphere(10 * pulse_factor, 10, 10)  # Eye size
        glPopMatrix()
        
        glPopMatrix()

def draw_quiones():
    """Draw the time-decreasing quiones"""
    for quione in quiones:
        glPushMatrix()
        glTranslatef(quione['pos'][0], quione['pos'][1], quione['pos'][2])
        
        # Rotate quione for visual effect
        quione['rotation'] += quione['rotation_speed']
        glRotatef(quione['rotation'], 0, 0, 1)
        
        # Draw quione as a spinning hourglass shape
        glColor3f(0.5, 0.2, 0.7)  # Purple color for quiones
        
        # Bottom pyramid
        glPushMatrix()
        glTranslatef(0, 0, -10)
        glRotatef(180, 1, 0, 0)  # Point downward
        glutSolidCone(QUIONE_RADIUS, 20, 10, 10)
        glPopMatrix()
        
        # Top pyramid
        glPushMatrix()
        glTranslatef(0, 0, 10)
        glutSolidCone(QUIONE_RADIUS, 20, 10, 10)
        glPopMatrix()
        
        glPopMatrix()

def draw_grid():
    """Draw the grid floor"""
    glBegin(GL_QUADS)
    glColor3f(0.25, 0.25, 0.25)  # Dark gray floor
    glVertex3f(-GRID_SIZE, -GRID_SIZE, 0)
    glVertex3f(-GRID_SIZE, GRID_SIZE, 0)
    glVertex3f(GRID_SIZE, GRID_SIZE, 0)
    glVertex3f(GRID_SIZE, -GRID_SIZE, 0)
    glEnd()
    
    # Draw grid lines
    glBegin(GL_LINES)
    glColor3f(0.35, 0.35, 0.35)  # Light gray grid lines
    for i in range(-GRID_SIZE, GRID_SIZE + 1, 50):
        # Horizontal lines
        glVertex3f(-GRID_SIZE, i, 0.1)
        glVertex3f(GRID_SIZE, i, 0.1)
        # Vertical lines
        glVertex3f(i, -GRID_SIZE, 0.1)
        glVertex3f(i, GRID_SIZE, 0.1)
    glEnd()

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18, color=(1, 1, 1)):
    glColor3f(*color)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def keyboardListener(key, x, y):
    global body_angle, player_pos, cheat_mode, auto_follow, game_over
    
    if game_over and key == b'r':
        init_game()
        return
    
    # Body rotation
    if key == b'a':  # Rotate body left
        body_angle += 5
    elif key == b'd':  # Rotate body right
        body_angle -= 5
    
    # Player movement (with collision detection)
    if key == b'w':  # Move forward
        rad = math.radians(body_angle)
        dx = math.sin(rad) * PLAYER_SPEED
        dy = math.cos(rad) * PLAYER_SPEED
        movement_with_collision_detection(dx, dy, player_pos, PLAYER_RADIUS)
    elif key == b's':  # Move backward
        rad = math.radians(body_angle)
        dx = -math.sin(rad) * PLAYER_SPEED
        dy = -math.cos(rad) * PLAYER_SPEED
        movement_with_collision_detection(dx, dy, player_pos, PLAYER_RADIUS)

    
    # Cheat modes
    if key == b'c':
        cheat_mode = not cheat_mode
    elif key == b'v' and cheat_mode:
        auto_follow = not auto_follow

def specialKeyListener(key, x, y):
    global camera_angle_x, camera_angle_y, camera_distance
    
    # Camera controls
    if key == GLUT_KEY_UP:
        camera_angle_x = min(89, camera_angle_x + 5)
    elif key == GLUT_KEY_DOWN:
        camera_angle_x = max(0, camera_angle_x - 5)
    elif key == GLUT_KEY_LEFT:
        camera_angle_y = (camera_angle_y + 5) % 360
    elif key == GLUT_KEY_RIGHT:
        camera_angle_y = (camera_angle_y - 5) % 360

def mouseListener(button, state, x, y):
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN and not game_over:
        toggle_camera_mode()
        
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        toggle_camera_mode()

def toggle_camera_mode():
    global camera_mode
    camera_mode = "first_person" if camera_mode == "third_person" else "third_person"

def update_camera():
    if camera_mode == "first_person":
        # First-person view from body perspective
        rad = math.radians(body_angle)
        eye_x = player_pos[0] + math.sin(rad) * 50
        eye_y = player_pos[1] + math.cos(rad) * 50
        eye_z = player_pos[2] + 30
        
        look_x = player_pos[0] + math.sin(rad) * 100
        look_y = player_pos[1] + math.cos(rad) * 100
        look_z = player_pos[2] + 30
        
        gluLookAt(eye_x, eye_y, eye_z,
                 look_x, look_y, look_z,
                 0, 0, 1)
    else:
        # Third-person view orbiting player
        rad_y = math.radians(camera_angle_y)
        rad_x = math.radians(camera_angle_x)
        
        cam_x = player_pos[0] + camera_distance * math.sin(rad_y) * math.cos(rad_x)
        cam_y = player_pos[1] + camera_distance * math.cos(rad_y) * math.cos(rad_x)
        cam_z = player_pos[2] + camera_distance * math.sin(rad_x)
        
        gluLookAt(cam_x, cam_y, cam_z,
                 player_pos[0], player_pos[1], player_pos[2],
                 0, 0, 1)

def update_enemies():
    global player_life, game_over
    
    # Move enemies toward player
    for enemy in enemies[:]:  # Create a copy for iteration since we might modify the list
        dx = player_pos[0] - enemy['pos'][0]
        dy = player_pos[1] - enemy['pos'][1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            # Normalize direction vector and apply speed
            dx = (dx / distance) * enemy['speed']
            dy = (dy / distance) * enemy['speed']
            movement_with_collision_detection(dx, dy, enemy['pos'], ENEMY_RADIUS)
        
        # Check for enemy-player collision
        if distance < ENEMY_RADIUS + PLAYER_RADIUS:
            player_life -= 1
            enemies.remove(enemy)
            spawn_enemy()  # Respawn enemy at new position
            if player_life <= 0:
                game_over = True

def update_quiones():
    """Update quiones (spawn new ones and check for collisions)"""
    global last_quione_spawn_time
    
    current_time = glutGet(GLUT_ELAPSED_TIME) / 1000.0
    
    # Spawn new quiones periodically
    if current_time - last_quione_spawn_time > QUIONE_SPAWN_INTERVAL and len(quiones) < 5:
        spawn_quione()
        last_quione_spawn_time = current_time
    
    # Check for player collision with quiones
    check_quione_collision()

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, 1.25, 1, 2000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    update_camera()

def idle():
    if not game_over:
        update_enemies()
        update_quiones()
        check_exit_reached()
    glutPostRedisplay()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    
    setupCamera()
    
    # Enable depth testing for proper 3D rendering
    glEnable(GL_DEPTH_TEST)
    
    # Draw game elements
    draw_grid()
    draw_maze()
    draw_player()
    draw_enemies()
    draw_quiones()
    
    # Calculate current game time
    current_time = 0
    if not game_completed and not game_over:
        current_time = (glutGet(GLUT_ELAPSED_TIME) / 1000.0) - game_start_time
    
    # Draw HUD
    draw_text(20, 740, f"Player Life: {player_life}")
    draw_text(20, 710, f"Enemies: {len(enemies)}")
    draw_text(20, 680, f"Time: {current_time:.1f}s")
    draw_text(20, 650, f"Quiones: {len(quiones)}")
    
    if cheat_mode:
        draw_text(20, 620, "CHEAT MODE ACTIVE", color=(1, 0, 0))
    
    if game_over:
        if game_completed:
            # Display completion results
            draw_text(350, 450, "MAZE COMPLETED!", GLUT_BITMAP_TIMES_ROMAN_24, color=(0, 1, 0))
    
            draw_text(400, 350, f"Time: {completion_time:.1f} seconds", GLUT_BITMAP_TIMES_ROMAN_24)
            if star_rating > 0:
                rating ="*"*star_rating
                draw_text(420, 300, f"Rating: {rating}", GLUT_BITMAP_TIMES_ROMAN_24)
            else:
                draw_text(420, 300, "Too slow! No stars earned", GLUT_BITMAP_TIMES_ROMAN_24)
            draw_text(350, 250, "Press R to play again", GLUT_BITMAP_TIMES_ROMAN_24)
        else:
            if completion_time >= 120:
                # Timeout game over
                draw_text(350, 450, "TIME'S UP!", GLUT_BITMAP_TIMES_ROMAN_24, color=(1, 0, 0))
                draw_text(400, 400, "You didn't reach the exit in time", GLUT_BITMAP_TIMES_ROMAN_24)
                draw_text(350, 350, "Press R to try again", GLUT_BITMAP_TIMES_ROMAN_24)
            else:
                # Game over from losing all lives
                draw_text(400, 400, "GAME OVER - Press R to restart", GLUT_BITMAP_TIMES_ROMAN_24, color=(1, 0, 0))
    
    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"3D Maze Game")
    
    # Initialize game
    init_game()
    
    # Register callbacks
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    
    # Set background color (sky blue)
    glClearColor(0.5, 0.7, 1.0, 1.0)
    
    # Enable lighting
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    
    # Set up light
    glLightfv(GL_LIGHT0, GL_POSITION, [0, 10, 0, 1])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.9, 0.9, 0.9, 1])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [0.5, 0.5, 0.5, 1])
    
    glutMainLoop()

if __name__ == "__main__":
    main()
