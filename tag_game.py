#!/usr/bin/env python3
"""
TAG  -  2 / 3 / 4 player hot-potato tag (local multiplayer, one keyboard)

There are no winners, only "not-losers": whoever is "it" when the clock hits
zero loses. Everyone else is safe.

Run:   pip install pygame      (once)
       python tag_game.py

Profiles, ratings, settings and stats are saved to  tag_data.json  next to
this script, so they persist between runs.
"""
import base64
import io
import json
import math
import os
import random
import sys
from datetime import datetime

import pygame

W, H = 1280, 720
FPS = 60
ZOOM_MAX = 1.5      # how far the camera may zoom in when players are close
ZOOM_MIN = 0.85     # how far it may zoom out (a bit past the map edge, so everyone always fits)


def app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


DATA_FILE = os.path.join(app_dir(), "tag_data.json")

# --------------------------------------------------------------------------
#  Static definitions
# --------------------------------------------------------------------------
# Player sprites (red, blue, yellow, green) - embedded so the game stays a single file.
SPRITE_B64 = [
    (
        "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"
    ),
    (
        "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"
    ),
    (
        "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"
        "CwwA/D8xFPPMQMqXEwAAAABJRU5ErkJggg=="
    ),
    (
        "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"
    ),
]
SPR_W = 34                       # on-screen sprite width (world pixels)
SPR_H = int(SPR_W * 70 / 71)
LEG_H = 9                        # how far the legs reach below the sprite body
SKIN = (11, 52, 66)
SKIN_STYLES = ("classic", "durag", "crown", "headphones", "shades")
SKIN_LABELS = {
    "classic": "Classic",
    "durag": "Durag",
    "crown": "Crown",
    "headphones": "Headphones",
    "shades": "Shades",
}
RESERVED_KEYS = (pygame.K_ESCAPE, pygame.K_F11, pygame.K_RETURN)

COLORS = [(235, 64, 52), (52, 120, 246), (250, 200, 40), (60, 200, 90)]
COLOR_NAMES = ["RED", "BLUE", "YELLOW", "GREEN"]
CONTROLS = [
    dict(left=pygame.K_a, right=pygame.K_d, jump=pygame.K_w, act=pygame.K_q, move="W A D"),
    dict(left=pygame.K_LEFT, right=pygame.K_RIGHT, jump=pygame.K_UP, act=pygame.K_c, move="Arrows"),
    dict(left=pygame.K_j, right=pygame.K_l, jump=pygame.K_i, act=pygame.K_y, move="I J L"),
    dict(left=pygame.K_f, right=pygame.K_h, jump=pygame.K_t, act=pygame.K_m, move="T F H"),
]
DEFAULT_DASH = [c["act"] for c in CONTROLS]
DEFAULT_DASH_KEYS = ["q", "c", "y", "m"]


def key_label(key):
    n = pygame.key.name(key).upper()
    return {"LEFT SHIFT": "L-SHIFT", "RIGHT SHIFT": "R-SHIFT", "LEFT CTRL": "L-CTRL",
            "RIGHT CTRL": "R-CTRL", "LEFT ALT": "L-ALT", "RIGHT ALT": "R-ALT"}.get(n, n)


def ctl_label(i):
    return "%s  +  %s" % (CONTROLS[i]["move"], key_label(CONTROLS[i]["act"]))


def apply_dash_keys(names):
    """Load saved dash keys into CONTROLS (falls back to the default if a name is unknown)."""
    for i, nm in enumerate((list(names) + [None] * 4)[:4]):
        try:
            CONTROLS[i]["act"] = pygame.key.key_code(nm)
        except (ValueError, TypeError, pygame.error):
            CONTROLS[i]["act"] = DEFAULT_DASH[i]

THEMES = {
    "forest": dict(sky_top=(58, 150, 240), sky_bot=(120, 225, 240), plat=(240, 50, 130),
                   top=(100, 225, 90), far=(70, 130, 225), trunk=(200, 30, 110),
                   leaf=(60, 240, 110), wall=(240, 45, 125), wall2=(205, 30, 105), deco="tree"),
    "desert": dict(sky_top=(250, 150, 80), sky_bot=(255, 224, 150), plat=(170, 95, 55),
                   top=(245, 205, 95), far=(235, 145, 95), trunk=(90, 160, 70),
                   leaf=(70, 180, 95), wall=(190, 110, 60), wall2=(165, 90, 45), deco="cactus"),
    "taiga": dict(sky_top=(140, 185, 230), sky_bot=(228, 242, 252), plat=(40, 85, 115),
                  top=(245, 250, 255), far=(135, 165, 205), trunk=(80, 55, 45),
                  leaf=(35, 120, 95), wall=(45, 90, 120), wall2=(30, 70, 100), deco="pine"),
}

# key, label, lo, hi, step, default, format
SETTINGS_DEF = [
    ("round_time", "Round length", 30, 300, 10, 120, "{:.0f} s"),
    ("buff_strength", "Power-up strength", 0.25, 3.0, 0.25, 1.0, "{:.2f}x"),
    ("buff_duration", "Power-up duration", 0.25, 3.0, 0.25, 1.0, "{:.2f}x"),
    ("buff_spawn", "Power-up spawn every", 2, 30, 1, 8, "{:.0f} s"),
    ("max_pickups", "Max power-ups on map", 1, 8, 1, 3, "{:.0f}"),
    ("gravity", "Gravity", 0.4, 2.0, 0.1, 1.0, "{:.1f}x"),
    ("move_speed", "Run speed", 0.5, 2.0, 0.1, 1.0, "{:.1f}x"),
    ("jump_power", "Jump power", 0.5, 1.6, 0.1, 1.0, "{:.1f}x"),
    ("air_jumps", "Extra air jumps", 0, 3, 1, 1, "{:.0f}"),
    ("tramp", "Trampoline strength", 0.5, 2.5, 0.1, 1.0, "{:.1f}x"),
    ("pad", "Speed-pad strength", 0.5, 3.0, 0.25, 1.0, "{:.2f}x"),
    ("dash", "Dash strength (0 = off)", 0, 2.5, 0.25, 1.0, "{:.2f}x"),
    ("tag_cd", "Re-tag lockout", 0.2, 3.0, 0.1, 1.0, "{:.1f} s"),
    ("it_bonus", "'It' speed bonus", 0, 0.5, 0.05, 0.10, "{:.0%}"),
]
DEFAULT_SETTINGS = {d[0]: d[5] for d in SETTINGS_DEF}
DEFAULT_SETTINGS.update(buffs_on=True, theme="random", motion_blur=0)

PICKUP_TYPES = {
    "speed": ((70, 170, 255), "SPD"),
    "jump": ((90, 235, 120), "JMP"),
    "shield": ((255, 215, 60), "SHD"),
    "freeze": ((170, 240, 255), "ICE"),
}

START_RATING = 1000.0


def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def fmt_time(s):
    s = max(0.0, s)
    return "%d:%04.1f" % (int(s // 60), s % 60)


# --------------------------------------------------------------------------
#  Persistent data
# --------------------------------------------------------------------------
def new_profile(color_idx):
    return dict(rating=START_RATING, peak=START_RATING, matches=0, losses=0, survived=0,
                total_hold=0.0, longest_hold=0.0, longest_hold_date="", time_played=0.0,
                tags_made=0, times_tagged=0, pickups=0, streak=0, best_streak=0,
                tagged={}, history=[START_RATING], color_idx=color_idx, skin="classic",
                created=datetime.now().strftime("%Y-%m-%d"))


def default_data():
    profiles = {"Player 1": new_profile(0), "Player 2": new_profile(1),
                "Player 3": new_profile(2), "Player 4": new_profile(3)}
    return dict(settings=dict(DEFAULT_SETTINGS),
                slots=["Player 1", "Player 2", "Player 3", "Player 4"],
                enabled=[True, True, False, False], dash_keys=list(DEFAULT_DASH_KEYS),
                profiles=profiles, history=[],
                records=dict(longest_hold=dict(name="", secs=0.0, date="")))


def load_data():
    d = default_data()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
        d["settings"].update(raw.get("settings", {}))
        if raw.get("profiles"):
            d["profiles"] = {}
            for name, p in raw["profiles"].items():
                base = new_profile(len(d["profiles"]) % 4)
                base.update(p)
                if base.get("skin") not in SKIN_STYLES:
                    base["skin"] = "classic"
                d["profiles"][name] = base
        d["slots"] = (raw.get("slots", d["slots"]) + [None] * 4)[:4]
        d["enabled"] = (raw.get("enabled", d["enabled"]) + [False] * 4)[:4]
        d["dash_keys"] = (raw.get("dash_keys", d["dash_keys"]) + DEFAULT_DASH_KEYS)[:4]
        d["history"] = raw.get("history", [])
        d["records"].update(raw.get("records", {}))
        for i, s in enumerate(d["slots"]):
            if s not in d["profiles"]:
                d["slots"][i] = None
    except (OSError, ValueError):
        pass
    return d


def save_data(d):
    tmp = DATA_FILE + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(d, f, indent=1)
        os.replace(tmp, DATA_FILE)
    except OSError as e:
        print("Could not save data:", e)


# --------------------------------------------------------------------------
#  Level
# --------------------------------------------------------------------------
class Level:
    def __init__(self, theme, seed):
        rng = random.Random(seed)
        self.theme = theme
        self.T = THEMES[theme]
        self.WW, self.WH = 1400, 760          # ~1/4 of the old map area
        WW, WH = self.WW, self.WH
        self.floor_y = WH - 30
        self.ROW = 150                          # vertical spacing between platform rows
        TH = 10                                 # platform thickness (platforms are solid)
        self.solids = [(0, self.floor_y, WW, WH + 200)]       # solid boxes (x1,y1,x2,y2)
        self.segs = [(0, self.floor_y, WW, self.floor_y)]     # things to draw as platforms
        self.flat = []
        self.rows = []
        y = self.floor_y - self.ROW
        while y > 100:
            self.rows.append(y)
            y -= self.ROW
        for y in self.rows:
            x = rng.randint(0, 120)
            while x < WW - 170:
                w = rng.randint(170, 340)
                x2 = min(WW, x + w)
                if WW - x2 < 110:
                    x2 = WW
                s_ = (x, y, x2, y)
                self.segs.append(s_)
                self.solids.append((x, y, x2, y + TH))
                self.flat.append(s_)
                x = x2 + rng.randint(110, 220)
        self.flat_nofloor = list(self.flat)
        # ramps: one per row, attached to the end of a platform, leading down to the row below
        self.ramps = []
        RW = 260
        for y_high in self.rows:
            y_low = y_high + self.ROW
            cands = [f for f in self.flat_nofloor if f[1] == y_high]
            rng.shuffle(cands)
            for f in cands:
                opts = []
                if f[0] - RW >= 8:
                    opts.append((f[0] - RW, y_low, f[0], y_high))
                if f[2] + RW <= WW - 8:
                    opts.append((f[2], y_high, f[2] + RW, y_low))
                if opts:
                    r = rng.choice(opts)
                    self.ramps.append(r)
                    self.segs.append(r)
                    # make sure something solid sits at the foot of the ramp so it is reachable
                    foot = r[0] if r[1] == y_low else r[2]
                    if y_low != self.floor_y and not any(
                            g_[1] == y_low and g_[0] - 30 <= foot <= g_[2] + 30 for g_ in self.flat_nofloor):
                        fx1, fx2 = max(0, foot - 90), min(WW, foot + 90)
                        g_ = (fx1, y_low, fx2, y_low)
                        self.segs.append(g_)
                        self.solids.append((fx1, y_low, fx2, y_low + TH))
                        self.flat.append(g_)
                        self.flat_nofloor.append(g_)
                    break
        self.flat.append(self.segs[0])   # floor counts as flat for spawns / pickups
        # --- props. Placed with a spacing check so nothing sits on top of anything else.
        self.occupied = []            # (y, x1, x2) of everything already standing on a platform

        def clear(y, x1, x2, pad=24):
            for (oy, a, b) in self.occupied:
                if oy == y and x1 - pad < b and x2 + pad > a:
                    return False
            return True

        def claim(y, x1, x2):
            self.occupied.append((y, x1, x2))

        # teleporters: ONE pair, on two different platforms that are far apart
        self.tele = []
        wide = [f for f in self.flat_nofloor if f[2] - f[0] >= 150]
        if len(wide) >= 2:
            best = None
            for _ in range(30):
                a_, b_ = rng.sample(wide, 2)
                dist = abs((a_[0] + a_[2]) / 2 - (b_[0] + b_[2]) / 2) + abs(a_[1] - b_[1])
                if a_[1] != b_[1] and (best is None or dist > best[0]):
                    best = (dist, a_, b_)
            if best:
                _, a_, b_ = best
                ax, bx = (a_[0] + a_[2]) / 2, (b_[0] + b_[2]) / 2
                self.tele.append(((ax, a_[1]), (bx, b_[1])))
                claim(a_[1], ax - 30, ax + 30)
                claim(b_[1], bx - 30, bx + 30)
        # crates (solid)
        self.crates = []
        for _ in range(2):
            for _try in range(8):
                f = rng.choice(self.flat_nofloor)
                if f[2] - f[0] < 130:
                    continue
                n = rng.choice([1, 2])
                cx = rng.randint(int(f[0] + 20), int(f[2] - 60))
                if not clear(f[1], cx, cx + 36):
                    continue
                self.crates.append((cx, f[1], n))
                self.solids.append((cx, f[1] - 36 * n, cx + 36, f[1]))
                claim(f[1], cx, cx + 36)
                break
        # trampolines
        self.tramps = []
        for _ in range(3):
            for _try in range(8):
                f = rng.choice(self.flat)
                if f[2] - f[0] < 120:
                    continue
                cx = rng.randint(int(f[0] + 40), int(f[2] - 40))
                if not clear(f[1], cx - 24, cx + 24):
                    continue
                self.tramps.append(dict(x1=cx - 24, x2=cx + 24, top=f[1] - 12, base=f[1]))
                claim(f[1], cx - 24, cx + 24)
                break
        # speed pads
        self.pads = []
        for _ in range(2):
            for _try in range(8):
                f = rng.choice(self.flat)
                if f[2] - f[0] < 220:
                    continue
                cx = rng.randint(int(f[0] + 80), int(f[2] - 80))
                if not clear(f[1], cx - 40, cx + 40):
                    continue
                self.pads.append((cx - 40, cx + 40, f[1]))
                claim(f[1], cx - 40, cx + 40)
                break
        # decor (kept sparse)
        self.decor = []
        for f in self.flat:
            w = f[2] - f[0]
            if w > 150 and rng.random() < 0.4:
                dx = rng.randint(int(f[0] + 20), int(f[2] - 20))
                if clear(f[1], dx - 20, dx + 20, 10):
                    self.decor.append(("big", dx, f[1], rng.randint(40, 80)))
                    claim(f[1], dx - 20, dx + 20)
            for _ in range(rng.randint(0, 1)):
                fx = rng.randint(int(f[0] + 10), int(f[2] - 10))
                if clear(f[1], fx - 6, fx + 6, 6):
                    self.decor.append(("flower", fx, f[1],
                                       rng.choice([(255, 80, 160), (255, 190, 60), (255, 255, 255)])))
        # far silhouettes
        self.far = [(rng.randint(-100, WW), rng.randint(120, 300), rng.randint(60, 140)) for _ in range(24)]
        # sky
        self.sky = pygame.Surface((W, H))
        for yy in range(H):
            t = yy / H
            c = tuple(int(self.T["sky_top"][i] * (1 - t) + self.T["sky_bot"][i] * t) for i in range(3))
            pygame.draw.line(self.sky, c, (0, yy), (W, yy))

    def y_at(self, s, x):
        if s[2] == s[0]:
            return s[1]
        return s[1] + (s[3] - s[1]) * (x - s[0]) / (s[2] - s[0])

    def random_spot(self, rng):
        s = rng.choice(self.flat)
        return rng.uniform(s[0] + 30, s[2] - 30), s[1]


# --------------------------------------------------------------------------
#  Player
# --------------------------------------------------------------------------
class Player:
    def __init__(self, slot, name, pos):
        self.slot, self.name = slot, name
        self.color = COLORS[slot]
        self.ctl = CONTROLS[slot]
        self.x, self.y = pos
        self.vx = self.vy = 0.0
        self.w, self.h = 22, 26
        self.on_ground = False
        self.coyote = 0.0
        self.jumps_left = 0
        self.jump_buf = 0.0
        self.facing = 1
        self.buffs = {}
        self.tag_immune = 0.0
        self.frozen = 0.0
        self.tp_cd = 0.0
        self.dash_cd = 0.0
        self.dash_t = 0.0
        self.pad_t = 0.0
        self.walk = 0.0           # leg-cycle phase
        self.prev_jump = self.prev_act = False
        # match stats
        self.hold = 0.0
        self.cur_hold = 0.0
        self.best_hold = 0.0
        self.tags_made = 0
        self.times_tagged = 0
        self.pickups = 0
        self.tagged = {}

    @property
    def cx(self):
        return self.x

    @property
    def cy(self):
        return self.y - self.h / 2

    def resolve_x(self, L):
        """Push the player out of solid boxes horizontally (with a small step-up so ramps join platforms)."""
        hw = self.w / 2
        for (x1, y1, x2, y2) in L.solids:
            left, right = self.x - hw, self.x + hw
            top, bottom = self.y - self.h, self.y
            if right > x1 and left < x2 and bottom > y1 + 0.5 and top < y2 - 0.5:
                if bottom - y1 <= 9 and self.vy >= 0:
                    self.y = y1
                elif self.vx > 0 or (self.vx == 0 and self.x < (x1 + x2) / 2):
                    self.x = x1 - hw
                    self.vx = 0
                else:
                    self.x = x2 + hw
                    self.vx = 0

    def step(self, g, dt, keys):
        S = g.S
        if keys is None:
            left = right = jump = act = False
        else:
            left, right = keys[self.ctl["left"]], keys[self.ctl["right"]]
            jump, act = keys[self.ctl["jump"]], keys[self.ctl["act"]]
        jp = jump and not self.prev_jump
        ap = act and not self.prev_act
        self.prev_jump, self.prev_act = jump, act
        if self.frozen > 0:
            self.frozen -= dt
            left = right = jump = False
            jp = ap = False
        for k in list(self.buffs):
            self.buffs[k] -= dt
            if self.buffs[k] <= 0:
                del self.buffs[k]
        self.tag_immune = max(0, self.tag_immune - dt)
        self.tp_cd = max(0, self.tp_cd - dt)
        self.dash_cd = max(0, self.dash_cd - dt)
        self.pad_t = max(0, self.pad_t - dt)

        speed = 300 * S["move_speed"]
        if g.it is self:
            speed *= 1 + S["it_bonus"]
        if "speed" in self.buffs:
            speed *= 1 + 0.5 * S["buff_strength"]
        if self.pad_t > 0:
            speed *= 1 + 0.6 * S["pad"]
        jump_v = 760 * S["jump_power"]
        if "jump" in self.buffs:
            jump_v *= min(2.2, 1 + 0.25 * S["buff_strength"])
        grav = 2000 * S["gravity"]

        if ap and S["dash"] > 0 and self.dash_cd <= 0:
            self.dash_t = 0.14
            self.dash_cd = 1.4
            self.vx = self.facing * 720 * S["dash"]
            self.vy *= 0.2
            g.burst(self.x, self.cy, self.color, 10)
        if self.dash_t > 0:
            self.dash_t -= dt
        else:
            target = (int(right) - int(left)) * speed
            acc = 3200 if self.on_ground else 1900
            if abs(self.vx) > speed * 1.05 and target * self.vx > 0:
                acc = 600  # keep pad / dash momentum a moment
            if self.vx < target:
                self.vx = min(target, self.vx + acc * dt)
            elif self.vx > target:
                self.vx = max(target, self.vx - acc * dt)
        if self.vx > 5:
            self.facing = 1
        elif self.vx < -5:
            self.facing = -1

        # jumping
        if jp:
            self.jump_buf = 0.12
        self.jump_buf = max(0, self.jump_buf - dt)
        self.coyote = max(0, self.coyote - dt)
        if self.jump_buf > 0:
            if self.coyote > 0:
                self.vy = -jump_v
                self.coyote = 0
                self.jump_buf = 0
                self.on_ground = False
                g.burst(self.x, self.y, (255, 255, 255), 5)
            elif self.jumps_left > 0 and not self.on_ground:
                self.vy = -jump_v * 0.92
                self.jumps_left -= 1
                self.jump_buf = 0
                g.burst(self.x, self.y, (255, 255, 255), 6)
        if self.vy < 0 and not jump and self.dash_t <= 0:
            self.vy += grav * 1.2 * dt   # short hop when released

        # move (platforms are solid: land on top, bump heads underneath, blocked at the sides)
        L = g.level
        hw = self.w / 2
        self.x = clamp(self.x + self.vx * dt, hw, L.WW - hw)
        self.resolve_x(L)
        prev_feet = self.y
        prev_top = prev_feet - self.h
        if self.dash_t <= 0:
            self.vy = min(self.vy + grav * dt, 1500)
        self.y += self.vy * dt
        was_ground = self.on_ground
        self.on_ground = False
        rising = self.vy < 0

        landed = False
        if not rising:
            for tr in L.tramps:
                if tr["x1"] <= self.x <= tr["x2"] and prev_feet <= tr["top"] + 10 and self.y >= tr["top"]:
                    self.vy = -min(2400, 980 * S["tramp"])
                    self.y = tr["top"]
                    self.jumps_left = int(S["air_jumps"])
                    g.burst(self.x, self.y, (120, 255, 150), 10)
                    landed = True
                    break
        if not landed:
            best = None
            for (x1, y1, x2, y2) in L.solids:
                if self.x + hw <= x1 or self.x - hw >= x2:
                    continue
                if not rising:
                    if prev_feet <= y1 + 1 and self.y >= y1:
                        if best is None or y1 < best:
                            best = y1
                elif self.y - self.h < y2 and prev_top >= y2 - 1:
                    self.y = y2 + self.h      # bonk head on the underside
                    self.vy = 0
            for s_ in L.ramps:
                if s_[0] <= self.x <= s_[2]:
                    ly = L.y_at(s_, self.x)
                    if not rising:
                        if prev_feet <= ly + 10 and self.y >= ly - 1:
                            if best is None or ly < best:
                                best = ly
                    elif self.y - self.h < ly + 10 and prev_top >= ly + 10 - 1:
                        self.y = ly + 10 + self.h
                        self.vy = 0
            if best is not None:
                self.y = best
                if self.vy > 500 and not was_ground:
                    g.burst(self.x, self.y, (255, 255, 255), 4)
                self.vy = 0
                self.on_ground = True
                self.coyote = 0.09
                self.jumps_left = int(S["air_jumps"])
        if self.y - self.h < 0:                 # ceiling at the top of the map
            self.y = self.h
            self.vy = max(self.vy, 0)
        if self.on_ground:
            for (x1, x2, py) in L.pads:
                if x1 <= self.x <= x2 and abs(self.y - py) < 5:
                    self.pad_t = 1.1
        # teleporters
        if self.tp_cd <= 0:
            for pa, pb in L.tele:
                for a, b in ((pa, pb), (pb, pa)):
                    if abs(self.x - a[0]) < 22 and abs(self.y - a[1]) < 40:
                        g.burst(self.x, self.cy, (200, 120, 255), 14)
                        self.x, self.y = b
                        self.vy = 0
                        self.tp_cd = 1.0
                        g.burst(self.x, self.cy, (200, 120, 255), 14)
                        break
                if self.tp_cd > 0:
                    break
        if self.y > L.WH + 200:
            self.x, self.y = L.random_spot(g.rng)
            self.vy = 0
        # leg animation: the cycle speeds up with run speed and only runs on the ground
        if self.on_ground and abs(self.vx) > 20:
            self.walk += abs(self.vx) * dt * 0.052


# --------------------------------------------------------------------------
#  Match
# --------------------------------------------------------------------------
class Game:
    def __init__(self, S, roster, theme, seed):
        """roster: list of (slot, profile_name)"""
        self.S = S
        self.rng = random.Random(seed)
        self.level = Level(theme, seed)
        spots = self.rng.sample(self.level.flat, min(len(roster), len(self.level.flat)))
        self.players = []
        for (slot, name), s in zip(roster, spots):
            x = self.rng.uniform(s[0] + 30, s[2] - 30)
            self.players.append(Player(slot, name, (x, s[1])))
        self.it = self.rng.choice(self.players)
        self.time_left = float(S["round_time"])
        self.elapsed = 0.0
        self.intro = 2.2
        self.pickups = []
        self.spawn_t = 3.0
        self.parts = []
        self.over = False
        self.log = []
        self.tag_flash = 0.0
        # camera: tracks all players, zooms in when they are close and out when they spread
        self.zmin = ZOOM_MIN
        self.zmax = max(self.zmin, ZOOM_MAX)
        for p in self.players:
            p.tx, p.ty = p.x, p.cy
        tx, ty, tz = self.cam_target()
        self.cc = [tx, ty]
        self.lz = math.log(tz)
        self.cv = [0.0, 0.0, 0.0]

    # ---- helpers
    CAM_PAD_X = 230
    CAM_PAD_Y = 170

    def cam_target(self):
        xs = [p.tx for p in self.players]
        ys = [p.ty for p in self.players]
        minx, maxx = min(xs) - self.CAM_PAD_X, max(xs) + self.CAM_PAD_X
        miny, maxy = min(ys) - self.CAM_PAD_Y, max(ys) + self.CAM_PAD_Y
        z = min(W / (maxx - minx), H / (maxy - miny))
        return (minx + maxx) / 2, (miny + maxy) / 2, clamp(z, self.zmin, self.zmax)

    @staticmethod
    def smooth_damp(cur, tgt, vel, smooth, dt):
        """Critically damped spring: eases in and out, never overshoots."""
        om = 2.0 / smooth
        x = om * dt
        e = 1.0 / (1.0 + x + 0.48 * x * x + 0.235 * x * x * x)
        ch = cur - tgt
        tmp = (vel + om * ch) * dt
        vel = (vel - om * tmp) * e
        return tgt + (ch + tmp) * e, vel

    def update_camera(self, dt):
        # The camera follows a smoothed copy of each player's position, so an instant
        # teleport turns into a glide instead of a jump cut.
        k = 1 - math.exp(-18 * dt)
        for p in self.players:
            lead_x = clamp(p.vx * 0.12, -50, 50)      # look ahead a little so fast movers stay in frame
            lead_y = clamp(p.vy * 0.10, -90, 90)
            p.tx += (p.x + lead_x - p.tx) * k
            p.ty += (p.cy + lead_y - p.ty) * k
        tx, ty, tz = self.cam_target()
        lt = math.log(tz)
        self.cc[0], self.cv[0] = self.smooth_damp(self.cc[0], tx, self.cv[0], 0.25, dt)
        self.cc[1], self.cv[1] = self.smooth_damp(self.cc[1], ty, self.cv[1], 0.25, dt)
        zs = 0.30 if lt < self.lz else 0.70       # zoom out fast, zoom in gently
        self.lz, self.cv[2] = self.smooth_damp(self.lz, lt, self.cv[2], zs, dt)
        self.lz = clamp(self.lz, math.log(self.zmin), math.log(self.zmax))

    def view(self):
        """Returns (left, top, view_w, view_h, zoom) in world units, kept inside the map."""
        z = math.exp(self.lz)
        vw, vh = W / z, H / z
        L = self.level
        cx = clamp(self.cc[0] - vw / 2, 0, L.WW - vw) if vw < L.WW else (L.WW - vw) / 2
        cy = clamp(self.cc[1] - vh / 2, 0, L.WH - vh) if vh < L.WH else (L.WH - vh) / 2
        return cx, cy, vw, vh, z

    def burst(self, x, y, color, n):
        for _ in range(n):
            a = self.rng.uniform(0, math.tau)
            sp = self.rng.uniform(40, 200)
            self.parts.append([x, y, math.cos(a) * sp, math.sin(a) * sp - 40,
                               self.rng.uniform(0.3, 0.7), 0.7, color, self.rng.uniform(2, 4)])

    # ---- logic
    def transfer(self, new):
        old = self.it
        old.best_hold = max(old.best_hold, old.cur_hold)
        old.tags_made += 1
        old.tagged[new.name] = old.tagged.get(new.name, 0) + 1
        new.times_tagged += 1
        old.tag_immune = self.S["tag_cd"]
        self.log.append((self.elapsed, old.name, new.name, old.cur_hold))
        old.cur_hold = 0.0
        new.cur_hold = 0.0
        self.it = new
        self.tag_flash = 0.25
        self.burst(new.cx, new.cy, (255, 255, 255), 24)

    def spawn_pickup(self):
        x, y = self.level.random_spot(self.rng)
        kind = self.rng.choice(list(PICKUP_TYPES))
        self.pickups.append(dict(kind=kind, x=x, y=y - 22, t=0.0))

    def apply_pickup(self, p, kind):
        S = self.S
        st, du = S["buff_strength"], S["buff_duration"]
        p.pickups += 1
        if kind == "speed":
            p.buffs["speed"] = 6 * du
        elif kind == "jump":
            p.buffs["jump"] = 6 * du
        elif kind == "shield":
            p.buffs["shield"] = 3 * st * du
        elif kind == "freeze":
            if p is self.it:
                others = [q for q in self.players if q is not p]
                tgt = min(others, key=lambda q: (q.x - p.x) ** 2 + (q.y - p.y) ** 2)
                dur = 1.0 * st
            else:
                tgt, dur = self.it, 1.5 * st
            if "shield" not in tgt.buffs:
                tgt.frozen = max(tgt.frozen, dur)
                self.burst(tgt.cx, tgt.cy, (170, 240, 255), 20)
        self.burst(p.cx, p.cy, PICKUP_TYPES[kind][0], 16)

    def update(self, dt, keys):
        dt = min(dt, 1 / 30)
        if self.over:
            return
        if self.intro > 0:
            self.intro -= dt
            keys = None
        else:
            self.elapsed += dt
            self.time_left -= dt
            self.it.hold += dt
            self.it.cur_hold += dt
        for p in self.players:
            p.step(self, dt, keys)
        if self.intro <= 0:
            # tagging
            it = self.it
            for q in self.players:
                if q is it or q.tag_immune > 0:
                    continue
                if (q.cx - it.cx) ** 2 + (q.cy - it.cy) ** 2 < 24 ** 2:
                    if "shield" in q.buffs:
                        self.burst(q.cx, q.cy, (255, 215, 60), 8)
                        q.tag_immune = 0.2
                        continue
                    self.transfer(q)
                    break
            # pickups
            if self.S["buffs_on"]:
                self.spawn_t -= dt
                if self.spawn_t <= 0 and len(self.pickups) < int(self.S["max_pickups"]):
                    self.spawn_pickup()
                    self.spawn_t = self.S["buff_spawn"]
                for pk in self.pickups[:]:
                    pk["t"] += dt
                    for p in self.players:
                        if (p.cx - pk["x"]) ** 2 + (p.cy - pk["y"]) ** 2 < 26 ** 2:
                            self.apply_pickup(p, pk["kind"])
                            self.pickups.remove(pk)
                            break
        # particles
        alive_parts = []
        for pt in self.parts:
            pt[4] -= dt
            if pt[4] <= 0:
                continue
            pt[0] += pt[2] * dt
            pt[1] += pt[3] * dt
            pt[3] += 500 * dt
            alive_parts.append(pt)
        self.parts = alive_parts
        self.tag_flash = max(0, self.tag_flash - dt)
        self.update_camera(dt)
        if self.time_left <= 0:
            self.time_left = 0
            self.over = True
            for p in self.players:
                p.best_hold = max(p.best_hold, p.cur_hold)


# --------------------------------------------------------------------------
#  App (menus, drawing, persistence)
# --------------------------------------------------------------------------
class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("TAG  -  2 / 3 / 4 players")
        self.screen = pygame.display.set_mode((W, H), pygame.SCALED | pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.data = load_data()
        apply_dash_keys(self.data["dash_keys"])
        self.rebind = None            # slot whose dash key is waiting for a key press
        self.sprites = {}
        self.state = "menu"
        self.fonts = {}
        self.click = False
        self.mouse = (0, 0)
        self.mouse_down = False
        self.drag = None
        self.msg = ""
        self.msg_t = 0.0
        self.game = None
        self.result = None
        self.scroll = 0
        self.max_scroll = 0
        self.sec_open = {"Leaderboard": True}
        self.newname = ""
        self.new_slot = 0
        self.menu_t = 0.0
        self.menu_sky = None
        self.t_acc = 0.0
        self.skin_profile = next(iter(self.data["profiles"]))
        self.game_view = pygame.Surface((math.ceil(W / ZOOM_MIN), math.ceil(H / ZOOM_MIN)))
        self.scaled_view = pygame.Surface((W, H))
        self.motion_frame = None
        self.motion_frame_valid = False

    # ---- sprites
    def sprite(self, slot, w=SPR_W, flip=False, skin="classic"):
        """Player sprite scaled to width w (cached). The artwork faces left; flip=True faces right."""
        if skin not in SKIN_STYLES:
            skin = "classic"
        k = (slot, w, flip, skin)
        if k not in self.sprites:
            base = self.sprites.get(("raw", slot))
            if base is None:
                base = pygame.image.load(io.BytesIO(base64.b64decode("".join(SPRITE_B64[slot]))), "x.png").convert_alpha()
                self.sprites[("raw", slot)] = base
            if skin != "classic":
                base = base.copy()
                if skin == "durag":
                    cloth = ((35, 155, 225), (220, 65, 92), (145, 85, 220), (235, 155, 40))[slot % 4]
                    shadow = (24, 27, 47)
                    pygame.draw.polygon(base, shadow, [(5, 21), (55, 21), (65, 25), (61, 33), (9, 33)])
                    pygame.draw.polygon(base, cloth, [(8, 22), (54, 22), (61, 26), (57, 30), (10, 30)])
                    pygame.draw.polygon(base, shadow, [(53, 23), (65, 25), (70, 42), (63, 39), (58, 31)])
                    pygame.draw.polygon(base, cloth, [(56, 25), (63, 27), (67, 38), (62, 35), (58, 30)])
                    highlight = tuple(min(255, c + 65) for c in cloth)
                    pygame.draw.line(base, highlight, (13, 23), (51, 23), 1)
                    pygame.draw.line(base, shadow, (14, 29), (52, 29), 1)
                    pygame.draw.circle(base, highlight, (58, 26), 2)
                elif skin == "crown":
                    gold = (255, 195, 55)
                    pygame.draw.polygon(base, (67, 40, 76), [(15, 22), (18, 8), (29, 17), (37, 4),
                                                              (47, 17), (57, 9), (56, 23)])
                    pygame.draw.polygon(base, gold, [(19, 20), (21, 12), (30, 19), (37, 8),
                                                     (46, 19), (54, 13), (52, 21)])
                    pygame.draw.rect(base, (255, 226, 130), (20, 20, 33, 4))
                    pygame.draw.circle(base, (255, 255, 235), (37, 13), 2)
                elif skin == "headphones":
                    pygame.draw.arc(base, (28, 34, 57), (9, 11, 53, 46), math.pi, math.tau, 5)
                    pygame.draw.circle(base, (28, 34, 57), (9, 34), 8)
                    pygame.draw.circle(base, (28, 34, 57), (62, 34), 8)
                    pygame.draw.circle(base, (125, 100, 245), (9, 34), 5)
                    pygame.draw.circle(base, (125, 100, 245), (62, 34), 5)
                    pygame.draw.circle(base, (215, 205, 255), (9, 34), 2)
                    pygame.draw.circle(base, (215, 205, 255), (62, 34), 2)
                elif skin == "shades":
                    pygame.draw.polygon(base, (20, 29, 53), [(10, 34), (32, 35), (34, 43), (28, 47),
                                                             (14, 45)])
                    pygame.draw.polygon(base, (20, 29, 53), [(37, 35), (60, 34), (57, 45), (43, 47),
                                                             (37, 43)])
                    pygame.draw.line(base, (20, 29, 53), (32, 37), (39, 37), 3)
                    pygame.draw.line(base, (125, 230, 255), (15, 37), (27, 38), 2)
                    pygame.draw.line(base, (125, 230, 255), (43, 38), (55, 37), 2)
            img = pygame.transform.smoothscale(base, (w, max(1, int(w * base.get_height() / base.get_width()))))
            self.sprites[k] = pygame.transform.flip(img, True, False) if flip else img
        return self.sprites[k]

    def icon(self, slot, center, w=40, skin="classic"):
        img = self.sprite(slot, w, skin=skin)
        self.screen.blit(img, img.get_rect(center=center))

    # ---- drawing helpers
    def font(self, size, bold=True):
        k = (size, bold)
        if k not in self.fonts:
            self.fonts[k] = pygame.font.SysFont("segoeui,arial,helvetica,dejavusans", size, bold=bold)
        return self.fonts[k]

    def t(self, s, size, pos, color=(255, 255, 255), anchor="topleft", shadow=False, bold=True):
        f = self.font(size, bold)
        surf = f.render(str(s), True, color)
        r = surf.get_rect(**{anchor: pos})
        if shadow:
            sh = f.render(str(s), True, (0, 0, 0))
            sh.set_alpha(110)
            self.screen.blit(sh, r.move(2, 3))
        self.screen.blit(surf, r)
        return r

    def button(self, rect, label, size=26, base=(60, 72, 120), enabled=True):
        rect = pygame.Rect(rect)
        hot = enabled and rect.collidepoint(self.mouse)
        col = (70, 70, 85) if not enabled else tuple(min(255, c + 40) for c in base) if hot else base
        pygame.draw.rect(self.screen, col, rect, border_radius=12)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, 2, border_radius=12)
        self.t(label, size, rect.center, (255, 255, 255) if enabled else (150, 150, 160), "center")
        if hot and self.click:
            self.click = False
            return True
        return False

    def slider(self, sid, rect, val, lo, hi, step):
        rect = pygame.Rect(rect)
        pygame.draw.rect(self.screen, (30, 36, 70), rect, border_radius=6)
        tfrac = (val - lo) / (hi - lo)
        fill = pygame.Rect(rect.x, rect.y, int(rect.w * tfrac), rect.h)
        pygame.draw.rect(self.screen, (90, 200, 255), fill, border_radius=6)
        pygame.draw.circle(self.screen, (255, 255, 255), (rect.x + int(rect.w * tfrac), rect.centery), 11)
        if self.click and rect.inflate(20, 24).collidepoint(self.mouse):
            self.drag = sid
            self.click = False
        if self.drag == sid:
            if self.mouse_down:
                tf = clamp((self.mouse[0] - rect.x) / rect.w, 0, 1)
                v = lo + tf * (hi - lo)
                v = round(v / step) * step
                val = clamp(round(v, 4), lo, hi)
            else:
                self.drag = None
        return val

    def toast(self, s):
        self.msg, self.msg_t = s, 3.0

    def menu_bg(self, dt):
        self.menu_t += dt
        if self.menu_sky is None:
            T = THEMES["forest"]
            self.menu_sky = pygame.Surface((W, H))
            for yy in range(H):
                tt = yy / H
                c = tuple(int(T["sky_top"][i] * (1 - tt) + T["sky_bot"][i] * tt) for i in range(3))
                pygame.draw.line(self.menu_sky, c, (0, yy), (W, yy))
        self.screen.blit(self.menu_sky, (0, 0))
        rng = random.Random(4)
        menu_theme = dict(plat=(72, 111, 158), top=(119, 181, 207))
        for i in range(9):
            y = 90 + i * 75
            w = rng.randint(220, 520)
            x = ((rng.randint(0, W) + self.menu_t * (20 + 8 * i) * (1 if i % 2 else -1)) % (W + w)) - w
            self.platform_rect(x, y, w, menu_theme)

    def platform_rect(self, x, y, w, T):
        pygame.draw.rect(self.screen, T["plat"], (x, y, w, 9), border_radius=3)
        pygame.draw.rect(self.screen, T["top"], (x, y - 1, w, 4), border_radius=2)

    # ---- profile helpers
    def profile(self, name):
        return self.data["profiles"][name]

    def add_profile(self, name):
        n = len(self.data["profiles"])
        self.data["profiles"][name] = new_profile(n % 4)

    def cycle_profile(self, slot, d):
        names = list(self.data["profiles"])
        taken = {self.data["slots"][i] for i in range(4) if i != slot and self.data["enabled"][i]}
        cur = self.data["slots"][slot]
        idx = names.index(cur) if cur in names else -1
        for _ in range(len(names)):
            idx = (idx + d) % len(names)
            if names[idx] not in taken:
                self.data["slots"][slot] = names[idx]
                return

    def open_skin_studio(self):
        names = list(self.data["profiles"])
        self.skin_profile = next(
            (self.data["slots"][i] for i in range(4)
             if self.data["enabled"][i] and self.data["slots"][i] in self.data["profiles"]),
            names[0],
        )
        self.state = "skins"

    def cycle_skin_profile(self, direction):
        names = list(self.data["profiles"])
        if not names:
            return
        try:
            index = names.index(self.skin_profile)
        except ValueError:
            index = 0
        self.skin_profile = names[(index + direction) % len(names)]

    def set_profile_skin(self, skin):
        if skin not in SKIN_STYLES:
            return
        self.profile(self.skin_profile)["skin"] = skin
        save_data(self.data)

    # ---- main loop
    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.click = False
            wheel = 0
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    save_data(self.data)
                    pygame.quit()
                    sys.exit()
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    self.click = True
                elif e.type == pygame.MOUSEWHEEL:
                    wheel = e.y
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_F11:
                        pygame.display.toggle_fullscreen()
                    self.on_key(e)
            self.mouse = pygame.mouse.get_pos()
            self.mouse_down = pygame.mouse.get_pressed()[0]
            if wheel and self.state == "stats":
                self.scroll = clamp(self.scroll - wheel * 55, 0, self.max_scroll)
            getattr(self, "s_" + self.state)(dt)
            if self.msg_t > 0:
                self.msg_t -= dt
                self.t(self.msg, 24, (W // 2, H - 30), (255, 230, 120), "center", True)
            pygame.display.flip()

    def try_rebind(self, e):
        slot = self.rebind
        if e.key == pygame.K_ESCAPE:
            self.rebind = None
            self.toast("Dash key unchanged")
            return
        if e.key in RESERVED_KEYS:
            self.toast("%s can't be used" % key_label(e.key))
            return
        for j, c in enumerate(CONTROLS):
            used = (c["left"], c["right"], c["jump"]) if j != slot else (c["left"], c["right"], c["jump"])
            if e.key in used:
                self.toast("%s is already a move key for %s" % (key_label(e.key), COLOR_NAMES[j]))
                return
            if j != slot and e.key == c["act"]:
                self.toast("%s is already %s's dash key" % (key_label(e.key), COLOR_NAMES[j]))
                return
        CONTROLS[slot]["act"] = e.key
        self.data["dash_keys"][slot] = pygame.key.name(e.key)
        save_data(self.data)
        self.toast("%s dash key set to %s" % (COLOR_NAMES[slot], key_label(e.key)))
        self.rebind = None

    def dash_button(self, rect, slot, size=22):
        waiting = self.rebind == slot
        label = "press a key..." if waiting else "Dash: " + key_label(CONTROLS[slot]["act"])
        base = (190, 120, 30) if waiting else (60, 72, 120)
        if self.button(rect, label, size, base):
            self.rebind = None if waiting else slot

    def on_key(self, e):
        if self.state == "skins":
            if e.key == pygame.K_ESCAPE:
                save_data(self.data)
                self.state = "menu"
            elif e.key in (pygame.K_LEFT, pygame.K_RIGHT):
                current = self.profile(self.skin_profile).get("skin", "classic")
                index = SKIN_STYLES.index(current) if current in SKIN_STYLES else 0
                direction = 1 if e.key == pygame.K_RIGHT else -1
                self.set_profile_skin(SKIN_STYLES[(index + direction) % len(SKIN_STYLES)])
            elif e.key in (pygame.K_UP, pygame.K_DOWN):
                self.cycle_skin_profile(1 if e.key == pygame.K_DOWN else -1)
            return
        if self.rebind is not None and self.state in ("players", "settings"):
            self.try_rebind(e)
            return
        if self.state == "newprofile":
            if e.key == pygame.K_RETURN:
                nm = self.newname.strip()
                if not nm:
                    return
                if nm in self.data["profiles"]:
                    self.toast("That name already exists")
                    return
                self.add_profile(nm)
                self.data["slots"][self.new_slot] = nm
                save_data(self.data)
                self.state = "players"
            elif e.key == pygame.K_ESCAPE:
                self.state = "players"
            elif e.key == pygame.K_BACKSPACE:
                self.newname = self.newname[:-1]
            elif e.unicode and e.unicode.isprintable() and len(self.newname) < 14:
                self.newname += e.unicode
        elif self.state == "game" and e.key == pygame.K_ESCAPE:
            self.state = "paused"
        elif self.state == "paused" and e.key == pygame.K_ESCAPE:
            self.state = "game"
        elif self.state in ("players", "settings", "stats") and e.key == pygame.K_ESCAPE:
            self.rebind = None
            save_data(self.data)
            self.state = "menu"

    # ---- screens
    def s_menu(self, dt):
        self.menu_bg(dt)
        bob = math.sin(self.menu_t * 2) * 6
        self.t("TAG", 150, (W // 2, 120 + bob), (255, 255, 255), "center", True)
        self.t("no winners  -  only not-losers", 28, (W // 2, 205), (255, 255, 255), "center", True)
        if self.button((W // 2 - 210, 260, 420, 62), "PLAY", 32, (40, 160, 90)):
            self.start_game()
        left, right, width = W // 2 - 290, W // 2 + 10, 280
        if self.button((left, 338, width, 54), "PLAYERS & CONTROLS", 22):
            self.state = "players"
        if self.button((right, 338, width, 54), "SKIN STUDIO", 24, (105, 75, 175)):
            self.open_skin_studio()
        if self.button((left, 404, width, 50), "SETTINGS", 24):
            self.state = "settings"
        if self.button((right, 404, width, 50), "STATS", 24):
            self.scroll = 0
            self.state = "stats"
        if self.button((W // 2 - 130, 466, 260, 48), "QUIT", 23, (130, 50, 60)):
            save_data(self.data)
            pygame.quit()
            sys.exit()
        # roster preview
        for i in range(4):
            on = self.data["enabled"][i] and self.data["slots"][i]
            px = W // 2 - 300 + i * 150
            if on:
                self.icon(i, (px, 636), 40, self.profile(self.data["slots"][i]).get("skin", "classic"))
            else:
                pygame.draw.circle(self.screen, (120, 130, 150), (px, 640), 14)
            if on:
                nm = self.data["slots"][i]
                self.t(nm, 18, (px, 662), (255, 255, 255), "midtop", True)
                self.t("%d" % round(self.profile(nm)["rating"]), 18, (px, 682), (255, 255, 255), "midtop", True)

    def s_skins(self, dt):
        self.menu_bg(dt)
        panel = pygame.Surface((1000, 555), pygame.SRCALPHA)
        pygame.draw.rect(panel, (12, 19, 46, 244), panel.get_rect(), border_radius=28)
        pygame.draw.rect(panel, (160, 190, 255, 100), panel.get_rect(), 2, border_radius=28)
        self.screen.blit(panel, (140, 62))
        self.t("SKIN STUDIO", 42, (W // 2, 86), anchor="center", shadow=True)
        self.t("Choose a look for your profile", 19, (W // 2, 126), (190, 205, 235),
               "center", bold=False)

        names = list(self.data["profiles"])
        if not names:
            self.t("Create a profile first to customize a skin.", 24,
                   (W // 2, 340), anchor="center")
            if self.button((W // 2 - 110, 630, 220, 48), "BACK", 22):
                self.state = "menu"
            return
        if self.skin_profile not in self.data["profiles"]:
            self.skin_profile = names[0]
        profile = self.profile(self.skin_profile)
        skin = profile.get("skin", "classic")
        if skin not in SKIN_STYLES:
            skin = "classic"
        skin_index = SKIN_STYLES.index(skin)
        profile_index = names.index(self.skin_profile)
        if self.button((430, 145, 52, 42), "<", 26):
            self.cycle_skin_profile(-1)
            profile = self.profile(self.skin_profile)
            profile_index = names.index(self.skin_profile)
            skin = profile.get("skin", "classic")
            skin_index = SKIN_STYLES.index(skin) if skin in SKIN_STYLES else 0
        self.t("%s  ·  PROFILE %d / %d" %
               (self.skin_profile.upper(), profile_index + 1, len(names)), 19,
               (W // 2, 156), (220, 230, 255), "center")
        if self.button((798, 145, 52, 42), ">", 26):
            self.cycle_skin_profile(1)
            profile = self.profile(self.skin_profile)
            profile_index = names.index(self.skin_profile)
            skin = profile.get("skin", "classic")
            skin_index = SKIN_STYLES.index(skin) if skin in SKIN_STYLES else 0

        accent = (125, 185, 255) if skin == "classic" else (190, 145, 255)
        pygame.draw.circle(self.screen, (36, 48, 83), (W // 2, 334), 142)
        pygame.draw.circle(self.screen, accent, (W // 2, 334), 142, 2)
        pygame.draw.ellipse(self.screen, (8, 12, 30), (W // 2 - 96, 439, 192, 22))
        slot = profile.get("color_idx", 0) % 4
        avatar = self.sprite(slot, 250, skin=skin)
        self.screen.blit(avatar, avatar.get_rect(center=(W // 2, 325 + int(math.sin(self.menu_t * 2) * 4))))
        if self.button((282, 315, 68, 76), "<", 46, (45, 59, 100)):
            self.set_profile_skin(SKIN_STYLES[(skin_index - 1) % len(SKIN_STYLES)])
        if self.button((930, 315, 68, 76), ">", 46, (45, 59, 100)):
            self.set_profile_skin(SKIN_STYLES[(skin_index + 1) % len(SKIN_STYLES)])

        skin = self.profile(self.skin_profile).get("skin", "classic")
        skin_index = SKIN_STYLES.index(skin) if skin in SKIN_STYLES else 0
        self.t(SKIN_LABELS[skin].upper(), 28, (W // 2, 474), (255, 255, 255), "center", True)
        self.t("%d cosmetics  ·  use ← → to browse" % len(SKIN_STYLES), 16,
               (W // 2, 507), (185, 198, 226), "center", bold=False)

        chip_width, chip_gap = 142, 12
        chip_x = (W - (chip_width * len(SKIN_STYLES) + chip_gap * (len(SKIN_STYLES) - 1))) // 2
        for index, option in enumerate(SKIN_STYLES):
            rect = (chip_x + index * (chip_width + chip_gap), 542, chip_width, 44)
            if index == skin_index:
                pygame.draw.rect(self.screen, (112, 80, 190), rect, border_radius=12)
                pygame.draw.rect(self.screen, (220, 205, 255), rect, 2, border_radius=12)
                self.t(SKIN_LABELS[option].upper(), 15, pygame.Rect(rect).center, anchor="center")
            elif self.button(rect, SKIN_LABELS[option].upper(), 15, (43, 53, 86)):
                self.set_profile_skin(option)
        if self.button((W // 2 - 110, 630, 220, 48), "BACK", 22):
            save_data(self.data)
            self.state = "menu"
        self.t("↑ ↓ switch profile", 15, (W // 2, 605), (180, 193, 221),
               "center", bold=False)

    def s_players(self, dt):
        self.menu_bg(dt)
        self.t("PLAYERS & CONTROLS", 44, (W // 2, 46), anchor="center", shadow=True)
        self.t("Each control scheme is bound to a profile. Click a Dash button, then press the key you want.",
               20, (W // 2, 90), anchor="center", shadow=True, bold=False)
        for i in range(4):
            y = 125 + i * 108
            panel = pygame.Rect(60, y, W - 120, 96)
            s = pygame.Surface(panel.size, pygame.SRCALPHA)
            pygame.draw.rect(s, (15, 20, 50, 190), s.get_rect(), border_radius=16)
            self.screen.blit(s, panel)
            cy = y + 48
            nm = self.data["slots"][i]
            skin = self.profile(nm).get("skin", "classic") if nm else "classic"
            self.icon(i, (panel.x + 46, cy - 4), 52, skin)
            self.t(COLOR_NAMES[i], 26, (panel.x + 92, y + 16))
            self.t("Move: " + CONTROLS[i]["move"], 19, (panel.x + 92, y + 54), (200, 210, 235), bold=False)
            on = self.data["enabled"][i]
            if self.button((panel.x + 250, cy - 24, 84, 48), "ON" if on else "OFF", 24,
                           (40, 150, 90) if on else (110, 60, 70)):
                self.data["enabled"][i] = not on
            self.dash_button((panel.x + 350, cy - 24, 200, 48), i, 22)
            if self.button((panel.x + 580, cy - 24, 44, 48), "<", 26):
                self.cycle_profile(i, -1)
            self.t(nm or "(none)", 28, (panel.x + 745, y + 14), anchor="midtop", shadow=True)
            if nm:
                p = self.profile(nm)
                self.t("Rating %d  |  %d matches" % (round(p["rating"]), p["matches"]), 18,
                       (panel.x + 745, y + 54), (200, 210, 235), "midtop", bold=False)
            if self.button((panel.x + 866, cy - 24, 44, 48), ">", 26):
                self.cycle_profile(i, 1)
            if self.button((panel.x + 930, cy - 24, 200, 48), "+ New profile", 22):
                self.new_slot, self.newname, self.state = i, "", "newprofile"
                self.rebind = None
        if self.button((W // 2 - 110, 662, 220, 46), "BACK", 24):
            self.rebind = None
            save_data(self.data)
            self.state = "menu"

    def s_newprofile(self, dt):
        self.menu_bg(dt)
        self.t("NEW PROFILE for %s controls" % COLOR_NAMES[self.new_slot], 36, (W // 2, 230),
               anchor="center", shadow=True)
        box = pygame.Rect(W // 2 - 220, 290, 440, 70)
        pygame.draw.rect(self.screen, (15, 20, 50), box, border_radius=14)
        pygame.draw.rect(self.screen, (255, 255, 255), box, 2, border_radius=14)
        cur = "|" if int(self.menu_t * 2) % 2 == 0 else ""
        self.t(self.newname + cur, 38, box.center, anchor="center")
        self.t("Type a name, press Enter to create (Esc to cancel)", 22, (W // 2, 390), anchor="center",
               shadow=True, bold=False)

    def s_settings(self, dt):
        self.menu_bg(dt)
        S = self.data["settings"]
        self.t("SETTINGS", 44, (W // 2, 40), anchor="center", shadow=True)

        def panel(rect):
            s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
            pygame.draw.rect(s, (15, 20, 50, 190), s.get_rect(), border_radius=18)
            self.screen.blit(s, (rect[0], rect[1]))

        # 1) sliders: 3 columns x 5 rows
        panel((40, 76, W - 80, 424))
        COLW, SLW = 390, 340
        for idx, (key, label, lo, hi, step, default, fmt) in enumerate(SETTINGS_DEF):
            col, row = idx // 5, idx % 5
            x, y = 75 + col * COLW, 96 + row * 80
            self.t(label, 21, (x, y))
            val = S[key]
            self.t(fmt.format(val), 21, (x + SLW, y), (130, 220, 255), "topright")
            S[key] = self.slider(key, (x, y + 40, SLW, 10), val, lo, hi, step)
            if isinstance(default, int):
                S[key] = int(round(S[key]))
        # 2) dash keys
        panel((40, 512, W - 80, 82))
        self.t("DASH KEYS", 20, (75, 524), (170, 190, 230))
        self.t("click one, then press a key", 16, (75, 548), (170, 190, 230), bold=False)
        for i in range(4):
            bx = 300 + i * 232
            pygame.draw.rect(self.screen, COLORS[i], (bx, 530, 6, 48), border_radius=3)
            self.icon(i, (bx + 30, 554), 34)
            self.dash_button((bx + 54, 530, 150, 48), i, 20)
        # 3) toggles + back
        on = S["buffs_on"]
        bw, gap = 200, 20
        x0 = (W - (5 * bw + 4 * gap)) // 2
        by = 616
        if self.button((x0, by, bw, 50), "Power-ups: " + ("ON" if on else "OFF"), 22,
                       (40, 150, 90) if on else (110, 60, 70)):
            S["buffs_on"] = not on
        opts = ["random", "forest", "desert", "taiga"]
        if self.button((x0 + (bw + gap), by, bw, 50), "Map: " + S["theme"].upper(), 22):
            S["theme"] = opts[(opts.index(S["theme"]) + 1) % 4]
        blur = int(clamp(S.get("motion_blur", 0), 0, 2))
        blur_labels = ("OFF", "LOW", "HIGH")
        if self.button((x0 + 2 * (bw + gap), by, bw, 50),
                       "Motion blur: " + blur_labels[blur], 20):
            S["motion_blur"] = (blur + 1) % len(blur_labels)
            self.motion_frame_valid = False
        if self.button((x0 + 3 * (bw + gap), by, bw, 50), "Reset defaults", 20, (130, 80, 50)):
            keep = S["theme"]
            S.update(DEFAULT_SETTINGS)
            S["theme"] = keep
            self.motion_frame_valid = False
            self.data["dash_keys"] = list(DEFAULT_DASH_KEYS)
            apply_dash_keys(self.data["dash_keys"])
        if self.button((x0 + 4 * (bw + gap), by, bw, 50), "BACK", 24):
            self.rebind = None
            save_data(self.data)
            self.state = "menu"

    # ---- game flow
    def start_game(self):
        roster = []
        names = set()
        for i in range(4):
            if self.data["enabled"][i]:
                nm = self.data["slots"][i]
                if not nm:
                    self.toast("%s controls have no profile assigned" % COLOR_NAMES[i])
                    return
                if nm in names:
                    self.toast("Profile '%s' is used twice" % nm)
                    return
                names.add(nm)
                roster.append((i, nm))
        if len(roster) < 2:
            self.toast("Enable at least 2 players")
            return
        self.launch(roster)

    def launch(self, roster):
        S = self.data["settings"]
        theme = S["theme"] if S["theme"] in THEMES else random.choice(list(THEMES))
        self.roster = roster
        self.game = Game(S, roster, theme, random.randrange(1 << 30))
        self.motion_frame_valid = False
        self.state = "game"

    def s_game(self, dt):
        g = self.game
        g.update(dt, pygame.key.get_pressed())
        self.draw_game(g)
        if g.over:
            self.result = self.finish_match(g)
            self.state = "result"

    def s_paused(self, dt):
        self.draw_game(self.game)
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        s.fill((0, 0, 20, 160))
        self.screen.blit(s, (0, 0))
        self.t("PAUSED", 80, (W // 2, 230), anchor="center", shadow=True)
        if self.button((W // 2 - 160, 320, 320, 56), "RESUME", 28, (40, 160, 90)):
            self.state = "game"
        if self.button((W // 2 - 160, 392, 320, 56), "QUIT TO MENU (no rating change)", 20, (130, 50, 60)):
            self.state = "menu"

    # ---- ratings / stats
    def finish_match(self, g):
        P = self.data["profiles"]
        names = [p.name for p in g.players]
        n = len(names)
        loser = g.it.name
        R = {nm: P[nm]["rating"] for nm in names}
        holds = {p.name: p.hold for p in g.players}
        mean_hold = (sum(holds.values()) / n) or 1e-9
        K = 32.0
        delta = {nm: 0.0 for nm in names}
        for nm in names:
            if nm == loser:
                continue
            E = 1 / (1 + 10 ** ((R[loser] - R[nm]) / 400))      # expected to stay safe vs the loser
            perf = clamp(1.3 - 0.3 * holds[nm] / mean_hold, 0.7, 1.3)  # holding less = slightly more credit
            delta[nm] = K * (1 - E) * perf / (n - 1)
        delta[loser] = -sum(delta.values())
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        rec = self.data["records"]["longest_hold"]
        for p in g.players:
            pr = P[p.name]
            new_r = max(100.0, pr["rating"] + delta[p.name])
            delta[p.name] = new_r - pr["rating"]
            pr["rating"] = new_r
            pr["peak"] = max(pr["peak"], new_r)
            pr["history"] = (pr["history"] + [round(new_r, 1)])[-200:]
            pr["matches"] += 1
            pr["time_played"] += g.elapsed
            pr["total_hold"] += p.hold
            pr["tags_made"] += p.tags_made
            pr["times_tagged"] += p.times_tagged
            pr["pickups"] += p.pickups
            for v, c in p.tagged.items():
                pr["tagged"][v] = pr["tagged"].get(v, 0) + c
            if p.best_hold > pr["longest_hold"]:
                pr["longest_hold"], pr["longest_hold_date"] = p.best_hold, now
            if p.best_hold > rec["secs"]:
                rec.update(name=p.name, secs=p.best_hold, date=now)
            if p.name == loser:
                pr["losses"] += 1
                pr["streak"] = 0
            else:
                pr["survived"] += 1
                pr["streak"] += 1
                pr["best_streak"] = max(pr["best_streak"], pr["streak"])
        self.data["history"].append(dict(
            date=now, duration=round(g.elapsed, 1), players=names, loser=loser, map=g.level.theme,
            holds={p.name: round(p.hold, 1) for p in g.players},
            best={p.name: round(p.best_hold, 1) for p in g.players},
            delta={k: round(v, 1) for k, v in delta.items()}))
        self.data["history"] = self.data["history"][-300:]
        save_data(self.data)
        return dict(loser=loser, delta=delta, players=g.players, time=g.elapsed)

    def s_result(self, dt):
        self.draw_game(self.game)
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        s.fill((10, 10, 40, 200))
        self.screen.blit(s, (0, 0))
        r = self.result
        self.t("TIME!", 70, (W // 2, 70), anchor="center", shadow=True)
        self.t("%s is the loser" % r["loser"], 46, (W // 2, 140), (255, 110, 110), "center", True)
        self.t("everyone else is safe", 24, (W // 2, 182), anchor="center", bold=False)
        hdr_y = 230
        cols = [240, 560, 740, 900, 1040]
        for x, h in zip(cols, ["PLAYER", "TIME AS IT", "LONGEST HOLD", "TAGS MADE", "RATING"]):
            self.t(h, 20, (x, hdr_y), (170, 190, 230))
        rows = sorted(r["players"], key=lambda p: -p.hold)
        for i, p in enumerate(rows):
            y = hdr_y + 40 + i * 52
            lose = p.name == r["loser"]
            self.icon(p.slot, (cols[0] - 26, y + 14), 36,
                      self.profile(p.name).get("skin", "classic"))
            self.t(p.name + ("   (LOSER)" if lose else "   safe"), 26, (cols[0], y),
                   (255, 130, 130) if lose else (255, 255, 255))
            self.t(fmt_time(p.hold), 26, (cols[1], y))
            self.t(fmt_time(p.best_hold), 26, (cols[2], y))
            self.t(str(p.tags_made), 26, (cols[3], y))
            d = r["delta"][p.name]
            self.t("%d  (%+.1f)" % (round(self.profile(p.name)["rating"]), d), 26, (cols[4], y),
                   (130, 255, 150) if d >= 0 else (255, 130, 130))
        by = 540
        if self.button((W // 2 - 340, by, 200, 56), "REMATCH", 26, (40, 160, 90)):
            self.launch(self.roster)
        if self.button((W // 2 - 100, by, 200, 56), "STATS", 26):
            self.scroll = 0
            self.state = "stats"
        if self.button((W // 2 + 140, by, 200, 56), "MENU", 26):
            self.state = "menu"

    # ---- stats screen (collapsible sections)
    def s_stats(self, dt):
        self.menu_bg(dt)
        self.t("STATS", 44, (W // 2, 40), anchor="center", shadow=True)
        self.t("click a heading to expand / collapse   |   mouse wheel scrolls", 18, (W // 2, 78),
               anchor="center", shadow=True, bold=False)
        area = pygame.Rect(50, 100, W - 100, H - 165)
        s = pygame.Surface(area.size, pygame.SRCALPHA)
        pygame.draw.rect(s, (12, 16, 44, 215), s.get_rect(), border_radius=16)
        self.screen.blit(s, area)
        self.screen.set_clip(area.inflate(-8, -8))
        y = area.y + 10 - self.scroll
        start_y = y
        sections = [("Leaderboard", self.sec_leaderboard), ("Longest holds & time as 'it'", self.sec_holds),
                    ("Tagging", self.sec_tags), ("Rivalries (who tags who)", self.sec_rivals),
                    ("Rating history", self.sec_chart), ("Recent matches", self.sec_recent)]
        for title, fn in sections:
            hr = pygame.Rect(area.x + 14, y, area.w - 28, 38)
            hot = hr.collidepoint(self.mouse) and area.collidepoint(self.mouse)
            pygame.draw.rect(self.screen, (70, 90, 160) if hot else (45, 58, 115), hr, border_radius=10)
            op = self.sec_open.get(title, False)
            cx, cy = hr.x + 22, hr.centery
            pts = [(cx - 7, cy - 5), (cx + 7, cy - 5), (cx, cy + 6)] if op else [(cx - 5, cy - 8), (cx - 5, cy + 8), (cx + 6, cy)]
            pygame.draw.polygon(self.screen, (255, 255, 255), pts)
            self.t(title, 24, (hr.x + 44, hr.y + 5))
            if hot and self.click:
                self.sec_open[title] = not op
                self.click = False
            y += 46
            if self.sec_open.get(title, False):
                y = fn(area.x + 30, y) + 10
        self.screen.set_clip(None)
        self.max_scroll = max(0, int(y - start_y - area.h + 30))
        self.scroll = clamp(self.scroll, 0, self.max_scroll)
        if self.button((W // 2 - 110, H - 52, 220, 42), "BACK", 22):
            save_data(self.data)
            self.state = "menu"

    def table(self, x, y, heads, widths, rows, colors=None):
        cx = x
        for h, w in zip(heads, widths):
            self.t(h, 18, (cx, y), (150, 175, 230))
            cx += w
        y += 28
        for ri, row in enumerate(rows):
            cx = x
            for ci, (cell, w) in enumerate(zip(row, widths)):
                col = (colors[ri][ci] if colors and colors[ri] and colors[ri][ci] else (240, 244, 255))
                self.t(cell, 20, (cx, y), col, bold=False)
                cx += w
            y += 28
        return y

    def ranked(self):
        return sorted(self.data["profiles"].items(), key=lambda kv: -kv[1]["rating"])

    def sec_leaderboard(self, x, y):
        rows, colors = [], []
        for i, (nm, p) in enumerate(self.ranked()):
            ctl = ""
            col = None
            for s in range(4):
                if self.data["slots"][s] == nm:
                    ctl = COLOR_NAMES[s] + " (" + ctl_label(s).replace("  ", " ") + ")"
                    col = COLORS[s]
            surv = 100.0 * p["survived"] / p["matches"] if p["matches"] else 0
            rows.append([str(i + 1), nm, "%d" % round(p["rating"]), "%d" % round(p["peak"]),
                         str(p["matches"]), str(p["losses"]), "%.0f%%" % surv,
                         "%d" % p["streak"], ctl])
            colors.append([None, col, None, None, None, None, None, None, col])
        return self.table(x, y, ["#", "Player", "Rating", "Peak", "Matches", "Lost", "Safe %", "Safe streak", "Controls"],
                          [40, 190, 90, 90, 100, 80, 90, 120, 300], rows, colors)

    def sec_holds(self, x, y):
        rec = self.data["records"]["longest_hold"]
        if rec["secs"] > 0:
            self.t("All-time longest hold: %s  -  %s  (%s)" % (rec["name"], fmt_time(rec["secs"]), rec["date"]),
                   22, (x, y), (255, 220, 120))
        else:
            self.t("No matches played yet.", 22, (x, y), (200, 210, 235), bold=False)
        y += 36
        rows = []
        for nm, p in sorted(self.data["profiles"].items(), key=lambda kv: -kv[1]["longest_hold"]):
            m = p["matches"]
            share = 100.0 * p["total_hold"] / p["time_played"] if p["time_played"] else 0
            rows.append([nm, fmt_time(p["longest_hold"]), fmt_time(p["total_hold"]),
                         fmt_time(p["total_hold"] / m) if m else "-", "%.0f%%" % share])
        return self.table(x, y, ["Player", "Longest single hold", "Total as 'it'", "Avg per match", "% of time as 'it'"],
                          [190, 220, 180, 180, 200], rows)

    def sec_tags(self, x, y):
        rows = []
        for nm, p in sorted(self.data["profiles"].items(), key=lambda kv: -kv[1]["tags_made"]):
            ratio = p["tags_made"] / p["times_tagged"] if p["times_tagged"] else float(p["tags_made"])
            rows.append([nm, str(p["tags_made"]), str(p["times_tagged"]), "%.2f" % ratio, str(p["pickups"]),
                         str(p["best_streak"])])
        return self.table(x, y, ["Player", "Tags made", "Times tagged", "Tag ratio", "Power-ups grabbed", "Best safe streak"],
                          [190, 130, 150, 120, 200, 180], rows)

    def sec_rivals(self, x, y):
        names = [nm for nm, _ in self.ranked()][:8]
        if not names:
            return y
        self.t("rows tagged columns", 16, (x, y), (150, 175, 230), bold=False)
        cw = 105
        for j, v in enumerate(names):
            self.t(v[:10], 17, (x + 150 + j * cw, y + 20), (150, 175, 230))
        y += 48
        for a in names:
            self.t(a[:14], 20, (x, y), (240, 244, 255), bold=False)
            for j, v in enumerate(names):
                c = self.profile(a)["tagged"].get(v, 0) if a != v else None
                self.t("-" if c is None else str(c), 20, (x + 150 + j * cw, y),
                       (255, 220, 120) if c else (140, 150, 180), bold=False)
            y += 28
        return y

    def sec_chart(self, x, y):
        box = pygame.Rect(x, y, 900, 220)
        pygame.draw.rect(self.screen, (22, 28, 64), box, border_radius=8)
        profs = [(nm, p) for nm, p in self.ranked() if len(p["history"]) > 1]
        if not profs:
            self.t("Play a few matches to see rating curves.", 20, box.center, (180, 190, 220), "center", bold=False)
            return box.bottom
        allv = [v for _, p in profs for v in p["history"]]
        lo, hi = min(allv) - 10, max(allv) + 10
        for gv in range(int(lo // 50 + 1) * 50, int(hi), 50):
            gy = box.bottom - 10 - (gv - lo) / (hi - lo) * (box.h - 20)
            pygame.draw.line(self.screen, (50, 60, 100), (box.x, gy), (box.right, gy))
            self.t(str(gv), 14, (box.x + 4, gy - 16), (120, 135, 180), bold=False)
        for k, (nm, p) in enumerate(profs):
            h = p["history"][-60:]
            col = COLORS[p["color_idx"] % 4]
            pts = [(box.x + 40 + i * (box.w - 60) / max(1, len(h) - 1),
                    box.bottom - 10 - (v - lo) / (hi - lo) * (box.h - 20)) for i, v in enumerate(h)]
            if len(pts) > 1:
                pygame.draw.lines(self.screen, col, False, pts, 3)
            pygame.draw.rect(self.screen, col, (box.right + 14, box.y + 6 + k * 24, 14, 14), border_radius=3)
            self.t(nm, 18, (box.right + 34, box.y + 2 + k * 24), bold=False)
        return box.bottom

    def sec_recent(self, x, y):
        hist = self.data["history"][-12:][::-1]
        if not hist:
            self.t("No matches yet.", 20, (x, y), (180, 190, 220), bold=False)
            return y + 28
        rows, colors = [], []
        for m in hist:
            top = max(m["best"], key=m["best"].get) if m["best"] else "-"
            rows.append([m["date"], fmt_time(m["duration"]), m["map"], m["loser"],
                         "%s (%s)" % (top, fmt_time(m["best"].get(top, 0))), ", ".join(m["players"])])
            colors.append([None, None, None, (255, 130, 130), None, None])
        return self.table(x, y, ["Date", "Length", "Map", "Loser", "Longest hold", "Players"],
                          [190, 90, 90, 150, 230, 360], rows, colors)

    # ---- in-game rendering
    def draw_game(self, g):
        cx, cy, vw, vh, z = g.view()
        vwi, vhi = int(math.ceil(vw)), int(math.ceil(vh))
        real = self.screen
        view = self.game_view.subsurface((0, 0, vwi, vhi))
        self.screen = view
        try:
            self.draw_world(g, int(cx), int(cy), vwi, vhi)
        finally:
            self.screen = real
        pygame.transform.smoothscale(view, (W, H), self.scaled_view)
        real.blit(self.scaled_view, (0, 0))
        blur = int(clamp(g.S.get("motion_blur", 0), 0, 2))
        if blur:
            if self.motion_frame is None:
                self.motion_frame = pygame.Surface((W, H))
            if self.motion_frame_valid:
                self.motion_frame.set_alpha((32, 64)[blur - 1])
                real.blit(self.motion_frame, (0, 0))
                self.motion_frame.set_alpha(None)
            self.motion_frame.blit(real, (0, 0))
            self.motion_frame_valid = True
        else:
            self.motion_frame_valid = False
        self.draw_offscreen(g, cx, cy, z)
        self.draw_hud(g)
        if g.tag_flash > 0:
            s = pygame.Surface((W, H), pygame.SRCALPHA)
            s.fill((255, 255, 255, int(120 * g.tag_flash / 0.25)))
            real.blit(s, (0, 0))

    def draw_world(self, g, cx, cy, W, H):
        """Draws the world into self.screen; W,H here are the (zoomed) view size in world pixels."""
        L, T = g.level, g.level.T
        scr = self.screen
        scr.blit(pygame.transform.scale(L.sky, (W, H)), (0, 0))
        # far parallax
        for (fx, fh, fw) in L.far:
            sx = fx - cx * 0.35
            if -200 < sx < W + 200:
                pygame.draw.rect(scr, T["far"], (sx, H - fh - (cy * 0.1) + 120, fw, fh + 200), border_radius=8)
        # walls
        for wx in (-400 - cx, L.WW - cx):
            if wx < W and wx + 400 > 0:
                pygame.draw.rect(scr, T["wall"], (wx, 0, 400, H))
                for k in range(0, H, 60):
                    pygame.draw.ellipse(scr, T["wall2"], (wx + 60 + (k * 7) % 200, k - cy % 60, 120, 34))
        pygame.draw.rect(scr, T["wall"], (0, -400 - cy, W, 400))   # ceiling panel
        # decor
        for d in L.decor:
            kind, x, y, extra = d
            sx, sy = x - cx, y - cy
            if not (-80 < sx < W + 80 and -120 < sy < H + 120):
                continue
            if kind == "flower":
                pygame.draw.line(scr, T["trunk"], (sx, sy), (sx, sy - 16), 3)
                pygame.draw.circle(scr, extra, (sx, sy - 18), 6)
            else:
                hgt = extra
                if T["deco"] == "tree":
                    pygame.draw.rect(scr, T["trunk"], (sx - 5, sy - hgt, 10, hgt))
                    pygame.draw.rect(scr, T["leaf"], (sx - 20, sy - hgt - 22, 40, 30), border_radius=8)
                elif T["deco"] == "cactus":
                    pygame.draw.rect(scr, T["leaf"], (sx - 6, sy - hgt, 12, hgt), border_radius=6)
                    pygame.draw.rect(scr, T["leaf"], (sx - 18, sy - hgt * 0.7, 12, 8), border_radius=4)
                    pygame.draw.rect(scr, T["leaf"], (sx - 18, sy - hgt * 0.7 - 20, 8, 28), border_radius=4)
                    pygame.draw.rect(scr, T["leaf"], (sx + 6, sy - hgt * 0.5, 12, 8), border_radius=4)
                    pygame.draw.rect(scr, T["leaf"], (sx + 10, sy - hgt * 0.5 - 20, 8, 28), border_radius=4)
                else:
                    pygame.draw.rect(scr, T["trunk"], (sx - 3, sy - 12, 6, 12))
                    for k in range(3):
                        wdt = 40 - k * 10
                        yy = sy - 12 - k * 22
                        pygame.draw.polygon(scr, T["leaf"], [(sx - wdt / 2, yy), (sx + wdt / 2, yy), (sx, yy - 30)])
        # crates
        for (x, y, n) in L.crates:
            for k in range(n):
                r = pygame.Rect(x - cx, y - 36 * (k + 1) - cy, 36, 36)
                pygame.draw.rect(scr, (245, 160, 60), r)
                pygame.draw.rect(scr, (200, 110, 30), r, 3)
        # platforms
        for s in L.segs:
            if s[2] < cx - 20 or s[0] > cx + W + 20 or max(s[1], s[3]) < cy - 20 or min(s[1], s[3]) > cy + H + 20:
                continue
            p1 = (s[0] - cx, s[1] - cy)
            p2 = (s[2] - cx, s[3] - cy)
            if s[1] == s[3]:
                if s is L.segs[0]:
                    pygame.draw.rect(scr, T["plat"], (p1[0], p1[1], s[2] - s[0], H * 2))
                else:
                    pygame.draw.rect(scr, T["plat"], (p1[0], p1[1], s[2] - s[0], 9), border_radius=3)
                pygame.draw.rect(scr, T["top"], (p1[0], p1[1] - 1, s[2] - s[0], 4), border_radius=2)
            else:
                pygame.draw.line(scr, T["plat"], p1, p2, 10)
                pygame.draw.line(scr, T["top"], (p1[0], p1[1] - 4), (p2[0], p2[1] - 4), 3)
        for (x1, x2, py) in L.pads:
            r = pygame.Rect(x1 - cx, py - cy - 4, x2 - x1, 5)
            pygame.draw.rect(scr, (255, 240, 80), r, border_radius=2)
            for k in range(3):
                ax = r.x + 14 + k * 24 + (g.elapsed * 60) % 24
                if ax < r.right - 8:
                    pygame.draw.polygon(scr, (255, 130, 40), [(ax, r.y - 5), (ax + 8, r.y + 2), (ax, r.y + 9)])
        for tr in L.tramps:
            sx, sy = tr["x1"] - cx, tr["top"] - cy
            pygame.draw.rect(scr, (190, 40, 100), (sx + 18, sy + 4, 12, 8))
            pygame.draw.ellipse(scr, (70, 245, 120), (sx, sy, 48, 14))
        for pa, pb in L.tele:
            for (px, py) in (pa, pb):
                c = (int(px - cx), int(py - cy - 22))
                for k in range(3):
                    ph = g.elapsed * 3 + k
                    pygame.draw.circle(scr, (190, 110, 255), c, int(8 + 8 * k + 2 * math.sin(ph)), 3)
        # pickups
        for pk in g.pickups:
            col, tag = PICKUP_TYPES[pk["kind"]]
            sx = pk["x"] - cx
            sy = pk["y"] - cy + math.sin(pk["t"] * 4) * 4
            pygame.draw.circle(scr, (255, 255, 255), (sx, sy), 17)
            pygame.draw.circle(scr, col, (sx, sy), 13)
            self.t(tag, 11, (sx, sy), (20, 20, 40), "center")
        # particles
        for pt in g.parts:
            a = pt[4] / pt[5]
            pygame.draw.circle(scr, pt[6], (pt[0] - cx, pt[1] - cy), max(1, int(pt[7] * a)))
        # players
        for p in g.players:
            self.draw_player(g, p, cx, cy)

    def draw_player(self, g, p, cx, cy):
        scr = self.screen
        view_w, view_h = scr.get_size()
        sx, sy = int(p.x - cx), int(p.y - cy)
        if not (-60 < sx < view_w + 60 and -90 < sy < view_h + 80):
            return
        moving = p.on_ground and abs(p.vx) > 20
        amp = min(1.0, abs(p.vx) / 160.0) if moving else 0.0
        bob = -abs(math.sin(p.walk)) * 2.0 * amp          # little hop in time with the steps
        hip_y = sy - LEG_H - 1
        # --- legs (drawn behind the body)
        for side in (-1, 1):
            hx = sx + side * 7
            if p.on_ground:
                ph = p.walk + (math.pi if side > 0 else 0)
                fx = hx + math.sin(ph) * 8 * amp
                fy = sy - 1 - max(0.0, math.cos(ph)) * 5 * amp
            else:
                t = clamp(p.vy / 700.0, -1, 1)               # rising: tucked, falling: dangling apart
                fx = hx + side * (2 + max(0.0, t) * 5)
                fy = sy - 5 + t * 4 + math.sin(g.elapsed * 14 + side) * 0.8
            pygame.draw.line(scr, SKIN, (hx, hip_y + bob), (fx, fy), 5)
            pygame.draw.ellipse(scr, SKIN, (fx - 4 + p.facing * 1, fy - 2, 8, 4))
        # --- body sprite (artwork faces left, so flip when facing right)
        profile = self.data["profiles"].get(p.name, {})
        img = self.sprite(p.slot, SPR_W, p.facing > 0, profile.get("skin", "classic"))
        scr.blit(img, (sx - img.get_width() // 2, sy - LEG_H - img.get_height() + 1 + bob))
        body = (sx, int(sy - LEG_H - img.get_height() * 0.45 + bob))
        top = sy - LEG_H - img.get_height() + bob
        if p.frozen > 0:
            s = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(s, (170, 240, 255, 150), (25, 25), 22)
            scr.blit(s, (body[0] - 25, body[1] - 25))
        if "shield" in p.buffs:
            pygame.draw.circle(scr, (255, 220, 80), body, 24, 3)
        if p.tag_immune > 0.05 and g.it is not p:
            pygame.draw.circle(scr, (255, 255, 255), body, 22, 1)
        if "speed" in p.buffs and abs(p.vx) > 50:
            pygame.draw.line(scr, (120, 190, 255), (sx - p.facing * 18, body[1]), (sx - p.facing * 36, body[1]), 3)
        self.t(p.name, 14, (sx, top - 12), p.color, "center", True)
        if g.it is p:
            ab = math.sin(pygame.time.get_ticks() / 150.0) * 4
            ty = top - 34 + ab
            pygame.draw.polygon(scr, (255, 255, 255), [(sx - 10, ty - 10), (sx + 10, ty - 10), (sx, ty + 4)])

    def draw_offscreen(self, g, cx, cy, z):
        for p in g.players:
            sx, sy = (p.x - cx) * z, (p.cy - cy) * z
            if 0 <= sx <= W and 0 <= sy <= H:
                continue
            ax, ay = clamp(sx, 28, W - 28), clamp(sy, 70, H - 28)
            ang = math.atan2(sy - ay, sx - ax)
            size = 18 if p is g.it else 12
            tip = (ax + math.cos(ang) * size, ay + math.sin(ang) * size)
            l = (ax + math.cos(ang + 2.5) * size, ay + math.sin(ang + 2.5) * size)
            r = (ax + math.cos(ang - 2.5) * size, ay + math.sin(ang - 2.5) * size)
            pygame.draw.polygon(self.screen, p.color, [tip, l, r])
            pygame.draw.polygon(self.screen, (255, 255, 255), [tip, l, r], 2)

    def draw_hud(self, g):
        tl = g.time_left
        low = tl <= 10
        col = (255, 90, 90) if low else (255, 255, 255)
        size = 72 + (int(14 * abs(math.sin(g.elapsed * 6))) if low and not g.over else 0)
        self.t(str(int(math.ceil(tl))), size, (W // 2, 44), col, "center", True)
        pygame.draw.rect(self.screen, (255, 255, 255), (W // 2 - 14, 92, 6, 18), border_radius=2)
        pygame.draw.rect(self.screen, (255, 255, 255), (W // 2 + 8, 92, 6, 18), border_radius=2)
        for i, p in enumerate(g.players):
            x, y = 14, 14 + i * 52
            profile = self.data["profiles"].get(p.name, {})
            self.icon(p.slot, (x + 14, y + 16), 30, profile.get("skin", "classic"))
            self.t(p.name, 20, (x + 32, y), (255, 255, 255), shadow=True)
            pr = profile
            sub = "%d  |  it: %s" % (round(pr["rating"]) if pr else 0, fmt_time(p.hold))
            self.t(sub, 15, (x + 32, y + 22), (235, 240, 255), shadow=True, bold=False)
            bx = x + 240
            for k in p.buffs:
                c = PICKUP_TYPES[k][0]
                pygame.draw.circle(self.screen, c, (bx, y + 14), 9)
                bx += 22
            if p.frozen > 0:
                pygame.draw.circle(self.screen, (170, 240, 255), (bx, y + 14), 9)
        if g.intro > 0:
            self.t("%s is IT!" % g.it.name, 64, (W // 2, H // 2 - 80), (255, 255, 255), "center", True)
            self.t("get ready", 28, (W // 2, H // 2 - 30), (255, 255, 255), "center", True)
        elif g.elapsed < 4:
            self.t("don't be IT when the timer hits 0", 22, (W // 2, 128), (255, 255, 255), "center", True, False)


def main():
    App().run()


if __name__ == "__main__":
    main()