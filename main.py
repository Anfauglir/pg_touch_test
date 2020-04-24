import pygame as pg
from pygame.locals import *
import pygame._sdl2 as sdl2

pg.init()
pg.mixer.init()
clock = pg.time.Clock()

snd_pinch = pg.mixer.Sound('1.wav')
snd_rainbow = pg.mixer.Sound('2.wav')
is_rainbow = False

pic_files = [ ["anfauglir.jpg", 0], ["arthvina.jpg", 1], ["eviat.jpg", 0 ], ["思飛球.jpg", 1], ["hsuan.jpg", 0], ["seayas.jpg", 1] ]
pic_index = 0

# 圖片的加載以及快取原本白毛毛的大小
surface_base = pg.image.load(pic_files[pic_index][0])
general_rect = surface_base.get_rect()

# 歡樂的SDL2視窗與刷新螢幕顏色
win = sdl2.Window(size=general_rect.size)
renderer = sdl2.Renderer(win)
renderer.draw_color = (255,255,255,255)

# 將圖片轉換成Image class方便處理
img_base = sdl2.Image(sdl2.Texture.from_surface(renderer, surface_base))
img_rainbows = [ sdl2.Image(sdl2.Texture.from_surface(renderer, pg.image.load("rainbow_wolves.png"))), 
                 sdl2.Image(sdl2.Texture.from_surface(renderer, pg.image.load("rainbow_dragons.png"))) ]
pos_shaking = general_rect.copy()

# 程式運行標誌及畫格
Running = True
frame = 0

# 目前有的手指ID
hands = []

# 有的手指ID的當前位置 {id: pos}
hands_pos = {}

# 手指ID的起始位置 {id: pos}
hands_start_pos = {}

cursor_start_x_pos = -1
cursor_x_accum_rel = 0

while Running:
    
    events = pg.event.get()
    for e in events:
        # 打叉離開
        if e.type == pg.QUIT:
            Running = False
            break
        elif e.type == pg.KEYDOWN:
            # Esc離開
            if e.key == pg.K_ESCAPE:
                Running = False
                break
        elif e.type == pg.FINGERDOWN:
            # 第一根手指放下去時重置吐彩虹狀態 & 播放擠壓聲
            if len(hands) == 0:
                snd_pinch.play()
                is_rainbow = False

            # 紀錄這根手指的位置
            hands.append(e.finger_id)
            hands_pos[e.finger_id] = e
            hands_start_pos[e.finger_id] = e
        elif e.type == pg.FINGERMOTION:
            # 紀錄手指移動位置
            hands_pos[e.finger_id] = e
        elif e.type == pg.FINGERUP:
            # 移除手指(怎麼聽起來有點可怕)
            hands.remove(e.finger_id)
            del(hands_pos[e.finger_id])
            del(hands_start_pos[e.finger_id])
        elif e.type == pg.MOUSEBUTTONDOWN:
            if e.button == 1:
                snd_pinch.play()
                is_rainbow = False
                cursor_start_x_pos = e.pos[0]
                cursor_x_accum_rel = 0
            elif e.button == 3:
                pic_index = (pic_index + 1) % len(pic_files)
                surface_base = pg.image.load(pic_files[pic_index][0])
                img_base = sdl2.Image(sdl2.Texture.from_surface(renderer, surface_base))
        elif e.type == pg.MOUSEMOTION:
            if 1 in e.buttons:
                cursor_x_accum_rel += e.rel[0]
                if cursor_x_accum_rel < 0:
                    cursor_x_accum_rel = 0
        elif e.type == pg.MOUSEBUTTONUP:
            if e.button == 1:
                cursor_x_accum_rel = 0
                cursor_start_x_pos = -1
    # 壓力值
    hold_pos = 0

    if (len(hands) > 1 or cursor_start_x_pos != -1):
        if (len(hands) > 0):
            h0 = hands_pos[hands[0]]
            h1 = hands_pos[hands[1]]
            starth0 = hands_start_pos[hands[0]]
            starth1 = hands_start_pos[hands[1]]
            dis = abs(h0.x - h1.x)
            dxabs = abs(starth0.x - h0.x) + abs(starth1.x - h1.x)
            #移動的距離越大且兩點間距離越短 壓力越大
            if dis == 0: #避免Divide by zero
                hold_pos = 10000
            else:
                hold_pos = dxabs / dis * 350
        else:
            hold_pos = cursor_x_accum_rel * 15

        pos_shaking.w = max(general_rect.w - hold_pos, general_rect.w/2)
    else:
        # 沒有兩根手指不擠壓
        pos_shaking.w = general_rect.w

    # 設定這隻可愛白毛毛的中心位置
    if pos_shaking.w <= general_rect.w/2:
        pos_shaking.center = int(win.size[0] / 2 - 10 + frame%2*20), int(win.size[1] / 2)
    else:
        pos_shaking.center = int(win.size[0] / 2), int(win.size[1] / 2)

    # 擠壓太大力所以吐彩虹
    if (hold_pos > general_rect.w*4 and not is_rainbow):
        is_rainbow = True
        snd_rainbow.play()

    # 繪製區域清除
    renderer.clear()

    # 吃一口彩虹，吐一口
    if is_rainbow:
        img_base.draw(dstrect=general_rect)
        img_rainbows[pic_files[pic_index][1]].draw(dstrect=general_rect)
    else:
        img_base.draw(dstrect=pos_shaking)
    
    # 刷新畫面
    renderer.present()
    frame += 1

    # 60fps
    clock.tick(60)

pg.quit()
