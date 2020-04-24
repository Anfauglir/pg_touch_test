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
surface_rainbow_wolves = pg.image.load("rainbow_wolves.png")
surface_rainbow_dragons = pg.image.load("rainbow_dragons.png")

win = None
renderer = None
img_base = None
img_rainbows = []
pos_shaking = None

def init_window():
    global win, renderer, img_base, img_rainbows, pos_shaking
    # 歡樂的SDL2視窗與刷新螢幕顏色
    win = sdl2.Window(size=general_rect.size)
    win.title = str(pic_files[pic_index])
    renderer = sdl2.Renderer(win)
    renderer.draw_color = (255,255,255,255)
    # 將圖片轉換成Image class方便處理
    img_base = sdl2.Image(sdl2.Texture.from_surface(renderer, surface_base))
    img_rainbows = [ sdl2.Image(sdl2.Texture.from_surface(renderer, surface_rainbow_wolves)), sdl2.Image(sdl2.Texture.from_surface(renderer, surface_rainbow_dragons)) ]
    pos_shaking = general_rect.copy()

def load_img(index):
    global surface_base, img_base, snd_pinch, is_rainbow, win, pic_index
    pic_index = index
    surface_base = pg.image.load(pic_files[pic_index][0])
    img_base = sdl2.Image(sdl2.Texture.from_surface(renderer, surface_base))
    snd_pinch.play()
    is_rainbow = False
    win.title = str(pic_files[pic_index])


init_window()

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
            elif e.key == pg.K_EQUALS:
                general_rect.width = general_rect.width << 1
                general_rect.height = general_rect.height << 1
                win.destroy()
                init_window()
            elif e.key == pg.K_MINUS:
                general_rect.width = general_rect.width >> 1
                general_rect.height = general_rect.height >> 1
                win.destroy()
                init_window()
            elif e.key == pg.K_1 or e.key == pg.K_KP_1:
                if len(pic_files) > 0: load_img(0)
            elif e.key == pg.K_2 or e.key == pg.K_KP_2:
                if len(pic_files) > 1: load_img(1)
            elif e.key == pg.K_3 or e.key == pg.K_KP_3:
                if len(pic_files) > 2: load_img(2)
            elif e.key == pg.K_4 or e.key == pg.K_KP_4:
                if len(pic_files) > 3: load_img(3)
            elif e.key == pg.K_5 or e.key == pg.K_KP_5:
                if len(pic_files) > 4: load_img(4)
            elif e.key == pg.K_6 or e.key == pg.K_KP_6:
                if len(pic_files) > 5: load_img(5)
            elif e.key == pg.K_7 or e.key == pg.K_KP_7:
                if len(pic_files) > 6: load_img(6)
            elif e.key == pg.K_8 or e.key == pg.K_KP_8:
                if len(pic_files) > 7: load_img(7)
            elif e.key == pg.K_9 or e.key == pg.K_KP_9:
                if len(pic_files) > 8: load_img(8)
            elif e.key == pg.K_0 or e.key == pg.K_KP_0:
                if len(pic_files) > 9: load_img(9)
            elif e.key == pg.K_SPACE:
                if (is_rainbow):
                    snd_pinch.play()
                else:
                    snd_rainbow.play()
                is_rainbow = is_rainbow ^ True
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
            elif e.button == 2 or e.button == 3:
                load_img((pic_index + 1) % len(pic_files))
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
        if (len(hands) > 1):
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
