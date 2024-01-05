# -*- coding: utf-8 -*-
from src.common import utils, config, vkeys
import cv2
import clipboard
import time

class WorldMap():
    # check_image dir 
    MAP_CHECK_DIR = 'assets/map_check'
    MAP_OPEN_PNG = cv2.imread('assets/world_map_open.png', 0)
    ARC_TARGET_MAP = cv2.imread('assets/arc_target_map_point.png', 0)
    AUT_TARGET_MAP = cv2.imread('assets/aut_target_map_point.png', 0)
    NORMAL_TARGET_MAP = cv2.imread('assets/normal_target_map_point.png', 0)
    STAR_TARGET_MAP = cv2.imread('assets/star_target_map_point.png', 0)
    MENU_GAP = 16

    def __init__(self):
        # standard point
        self.standard_point = (235,170)
        self.refresh_standard_point()
        
        # fixed points
        self.WORLD_MENU = self.get_final_pos(115,15)
        self.AREA_MENU = self.get_final_pos(250,15)
        self.SEARCH_BAR = self.get_final_pos(700,15)
        self.SEARCH_BTN = self.get_final_pos(765,15)
        self.FIRST_RESULT = self.get_final_pos(715,55)
        self.MAP_CHECK_LT = self.get_final_pos(47,16)
        self.MAP_CHECK_BR = self.get_final_pos(200,48)

        # worlds
        self.MAPLE_WORLD_POINT = self.get_final_pos(60,31)
        self.GRANDIS_POINT = self.get_final_pos(60,31+self.MENU_GAP*1)
        self.ARCANE_RIVER_POINT = self.get_final_pos(60,31+self.MENU_GAP*2)

        # areas - arcane river
        self.VANISHING_JOURNEY = self.get_final_pos(185,47)
        self.REVERSE_CITY = self.get_final_pos(185,47+self.MENU_GAP*1)
        self.CHU_CHU_ISLAND = self.get_final_pos(185,47+self.MENU_GAP*2)
        self.YUM_YUM_ISLAND = self.get_final_pos(185,47+self.MENU_GAP*3)
        self.LACHELEIN = self.get_final_pos(185,47+self.MENU_GAP*4)
        self.ARCANA = self.get_final_pos(185,47+self.MENU_GAP*5)
        self.MORASS = self.get_final_pos(185,47+self.MENU_GAP*6)
        self.ESFERA = self.get_final_pos(185,47+self.MENU_GAP*7)
        self.SELLAS = self.get_final_pos(185,47+self.MENU_GAP*8)
        self.TENEBRIS = self.get_final_pos(185,47+self.MENU_GAP*9)
        self.MOONBRIDGE = self.get_final_pos(185,47+self.MENU_GAP*10)
        self.SUFFERING = self.get_final_pos(185,47+self.MENU_GAP*11)
        self.LIMINA = self.get_final_pos(185,47+self.MENU_GAP*12)
        
        # areas - grandis
        # self.CERNIUM = 
        # self.HOTEL = 
        # self.ODIUM = 
        # self.SHANGRI_LA = 
        # self.ARTERIA = 
        # self.CARCION = 

        self.maps_info = {
            "mts3" : {
                'map_name' : 'mts3',
                'check_image' : self.MAP_CHECK_DIR + '/mirror_touched_sea3.png',
                'world_selection_point':self.ARCANE_RIVER_POINT,
                'area_selection_point':self.ESFERA,
                'point':self.get_final_pos(487,430)
            },
            "mts2" : {
                'map_name' : 'mts2',
                'check_image' : self.MAP_CHECK_DIR + '/mirror_touched_sea2.png',
                'world_selection_point':self.ARCANE_RIVER_POINT,
                'area_selection_point':self.ESFERA,
                'point':self.get_final_pos(416,394)
            },
            "五道洞穴的上路" : {
                'map_name' : '五道洞穴的上路',
                'check_image' : self.MAP_CHECK_DIR + '/five_road_upper_path.png',
                'world_selection_point':self.ARCANE_RIVER_POINT,
                'area_selection_point':self.ARCANA,
                'point':self.get_final_pos(256,455)
            },
        }

    def refresh_standard_point(self):
        for _ in range(10):
            frame = config.capture.frame
            point = utils.multi_match(frame, self.MAP_OPEN_PNG, threshold=0.95)
            if len(point) > 0:
                print("world map opened")
                print(f'point: {point}')
                self.standard_point = (point[0][0]-431,point[0][1]-10)
                print(f'standard point: {self.standard_point}')
                return self.standard_point
            else:
                time.sleep(0.3)
        return False

    def get_final_pos(self,x,y):
        return (lambda x : (self.standard_point[0]+x[0],self.standard_point[1]+x[1]))((x,y))

    def check_if_in_correct_map(self,map_name):
        if map_name in self.maps_info:
            frame = config.capture.frame
            frame = frame[10:57, 10:234]
            template = cv2.imread(self.maps_info[map_name]['check_image'], 0)
            point = utils.multi_match(frame, template, threshold=0.9)
            if len(point) > 0:
                print("in correct map")
                return True
            else:
                return False
        return True

    def search_map(self,map_name):
        utils.game_window_click(self.SEARCH_BAR)
        time.sleep(utils.rand_float(0.5,0.6))
        clipboard.copy(map_name)
        vkeys.key_down("ctrl")
        time.sleep(utils.rand_float(0.2,0.25))
        vkeys.key_down("v")
        time.sleep(utils.rand_float(0.03,0.05))
        vkeys.key_up("v")
        time.sleep(utils.rand_float(0.1,0.15))
        vkeys.key_up("ctrl")
        time.sleep(utils.rand_float(0.5,0.6))
        utils.game_window_click(self.SEARCH_BTN)
        time.sleep(utils.rand_float(0.7,0.8))
        utils.game_window_click(self.FIRST_RESULT)
        time.sleep(utils.rand_float(0.5,0.7))
        for i in range(100):
            frame = config.capture.frame
            # frame = frame[10:57, 10:234]
            point = utils.single_match_with_threshold(frame, self.ARC_TARGET_MAP, threshold=0.9)
            if len(point) > 0:
                print("find arc target map")
                utils.game_window_click(point[0],click_time=2)
                return True
            point = utils.single_match_with_threshold(frame, self.AUT_TARGET_MAP, threshold=0.9)
            if len(point) > 0:
                print("find aut target map")
                utils.game_window_click(point[0],click_time=2)
                return True
            point = utils.single_match_with_threshold(frame, self.NORMAL_TARGET_MAP, threshold=0.9)
            if len(point) > 0:
                print("find normal target map")
                utils.game_window_click(point[0],click_time=2)
                return True
            point = utils.single_match_with_threshold(frame, self.STAR_TARGET_MAP, threshold=0.9)
            if len(point) > 0:
                print("find star target map")
                utils.game_window_click(point[0],click_time=2)
                return True
            time.sleep(0.01)
        return False