# import所需套件
import pygame
import sys
import random
import csv

non_property = ["Start", "Fate", "Chance", "Jail","HSR Station",'HSR Station']

# 定義函數，將敘述過長內容依最大寬度自動換行 
def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = []
    current_width = 0
    
    for word in words:
        word_width, _ = font.size(word + ' ')
        if current_width + word_width > max_width:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_width = word_width
        else:
            current_line.append(word)
            current_width += word_width
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines


# 定義函數，利用wrap_text函數來實現在給定的矩形上顯示文字
def draw_text(screen, text, rect, font, color, padding):
    x, y, width, height = rect
    line_height = font.get_linesize()
    lines = wrap_text(text, font, width - 2*padding)

    for line in lines:
        text_surface = font.render(line, True, color)
        screen.blit(text_surface, (x + padding, y + padding))
        y += font.get_linesize() 



# 定義遊戲版面格子的屬性，藉輸入房地產名稱、房地產價錢、過路費(或者說罰金)、持有者名稱、顏色、座標來定義
class boardattr:
    def __init__(self, name, price, fine, playerId, color, picture, info, location, region, height=0, width = 0,x=0, y=0):
        self.name = name
        self.price = price
        self.fine = fine
        self.who = playerId
        self.picture = picture
        self.info = info
        self.location = location
        self.region = region
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color


# 定義遊戲的按鈕格式
class Button: 

    # 定義按鈕本身的屬性，藉輸入按鈕文字、按鈕位置、按鈕主顏色、鼠標重疊按鈕後的變色(鼠標放置在按鈕上時，按鈕顏色會變深)、按鈕大小來定義
    def __init__(self, text, position, color, hover_color, size=(100, 50)):
        self.text = text
        self.position = position
        self.size = size
        self.color = color
        self.hover_color = hover_color
        self.font = pygame.font.SysFont('arialunicode', 20)
        self.rect = pygame.Rect(position, size)
        self.text_surf = self.font.render(text, True, BLACK)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

    # 定義繪製按鈕的函數
    def draw(self, screen): 
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.hover_color, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.text_surf, self.text_rect)

    # 定義按鈕區域被點擊的函數
    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    # 檢查鼠標是否重疊在按鈕格子內，如果有則變色
    def check_hover(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
            self.draw(screen)
        else:
            self.current_color = self.color
            self.draw(screen)

class People:
    own_region = {"North": 0, "South": 0, "East": 0, "Central":0}
    def __init__(self, id, color,colorname, money= 2000, status = 0, position = 0):
        self.id = id
        self.color = color
        self.color_name=colorname
        self.money = money
        self.status = status
        self.position = position
    


# 存入骰子六面的圖像，使後續能創造擲骰子的動畫效果
dice = [pygame.transform.scale(pygame.image.load('dice/1.png'), (75, 75)),
        pygame.transform.scale(pygame.image.load('dice/2.png'), (75, 75)),
        pygame.transform.scale(pygame.image.load('dice/3.png'), (75, 75)),
        pygame.transform.scale(pygame.image.load('dice/4.png'), (75, 75)),
        pygame.transform.scale(pygame.image.load('dice/5.png'), (75, 75)),
        pygame.transform.scale(pygame.image.load('dice/6.png'), (75, 75))]


# 初始化Pygame
pygame.init()


# 建立遊戲初始畫面
width, height = 900, 900 # 遊戲視窗大小
grid_size = 12 # 遊戲每邊的格子數量
grid_num = 36
cell_width = width/grid_size  # 格子大小
cell_height = 2*cell_width
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Taiwan Tourists Monopoly")
dice_rect = pygame.Rect(width / 2-40, cell_height*1.8, 80, 80)
GridInfo = list()


# 設定顏色，以利後面輸入顏色的方便
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
CHANCE_COLOR=(198,78,78)
FATE_COLOR = (0,202,128)
LIGHT_BLUE = (173, 216, 230)
LIGHT_RED = (255, 182, 193)
LIGHT_GREEN = (144, 238, 144)
LIGHT_YELLOW = (255, 255, 224)
LIGHT_PURPLE = (216, 191, 216)
LIGHT_ORANGE = (255, 228, 181)
CORNER_COLOR = LIGHT_BLUE
SIDE_COLORS = [LIGHT_RED, LIGHT_GREEN, LIGHT_YELLOW, LIGHT_ORANGE]
COLORS = [RED, BLUE, GREEN, YELLOW]
COLOR_NAMES = ["Red", "Blue", "Green", "Yellow"]

with open("properties.csv", encoding='utf-8-sig') as csvfile:
    csv_reader = csv.DictReader(csvfile)
    counter = 0
    for row in csv_reader:
        color =SIDE_COLORS[counter//6]
        row['Name'] = wrap_text(row['Name'],pygame.font.SysFont('arialunicode', 11),cell_width)
        thisGrid = boardattr(row['Name'], int(row['Price']), int(row['Fine']),-1,color, row['jpg'], row['Introduction'], row['Location'], row['Region'])
        counter += 1
        GridInfo.append(thisGrid)
chance_info = "When a player lands on a Chance square, they must draw a card from the Chance deck. These cards can have various effects, such as advancing the player to a specific square, rewarding them with money, or imposing a financial penalty. The Chance cards can significantly impact a player's strategy and fortune, providing opportunities for unexpected gains or setbacks."
# 將機會格子隨機插入GridInfo清單，使每次遊戲執行能產出不同位置的機會命運，以提高遊戲新鮮感
color=CHANCE_COLOR
element1 = random.randint(0, 5)
thisGrid = boardattr("Chance", 0, 0, -1, color,'none',chance_info,'none','none')
GridInfo.insert(element1,thisGrid)
element2 = random.randint(7, 12)
thisGrid = boardattr("Chance", 0, 0, -1, color,'none',chance_info,'none','none')
GridInfo.insert(element2,thisGrid)
element3 = random.randint(14, 19)
thisGrid = boardattr("Chance", 0, 0, -1, color,'none',chance_info,'none','none')
GridInfo.insert(element3,thisGrid)
element4 = random.randint(21, 26)
thisGrid = boardattr("Chance", 0, 0, -1, color,'none',chance_info,'none','none')
GridInfo.insert(element4,thisGrid)

# 將命運格子隨機插入GridInfo清單，使每次遊戲執行能產出不同位置的機會命運，以提高遊戲新鮮感
fate_info = "When a player lands on a Fate square, they draw a card from the Fate deck. These cards can influence the game's dynamics in numerous ways, such as sending the player to jail, requiring them to pay fines, or allowing them to collect money from other players. The Fate cards serve as a reminder that luck and chance play a crucial role in Monopoly, making each game unique and challenging."
color=FATE_COLOR
element1 = random.randint(0, 6)
thisGrid = boardattr("Fate", 0, 0, -1, color,'none',fate_info,'none','none')
GridInfo.insert(element1,thisGrid)
element2 = random.randint(8, 14)
thisGrid = boardattr("Fate", 0, 0, -1, color,'none',fate_info,'none','none')
GridInfo.insert(element2,thisGrid)
element3 = random.randint(16, 22)
thisGrid = boardattr("Fate", 0, 0, -1, color,'none',fate_info,'none','none')
GridInfo.insert(element3,thisGrid)
element4 = random.randint(24, 30)
thisGrid = boardattr("Fate", 0, 0, -1, color,'none',fate_info,'none','none')
GridInfo.insert(element4,thisGrid)

# 將四角格子(start起點、YouBike站、監獄)隨機插入GridInfo清單，使每次遊戲執行能產出不同位置的機會命運，以提高遊戲新鮮感
color =CORNER_COLOR
thisGrid = boardattr("Start", 0, 0, -1, color,'none',"Welcome to the starting point of Monopoly! This is where every player's journey begins. The Start Block is a crucial space on the board, marking the beginning of each round. Every time a player passes by this block, they receive $500, providing a financial boost to continue their endeavors.",'none','none')
GridInfo.insert(0,thisGrid)
thisGrid = boardattr("HSR Station", 0, 0, -1, color,'none',"The High-Speed Rail (HSR) Station is a special space on the Monopoly board that offers players a unique and strategic advantage. When a player lands on this block, they are immediately transported to another HSR Station located directly across the board. This rapid transit feature allows for swift movement and can be a game-changer in terms of positioning and strategy.",'none','none')
GridInfo.insert(9,thisGrid)
thisGrid = boardattr("Jail", 0, 0, -1, color,'none',"""The Jail block is a notorious and strategic space on the Monopoly board that can both hinder and present opportunities for players. When a player lands on this block, they are immediately placed in jail and are suspended from normal movement for one round. However, the game doesn't come to a complete halt for them. During their turn in jail, the player still gets to roll the dice. If they roll a six, they are granted an immediate release and can move forward six steps, escaping the jail and rejoining the race with a fresh start. This chance to roll a six adds a layer of excitement and hope, as players anticipate a lucky break to get back into the game swiftly.""",'none','none')
GridInfo.insert(18,thisGrid)
thisGrid = boardattr("HSR Station", 0, 0, -1, color,'none',"The High-Speed Rail (HSR) Station is a special space on the Monopoly board that offers players a unique and strategic advantage. When a player lands on this block, they are immediately transported to another HSR Station located directly across the board. This rapid transit feature allows for swift movement and can be a game-changer in terms of positioning and strategy.",'none','none')
GridInfo.insert(27,thisGrid)
for i in range(grid_num):
    if i < grid_num/4:
        GridInfo[i].y = 0
        GridInfo[i].height = cell_height
        if i == 0:
            GridInfo[i].x = 0
            GridInfo[i].width = cell_width*2
        else:
            GridInfo[i].x = cell_width*(i+1)
            GridInfo[i].width = cell_width
    elif i < grid_num/2:
        GridInfo[i].x = cell_width*10
        GridInfo[i].width = cell_height
        if i % 9== 0:
            GridInfo[i].y = 0
            GridInfo[i].height = cell_width*2
        else:
            GridInfo[i].y = cell_width*((i-9)+1)
            GridInfo[i].height = cell_width
    elif i < grid_num*3/4:
        GridInfo[i].y = cell_width*10
        GridInfo[i].height = cell_height
        if i %9 == 0 :
            GridInfo[i].x = cell_width*10
            GridInfo[i].width = cell_width*2
        else:
            GridInfo[i].x = cell_width*11 - cell_width * (i-18+1)
            GridInfo[i].width = cell_width
    elif i < grid_num:
        GridInfo[i].x = 0
        GridInfo[i].width = cell_height
        if i % 9== 0:
            GridInfo[i].y = cell_width*10
            GridInfo[i].height = cell_width*2
        else:
            GridInfo[i].y = cell_width*11 - cell_width*((i-27)+1)
            GridInfo[i].height = cell_width



# 設置遊戲時鐘，使後續能控制遊戲幀數
clock = pygame.time.Clock()

# 初始化遊戲視窗，選擇玩家人數
while True:

    # 繪製出遊戲初始視窗、人數選擇說明及規則說明
    screen.fill((255, 222, 173))
    font = pygame.font.SysFont('arialunicode', 40)
    message = "Please choose the number of players."
    word_width, word_height = font.size(message+'  ')
    text_surface = font.render(message, True, BLACK)
    message_bg_rect = pygame.Rect((width-word_width)/2, 100, word_width, word_height)
    pygame.draw.rect(screen, (255, 250, 205), message_bg_rect.inflate(20, 10))
    text_rect = text_surface.get_rect(midtop=message_bg_rect.midtop)
    screen.blit(text_surface, text_rect)
    rules_text = [
        "Gaming Rules:",
        "1. Each player takes turns rolling the dice and moves the corresponding number of steps.",
        "2. Each time a player passes the starting point (completes a lap), they receive $500.",
        "3. If a player lands on a special square, they perform the corresponding special action.",
        "4. If any player runs out of money, the game ends, and the player with the most money left is the winner.",
        "5. Each player starts with $2000; use it wisely.",
        "6. Each square contains relevant information that will be displayed when you hover the mouse over it."
    ]
    rules_font = pygame.font.SysFont('arialunicode', 20)
    rules = list()
    for rule in rules_text:
        rules.extend(wrap_text(rule,rules_font,word_width))
    word_height = len(rules) * (rules_font.get_linesize()+3)
    rules_bg_rect = pygame.Rect((width-word_width)/2, 200, word_width, word_height)
    pygame.draw.rect(screen, (255, 250, 205), rules_bg_rect.inflate(20, 10))
    for i, line in enumerate(rules):
        rule_surface = rules_font.render(line, True, BLACK)
        rule_rect = rule_surface.get_rect(topleft=(rules_bg_rect.left + 10, rules_bg_rect.top + 0 + i * 30))
        screen.blit(rule_surface, rule_rect)

    # 將人數各選項令為按鈕屬性，並繪製在視窗上
    two_player = Button("2 Players", (390, 600), (255, 182, 193), (219, 112, 147), (120, 50))
    three_player = Button("3 Players", (390, 680), (135, 206, 235), (70, 130, 180), (120, 50))
    four_player = Button("4 Players", (390, 760), (60, 179, 113), (46, 139, 87), (120, 50))
    two_player.draw(screen)
    three_player.draw(screen)
    four_player.draw(screen)
    pygame.display.flip()

    # 檢查鼠標是否有選擇人數
    confirm = False
    while not confirm:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if two_player.is_clicked(event):
                confirm = True
                num_players = 2
            elif three_player.is_clicked(event):
                confirm = True
                num_players = 3
            elif four_player.is_clicked(event):
                confirm = True
                num_players = 4
        two_player.check_hover()
        three_player.check_hover()
        four_player.check_hover()
        clock.tick(30)
        pygame.display.flip()
    break


# 繪製主遊戲版面
def draw_board():

    corner_font = pygame.font.SysFont('arialunicode', 15)
    font = pygame.font.SysFont('arialunicode', 11)
    fine_font = pygame.font.SysFont('arialunicode', 10)
    for i in [0,9,18,27]:
        rect = pygame.Rect(GridInfo[i].x, GridInfo[i].y, GridInfo[i].width, GridInfo[i].height)
        pygame.draw.rect(screen, GridInfo[i].color, rect)
        pygame.draw.rect(screen, BLACK, rect, 1)
        if i ==0:
            tilt = -135
            x = cell_height *3/4
            y = cell_height *3/4
        elif i == 9:
            tilt = 135
            x = cell_height *21/4
            y = cell_height *3/4
        elif i ==18:
            tilt =45
            x = cell_height *21/4
            y = cell_height *21/4
        elif i ==27:
            tilt = -45
            x = cell_height *3/4
            y = cell_height *21/4
        text = pygame.transform.rotate(corner_font.render(GridInfo[i].name, True, BLACK),tilt)
        text_rect = text.get_rect(center =(x,y))
        screen.blit(text, text_rect)
        while rect.collidepoint(pygame.mouse.get_pos()):
            screen.fill(WHITE)
            rect = pygame.Rect(GridInfo[i].x, GridInfo[i].y, GridInfo[i].width, GridInfo[i].height)
            pygame.draw.rect(screen, GridInfo[i].color, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)
            text = pygame.transform.rotate(font.render(GridInfo[i].name, True, BLACK),tilt)
            text_rect = text.get_rect(center =(x,y))
            screen.blit(text, text_rect)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            clock.tick(30)
            infoRect = pygame.Rect(cell_height, cell_height, cell_height*4, cell_height*4)
            pygame.draw.rect(screen,WHITE,infoRect)
            display_text =["Name: "+GridInfo[i].name]
            display_text.extend(wrap_text(GridInfo[i].info,corner_font,cell_height*4-10))
            for j, line in enumerate(display_text):
                info_surface = corner_font.render(line, True, BLACK)
                info_rect = info_surface.get_rect(topleft=(infoRect.left + 10, infoRect.top + 10 + j * 30))
                screen.blit(info_surface, info_rect)
            pygame.display.flip()

    for i in range(1,9):
        rect = pygame.Rect(GridInfo[i].x, GridInfo[i].y, GridInfo[i].width, GridInfo[i].height)
        pygame.draw.rect(screen, GridInfo[i].color, rect)

        if GridInfo[i].who!=-1:
            house =pygame.Rect(GridInfo[i].x, GridInfo[i].y, cell_width/5, cell_width/5)
            message = f"Toll:{GridInfo[i].fine}"
            text_surface =pygame.transform.rotate(fine_font.render(message, True, BLACK),180)
            showfine = text_surface.get_rect(center=(GridInfo[i].x + cell_width/2 , GridInfo[i].y + cell_height/3))
            pygame.draw.rect(screen, COLORS[GridInfo[i].who], house)
            screen.blit(text_surface, showfine)
        pygame.draw.rect(screen, BLACK, rect, 1)
        _,y = rect.midbottom
        if GridInfo[i].name not in['Fate','Chance']:
            for line in GridInfo[i].name:
                text = pygame.transform.rotate(font.render(line, True, BLACK),180)
                text_rect = text.get_rect(center =(rect.centerx,y-font.get_height() // 2))
                screen.blit(text, text_rect)
                y-=font.get_height()
        else:
            text = pygame.transform.rotate(font.render(GridInfo[i].name, True, BLACK),180)
            text_rect = text.get_rect(center =(rect.centerx,y-font.get_height() // 2))
            screen.blit(text, text_rect)

        while rect.collidepoint(pygame.mouse.get_pos()):
            screen.fill(WHITE)
            rect = pygame.Rect(GridInfo[i].x, GridInfo[i].y, GridInfo[i].width, GridInfo[i].height)
            pygame.draw.rect(screen, GridInfo[i].color, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)
            _,y = rect.midbottom
            if GridInfo[i].name not in['Fate','Chance']:
                for line in GridInfo[i].name:
                    text = pygame.transform.rotate(font.render(line, True, BLACK),180)
                    text_rect = text.get_rect(center =(rect.centerx,y-font.get_height() // 2))
                    screen.blit(text, text_rect)
                    y-=font.get_height()
                photo = pygame.image.load(GridInfo[i].picture)
                photo.set_alpha(76)
                photo = pygame.transform.scale(photo, (4*cell_height, 4*cell_height))
                photo_rect = photo.get_rect()
                photo_rect.bottomright = (cell_height*5,cell_height*5)
            else:
                text = pygame.transform.rotate(font.render(GridInfo[i].name, True, BLACK),180)
                text_rect = text.get_rect(center =(rect.centerx,y-font.get_height() // 2))
                screen.blit(text, text_rect)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            clock.tick(30)
            infoRect = pygame.Rect(cell_height, cell_height, cell_height*4, cell_height*4)
            pygame.draw.rect(screen,WHITE,infoRect)
            if GridInfo[i].picture!='none':
                screen.blit(photo, photo_rect)
            if GridInfo[i].name not in['Fate','Chance']:
                display_text =["Name: "+" ".join(GridInfo[i].name),"Region: "+str(GridInfo[i].region)]
                display_text.extend(wrap_text(GridInfo[i].info,corner_font,cell_height*4-10))
                display_text.append("Price: $"+str(GridInfo[i].price)+", Toll: $"+str(GridInfo[i].fine))
            else:
                display_text =["Name: "+GridInfo[i].name]
                display_text.extend(wrap_text(GridInfo[i].info,corner_font,cell_height*4-10))

            for j, line in enumerate(display_text):
                info_surface = corner_font.render(line, True, BLACK)
                info_rect = info_surface.get_rect(topleft=(infoRect.left + 10, infoRect.top + 10 + j * 30))
                screen.blit(info_surface, info_rect)
            pygame.display.flip()

    # 繪製遊戲版面右邊
    for i in range(10,18):
        rect = pygame.Rect(GridInfo[i].x, GridInfo[i].y, GridInfo[i].width, GridInfo[i].height)
        pygame.draw.rect(screen, GridInfo[i].color, rect)
        if GridInfo[i].who!=-1:
            house =pygame.Rect(GridInfo[i].x+GridInfo[i].width-cell_width/5, GridInfo[i].y, cell_width/5, cell_width/5)
            message = f"Toll:{GridInfo[i].fine}"
            text_surface = pygame.transform.rotate(fine_font.render(message, True, BLACK),90)
            showfine = text_surface.get_rect(center=(GridInfo[i].x + cell_height* 2/3 , GridInfo[i].y + cell_width/2))
            pygame.draw.rect(screen, COLORS[GridInfo[i].who], house)
            screen.blit(text_surface, showfine)
        pygame.draw.rect(screen, BLACK, rect, 1)
        x = rect.left
        if GridInfo[i].name not in['Fate','Chance']:
            for line in GridInfo[i].name:
                text = pygame.transform.rotate(font.render(line, True, BLACK),90)
                text_rect = text.get_rect(center = (x + font.get_height() // 2, rect.centery))
                screen.blit(text, text_rect)
                x += font.get_height()
        else:
            text = pygame.transform.rotate(font.render(GridInfo[i].name, True, BLACK),90)
            text_rect = text.get_rect(center = (x + font.get_height() // 2, rect.centery))
            screen.blit(text, text_rect)

        while rect.collidepoint(pygame.mouse.get_pos()):
            screen.fill(WHITE)
            rect = pygame.Rect(GridInfo[i].x, GridInfo[i].y, GridInfo[i].width, GridInfo[i].height)
            pygame.draw.rect(screen, GridInfo[i].color, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)
            x = rect.left
            if GridInfo[i].name not in['Fate','Chance']:
                for line in GridInfo[i].name:
                    text = pygame.transform.rotate(font.render(line, True, BLACK),90)
                    text_rect = text.get_rect(center = (x + font.get_height() // 2, rect.centery))
                    screen.blit(text, text_rect)
                    x += font.get_height()
                photo = pygame.image.load(GridInfo[i].picture)
                photo.set_alpha(76)
                photo = pygame.transform.scale(photo, (4*cell_height, 4*cell_height))
                photo_rect = photo.get_rect()
                photo_rect.bottomright = (cell_height*5,cell_height*5)
            else:
                text = pygame.transform.rotate(font.render(GridInfo[i].name, True, BLACK),90)
                text_rect = text.get_rect(center = (x + font.get_height() // 2, rect.centery))
                screen.blit(text, text_rect)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            clock.tick(30)
            infoRect = pygame.Rect(cell_height, cell_height, cell_height*4, cell_height*4)
            pygame.draw.rect(screen,WHITE,infoRect)
            if GridInfo[i].picture!='none':
                screen.blit(photo, photo_rect)
            if GridInfo[i].name not in['Fate','Chance']:
                display_text =["Name: "+" ".join(GridInfo[i].name),"Region: "+str(GridInfo[i].region)]
                display_text.extend(wrap_text(GridInfo[i].info,corner_font,cell_height*4 - 10))
                display_text.append("Price: $"+str(GridInfo[i].price)+", Toll: $"+str(GridInfo[i].fine))
            else:
                display_text =["Name: "+GridInfo[i].name]
                display_text.extend(wrap_text(GridInfo[i].info,corner_font,cell_height*4-10))
            for j, line in enumerate(display_text):
                info_surface = corner_font.render(line, True, BLACK)
                info_rect = info_surface.get_rect(topleft=(infoRect.left + 10, infoRect.top + 10 + j * 30))
                screen.blit(info_surface, info_rect)
            pygame.display.flip()

    # 繪製遊戲版面下邊
    for i in range(19,27):
        rect = pygame.Rect(GridInfo[i].x, GridInfo[i].y, GridInfo[i].width, GridInfo[i].height)
        pygame.draw.rect(screen, GridInfo[i].color, rect)
        if GridInfo[i].who!=-1:
            house =pygame.Rect(GridInfo[i].x+cell_width-cell_width/5, GridInfo[i].y+cell_height-cell_width/5, cell_width/5, cell_width/5)
            message = f"Toll:{GridInfo[i].fine}"
            text_surface = fine_font.render(message, True, BLACK)
            showfine = text_surface.get_rect(center=(GridInfo[i].x + cell_width/2 , GridInfo[i].y + cell_height*2/3))
            pygame.draw.rect(screen, COLORS[GridInfo[i].who], house)
            screen.blit(text_surface, showfine)
        pygame.draw.rect(screen, BLACK, rect, 1)
        _,y = rect.midtop
        if GridInfo[i].name not in['Fate','Chance']:
            for line in GridInfo[i].name:
                text = font.render(line, True, BLACK)
                text_rect = text.get_rect(center =(rect.centerx,y+font.get_height() // 2))
                screen.blit(text, text_rect)
                y+=font.get_height()
        else:
            text = font.render(GridInfo[i].name, True, BLACK)
            text_rect = text.get_rect(center =(rect.centerx,y+font.get_height() // 2))
            screen.blit(text, text_rect)
        while rect.collidepoint(pygame.mouse.get_pos()):
            screen.fill(WHITE)
            rect = pygame.Rect(GridInfo[i].x, GridInfo[i].y, GridInfo[i].width, GridInfo[i].height)
            pygame.draw.rect(screen, GridInfo[i].color, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)
            _,y = rect.midtop
            if GridInfo[i].name not in['Fate','Chance']:
                for line in GridInfo[i].name:
                    text = font.render(line, True, BLACK)
                    text_rect = text.get_rect(center =(rect.centerx,y+font.get_height() // 2))
                    screen.blit(text, text_rect)
                    y+=font.get_height()
                photo = pygame.image.load(GridInfo[i].picture)
                photo.set_alpha(76)
                photo = pygame.transform.scale(photo, (4*cell_height, 4*cell_height))
                photo_rect = photo.get_rect()
                photo_rect.bottomright = (cell_height*5,cell_height*5)
            else:
                text = font.render(GridInfo[i].name, True, BLACK)
                text_rect = text.get_rect(center =(rect.centerx,y+font.get_height() // 2))
                screen.blit(text, text_rect)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            clock.tick(30)
            infoRect = pygame.Rect(cell_height, cell_height, cell_height*4, cell_height*4)
            pygame.draw.rect(screen,WHITE,infoRect)
            if GridInfo[i].picture!='none':
                screen.blit(photo, photo_rect)
            if GridInfo[i].name not in['Fate','Chance']:
                display_text =["Name: "+" ".join(GridInfo[i].name),"Region: "+str(GridInfo[i].region)]
                display_text.extend(wrap_text(GridInfo[i].info,corner_font,cell_height*4-10))
                display_text.append("Price: $"+str(GridInfo[i].price)+", Toll: $"+str(GridInfo[i].fine))
            else:
                display_text =["Name: "+GridInfo[i].name]
                display_text.extend(wrap_text(GridInfo[i].info,corner_font,cell_height*4-10))
            for j, line in enumerate(display_text):
                info_surface = corner_font.render(line, True, BLACK)
                info_rect = info_surface.get_rect(topleft=(infoRect.left + 10, infoRect.top + 10 + j * 30))
                screen.blit(info_surface, info_rect)
            pygame.display.flip()

    # 繪製遊戲版面左邊
    for i in range(28,36):
        rect = pygame.Rect(GridInfo[i].x, GridInfo[i].y, GridInfo[i].width, GridInfo[i].height)
        pygame.draw.rect(screen, GridInfo[i].color, rect)
        if GridInfo[i].who!=-1:
            house =pygame.Rect(GridInfo[i].x, GridInfo[i].y+cell_width-cell_width/5, cell_width/5, cell_width/5)
            message = f"Toll:{GridInfo[i].fine}"
            text_surface = pygame.transform.rotate(fine_font.render(message, True, BLACK),-90)
            showfine = text_surface.get_rect(center=(GridInfo[i].x + cell_height/3 , GridInfo[i].y + cell_width/2))
            pygame.draw.rect(screen, COLORS[GridInfo[i].who], house)
            screen.blit(text_surface, showfine)
        pygame.draw.rect(screen, BLACK, rect, 1)
        x= rect.right
        if GridInfo[i].name not in['Fate','Chance']:
            for line in GridInfo[i].name:
                text = pygame.transform.rotate(font.render(line, True, BLACK),-90)
                text_rect = text.get_rect(center = (x - font.get_height() // 2, rect.centery))
                screen.blit(text, text_rect)
                x -= font.get_height()
        else:
            text = pygame.transform.rotate(font.render(GridInfo[i].name, True, BLACK),-90)
            text_rect = text.get_rect(center = (x - font.get_height() // 2, rect.centery))
            screen.blit(text, text_rect)
        while rect.collidepoint(pygame.mouse.get_pos()):
            screen.fill(WHITE)
            rect = pygame.Rect(GridInfo[i].x, GridInfo[i].y, GridInfo[i].width, GridInfo[i].height)
            pygame.draw.rect(screen, GridInfo[i].color, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)
            x= rect.right
            if GridInfo[i].name not in['Fate','Chance']:
                for line in GridInfo[i].name:
                    text = pygame.transform.rotate(font.render(line, True, BLACK),-90)
                    text_rect = text.get_rect(center = (x - font.get_height() // 2, rect.centery))
                    screen.blit(text, text_rect)
                    x -= font.get_height()
                photo = pygame.image.load(GridInfo[i].picture)
                photo.set_alpha(76)
                photo = pygame.transform.scale(photo, (4*cell_height, 4*cell_height))
                photo_rect = photo.get_rect()
                photo_rect.bottomright = (cell_height*5,cell_height*5)
            else:
                text = pygame.transform.rotate(font.render(GridInfo[i].name, True, BLACK),-90)
                text_rect = text.get_rect(center = (x - font.get_height() // 2, rect.centery))
                screen.blit(text, text_rect)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            clock.tick(30)
            infoRect = pygame.Rect(cell_height, cell_height, cell_height*4, cell_height*4)
            pygame.draw.rect(screen,WHITE,infoRect)
            if GridInfo[i].picture!='none':
                screen.blit(photo, photo_rect)
            if GridInfo[i].name not in['Fate','Chance']:
                display_text =["Name: "+" ".join(GridInfo[i].name),"Region: "+str(GridInfo[i].region)]
                display_text.extend(wrap_text(GridInfo[i].info,corner_font,cell_height*4-10))
                display_text.append("Price: $"+str(GridInfo[i].price)+", Toll: $"+str(GridInfo[i].fine))
            else:
                display_text =["Name: "+GridInfo[i].name]
                display_text.extend(wrap_text(GridInfo[i].info,corner_font,cell_height*4-10))
            for j, line in enumerate(display_text):
                info_surface = corner_font.render(line, True, BLACK)
                info_rect = info_surface.get_rect(topleft=(infoRect.left + 10, infoRect.top + 10 + j * 30))
                screen.blit(info_surface, info_rect)
            pygame.display.flip()


# 繪製玩家，並輸入位置與顏色屬性
def draw_players(players):
    player_positions = {}
    for player in players:
        if player.position not in player_positions:
            player_positions[player.position] = []
        player_positions[player.position].append(player.color)

    for position, player_colors in player_positions.items():
        x = GridInfo[position].x+GridInfo[position].width/2
        y = GridInfo[position].y+GridInfo[position].height/2
        offset = 0
        for player_color in player_colors:
            pygame.draw.circle(screen, player_color,(x, y + offset), (cell_width-40) // 2 - 5)
            offset += 10


# 繪製當前玩家訊息提醒(提醒輪到誰擲骰子)
def draw_current_player_message(current_player, color):
    font = pygame.font.Font(None, 36)
    message = f"{COLOR_NAMES[current_player]} Player's Turn"
    text_surface = font.render(message, True, BLACK)
    message_bg_rect = text_surface.get_rect(
        center=(width // 2, height - cell_height - 50))
    pygame.draw.rect(screen, color, message_bg_rect.inflate(20, 10))
    screen.blit(text_surface, message_bg_rect)


# 繪製玩家現金訊息
def draw_player_money(players):
    font = pygame.font.Font(None, 24)
    for player in players:
        message = f"{player.color_name}: ${player.money}"
        text_surface = font.render(message, True, BLACK)
        screen.blit(text_surface, (width // 2-40,3.5*cell_height + 30 * (player.id + 1)))

players = list()
# 初始化玩家相關資訊
for i in range(num_players):
    players.append(People(i,COLORS[i],COLOR_NAMES[i]))

current_player = 0 # 起始玩家為編號零玩家(即第一位玩家)
dice_result = -1 # 初始化骰子結果為-1(即尚未擲骰子)
diceturn = 0 # 初始化骰子回合數為0
dice_image = None # 初始化骰子圖像為None，待擲骰子後會進行圖像轉換，以達到擲骰子的動畫效果
rolling = Button("Roll Dice", (3*cell_height-60, 1.5*cell_height-25), (255, 215, 0), (218, 165, 32), (120, 50)) # 將擲骰子按鈕設為按鈕屬性


# 開始進行遊戲
while True:
    stop =0
    # 利用先前定義的函數繪製出主遊戲視窗
    screen.fill(WHITE)
    draw_board()
    draw_players(players)
    draw_current_player_message(current_player, players[current_player].color)
    rolling.draw(screen)
    if dice_result != -1:
        dice_image_rect = dice[dice_result].get_rect(center=dice_rect.center)
        screen.blit(dice[dice_result], dice_image_rect)
    draw_player_money(players)
    pygame.display.flip()
    clock.tick(30)
    
    # 依照遊戲發生事件來執行不同效果
    for event in pygame.event.get():

        # 若視窗關閉，則結束程式
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if players[current_player].status == 1 and GridInfo[players[current_player].position].name!="Jail":
            players[current_player].status =0
            current_player = (current_player + 1) % num_players
            continue

        # 若擲骰子按鈕被點擊
        if rolling.is_clicked(event):

            # 隨機得出骰子結果，並且利用骰子不同點數的圖像轉換，來實現擲骰子結果
            diceturn = random.randint(2, 6)
            while diceturn > 0:
                dice_result = random.randint(0, 5)
                dice_image_rect = dice[dice_result].get_rect(center=dice_rect.center)
                screen.blit(dice[dice_result], dice_image_rect)
                pygame.display.flip()
                clock.tick(10)
                diceturn -= 1 
            
            # 若玩家的監獄值=1，則玩家位置留在監獄，並把其監獄回合數增加至2
            if players[current_player].status == 1 and dice_result != 5:
                players[current_player].status = 0
                current_player = (current_player + 1) % num_players
                continue
            
            # 若玩家不在監獄，則依照骰子值移動
            else:
                new_position = (players[current_player].position + dice_result + 1) % ((grid_size-3) * 4)
                players[current_player].status = 0
            
            # 玩家新位置小於舊位置(即通過原點，重新計算位置)，則領500元
            if new_position < players[current_player].position:
                players[current_player].money += 500
            players[current_player].position = new_position
            
            # 重新繪製遊戲版面(更新畫面用)
            screen.fill(WHITE)
            draw_board()
            rolling.draw(screen)
            draw_players(players)
            pygame.display.flip()
            
            # 顯示出骰子圖像及數字
            dice_image_rect = dice[dice_result].get_rect(center=dice_rect.center)
            screen.blit(dice[dice_result], dice_image_rect)
            font = pygame.font.SysFont('arialunicode', 20)
            
            # 如果位置的房地產尚未被購買，且該位置並非機會or命運or監獄orYouBike站orStart，且該玩家現金大於房地產價格，則跳出是否購買的視窗
            if GridInfo[new_position].who == -1 and GridInfo[new_position].name not in non_property and players[current_player].money >= GridInfo[new_position].price:

                # 是否購買的文字屬性
                message1 = f"Do you want to buy {' '.join(GridInfo[new_position].name)}?"
                text_surface1 = font.render(message1, True, BLACK)
                message2 = f"Price: ${GridInfo[new_position].price}, Tolls: ${GridInfo[new_position].fine}"
                text_surface2 = font.render(message2, True, BLACK)
                
                # 繪製是否購買的矩形及內容
                message_bg_rect = pygame.Rect(cell_width*2.5, cell_width*5, 7*cell_width, cell_width*2)
                inflated_bg_rect = message_bg_rect.inflate(20, 10)
                pygame.draw.rect(screen, GridInfo[new_position].color, message_bg_rect.inflate(20, 10))
                
                # 放置是否購買的矩形在視窗正確的位置
                text_rect1 = text_surface1.get_rect(center=(inflated_bg_rect.centerx, inflated_bg_rect.centery - 47))
                text_rect2 = text_surface2.get_rect(center=(inflated_bg_rect.centerx, inflated_bg_rect.centery - 16))
                screen.blit(text_surface1, text_rect1)
                screen.blit(text_surface2, text_rect2)

                # 將確認及拒絕購買的按鈕設置按鈕性質，並放在矩形內的位置
                confirm_button = Button("Accept", (300, 200), (155, 236, 173), (128, 189, 142))
                reject_button = Button("Reject", (450, 200), (215, 122, 128), (188, 75, 75))
                confirm_button.rect.topleft = (message_bg_rect.left + 50, message_bg_rect.bottom - 60)
                confirm_button.text_rect = confirm_button.text_surf.get_rect(center = confirm_button.rect.center)
                reject_button.rect.topleft = (message_bg_rect.right - 150, message_bg_rect.bottom - 60)
                reject_button.text_rect = reject_button.text_surf.get_rect(center = reject_button.rect.center)
                confirm_button.draw(screen)
                reject_button.draw(screen)
                pygame.display.flip()

                # 檢查鼠標是否有選擇購買與否
                confirm = False
                while not confirm:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if confirm_button.is_clicked(event):
                            confirm = True
                            GridInfo[new_position].who = current_player
                            players[current_player].money -= GridInfo[new_position].price
                            players[current_player].own_region[GridInfo[new_position].region]+=1
                        elif reject_button.is_clicked(event):
                            confirm = True
                    confirm_button.check_hover()
                    reject_button.check_hover()
                    clock.tick(30)
                    draw_player_money(players)
                    draw_current_player_message(current_player, players[current_player].color)
                    pygame.display.flip()
            
            # 不然如果該位置有持有者，且持有者並非當前玩家，且該位置並非機會or命運or監獄orYouBike站orStart，則從當前玩家的現金中扣除過路費，並給予持有者等值現金
            elif GridInfo[new_position].who != -1 and GridInfo[new_position].who!= current_player and GridInfo[new_position].name not in non_property:
                font = pygame.font.Font(None, 24)
                message1 = f"+${GridInfo[new_position].fine}"
                text_surface1 = font.render(message1, True, RED)
                screen.blit(text_surface1, (width // 2+67, 3.5*cell_height + 30 * (GridInfo[new_position].who+1)))
                message2 = f"-${GridInfo[new_position].fine}"
                text_surface2 = font.render(message2, True, GREEN)
                screen.blit(text_surface2, (width // 2+67, 3.5*cell_height + 30 * (current_player+1)))
                draw_player_money(players)
                draw_current_player_message(current_player, players[current_player].color)
                pygame.display.flip()
                pygame.time.wait(2000)
                players[current_player].money -= GridInfo[new_position].fine
                players[GridInfo[new_position].who].money += GridInfo[new_position].fine
            
            # 如果該位置為機會或命運，則隨機執行機會或命運的效果
            if GridInfo[new_position].name in ["Chance", "Fate"]:

                # 隨機產出機會命運的效果
                select = random.randint(0,11)
                if select == 0:
                    text ="""Due to the unfortunate breaking of the Queen's Head rock formation at Yehliu, toll fees in the northern region are now 50 percent off as a gesture of goodwill."""
                elif select == 1:
                    text ="""To boost tourism, the government is offering a subsidy. Players who own properties in the north, center, south, and east regions will receive a generous $500 bonus!"""
                elif select == 2:
                    text ="""Due to a high-speed rail power outage, you are stuck in transit and must skip your next turn."""
                elif select == 3:
                    text ="""The government has collected too much tax revenue, resulting in a windfall! Each player receives a $300 payout."""
                elif select == 4:
                    text ="""A powerful typhoon has struck the south, completely destroying all properties there. All southern properties are wiped out."""
                elif select == 5:
                    text ="""A severe earthquake has ravaged the eastern region, obliterating all constructions. All properties in the east are lost. Players affected by this disaster receive a $1000 consolation fund from the government."""
                elif select == 6:
                    text ="""Rents in the central region have surged, doubling the toll fees for anyone passing through."""
                elif select == 7:
                    text ="""Celebrating National Taiwan University's rise in global rankings, toll fees in the northern region are now doubled."""
                elif select == 8:
                    text ="""You play an attack card, forcing the next player to skip their turn. Those already in jail are unaffected."""
                elif select == 9:
                    text ="""You have obtained a teleportation door! Use it to return directly to the start and get a fresh beginning."""
                elif select == 10:
                    text ="""You play an attack card, cleverly stealing $500 from the previous player."""
                elif select == 11:
                    text ="""You have a run-in with a robber and lose $500 from your funds. Stay vigilant!"""
                
                # 繪製機會命運效果的文字
                message_bg_rect = pygame.Rect(cell_height*1.5, cell_height*2.3, 3*cell_height, cell_height*1.4)
                pygame.draw.rect(screen, GridInfo[new_position].color, message_bg_rect)
                font = pygame.font.SysFont('arialunicode', 20)
                draw_text(screen, text, message_bg_rect, font, pygame.Color('black'), 10)

                # 設置確認的按鈕，並將其繪製在視窗上
                confirm_button = Button("Confirm", (300, 200), (155, 236, 173), (128, 189, 142))
                confirm_button.rect.topleft = (message_bg_rect.right - 120, message_bg_rect.bottom - 60)
                confirm_button.text_rect = confirm_button.text_surf.get_rect(center = confirm_button.rect.center)
                confirm_button.draw(screen)
                pygame.display.flip()

                # 檢查確認按鈕是否被鼠標點擊，若有則執行機會命運效果
                confirm = False
                while not confirm:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if confirm_button.is_clicked(event):
                            confirm = True            
                    confirm_button.check_hover()
                    clock.tick(30)
                    draw_player_money(players)
                    draw_current_player_message(current_player, players[current_player].color)
                    pygame.display.flip()
                
                if select == 0:
                    for i in range(1,9):
                        GridInfo[i].fine=int(GridInfo[i].fine/2)
                elif select == 1:
                    for i in range(num_players):
                        get = True
                        for j in ["North", "South", "East","Central"]:
                            if players[i].own_region[j]==0:
                                get =False
                        if get == True:
                            players[i].money +=500
                elif select == 2:
                    players[current_player].status =1
                elif select == 3:
                    for i in range(num_players):
                        players[i].money+=300
                elif select == 4:
                    for i in range(19,27):
                        if GridInfo[i].who!=-1:
                            players[GridInfo[i].who].own_region[GridInfo[i].region]-=1
                            GridInfo[i].who = -1
                elif select == 5:
                    for i in range(28,36):
                        if GridInfo[i].who!=-1:
                            players[GridInfo[i].who].own_region[GridInfo[i].region]-=1
                            players[GridInfo[i].who].money +=1000
                            GridInfo[i].who = -1
                elif select == 6:
                    for i in range(10,18):
                        GridInfo[i].fine *=2
                elif select == 7:
                    for i in range(1,9):
                        GridInfo[i].fine *=2
                elif select == 8:
                    players[(current_player + 1) % num_players].status = 1
                elif select == 9:
                    players[current_player].position = 0
                    players[current_player].money +=500
                elif select == 10:
                    players[current_player].money +=500
                    target = current_player-1
                    if target <0:
                        target += num_players
                    players[target].money -=500
                    if players[target].money < 0:
                        stop = 1
                        break
                elif select == 11:
                    players[current_player].money -=500
                
                draw_player_money(players)
                draw_current_player_message(current_player, players[current_player].color)
                
            
            # 不然如果位置在監獄，且玩家監獄值為0(代表尚未被停留在監獄)，則玩家停留一回合並扣200元        
            elif GridInfo[new_position].name =="Jail" and players[current_player].status == 0 :
                # 玩家監獄值變成1
                players[current_player].status = 1
                
            # 不然如果位置在YouBike站，則將玩家位置移動到另一個YouBike站
            elif GridInfo[new_position].name == "HSR Station":
                if players[current_player].position == 9:
                    players[current_player].position = 27
                else:
                    players[current_player].position = 9
                    players[current_player].money +=500
                

            # 如果玩家現金小於0，則結束遊戲
            if players[current_player].money < 0:
                print("1")
                stop = 1
                break

            # 換下一位玩家
            current_player = (current_player + 1) % num_players
    if stop == 1:
        break
    
# 計算出擁有最多現金的玩家
max_name = str()
max_wealth = 0
for player in players:
    if player.money> max_wealth:
        max_name = player.color_name
        max_wealth = player.money

# 設置贏家資訊並將其繪製於遊戲視窗上
while True:
    screen.fill((255, 222, 173))
    font = pygame.font.SysFont('arialunicode', 35)
    message10 = f"Winner: {max_name}"
    text_surface10 = font.render(message10, True, BLACK)
    message11 = f"wealth: ${max_wealth}"
    text_surface11 = font.render(message11, True, BLACK)
    message_bg_rect = pygame.Rect(250, 100, 400, 70)
    pygame.draw.rect(screen, (255, 250, 205), message_bg_rect.inflate(20, 10))
    text_rect10 = text_surface10.get_rect(midtop=message_bg_rect.midtop)
    text_rect11 = text_surface11.get_rect(midtop=message_bg_rect.midtop)
    text_rect10.y -= 16
    text_rect11.y += 30
    screen.blit(text_surface10, text_rect10)
    screen.blit(text_surface11, text_rect11)

    # 設置結束遊戲按鈕，並繪製於視窗上，如果被點擊則結束程式
    quitbutton = Button("Quit", (390, 500), (255, 182, 193), (219, 112, 147), (120, 50))
    quitbutton.draw(screen)
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if quitbutton.is_clicked(event):
            pygame.quit()
            sys.exit()
