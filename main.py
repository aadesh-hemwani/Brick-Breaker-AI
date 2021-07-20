from neat import genome
import pygame
import os, math, random
import time
import pickle
import neat

class BrickBreaker:
    def __init__(self):
        pygame.font.init()
        self.WIDTH, self.HEIGHT = 600, 600
        self.WINDOW = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.BACKGROUND = (31, 31, 31)
        self.FPS = 60

        self.life = 3
        self.score = 0
        self.scoreFont = pygame.font.SysFont('Google Sans', 20)
        
        self.BOARD_W, self.BOARD_H = self.WIDTH//10, 16
        self.BOARD_X, self.BOARD_Y = (self.WIDTH//2)-(self.BOARD_W//2), self.HEIGHT-40
        self.BOARD_IMAGE = pygame.image.load(os.path.join('Assets','board.png'))
        self.BOARD = pygame.transform.scale(self.BOARD_IMAGE, (self.BOARD_W, self.BOARD_H))

        self.BALL_DIAM = 20        
        self.BALL_IMAGE = pygame.image.load(os.path.join('Assets','ball.png'))
        self.BALL = pygame.transform.scale(self.BALL_IMAGE, (self.BALL_DIAM, self.BALL_DIAM))

        self.BRICK_W, self.BRICK_H = self.WIDTH//10, 20
        self.BRICK = []
        for i in range(5):
            self.BRICK.append(pygame.transform.scale(pygame.image.load(os.path.join('Assets',f"brick{i}.png")), (self.BRICK_W, self.BRICK_H)))
        self. bricks = []

        self.BOARD_SPEED = 10
        self.BALL_SPEED = 10
        self.won = 0


    def draw(self, board_pos, ball_pos):
        self.WINDOW.fill(self.BACKGROUND)
        for board in board_pos:
            self.WINDOW.blit(self.BOARD, (board.x, board.y))
        self.WINDOW.blit(self.BALL, (ball_pos.x, ball_pos.y))        
        for i in range(len(self.bricks)):
            self.WINDOW.blit(self.BRICK[self.bricks[i].y//10%5], (self.bricks[i].x, self.bricks[i].y))
        
        score_text = self.scoreFont.render("SCORE: "+str(self.score) + " - alive: "+str(len(board_pos)), False, (255, 255, 255))
        self.WINDOW.blit(score_text, (10, self.HEIGHT-20))
        
        instructions_text = self.scoreFont.render("LEFT: (left key)  -  RIGHT: (right key)  -  PAUSE: (Esc)", False, (255, 255, 255))
        self.WINDOW.blit(instructions_text, (self.WIDTH-400, self.HEIGHT-20))
        
        pygame.display.update()

    def board_controller(self, keys_pressed, board_pos, ball_pos):
        board_pos.x = ball_pos.x-20
            
        if keys_pressed[pygame.K_LEFT] and board_pos.x-self.BOARD_SPEED >= 0:
            board_pos.x -= self.BOARD_SPEED
            
        if keys_pressed[pygame.K_RIGHT] and board_pos.x + self.BOARD_SPEED + self.BOARD_W <= self.WIDTH:
            board_pos.x += self.BOARD_SPEED
    
    def ball_movement(self, ball_pos, board_pos, addX, addY, ge):        
        for brick in self.bricks:
            if ball_pos.colliderect(brick):
                addY = not addY
                if ball_pos.x+self.BALL_SPEED >= brick.x+self.BRICK_W or ball_pos.x < brick.x:
                    addX = not addX
                    addY = not addY
                self.bricks.remove(brick)
                self.score += 1
        # X direction
        if ball_pos.x+self.BALL_SPEED+self.BALL_DIAM > self.WIDTH: addX = False
        elif ball_pos.x-self.BALL_SPEED < 0: addX = True
            
        if addX: ball_pos.x += self.BALL_SPEED
        else: ball_pos.x -= self.BALL_SPEED
        
        # Y direction
        for x, board in enumerate(board_pos):
            if ball_pos.colliderect(board): 
                addY = False
                ge[x].fitness += 2
            elif ball_pos.y-self.BALL_SPEED < 0: addY = True

        if addY: ball_pos.y += self.BALL_SPEED
        else: ball_pos.y -= self.BALL_SPEED         
        
        return addX, addY


    def display_message(self, won, game_over):
        message = "PAUSED, SCORE: "+str(self.score)
        if won: message = "YOU WON, SCORE: "+str(self.score)
        if game_over: message = "GAME OVER, SCORE: "+str(self.score)
        font = pygame.font.SysFont('Google Sans', 40)
        text = font.render(message, True, (255,255,255))
        textRect = text.get_rect()
        textRect.center = (self.WIDTH // 2, self.HEIGHT // 2)
        self.WINDOW.blit(text, textRect)
        pygame.display.update()

    def main(self, genomes, config):
        pygame.display.set_caption("brick breaker alpha")
        
        boards = []
        nets = []
        ge = []

        for _, g in genomes:
            net = neat.nn.FeedForwardNetwork.create(g, config)
            nets.append(net)
            boards.append(pygame.Rect(self.BOARD_X, self.BOARD_Y, self.BOARD_W, self.BOARD_H))
            g.fitness = 0
            ge.append(g)


        # board_pos = pygame.Rect(self.BOARD_X, self.BOARD_Y, self.BOARD_W, self.BOARD_H)
        ball_pos = pygame.Rect(math.floor(random.random() *(self.WIDTH-0)+20), self.HEIGHT//2-self.BALL_DIAM, self.BALL_DIAM, self.BALL_DIAM)
        for j in range(10):
            for i in range(10):
                self.bricks.append(pygame.Rect(i*self.BRICK_W, j*self.BRICK_H, self.BRICK_W, self.BRICK_H))
        
        clock = pygame.time.Clock()
        running = True
        # won, game_over, pause = False, False, False
        addX, addY = False, False
        
        while running:
            clock.tick(self.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                # elif event.type == pygame.KEYDOWN:
                #     if event.key == pygame.K_ESCAPE:
                #         pause = not pause

            if self.won == 2:
                running = False
                pygame.quit()
            if len(boards) == 0:
                running = False
                break
            for x, board in enumerate(boards):
                # ge[x].fitness += 0.1
                output = nets[x].activate((board.x, ball_pos.x))
                # print(output)

                if output[0] > output[1] :
                    board.x += self.BOARD_SPEED
                else:
                    board.x -= self.BOARD_SPEED


            # keys_pressed = pygame.key.get_pressed()
            for x, board in enumerate(boards):
                # if ball_pos.y >= self.HEIGHT-self.BALL_DIAM: 
                if board.x-self.BOARD_SPEED < 0 or board.x + self.BOARD_SPEED + self.BOARD_W > self.WIDTH:
                     ge[x].fitness -= 1
                     boards.pop(x)
                     nets.pop(x)
                     ge.pop(x)
            if ball_pos.y >= self.HEIGHT-self.BALL_DIAM: 
                running = False
                break
            
                    # self.life -= 1
                    # ball_pos.x, ball_pos.y = math.floor(random.random()*(self.WIDTH-0)+20), self.HEIGHT//2-self.BALL_DIAM
                    # self.draw(board_pos, ball_pos)
                    # time.sleep(0.5)

                    # if self.life == 0:
                    #     game_over = True
                    #     pause = True
            self.draw(boards, ball_pos)
            addX, addY = self.ball_movement(ball_pos, boards, addX, addY, ge)                   

            if len(self.bricks) == 0:
                for g in ge:
                    g.fitness += 5
                self.won += 1
                for j in range(10):
                    for i in range(10):
                        self.bricks.append(pygame.Rect(i*self.BRICK_W, j*self.BRICK_H, self.BRICK_W, self.BRICK_H))

                # running = False
                # pause = True
        
            # if not pause:
            #     self.draw(board_pos, ball_pos)
            #     addX, addY = self.ball_movement(ball_pos, board_pos, addX, addY)                   
            #     self.board_controller(keys_pressed, board_pos, ball_pos)
            # else:
            #     self.display_message(won, game_over)                
        


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    bb = BrickBreaker()
    # p = neat.Population(config=config)
    # p.add_reporter(neat.StdOutReporter(True))
    # p.add_reporter(neat.StatisticsReporter())
    # winner = p.run(bb.main, 50)
    # print("winner", winner)
    # with open("winner.pkl", "wb") as f:
    #     pickle.dump(winner, f)
    #     f.close()
    # print("saved")
    
    with open("winner.pkl", "rb") as f:
        genome = pickle.load(f)
    
    genomes = [(1, genome)]
    bb.main(genomes, config)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)