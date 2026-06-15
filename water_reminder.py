"""
💧 喝水提醒小工具 v2
- 每隔1小时从左上角弹出可爱水杯
- 不喝水 → 每5秒变大，直到铺满屏幕
- 点击"我喝了！"→ 消失，1小时后再来
"""

import tkinter as tk
import math

# ══════════════════════════════════════
# 配置（想改就改这里）
# ══════════════════════════════════════
REMIND_INTERVAL = 60 * 60   # 提醒间隔：3600秒=1小时（测试用改成10）
GROW_INTERVAL   = 5         # 多少秒变大一次
GROW_STEP       = 0.08      # 每次增大幅度（相对屏幕宽度）
INIT_FRAC       = 0.20      # 初始大小（屏幕宽度的20%）


def draw_cup(canvas, cx, cy, size):
    """绘制可爱水杯"""
    s = size
    tw = s * 0.65
    bw = s * 0.50
    h  = s * 0.78

    x0, x1 = cx - tw/2, cx + tw/2
    x2, x3 = cx + bw/2, cx - bw/2
    y0, y1 = cy, cy + h

    # 杯身
    canvas.create_polygon(x0,y0, x1,y0, x2,y1, x3,y1,
        fill="#AEE4FF", outline="#5BB8F5", width=max(2,s*0.025))

    # 水体
    m = s*0.04
    wy = y0 + h*0.28
    canvas.create_polygon(
        x3+m, wy, x2-m, wy, x2-m, y1-m, x3+m, y1-m,
        fill="#5BB8F5", outline="")

    # 水面波浪
    wave_h = s*0.04
    for off in [-s*0.07, 0, s*0.07]:
        wx0 = x3+m + off*0.3
        wx1 = x2-m + off*0.3
        canvas.create_arc(wx0, wy-wave_h, wx1, wy+wave_h*0.5,
            start=0, extent=180, style="arc",
            outline="#AEE4FF", width=max(1,s*0.018))

    # 把手
    canvas.create_arc(x2-s*0.04, y0+h*0.22, x2+s*0.28, y0+h*0.65,
        start=-90, extent=180, style="arc",
        outline="#5BB8F5", width=max(2,s*0.04))

    # 气泡
    for bx,by,br in [(cx+s*.07,cy+h*.55,s*.037),(cx-s*.05,cy+h*.66,s*.024),(cx,cy+h*.76,s*.019)]:
        canvas.create_oval(bx-br,by-br,bx+br,by+br, fill="#FFFFFF", outline="#AEE4FF")

    # 杯口高光
    canvas.create_line(x0,y0,x1,y0, fill="#FFFFFF", width=max(2,s*0.03), capstyle="round")

    # 眼睛
    ey = cy + h*0.42
    er = s*0.055
    for ex in [cx-s*.10, cx+s*.10]:
        canvas.create_oval(ex-er,ey-er,ex+er,ey+er, fill="#2C5F8A", outline="")
        canvas.create_oval(ex+er*.2,ey-er*.5,ex+er*.7,ey, fill="#FFFFFF", outline="")

    # 嘴巴
    canvas.create_arc(cx-s*.12,ey+s*.06,cx+s*.12,ey+s*.20,
        start=200, extent=140, style="arc", outline="#2C5F8A", width=max(1,s*0.022))

    # 脸颊
    for ox,oy in [(-s*.19,s*.02),(s*.19,s*.02)]:
        cr = s*0.065
        canvas.create_oval(cx+ox-cr,ey+oy,cx+ox+cr,ey+oy+cr*1.2,
            fill="#FFB3B3", outline="", stipple="gray50")

    # 水滴装饰
    dx,dy,dr = cx-tw*.35, cy-s*.10, s*.06
    canvas.create_oval(dx-dr,dy-dr*1.6,dx+dr,dy+dr*.4,
        fill="#5BB8F5", outline="#AEE4FF")


class WaterReminder:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # 先隐藏

        self.sw = self.root.winfo_screenwidth()
        self.sh = self.root.winfo_screenheight()

        self.win       = None
        self.frac      = INIT_FRAC
        self.growing   = False
        self.grow_job  = None
        self.anim_job  = None
        self.anim_tick = 0

        # 启动后立即弹出（方便测试）
        self.root.after(1000, self.show)

    def show(self):
        if self.win and self.win.winfo_exists():
            return
        self.frac    = INIT_FRAC
        self.growing = True

        self.win = tk.Toplevel(self.root)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-alpha", 0.95)
        self.win.lift()
        self.win.focus_force()

        self.canvas = tk.Canvas(self.win, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self._refresh()
        self._schedule_grow()
        self._animate()

    def _refresh(self):
        if not (self.win and self.win.winfo_exists()):
            return
        self.canvas.delete("all")

        takeover = self.frac >= 0.98
        if takeover:
            w, h = self.sw, self.sh
            self.win.geometry(f"{w}x{h}+0+0")
        else:
            size = int(self.sw * self.frac)
            w = h = size
            self.win.geometry(f"{w}x{h}+10+10")

        self.canvas.configure(width=w, height=h)

        if takeover:
            self.canvas.configure(bg="#0D2137")
            cup_s = w * 0.30
            draw_cup(self.canvas, w//2, h*0.08, cup_s)

            # 闪烁文字
            self.canvas.create_text(w//2, h*0.58,
                text="当前屏幕已被霸占",
                fill="#AEE4FF",
                font=("Microsoft YaHei", max(16, w//10), "bold"),
                tags="warn")
            self.canvas.create_text(w//2, h*0.68,
                text="请立即喝水！💧",
                fill="#5BB8F5",
                font=("Microsoft YaHei", max(14, w//13), "bold"))
        else:
            self.canvas.configure(bg="#F0F9FF")
            # 标题
            self.canvas.create_text(w//2, w*0.10,
                text="💧 该喝水啦！",
                fill="#2C5F8A",
                font=("Microsoft YaHei", max(10, w//10), "bold"))
            # 水杯
            draw_cup(self.canvas, w//2, w*0.20, w*0.44)
            # 提示
            self.canvas.create_text(w//2, w*0.80,
                text="不喝我会变大哦 👀",
                fill="#5BB8F5",
                font=("Microsoft YaHei", max(8, w//18)))

        # 按钮
        bw2 = max(90, w//3)
        bh2 = max(36, w//10)
        bx  = w//2
        by  = (h if takeover else w) * 0.90

        self._rounded_rect(bx-bw2//2, by-bh2//2, bx+bw2//2, by+bh2//2,
            bh2//2, fill="#5BB8F5", outline="#3A9FE8",
            width=2, tags="drinked")
        self.canvas.create_text(bx, by,
            text="✅  我喝了！",
            fill="white",
            font=("Microsoft YaHei", max(10, w//16), "bold"),
            tags="drinked")

        self.canvas.tag_bind("drinked", "<Button-1>", self._on_drink)
        self.canvas.tag_bind("drinked", "<Enter>",
            lambda e: self.canvas.itemconfig("drinked", fill="#3A9FE8"))
        self.canvas.tag_bind("drinked", "<Leave>",
            lambda e: self.canvas.itemconfig("drinked", fill="#5BB8F5"))

    def _rounded_rect(self, x1,y1,x2,y2,r,**kw):
        pts=[x1+r,y1, x2-r,y1, x2,y1, x2,y1+r,
             x2,y2-r, x2,y2, x2-r,y2, x1+r,y2,
             x1,y2, x1,y2-r, x1,y1+r, x1,y1]
        kw["smooth"]=True
        self.canvas.create_polygon(*pts,**kw)

    def _animate(self):
        """水杯浮动 + 全屏时文字闪烁"""
        if not (self.win and self.win.winfo_exists()):
            return
        self.anim_tick += 1

        # 浮动（通过微调Y坐标）
        if self.frac < 0.98:
            offset = int(math.sin(math.radians(self.anim_tick * 4)) * 5)
            self.win.geometry(f"+10+{10+offset}")

        # 全屏时文字闪烁
        if self.frac >= 0.98:
            alpha = 0.6 + 0.4 * abs(math.sin(math.radians(self.anim_tick * 3)))
            color = self._lerp_color("#0D2137", "#AEE4FF", alpha)
            try:
                self.canvas.itemconfig("warn", fill=color)
            except Exception:
                pass

        self.anim_job = self.win.after(40, self._animate)

    def _lerp_color(self, c1, c2, t):
        r1,g1,b1 = int(c1[1:3],16),int(c1[3:5],16),int(c1[5:7],16)
        r2,g2,b2 = int(c2[1:3],16),int(c2[3:5],16),int(c2[5:7],16)
        r=int(r1+(r2-r1)*t); g=int(g1+(g2-g1)*t); b=int(b1+(b2-b1)*t)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _schedule_grow(self):
        if self.grow_job:
            try: self.win.after_cancel(self.grow_job)
            except: pass
        self.grow_job = self.win.after(int(GROW_INTERVAL*1000), self._grow)

    def _grow(self):
        if not self.growing:
            return
        if not (self.win and self.win.winfo_exists()):
            return
        self.frac = min(self.frac + GROW_STEP, 1.0)
        self._refresh()
        # 抖动
        self._shake()
        if self.frac < 1.0:
            self._schedule_grow()

    def _shake(self, n=0):
        if not (self.win and self.win.winfo_exists()):
            return
        if n >= 8:
            return
        dx = 8 if n % 2 == 0 else -8
        try:
            geo = self.win.geometry()
            _, pos = geo.split("+", 1)
            px, py = pos.split("+")
            self.win.geometry(f"+{int(px)+dx}+{py}")
        except: pass
        self.win.after(35, lambda: self._shake(n+1))

    def _on_drink(self, e=None):
        self.growing = False
        if self.grow_job:
            try: self.win.after_cancel(self.grow_job)
            except: pass
        if self.anim_job:
            try: self.win.after_cancel(self.anim_job)
            except: pass
        # 淡出
        self._fade_out(0.95)

    def _fade_out(self, alpha):
        if not (self.win and self.win.winfo_exists()):
            self._next_remind()
            return
        alpha -= 0.07
        if alpha <= 0:
            self.win.destroy()
            self.win = None
            self._next_remind()
            return
        self.win.attributes("-alpha", alpha)
        self.win.after(20, lambda: self._fade_out(alpha))

    def _next_remind(self):
        self.root.after(int(REMIND_INTERVAL*1000), self.show)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = WaterReminder()
    app.run()
