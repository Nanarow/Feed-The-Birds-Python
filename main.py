import math
import random
from tkinter import HIDDEN, NORMAL, Tk, Canvas
import time


def toggle_state(current_state):
    return NORMAL if current_state == HIDDEN else HIDDEN


def current_time_mil():
    return round(time.time() * 1000)


def easeInOutQuart(x):
    if x < 0.5:
        return 8 * x * x * x * x
    elif x < 1:
        return 1 - math.pow(-2 * x + 2, 4) / 2
    return x


root = Tk()
root.resizable(False, False)
c = Canvas(root, width=1200, height=650)
c.configure(bg='#edffff', highlightthickness=0)
c.can_summon = True


class Bird:
    def __init__(self, canvas, x=180, y=80, scale: float = 1):
        self.tags = f"bird{random.randrange(1000, 9999)}"
        self.x = x
        self.y = y
        self.scale = scale
        self.canvas: Canvas = canvas
        self.clicked = True
        self.food_count = 0
        # --- create bird ----
        self.food = self.oval(40, 0, 20, 14, fill="#fada5c", state=HIDDEN, tags=self.tags)
        self.back = self.polygon([(182, 62), (106, 230), (406, 230)], fill="#85a7af", tags=self.tags)
        self.head = self.oval(86, 50, 120, 120, fill="#3e4645", tags=self.tags)
        self.neck = self.rectangle(86, 110, 60, 60, fill="#3e4645", tags=self.tags)
        self.outer_eye = self.oval(126, 90, 40, 40, fill="#293835", tags=self.tags)
        self.inner_eye = self.oval(136, 100, 20, 20, fill="#4f5c57", tags=self.tags)
        self.mouth_top = self.polygon([(46, 135), (86, 135), (86, 110)], fill="#6b6970", tags=self.tags)
        self.mouth_bottom = self.polygon([(46, 135), (86, 135), (86, 160)], fill="#6b6970", tags=self.tags)
        self.front_body = self.arc(86, 50, 240, 240, start=180, fill="#f55851", tags=self.tags)
        self.back_body = self.arc(86, 50, 240, 240, start=270, fill="#c54740", tags=self.tags)
        self.tail = self.arc(206, 50, 240, 240, start=315, fill="#364542", extent=45, tags=self.tags)
        self.tail2 = self.arc(206, 50, 240, 240, start=300, fill="#364542", extent=45, state=HIDDEN, tags=self.tags)
        self.outer_wing_up = self.arc(136, 0, 240, 240, start=225, fill="#364542", extent=180, tags=self.tags)
        self.inner_wing_up = self.arc(176, 40, 160, 160, start=225, fill="#d6e1e5", extent=180, tags=self.tags)
        self.outer_wing_down = self.arc(0, 56, 240, 240, start=180, fill="#364542",
                                        extent=180, state=NORMAL, tags=self.tags)
        self.inner_wing_down = self.arc(40, 96, 160, 160, start=180, fill="#d6e1e5",
                                        extent=180, state=NORMAL, tags=self.tags)
        self.hearts = [self.polygon([(5 + i, 0), (10 + i, 5), (15 + i, 0), (20 + i, 5), (20 + i, 10), (10 + i, 20),
                                     (0 + i, 10), (0 + i, 5)], fill="", outline="#fa5c5c", width=2 * self.scale,
                                    tags=self.tags) for i in range(120, 181, 30)]

        self.main_frame = self.rectangle(0, 0, 446, 300, fill="", outline="", tags=self.tags)
        self.collision = self.polygon([(140, 35), (258, 112), (340, 35), (376, 70), (376, 170),
                                       (446, 170), (446, 230), (386, 276), (360, 230),
                                       (310, 230), (260, 300), (60, 300), (0, 220), (0, 175),
                                       (45, 175), (45, 120)], fill="", outline="", tags=self.tags)
        # --- created bird ---
        self.landing()
        self.idle_animation()
        self.canvas.tag_bind(self.collision, '<Button-1>', self.on_click)

    def create_shape(self, x, y, width, height, shape_type, outline="", **kwargs):
        x_scale = self.scale * x + self.x
        y_scale = self.scale * y + self.y
        w_scale = self.scale * width
        h_scale = self.scale * height
        return getattr(self.canvas, "create_" + shape_type)(x_scale, y_scale, x_scale + w_scale, y_scale + h_scale,
                                                            outline=outline, **kwargs)

    def oval(self, x, y, width, height, outline="", **kwargs):
        return self.create_shape(x, y, width, height, "oval", outline=outline, **kwargs)

    def rectangle(self, x, y, width, height, outline="", **kwargs):
        return self.create_shape(x, y, width, height, "rectangle", outline=outline, **kwargs)

    def arc(self, x, y, width, height, outline="", **kwargs):
        return self.create_shape(x, y, width, height, "arc", outline=outline, **kwargs)

    def scale_point(self, point):
        x, y = point
        return x * self.scale + self.x, y * self.scale + self.y

    def polygon(self, points: list, outline="", **kwargs):
        new_points = list(map(self.scale_point, points))
        return self.canvas.create_polygon(new_points, outline=outline, **kwargs)

    def get_rectangle(self, target, **kwargs):
        return self.canvas.create_rectangle(self.canvas.coords(target), outline="red", **kwargs)

    def show_frame(self, _event):
        self.get_rectangle(self.head)
        self.get_rectangle(self.neck)
        self.get_rectangle(self.inner_eye)
        self.get_rectangle(self.outer_eye)
        self.get_rectangle(self.tail)
        self.get_rectangle(self.inner_wing_up)
        self.get_rectangle(self.outer_wing_up)
        self.get_rectangle(self.inner_wing_down)
        self.get_rectangle(self.outer_wing_down)
        self.get_rectangle(self.front_body)
        self.get_rectangle(self.back_body)

    def idle_animation(self):
        self.bird_move(start=random.randrange(314))
        self.bird_blink()
        self.bird_fly()
        self.bird_tailing()

    def move(self, x):
        sin_y = math.sin(x) * 2 * self.scale
        self.canvas.move(self.tags, 0, sin_y)

    def blink(self):
        current_state = self.canvas.itemcget(self.inner_eye, 'state')
        self.canvas.itemconfigure(self.inner_eye, state=toggle_state(current_state))

    def fly(self):
        current_state = self.canvas.itemcget(self.inner_wing_up, 'state')
        new_state = toggle_state(current_state)
        self.canvas.itemconfigure(self.outer_wing_up, state=new_state)
        self.canvas.itemconfigure(self.inner_wing_up, state=new_state)
        self.canvas.itemconfigure(self.outer_wing_down, state=toggle_state(new_state))
        self.canvas.itemconfigure(self.inner_wing_down, state=toggle_state(new_state))

    def tailing(self):
        current_state = self.canvas.itemcget(self.tail, 'state')
        new_state = toggle_state(current_state)
        self.canvas.itemconfigure(self.tail, state=new_state)
        self.canvas.itemconfigure(self.tail2, state=toggle_state(new_state))

    def bird_move(self, start=0):
        frame_time = 40
        for i in range(start, math.ceil(math.pi * 100)):
            root.after(frame_time, lambda _=i / 10: self.move(_))
            frame_time += 40
        # print(f"move: {frame_time} millisecond")
        self.canvas.after(frame_time, self.bird_move)

    def bird_blink(self):
        frame_time = 0
        for i in range(10):
            frame_time += random.randrange(200, 1200, 10)
            root.after(frame_time, self.blink)
            frame_time += random.randrange(200, 600, 10)
            root.after(frame_time, self.blink)
        # print(f"blink: {frame_time} millisecond")
        self.canvas.after(frame_time, self.bird_blink)

    def bird_fly(self):
        frame_time = 0
        for i in range(30):
            pass
        frame_time += random.randrange(100, 200, 10)
        root.after(frame_time, self.fly)
        frame_time += random.randrange(100, 200, 10)
        root.after(frame_time, self.fly)
        # print(f"fly: {frame_time} millisecond")
        self.canvas.after(frame_time, self.bird_fly)

    def bird_tailing(self):
        frame_time = 0
        for i in range(8):
            frame_time += random.randrange(200, 1000, 10)
            root.after(frame_time, self.tailing)
            frame_time += random.randrange(200, 1000, 10)
            root.after(frame_time, self.tailing)
        # print(f"tailing: {frame_time} millisecond")
        self.canvas.after(frame_time, self.bird_tailing)

    def on_click(self, event):
        if not self.clicked and not self.canvas.can_summon:
            self.canvas.itemconfigure(self.food, state=NORMAL)
            self.drop_food()
            self.clicked = True

    def drop_food(self):
        self.canvas.move(self.food, 0, 3 * self.scale)
        x1, y1, x2, y2 = self.canvas.coords(self.food)
        result = self.canvas.find_overlapping(x1, y1, x2, y2)
        if self.mouth_bottom in result:
            self.canvas.itemconfigure(self.food, tags=self.tags)
            self.eat()
        else:
            root.after(50, self.drop_food)

    def eating(self, x=1, y=-1):
        top = self.canvas.coords(self.mouth_top)
        top[1] = top[1] + x * self.scale
        bottom = self.canvas.coords(self.mouth_bottom)
        bottom[1] = bottom[1] + y * self.scale
        self.canvas.coords(self.mouth_top, top)
        self.canvas.coords(self.mouth_bottom, bottom)

    def eat(self):
        self.eating(x=-10, y=10)
        self.canvas.move(self.food, 0, 6 * self.scale)
        for i in range(100, 801, 100):
            root.after(i, lambda: self.canvas.move(self.food, 3 * self.scale, 0))
        for i in range(100, 1001, 100):
            root.after(i, self.eating)
        root.after(800, self.reset_food)

    def reset_food(self):
        self.canvas.itemconfigure(self.food, tags=f"food_{self.tags}")
        self.canvas.moveto(self.food, self.x + 40 * self.scale, self.y)
        self.canvas.itemconfigure(self.food, state=HIDDEN)
        self.clicked = False
        self.canvas.itemconfigure(self.hearts[self.food_count], fill="#fa5c5c")
        self.food_count += 1
        if self.food_count == 3:
            self.clicked = True
            self.take_off()

    def take_off(self, start=0):
        if self.canvas.coords(self.main_frame)[0] < 0:
            root.after(1000, lambda: self.canvas.delete(self.tags))
            root.after(1000, lambda: self.canvas.delete(f"food_{self.tags}"))
        else:
            root.after(start, lambda: self.canvas.move(self.tags, -easeInOutQuart(start / 1000) * 10 * self.scale, 0))
            root.after(10, lambda: self.take_off(start + 10))

    def landing(self):
        distance = 1200 - self.x
        self.canvas.move(self.tags, distance, 0)
        time_frame = 100
        for i in range(0, int(distance / 2)):
            root.after(time_frame, lambda: self.canvas.move(self.tags, -2, 0))
            time_frame += 10
        root.after(time_frame, self.canClick)
        root.after(time_frame, lambda: self.canvas.itemconfigure(self.food, tags=f"food_{self.tags}"))

    def canClick(self):
        self.clicked = False


c.pack()
c.create_text(86, 20, text="Summon Bird", font="bold")
c.create_text(74, 50, text="Feed Bird", font="bold")
choice1 = c.create_text(16, 20, text=">>", font="bold", fill="#f73b3b")
choice2 = c.create_text(16, 50, text="", font="bold", fill="#f73b3b")


def summon_bird(event):
    if c.can_summon:
        scale = random.randrange(2, 11) / 10
        x = event.x - (223 * scale)
        y = event.y - (150 * scale)
        Bird(c, x, y, scale)


def handle_mode(_event):
    c.can_summon = not c.can_summon
    if c.can_summon:
        c.itemconfigure(choice1, text=">>")
        c.itemconfigure(choice2, text="")
    else:
        c.itemconfigure(choice2, text=">>")
        c.itemconfigure(choice1, text="")


c.bind_all('<space>', handle_mode)
c.bind('<Button-1>', summon_bird)
root.mainloop()

