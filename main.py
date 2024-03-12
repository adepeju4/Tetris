import pygame
import random

pygame.font.init()


s_width = 800
s_height = 750
play_width = 300
play_height = 600
block_size = 30

button_width = 100
button_height = 50
button_margin = 2

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height - 50

pygame.mixer.init()
move_sound = pygame.mixer.Sound("assets/move.mp3")

move_sound.set_volume(0.5)

# SHAPE FORMATS
S = [
    [".....", ".....", "..00.", ".00..", "....."],
    [".....", "..0..", "..00.", "...0.", "....."],
]

Z = [
    [".....", ".....", ".00..", "..00.", "....."],
    [".....", "..0..", ".00..", ".0...", "....."],
]

I = [
    [".....", ".....", "0000.", ".....", "....."],
    [".....", "..0..", "..0..", "..0..", "..0.."],
]

O = [[".....", ".....", ".00..", ".00..", "....."]]

J = [
    [".....", ".0...", "000..", ".....", "....."],
    [".....", "..00.", "..0..", "..0..", "....."],
    [".....", ".....", "..000", "...0.", "....."],
    [".....", "..0..", "..0..", ".00..", "....."],
]

L = [
    [".....", "...0.", "000..", ".....", "....."],
    [".....", "..0..", "..0..", "..00.", "....."],
    [".....", ".....", "..000", ".0...", "....."],
    [".....", ".00..", "..0..", "..0..", "....."],
]

T = [
    [".....", "..0..", "000..", ".....", "....."],
    [".....", "..0..", "..00.", "..0..", "....."],
    [".....", ".....", "..000", "..0..", "....."],
    [".....", "..0..", ".00..", "..0..", "....."],
]


shapes = [S, Z, I, O, J, L, T]
shape_colors = [
    (0, 255, 0),
    (255, 0, 0),
    (0, 255, 255),
    (255, 255, 0),
    (255, 165, 0),
    (0, 0, 255),
    (128, 0, 128),
]


class Piece(object):
    def __init__(self, column, row, shape):
        self.x = column
        self.y = row
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0


class Button:
    def __init__(self, color, x, y, width, height, text=""):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self, win, outline=None):
        if outline:
            pygame.draw.rect(
                win,
                outline,
                (self.x - 2, self.y - 2, self.width + 4, self.height + 4),
                0,
            )
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), 0)
        if self.text != "":
            font = pygame.font.SysFont(None, 50)
            text = font.render(self.text, 1, (0, 0, 0))
            win.blit(
                text,
                (
                    self.x + (self.width / 2 - text.get_width() / 2),
                    self.y + (self.height / 2 - text.get_height() / 2),
                ),
            )

    def isOver(self, pos):
        if self.x < pos[0] < self.x + self.width:
            if self.y < pos[1] < self.y + self.height:
                return True
        return False


def main_menu(win):
    run = True
    colors = [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (255, 255, 0),
        (0, 255, 255),
        (255, 0, 255),
    ]  # Define a list of colors
    while run:
        win.fill((0, 0, 0))
        font = pygame.font.SysFont("comicsans", 60)
        letters = ["T", "E", "T", "R", "I", "S"]
        colors = [
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
            (255, 255, 0),
            (0, 255, 255),
            (255, 0, 255),
        ]  # Define a list of colors
        x_offset = 0
        spacing = 10  # Define a spacing between letters
        for i, letter in enumerate(letters):
            label = font.render(letter, 1, colors[i])
            win.blit(
                label,
                (
                    top_left_x
                    + play_width / 2
                    - (
                        label.get_width() * len(letters) / 2
                        + spacing * (len(letters) - 1) / 2
                    )
                    + x_offset,
                    top_left_y + play_height / 2 - 100,
                ),
            )
            x_offset += label.get_width() + spacing  # Add spacing to x_offset
        draw_text_middle(
            win, "Press any key to begin", 60, (255, 255, 255), offset_y=30
        )
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                run = False


def load_image_with_transparency(image_path, transparency):
    # Load the original image
    image = pygame.image.load(image_path)

    # Create a new Surface with the same size as the image
    overlay = pygame.Surface(image.get_size(), pygame.SRCALPHA)

    # Fill the new Surface with the semi-transparent black color
    overlay.fill((0, 0, 0, transparency))

    # Blit the overlay onto the image
    image.blit(overlay, (0, 0))

    return image


def text_objects(text, font):
    text_surface = font.render(text, True, (0, 0, 0))
    return text_surface, text_surface.get_rect()


def create_grid(locked_positions={}):
    grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]

    for y in range(len(grid)):
        for x in range(len(grid[y])):
            if (x, y) in locked_positions:
                c = locked_positions[(x, y)]
                grid[y][x] = c
    return grid


def convert_shape_format(piece):
    positions = []
    format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == "0":
                positions.append((piece.x + j, piece.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions


def valid_space(grid, piece):
    accepted_positions = [
        [(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)] for i in range(20)
    ]
    accepted_positions = [j for sub in accepted_positions for j in sub]

    formatted = convert_shape_format(piece)

    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False
    return True


def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False


def get_shape():
    return Piece(5, 0, random.choice(shapes))


def draw_text_middle(surface, text, size, color, offset_y=0):
    font = pygame.font.SysFont("comicsans", size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(
        label,
        (
            top_left_x + play_width / 2 - (label.get_width() / 2),
            top_left_y + play_height / 2 - (label.get_height() / 2) + offset_y,
        ),
    )


def draw_grid(surface, grid):
    sx = top_left_x
    sy = top_left_y

    for i in range(1, len(grid)):  # Start from 1 to avoid drawing on the top border
        pygame.draw.line(
            surface,
            (128, 128, 128),
            (sx, sy + i * block_size),
            (sx + play_width, sy + i * block_size),
        )
    for j in range(1, len(grid[0])):  # Start from 1 to avoid drawing on the left border
        pygame.draw.line(
            surface,
            (128, 128, 128),
            (sx + j * block_size, sy),
            (sx + j * block_size, sy + play_height),
        )


def clear_rows(grid, locked):
    inc = 0
    for i in range(len(grid) - 1, -1, -1):
        row = grid[i]
        if (0, 0, 0) not in row:
            inc += 1
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue

    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)

    return inc


def draw_next_shape(shape, surface):
    font = pygame.font.SysFont("comicsans", 30)
    label = font.render("Next Shape", 1, (255, 255, 255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height / 2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == "0":
                pygame.draw.rect(
                    surface, shape.color, (sx + j * 30, sy + i * 30, 30, 30), 0
                )

    surface.blit(label, (sx + 10, sy - 30))


def draw_window(
    surface,
    grid,
    quitButton,
    score=0,
):

    pygame.font.init()
    font = pygame.font.SysFont("comicsans", 60)
    label = font.render("Tetris", 1, (255, 255, 255))

    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), 10))

    font = pygame.font.SysFont("comicsans", 30)
    label = font.render("Score: " + str(score), 1, (255, 255, 255))
    # Position the score label to the right of the game board.
    surface.blit(label, (top_left_x + play_width + 50, top_left_y))

    quitButton.draw(surface, (0, 0, 0))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(
                surface,
                grid[i][j],
                (top_left_x + j * 30, top_left_y + i * 30, 30, 30),
                0,
            )

    pygame.draw.rect(
        surface, "#183130", (top_left_x, top_left_y, play_width, play_height), 5
    )

    draw_grid(surface, grid)


def draw_button(surface, text, x, y, w, h, ic, ac, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(surface, ac, (x, y, w, h))
        if click[0] == 1 and action != None:
            action()
    else:
        pygame.draw.rect(surface, ic, (x, y, w, h))

    small_text = pygame.font.SysFont("comicsansms", 20)
    text_surf, text_rect = text_objects(text, small_text)
    text_rect.center = ((x + (w / 2)), (y + (h / 2)))
    surface.blit(text_surf, text_rect)


def game_over_screen(win, score):
    game_over = True
    while game_over:
        win.fill((0, 0, 0))  # Fill the window with black
        font = pygame.font.SysFont("comicsans", 60)
        label = font.render(
            "Game Over! Your score is " + str(score), 1, (255, 255, 255)
        )
        win.blit(
            label,
            (
                top_left_x + play_width / 2 - (label.get_width() / 2),
                top_left_y + play_height / 2,
            ),
        )

        label = font.render("Press any key to return to main menu", 1, (255, 255, 255))
        win.blit(
            label,
            (
                top_left_x + play_width / 2 - (label.get_width() / 2),
                top_left_y + play_height / 2 + 60,
            ),
        )

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                game_over = False

    # Reset the game
    main(win)


def main(win):

    locked_positions = {}
    grid = create_grid(locked_positions)
    game_over = False
    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()

    fall_time = 0
    fall_speed = 0.27
    level_time = 0
    score = 0

    background = load_image_with_transparency("./assets/background.jpeg", 128)
    background = pygame.transform.scale(background, (s_width, s_height))

    quitButton = Button(
        (255, 0, 0), button_margin, button_margin, button_width, button_height, "Quit"
    )

    main_menu(win)

    while run:
        win.blit(background, (0, 0))
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()

        if level_time / 1000 > 5:
            level_time = 0
            if fall_speed > 0.12:
                fall_speed -= 0.005

        if fall_time / 1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(grid, current_piece) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()

            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if quitButton.isOver(pos):
                    run = False

            if game_over and event.type == pygame.KEYDOWN:
                score = 0
                grid = create_grid()
                game_over = False

            if event.type == pygame.KEYDOWN:
                move_sound.play()
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(grid, current_piece):
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(grid, current_piece):
                        current_piece.x -= 1
                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(grid, current_piece):
                        current_piece.y -= 1
                if event.key == pygame.K_UP:
                    current_piece.rotation += 1
                    if not valid_space(grid, current_piece):
                        current_piece.rotation -= 1

        shape_pos = convert_shape_format(current_piece)

        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            score += clear_rows(grid, locked_positions) * 10

        draw_window(
            win,
            grid,
            quitButton,
            score,
        )
        draw_next_shape(next_piece, win)
        pygame.display.flip()

        if check_lost(locked_positions):
            game_over = True

        if game_over:
            game_over_screen(win, score)
            continue

    draw_text_middle(win, "Press any key to return to main menu", 30, (255, 255, 255))

    pygame.time.delay(2000)


pygame.init()
win = pygame.display.set_mode((s_width, s_height))


main(win)
