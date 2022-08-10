import pygame
import random

pygame.init()
pygame.mixer.init()
clock = pygame.time.Clock()
fps = 60
width = 400
height = 600
ground_scroll = 0
scroll_speed = 4
pipe_gaps = 150
pipe_frequency = 1000  # milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0

flying = False
game_over = False
in_menu = True
passed_pipe = False

# Load images
bg = pygame.image.load('assets/sprites/bg.png')
base_bg = pygame.image.load('assets/sprites/ground.png')
main_menu = pygame.image.load('assets/sprites/main_menu.png')
restart_btn = pygame.image.load('assets/sprites/restart.png')
game_over_txt = pygame.image.load('assets/sprites/gameover.png')

# Transform image to fit into screen
bg = pygame.transform.scale(bg, (400, 600))
main_menu = pygame.transform.scale(main_menu, (300, 400))
restart_btn = pygame.transform.scale(restart_btn, (150, 50))

# Load sounds
menu_sound = pygame.mixer.Sound('assets/audio/main_menu.mp3')
main_sound = pygame.mixer.music.load('assets/audio/main_menu.mp3')
hit_sound = pygame.mixer.Sound('assets/audio/hit.wav')
wing_sound = pygame.mixer.Sound('assets/audio/wing.wav')
die_sound = pygame.mixer.Sound('assets/audio/die.wav')
point_sound = pygame.mixer.Sound('assets/audio/point.wav')

font = pygame.font.Font('assets/Bauhaus.ttf', 40)
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('FlappyBirds')
favicon = pygame.image.load('assets/favicon.ico')
pygame.display.set_icon(favicon)

# Play background music
pygame.mixer.music.play(-1)


def reset_game():
    """
    Function to reset the game after game over
    :return: None
    """
    pipe_group.empty()
    bird.rect.x = 100
    bird.rect.y = int(height) / 2
    bird.collision = False
    bird.died = False


def draw_score(text, font, text_col):
    """
    Function to draw the score on top of the screen
    :param text: Score as string
    :param font: The font name
    :param text_col: The font color
    :return: None
    """
    img = font.render(text, True, text_col)
    img_rect = img.get_rect(center=(width/2, 30))
    screen.blit(img, img_rect)


def update_score(bird_grp, pipe_grp, passed, score):
    """
    Function to update score
    :param bird_grp: Sprite group for bird
    :param pipe_grp: Sprite group for pipes
    :param passed: Boolean value if bird passed the pipe
    :param score: The score which gets updated
    :return: Passed and score value
    """
    # Check if bird passed the left corner of the pipe
    if bird_grp.sprites()[0].rect.left > pipe_grp.sprites()[0].rect.left and \
            bird_grp.sprites()[0].rect.right < pipe_grp.sprites()[0].rect.right and \
            not passed:
                passed = True
    if passed:
        # Check if bird also passed the right side of the pipe
        if bird_grp.sprites()[0].rect.left > pipe_grp.sprites()[0].rect.right:
            play_sound(point_sound)
            score += 1
            passed = False
    return passed, score


def play_sound(sound):
    """
    Helper function to play a sound
    :param sound: The loaded sound object
    :return: None
    """
    sound.play()


class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.idx = 0
        self.cnt = 0
        # Load flappy images
        for i in range(1, 4):
            img = pygame.image.load(f'assets/sprites/redbird{i}.png')
            self.images.append(img)
        self.image = self.images[self.idx]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.velocity = 0
        self.click = False
        self.collision = False
        self.died = False

    def update(self):
        """
        Function to update the bird (animation, flying)
        :return: None
        """
        # Add gravity
        if flying:
            self.velocity += 0.5
            if self.velocity > 8:
                self.velocity = 8
            if self.rect.bottom <= 500:
                self.rect.y += int(self.velocity)

        if not game_over:
            # Jump
            # Prevent bird from flying to high if mouse is not released
            if pygame.mouse.get_pressed()[0] == 1 and not self.click:
                self.click = True
                self.velocity -= 11
                play_sound(wing_sound)
            if pygame.mouse.get_pressed()[0] == 0:
                self.click = False

            # Animation handling
            self.cnt += 1
            cooldown = 5

            # Loop over image list and animate the bird
            if self.cnt > cooldown:
                self.cnt = 0
                self.idx += 1
                if self.idx >= len(self.images):
                    self.idx = 0
            self.image = self.images[self.idx]

            # Rotate the bird
            self.image = pygame.transform.rotate(self.images[self.idx], self.velocity * -3)
        else:
            self.image = pygame.transform.rotate(self.images[self.idx], -90)


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/sprites/pipe.png')
        self.rect = self.image.get_rect()

        # Pos 1 is from the op and pos -1 is from the bottom
        if pos == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gaps / 2)]
        if pos == -1:
            self.rect.topleft = [x, y + int(pipe_gaps / 2)]

    def update(self):
        """
        Function for letting the pipes fly through the game window
        :return: None
        """
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()


class Restart():
    def __init__(self, x, y, btn_img, text_img):
        self.btn_img = btn_img
        self.text_img = text_img
        self.btn_rect = self.btn_img.get_rect()
        self.btn_rect.topleft = [x, y]

    def draw(self):
        """
        Function to draw the button to the game over screen
        :return:
        """
        restart_action = False
        # Get mouse position
        mpos = pygame.mouse.get_pos()
        # Check if mouse click is in the button
        if self.btn_rect.collidepoint(mpos):
            if pygame.mouse.get_pressed()[0] == 1:
                restart_action = True

        # Draw button to screen
        screen.blit(self.text_img, ((int(width - self.text_img.get_width()) / 2),
                                    (int(height - self.text_img.get_height()) / 2) - 100))
        screen.blit(self.btn_img, (self.btn_rect.x, self.btn_rect.y))

        return restart_action


# Create Groups
bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

bird = Bird(100, int(height) / 2)

# Add objects to group
bird_group.add(bird)

restart = Restart(int((width - restart_btn.get_width()) / 2),
                  int((height - restart_btn.get_height()) / 2),
                  restart_btn, game_over_txt)

run = True
while run:
    clock.tick(fps)

    screen.blit(bg, (0, 0))
    screen.blit(main_menu, (int((width - main_menu.get_width()) / 2),
                            int((height - main_menu.get_height()) / 2)))

    if not in_menu:
        screen.blit(bg, (0, 0))
        draw_score(str(score), font, (255, 255, 255))
        bird_group.draw(screen)
        bird_group.update()
        pipe_group.draw(screen)

    # Draw and scroll the ground
    screen.blit(base_bg, (ground_scroll, 500))

    # Update score
    if len(pipe_group) > 0:
        passed_pipe, score = update_score(bird_group, pipe_group, passed_pipe, score)

    # Check if bird hits the ground
    if bird.rect.bottom > 500 and not bird.collision:
        flying = False
        bird.collision = True
        play_sound(hit_sound)
        game_over = True

    # Check if bird hits a pipe or hits to top of the screen
    if (pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or bird.rect.top <= 0) \
            and not bird.collision and not bird.died:
        bird.collision = True
        play_sound(hit_sound)
        bird.died = True
        play_sound(die_sound)
        game_over = True

    # Create new pipe instances
    if not game_over and flying:
        # Get current time
        time_now = pygame.time.get_ticks()
        # Check if 1000ms passed and create new pipe object
        if time_now - last_pipe > pipe_frequency:
            rand_height = random.randint(-100, 100)
            btm_pipe = Pipe(width, int(height / 2) + rand_height, -1)
            top_pipe = Pipe(width, int(height / 2) + rand_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0

        pipe_group.update()

    # Check for game over
    if game_over:
        if restart.draw() == True:
            game_over = False
            reset_game()
            score = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
            flying = True
            in_menu = False

    pygame.display.update()

pygame.quit()