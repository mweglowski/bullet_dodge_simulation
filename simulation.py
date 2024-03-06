import pygame
import random
import agent
from utils import should_bullet_spawn, get_nearest_point, get_distance

pygame.init()

# SCREEN DIMENSIONS
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 600
HALF_WIDTH = SCREEN_WIDTH // 2
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# ELEMENT PROPERTIES
BULLET_WIDTH = 10
BULLET_HEIGHT = 20
BULLET_SPEED = 3
PLAYER_SIZE = 50
PLAYER_SPEED = 6
DIVISION_LINE_WIDTH = 5

# COLORS
WHITE = (255, 255, 255) # USER PLAYER, LINE
BLACK = (0, 0, 0) # BACKGROUND
RED = (255, 0, 0) # BULLETS
BLUE = (0, 0, 255) # AGENT PLAYER

# FPS CONTROLS
clock = pygame.time.Clock()
FPS = 10

class BulletDodgeSimulation:
    def __init__(self):
        self.player_size = PLAYER_SIZE
        self.human_player_x = SCREEN_WIDTH // 4
        self.agent_player_x = 3 * SCREEN_WIDTH // 4
        self.player_speed = PLAYER_SPEED
        self.human_bullets = []
        self.agent_bullets = []
        self.game_over = False
        self.agent = agent.QLearningAgent(n_states=100, n_actions=3)

    def add_bullet(self, agent=False):
        # AGENT SIDE
        if agent:
            x_pos = random.randint(HALF_WIDTH, SCREEN_WIDTH - 10)
        # USER SIDE
        else:
            x_pos = random.randint(0, HALF_WIDTH - 10)

        # 0 -> TOP
        y_pos = 0
        if agent:
            self.agent_bullets.append([x_pos, y_pos])
        else:
            self.human_bullets.append([x_pos, y_pos])

    def update_player(self, action, agent=False):
        if agent:
            if action == "LEFT" and self.agent_player_x > HALF_WIDTH:
                self.agent_player_x -= self.player_speed
            elif action == "RIGHT" and self.agent_player_x < SCREEN_WIDTH - self.player_size:
                self.agent_player_x += self.player_speed
        else:
            if action == "LEFT" and self.human_player_x > 0:
                self.human_player_x -= self.player_speed
            elif action == "RIGHT" and self.human_player_x < HALF_WIDTH - self.player_size:
                self.human_player_x += self.player_speed

    def update_bullets(self, agent=False):
        if agent:
            bullets = self.agent_bullets
        else:
            bullets = self.human_bullets

        for bullet in bullets:
            # UPDATING y VALUE TO MOVE DOWN
            bullet[1] += BULLET_SPEED

            # CLEANING BULLETS THAT EXCEED THE WINDOW
            if bullet[1] > SCREEN_HEIGHT:
                bullets.remove(bullet) 

    def draw_elements(self):
        screen.fill(BLACK)

        # HUMAN PLAYER
        pygame.draw.rect(screen, WHITE, (self.human_player_x, SCREEN_HEIGHT - self.player_size, self.player_size, self.player_size))
        # HUMAN BULLETS
        for bullet in self.human_bullets:
            current_bullet_x, current_bullet_y = bullet[0], bullet[1]
            pygame.draw.rect(screen, RED, (current_bullet_x, current_bullet_y, BULLET_WIDTH, BULLET_HEIGHT))

        # AGENT PLAYER
        pygame.draw.rect(screen, BLUE, (self.agent_player_x, SCREEN_HEIGHT - self.player_size, self.player_size, self.player_size))
        # AGENT BULLETS
        for bullet in self.agent_bullets:
            current_bullet_x, current_bullet_y = bullet[0], bullet[1]
            pygame.draw.rect(screen, RED, (current_bullet_x, current_bullet_y, BULLET_WIDTH, BULLET_HEIGHT))

        # DIVISION LINE
        pygame.draw.line(screen, WHITE, (HALF_WIDTH, 0), (HALF_WIDTH, SCREEN_HEIGHT), DIVISION_LINE_WIDTH)

    def get_agent_position(self):
        # MIDDLE OF THE BOX
        agent_position_x = self.agent_player_x + PLAYER_SIZE // 2
        # TOP BORDER OF THE BOX
        agent_position_y = SCREEN_HEIGHT - PLAYER_SIZE

        agent_position = [agent_position_x, agent_position_y]
        return agent_position

    def get_agent_discretize_position(self):
        position_x = self.agent_player_x
        if position_x < HALF_WIDTH + HALF_WIDTH / 3:
            return 'left'
        elif position_x < HALF_WIDTH + 2 * HALF_WIDTH / 3:
            return 'center'
        else:
            return 'right'
        
    def get_bullet_discretize_position(self):
        bullet_x, bullet_y = self.get_nearest_bullet_position()

        if bullet_y > SCREEN_HEIGHT * 2 / 3:
            distance = 'far'
        elif bullet_y > SCREEN_HEIGHT / 3:
            distance = 'medium'
        else:
            distance = 'close'
        
        if bullet_x < self.agent_player_x:
            position = 'left'
        elif bullet_x > self.agent_player_x + self.player_size:
            position = 'right'
        else:
            position = 'above'

        return position, distance

    def get_nearest_bullet_position(self):
        agent_position = self.get_agent_position()
        return get_nearest_point(agent_position, self.agent_bullets)
    
    def get_current_state(self):
        agent_discretize_position = self.get_agent_discretize_position()
        bullet_discretize_position = self.get_bullet_discretize_position()
        bullet_distance = get_distance(self.get_agent_position(), self.get_nearest_bullet_position())

        return (agent_discretize_position, bullet_discretize_position, bullet_distance)

    def agent_got_hit(self):
        bullet_x, bullet_y = self.get_nearest_bullet_position()
        agent_x, agent_y = self.get_agent_position()

        hit = agent_x < bullet_x < agent_x + self.player_size and agent_y < bullet_y < agent_y + self.player_size
        return hit
    
    def bullet_missed_agent(self):
        closest_bullet = self.get_nearest_bullet_position()
        bullet_y = closest_bullet[1]
        agent_x = self.agent_player_x
        agent_y = SCREEN_HEIGHT - self.player_size

        missed = bullet_y > agent_y and not self.agent_got_hit(closest_bullet, agent_x, agent_y)
        return missed

    def run_game_loop(self):
        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_over = True

            # HUMAN PLAYER MOVEMENT
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.update_player("LEFT")
            if keys[pygame.K_RIGHT]:
                self.update_player("RIGHT")

            # AGENT STATE
            current_state = self.get_current_state()

            # AGENT PLAYER MOVEMENT
            agent_action = self.agent.choose_action(current_state)
            action_commands = ["LEFT", "NONE", "RIGHT"]
            self.update_player(action_commands[agent_action], agent=True)

            # ADDING BULLETS
            if should_bullet_spawn(0.1):
                self.add_bullet()
            if should_bullet_spawn(0.1):
                self.add_bullet(agent=True)

            # BULLETS MOVEMENT
            self.update_bullets()
            self.update_bullets(agent=True)

            # CALCULATE REWARD
            reward = -0.1
            if self.agent_got_hit():
                reward = -1
            elif self.bullet_missed_agent():
                reward = 1

            # UPDATING AGENT KNOWLEDGE
            new_state = self.get_current_state()
            self.agent.update_q_table(current_state, agent_action, reward, new_state)

            # SHOWING ELEMENTS
            self.draw_elements()

            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()

# INITIALIZE GAME
game = BulletDodgeSimulation()
# RUN GAME
game.run_game_loop()
