"""
💧 喝水提醒小工具 v4
"""

import tkinter as tk
import math
import random

REMIND_INTERVAL = 60 * 60
GROW_INTERVAL = 5
STEPS = 5

BG_COLOR = "#E8F6FF"
CUP_BODY = "#AEE4FF"
CUP_WATER = "#5BB8F5"
CUP_OUTLINE = "#5BB8F5"
CUP_STRAW = "#FF9EAD"
TEXT_TITLE = "#2C7FC0"
TEXT_SUB = "#6BB8E0"
BTN_COLOR = "#2C7FC0"
BTN_TEXT = "#FFFFFF"
BTN_HOVER = "#2070B0"

BTN_FONT_SIZE = 14
BTN_H_FIXED = 44
BTN_W_RATIO = 0.72

class Bubble:
    def __init__(self, w, h):
        self.w = w; self.h = h
        self.reset(init=True)

    def reset(self, init=False):
        self.x            = random.uniform(0.05, 0.95)
        self.y            = random.uniform(0.1, 0.95) if init else 1.05
        self.r            = random.uniform(0.010, 0.022)
        self.speed        = random.uniform(0.0006, 0.0015)
        self.wobble       = random.uniform(0, math.pi * 2)
        self.wobble_speed = random.uniform(0.02, 0.05)

    def update(self):
        self.y -= self.speed
        self.wobble += self.wobble_speed
        self.x += math.sin(self.wobble) * 0.002
        self.x = max(0.03, min(0.97, self.x))

    def is_gone(self):
        return self.y < -0.05

def draw_cup(canvas, cx, cy, size, wave_offset=0):
    s=size; tw=s*0.62; bw=s*0.48; h=s*0.80
    x0,x1=cx-tw/2,cx+tw/2; x2,x3=cx+bw/2,cx-bw/2; y0,y1=cy,cy+h

    canvas.create_polygon(x0,y0,x1,y0,x2,y1,x3,y1,
        fill=CUP_BODY,outline=CUP_OUTLINE,width=max(2,s*0.022),smooth=False,tags="cup")

    m=s*0.035; wy=y0+h*0.32; ratio=(wy-y0)/h
    wl=x0+(x3-x0)*ratio+m; wr=x1+(x2-x1)*ratio-m

    canvas.create_polygon(wl,wy,wr,wy,x2-m,y1-m,x3+m,y1-m,
        fill=CUP_WATER,outline="",smooth=False,tags="cup")

    steps=20; pts=[]
    for i in range(steps+1):
        t=i/steps; pts.extend([wl+(wr-wl)*t, wy+math.sin(t*math.pi*2+wave_offset)*s*0.018])
    pts.extend([wr,wy,wl,wy])
    canvas.create_polygon(pts,fill=CUP_WATER,outline="",smooth=True,tags="cup")

    hl=[]
    for i in range(steps+1):
        t=i/steps; hl.extend([wl+(wr-wl)*t, wy+math.sin(t*math.pi*2+wave_offset)*s*0.018])
    canvas.create_line(hl,fill="#FFFFFF",width=max(1.5,s*0.018),smooth=True,tags="cup")

    sx=cx+tw*0.15; st=y0-s*0.26; sb=wy-s*0.02; sw=max(3,s*0.052)
    canvas.create_rectangle(sx-sw/2,st,sx+sw/2,sb,fill=CUP_STRAW,outline="#FF7A8A",width=max(1,s*0.012),tags="cup")
    canvas.create_oval(sx-sw/2,st-sw/2,sx+sw/2,st+sw/2,fill=CUP_STRAW,outline="#FF7A8A",tags="cup")

    ey=cy+h*0.50; er=s*0.048
    for ex in [cx-s*0.12, cx+s*0.06]:
        canvas.create_oval(ex-er,ey-er,ex+er,ey+er,fill="#2C5F8A",outline="",tags="cup")
        canvas.create_oval(ex+er*0.2,ey-er*0.55,ex+er*0.7,ey+er*0.05,fill="#FFFFFF",outline="",tags="cup")

    canvas.create_arc(cx-s*0.13,ey+s*0.04,cx+s*0.13,ey+s*0.22,
        start=200,extent=140,style="arc",outline="#2C5F8A",width=max(1.5,s*0.022),tags="cup")

    for ox in [-s*0.19, s*0.14]:
        cr=s*0.058
        canvas.create_oval(cx+ox-cr,ey+s*0.02,cx+ox+cr,ey+s*0.02+cr*1.3,
            fill="#FFB3B3",outline="",stipple="gray50",tags="cup")

    canvas.create_line(x0+2,y0,x1-2,y0,fill="#FFFFFF",width=max(2,s*0.028),capstyle="round",tags="cup")

class WaterReminder:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.sw = self.root.winfo_screenwidth()
        self.sh = self.root.winfo_screenheight()

        self.win        = None
        self.canvas     = None
        self.grow_count = 0
        self.growing    = False
        self.grow_job   = None
        self.anim_job   = None
        self.anim_tick  = 0
        self.wave_off   = 0.0
        self.bubbles    = []
        self.cur_w      = 0
        self.cur_h      = 0
        self.tgt_w      = 0
        self.tgt_h      = 0
        self.cur_x      = 12
        self.cur_y      = 12
        self.tgt_x      = 12
        self.tgt_y      = 12

        # 防闪烁追踪
        self._last_geo_w  = -1
        self._last_geo_h  = -1
        self._last_draw_w = -1
        self._last_draw_h = -1

        self._remind_job  = None

        self.root.after(1000, self.show)

    def _init_wh(self):
        s = int(min(self.sw, self.sh) * 0.28)
        return s, s

    def _target_wh(self, step):
        iw, ih = self._init_wh()
        frac = step / STEPS
        w = int(iw + (self.sw - iw) * frac)
        h = int(ih + (self.sh - ih) * frac)
        return w, h

    def show(self):
        if self.win and self.win.winfo_exists():
            return
        self.grow_count = 0
        self.growing    = True
        self.anim_tick  = 0
        self.wave_off   = 0.0

        iw, ih = self._init_wh()
        self.cur_w = iw; self.cur_h = ih
        self.tgt_w = iw; self.tgt_h = ih
        self.cur_x = 12; self.cur_y = 12
        self.tgt_x = 12; self.tgt_y = 12

        self.win = tk.Toplevel(self.root)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-alpha", 0.0)
        self.win.geometry(f"{iw}x{ih}+12+12")
        self.win.lift()

        self.canvas = tk.Canvas(self.win, highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)
        self.bubbles = [Bubble(iw, ih) for _ in range(6)]

        self._fade_in()
        self._schedule_grow()
        self._animate()

    def _animate(self):
        if not (self.win and self.win.winfo_exists()):
            return
        self.anim_tick += 1
        self.wave_off  += 0.08

        self.cur_w += (self.tgt_w - self.cur_w) * 0.12
        self.cur_h += (self.tgt_h - self.cur_h) * 0.12
        self.cur_x += (self.tgt_x - self.cur_x) * 0.12
        self.cur_y += (self.tgt_y - self.cur_y) * 0.12
        W = int(self.cur_w)
        H = int(self.cur_h)
        X = int(self.cur_x)
        Y = int(self.cur_y)

        # 仅在尺寸实际变化时调整窗口几何形状，避免闪屏
        if W != self._last_geo_w or H != self._last_geo_h:
            self._last_geo_w, self._last_geo_h = W, H
            try:
                self.win.geometry(f"{W}x{H}+{X}+{Y}")
            except Exception:
                pass

        for b in self.bubbles:
            b.w = W; b.h = H
            b.update()
            if b.is_gone(): b.reset()

        # 尺寸变化时或每3帧才做全量重绘，降低canvas刷新频率
        if W != self._last_draw_w or H != self._last_draw_h or self.anim_tick % 3 == 0:
            self._last_draw_w, self._last_draw_h = W, H
            self._redraw(W, H)
        self.anim_job = self.win.after(30, self._animate)

    def _redraw(self, W, H):
        if not (self.win and self.win.winfo_exists()):
            return
        c = self.canvas
        c.configure(width=W, height=H)
        c.delete("all")

        c.create_rectangle(0, 0, W, H, fill=BG_COLOR, outline="")

        for b in self.bubbles:
            bx=b.x*W; by=b.y*H; br=b.r*min(W,H)
            c.create_oval(bx-br,by-br,bx+br,by+br,
                fill="#FFFFFF",outline=CUP_WATER,
                width=max(1,br*0.25),stipple="gray75")

        # ── 比例布局，随窗口大小自适应 ──
        title_y  = int(H * 0.09)
        sub_y    = int(H * 0.19)
        cup_top  = int(H * 0.36)
        btn_bot  = H - int(H * 0.09)
        btn_cy   = btn_bot - BTN_H_FIXED // 2

        # 水杯可用高度 = 按钮顶部 - 水杯顶部
        btn_top  = btn_cy - BTN_H_FIXED // 2
        cup_avail_h = btn_top - cup_top - 12   # 留12px间隙
        cup_avail_w = W * 0.68
        cup_size = min(cup_avail_h * 0.88, cup_avail_w)
        cup_cy   = cup_top + cup_size * 0.10   # 水杯绘制起点

        # 文案（字号用 H 基准，与坐标一致）
        phase = self._get_phase()
        if phase == "takeover":
            main_text = "警告！
...(truncated)...
