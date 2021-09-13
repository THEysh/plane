import random
import pygame
from p_main import PlaneGame

pygame.init()
SCREEN_RECT = pygame.Rect(0, 0, 480, 700)
FRAME_FPS = 60
ENEMY_SECOND = 500  #te出现de敌人
ENEMY_SECOND2 = 1800
FIRST_SPEED, SECOND_SPEED = 2, 5 #敌人1，出现的随机最低和最高速度
FIRST_SPEED2, SECOND_SPEED2 = 1, 3 #敌人2，出现的随机最低和最高速度
CREATE_ENEMY_EVENT = pygame.USEREVENT  # 敌机的定时器事件常量
HERO_FIRE = pygame.USEREVENT+1
CREATE_ENEMY_EVENT2 = pygame.USEREVENT+2
HERO_WEAPON =pygame.USEREVENT+3
HERO_WEAPON_SETIME = 3000

HERO_FIRE_SPEED2, HERO_FIRE_SPEED2_ = 100, 8#飞机子弹的控制
HERO_FIRE_SPEED3, HERO_FIRE_SPEED3_ = 300, 5#飞机子弹的控制
HERO_SPEED = 10
SIGN = 0


class GameSprite(pygame.sprite.Sprite):

    def __init__(self, image_name, speed=1):
        super().__init__()
        self.image_name =image_name
        self.image = pygame.image.load(image_name)
        self.rect = self.image.get_rect()
        self.speed = speed

    def update(self):
        self.rect.y += self.speed


class Background(GameSprite):
    def __init__(self, is_alt=False):
        image_name = "./images/background.png"
        super().__init__(image_name)
        if is_alt:
            self.rect.y = -self.rect.height

    def update(self):
        super().update()
        if self.rect.y >= SCREEN_RECT.height:
            self.rect.y = -SCREEN_RECT.height


class Display_Button_Gameover(GameSprite):
    def __init__(self):
        self.is_alt = 0
        super().__init__("./images/gameover.png")
        self.rect.bottom = SCREEN_RECT.height - 2.5*self.rect.height
        self.rect.centerx = SCREEN_RECT.width / 2
    def update(self):
        if self.is_alt == 1:
            self.image = pygame.image.load("./images/gameover2.png")
            self.is_alt = 0
        else:
            self.image = pygame.image.load("./images/gameover.png")
        super().update()
        self.rect.y += -self.speed
        self.rect.centerx = SCREEN_RECT.width / 2


class Display_Button_Begin(GameSprite):
    def __init__(self):
        self.is_alt = 0
        super().__init__("./images/resume_nor.png")

        self.rect.bottom = SCREEN_RECT.height - 4*self.rect.height
        self.rect.centerx = SCREEN_RECT.width/2
    def update(self):
        image_name1 = "./images/resume_nor.png"
        image_name2 = "./images/resume_pressed.png"
        if self.is_alt == 1:
            self.image = pygame.image.load(image_name2)
            self.is_alt = 0
        else:
            self.image = pygame.image.load(image_name1)
        super().update()
        self.rect.y += -self.speed
        self.rect.centerx = SCREEN_RECT.width/2


class Hero_Weapon(GameSprite):

    def __init__(self):
        super().__init__("./images/bullet_supply.png")
        max_x = SCREEN_RECT.width - self.rect.width
        self.image_names = ["./images/bullet_supply.png", "./images/bullet_supply2.png"]
        self.image_tip = random.randint(0,1)
        self.rect.x = random.randint(0,max_x)
        self.rect.y = 0
        self.speed = random.randint(1,5)
    def update(self):
        self.image = pygame.image.load(self.image_names[self.image_tip])
        super().update()
        if self.rect.y >= SCREEN_RECT.height:
            self.kill()


class PlaneSprite(GameSprite):
    """飞机精灵，包括敌机和英雄"""

    def __init__(self, image_names, destroy_names, life=1, speed=1):

        image_name = image_names[0]
        super().__init__(image_name, speed)
        # 生命值
        self.life = life
        # 正常图像列表
        self.__life_images = []
        for file_name in image_names:
            image = pygame.image.load(file_name)
            self.__life_images.append(image)
        # 被摧毁图像列表
        self.__destroy_images = []
        for file_name in destroy_names:
            image = pygame.image.load(file_name)
            self.__destroy_images.append(image)

        self.images = self.__life_images

        # 毁坏刷新标记
        self.tip = 0
        self.tip2 = 0
        # 显示图像索引
        self.show_image_index = 0
        # 是否可以被删除
        self.can_destroied = False

    def update(self):
        self.update_images()

        super().update()

    def update_images(self):
        """更新图像"""
        #每次运行 每当elf.show_image_index +1时 精灵更新一次图片
        self.show_image_index += 0.2
        count = len(self.images)

        # 用于判断 飞机被击中后 避免self.images[?]中， ？的数值超过 列表的len
        if self.show_image_index > count and self.life > 0:
            self.show_image_index = 0
        elif self.show_image_index > count and self.life <= 0:
            self.show_image_index = count-1

        current_index = int(self.show_image_index)
        self.image = self.images[current_index]

        # 判断飞机是否毁坏，更换飞机损坏的图片帧
        if self.life <= 0 or self.tip2 == 1:
            self.tip += 1
            self.tip2 = 1
            # 为了避免重复赋值 self.image = self.enemy_destory()
            if self.tip == 1:
                self.enemy_destory()
            # 敌机被射击后 坠机动画的时间 是FRAME_FPS/3帧
            if self.tip > FRAME_FPS/3:
                self.tip = 0
                self.tip2 = 0
                self.can_destroied = True
            #强制保留 最后一张坠机的 图片帧
            elif self.tip <= FRAME_FPS/3 and self.tip >= FRAME_FPS/3/(count/2):
                self.image = self.images[count-1]
            else:
                self.image = self.images[current_index]

    def enemy_destory(self):
        # 默认播放生存图片
        self.images = self.__destroy_images
        # 显示图像索引
        self.show_image_index = 0

class Enemy(PlaneSprite):
    def __init__(self):
        image_names = ["./images/enemy1.png","./images/enemy1.png"]
        destroy_names = ["./images/enemy1_down1.png",
                         "./images/enemy1_down2.png",
                         "./images/enemy1_down3.png",
                         "./images/enemy1_down4.png"]
        super().__init__(image_names,destroy_names)
        self.life = 2
        self.speed = random.randint(FIRST_SPEED, SECOND_SPEED)
        self.rect.bottom = 0

        max_x = SCREEN_RECT.width-self.rect.width
        self.rect.x = random.randint(0, max_x)

    def update(self):
        super().update()
        if self.rect.y >= SCREEN_RECT.height:
            self.kill()
        elif self.can_destroied:
            self.kill()


class Enemy2(PlaneSprite):
    def __init__(self):
        image_names = ["./images/enemy2_hit.png", "./images/enemy2_hit2.png"]
        destroy_names = ["./images/enemy2_down1.png",
                         "./images/enemy2_down2.png",
                         "./images/enemy2_down3.png",
                         "./images/enemy2_down4.png"]
        super().__init__(image_names, destroy_names)
        self.life = 6
        self.speed = random.randint(FIRST_SPEED2, SECOND_SPEED2)
        self.rect.bottom = 0
        max_x = SCREEN_RECT.width-self.rect.width
        self.rect.x = random.randint(0, max_x)
    def update(self):
        super().update()
        if self.rect.y >= SCREEN_RECT.height:
            self.kill()
        elif self.can_destroied:
            self.kill()


class hero(PlaneSprite):
    def __init__(self):
        image_names = ["./images/me1.png","./images/me2.png"]
        destroy_names =["./images/me_destroy_1.png","./images/me_destroy_2.png","./images/me_destroy_3.png"]
        super().__init__(image_names,destroy_names)
        # 最开始的位置
        self.weapon_type = 0
        self.rect.x = (SCREEN_RECT.width-self.rect.width)/2
        self.rect.y = SCREEN_RECT.height-2*self.rect.height
        self.speed = HERO_SPEED
        # 将精灵添加到精灵组
        self.bullets = pygame.sprite.Group()
    def fire (self):
        plane_bullet = Bullet()
        if self.weapon_type == 1:
            plane_bullet = Bullet3()
            # 改子弹后 重新设置子弹的 间隔
            pygame.time.set_timer(HERO_FIRE, HERO_FIRE_SPEED3)
        plane_bullet.rect.bottom = self.rect.y
        plane_bullet.rect.centerx = self.rect.centerx
        # 精灵组添加一个精灵
        self.bullets.add(plane_bullet)

    def update(self):
        super().update()
        #用于抵消 最开始update的self.rect.y += self.speed
        self.rect.y -= self.speed
        if self.can_destroied == True:
            self.kill()
            print("游戏结束")


        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_d]:
            self.rect.x += self.speed
        if keys_pressed[pygame.K_a]:
            self.rect.x += -self.speed
        if keys_pressed[pygame.K_s]:
            self.rect.y += self.speed
        if keys_pressed[pygame.K_w]:
            self.rect.y += -self.speed

        if self.rect.y >= SCREEN_RECT.height-self.rect.height:
            self.rect.y = SCREEN_RECT.height-self.rect.height
        if self.rect.x >= SCREEN_RECT.width-self.rect.width:
            self.rect.x = SCREEN_RECT.width-self.rect.width
        if self.rect.left < 0:
            self.rect.x = 0


class Bullet(GameSprite):
    def __init__(self):
        image_name = "./images/bullet1.png"
        super().__init__(image_name)
        self.act = 1
        self.speed = -HERO_FIRE_SPEED2_
    def update(self):
        super().update()
        if self.rect.bottom < 0:
            self.kill()

class Bullet3(GameSprite):
    def __init__(self):
        image_name = "./images/bullet3.png"
        super().__init__(image_name)
        self.act = 3
        self.speed = -HERO_FIRE_SPEED3_
    def update(self):
        super().update()
        if self.rect.bottom < 0:
            self.kill()









