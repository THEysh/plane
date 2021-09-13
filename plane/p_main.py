import time
import pygame
import os
from pygame.locals import *
from p_sprites import *

class PlaneGame(object):

    def __init__(self):
        print("游戏初始化")
        self.screen = pygame.display.set_mode(SCREEN_RECT.size)
        self.clock = pygame.time.Clock()
        self.__create_sprites()
        pygame.time.set_timer(HERO_FIRE, HERO_FIRE_SPEED2)

    def __create_sprites(self):
        self.bf = Display_Button_Begin()
        self.display_group = pygame.sprite.Group(self.bf)

        self.gv = Display_Button_Gameover()
        self.display_group_gameove = pygame.sprite.Group(self.gv)
        bg1 = Background()
        bg2 = Background(True)
        self.back_group = pygame.sprite.Group(bg1, bg2)


        self.enemy_group = pygame.sprite.Group()

        self.hero_weapon_group = pygame.sprite.Group()
        self.hero = hero()
        self.hero_group = pygame.sprite.Group(self.hero)

    def interface_display(self):
        print("显示界面")
    #libpng warning

        while True:
            self.clock.tick(FRAME_FPS)
            self.__event_handler()

            self.back_group.update()
            self.back_group.draw(self.screen)
            self.display_group_gameove.update()
            self.display_group_gameove.draw(self.screen)
            self.display_group.update()
            self.display_group.draw((self.screen))
            pygame.display.update()

    def start_game(self):
        print("开始游戏")
        pygame.time.set_timer(CREATE_ENEMY_EVENT, ENEMY_SECOND)
        pygame.time.set_timer(CREATE_ENEMY_EVENT2, ENEMY_SECOND2)
        pygame.time.set_timer(HERO_WEAPON, HERO_WEAPON_SETIME)
        while True:
            self.clock.tick(FRAME_FPS)
            self.__event_handler()
            self.__check_collide()
            self.__update_sprites()
            pygame.display.update()

    def __event_handler(self):
        """事件监听"""

        #获取鼠标位置
        pos = pygame.mouse.get_pos()
        tip = 0
        # (224 475),(259,516) 开始按钮
        # 94 558 ，390 595 结束游戏按钮
        #获取 鼠标 开始游戏键 的位置
        if pos[0] <= 259 and pos[0] >= 224 and pos[1] <= 516 and pos[1] >= 475:
            tip = 1
        elif pos[0] <= 390 and pos[0] >= 94 and pos[1] <=595 and pos[1] >= 558:
            tip = 2
        # 实现开始游戏时，按钮点击图像变化
        # mouse_pressed == (0, 0, 0) 表示鼠标属于放空状态
        mouse_pressed = pygame.mouse.get_pressed()
        if mouse_pressed == (0, 0, 0) and tip == 1:
            self.bf.is_alt = 1
        elif mouse_pressed == (0,0,0) and tip == 2:
            self.gv.is_alt = 1
        elif mouse_pressed == (1,0,0) and tip == 2:
            self.__game_over()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                PlaneGame.__game_over()
            elif event.type == CREATE_ENEMY_EVENT:
                self.enemy_group.add(Enemy())
            elif event.type == CREATE_ENEMY_EVENT2:
                self.enemy_group.add(Enemy2())
            elif event.type == HERO_WEAPON:
                #当出现事件后，并且随机种子等于1 才添加一个弹药包
                if random.randint(0,3) == 1:
                    self.hero_weapon_group.add(Hero_Weapon())
            elif event.type == HERO_FIRE and self.hero.life > 0:
                    self.hero.fire()
            #elif event.type == MOUSEBUTTONDOWN:  # 监测鼠标点击事件
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1 and tip==1 :  #event.button == 1表示鼠标左键释放，=2表示鼠标中键释放 =3表示右键释放
                    print("鼠标左键释放")
                    self.start_game()

        if self.hero.can_destroied == True:
            #清空计时器
            pygame.time.set_timer(CREATE_ENEMY_EVENT, 0)
            pygame.time.set_timer(CREATE_ENEMY_EVENT2, 0)
            pygame.time.set_timer(HERO_WEAPON, 0)
            game2 = PlaneGame()
            game2.interface_display()

    def __check_collide(self):
        """碰撞检测"""
        # 1. 子弹摧毁敌机
        brack1 = pygame.sprite.groupcollide(self.enemy_group, self.hero.bullets, False, True)
        # brack1 是一个字典。
        for enemy in brack1:
            #每一次的遍历 enemy 代表着字典的键，也是 class Enemy的一个对象
            # brack1.get(enemy)[0]  表示hero.bullets的一个对象，其中brack1.get(enemy)是一个列表
            if self.hero.weapon_type == 0:
                enemy.life -= brack1.get(enemy)[0].act
            elif self.hero.weapon_type == 1 :
                enemy.life -= brack1.get(enemy)[0].act
            #dict_items([(<Enemy2 Sprite(in 1 groups)>, [<Bullet Sprite(in 0 groups)>])])
        # 2. 敌机撞毁英雄
        brack2 = pygame.sprite.groupcollide(self.hero_group, self.enemy_group, False, False)
        for hero in brack2:
            hero.life -=1
        brack3 = pygame.sprite.groupcollide(self.enemy_group, self.hero_group,  False, False)
        for enemy in brack3:
            enemy.life -=1

        # 3.英雄吃弹药：
        brack4 = pygame.sprite.groupcollide(self.hero_group, self.hero_weapon_group,False, True)
        for weapon in brack4:
            #每次吃一个新的子弹 重新启动改子弹的计时器
            if brack4.get(weapon)[0].image_tip == 0:#导弹
                weapon.weapon_type = 1  #导弹
                pygame.time.set_timer(HERO_FIRE, 0)
                pygame.time.set_timer(HERO_FIRE, HERO_FIRE_SPEED3)
            elif brack4.get(weapon)[0].image_tip == 1:#小子弹
                weapon.weapon_type = 0 #小子弹
                pygame.time.set_timer(HERO_FIRE, 0)
                pygame.time.set_timer(HERO_FIRE, HERO_FIRE_SPEED2)
            #else:
            #weapon.weapon_type = 0

    def __update_sprites(self):
        """更新精灵组"""
        self.back_group.update()
        self.back_group.draw(self.screen)

        self.enemy_group.update()
        self.enemy_group.draw(self.screen)

        self.hero_weapon_group.update()
        self.hero_weapon_group.draw(self.screen)
        self.hero_group.update()
        self.hero_group.draw(self.screen)

        self.hero.bullets.update()
        self.hero.bullets.draw(self.screen)

    @staticmethod
    def __game_over():
        """游戏结束"""

        print("游戏结束")
        exit()
if __name__ == "__main__":
    game = PlaneGame()
    game.interface_display()