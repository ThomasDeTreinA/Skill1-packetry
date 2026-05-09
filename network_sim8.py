import pygame
import math
import sys
import os
import random

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Sprites V2")

WIDTH, HEIGHT = 1000, 700
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 150, 255)
YELLOW = (255, 255, 50)
GRAY = (150, 150, 150)
CYAN = (100, 255, 255)

# --- TAAL SYSTEEM ---
current_lang = 'nl' # Alleen Nederlands

LANGS = {
    'nl': {
        'play': 'START SPEL',
        'quit': 'AFSLUITEN',
        'select_lang': 'TAAL: NEDERLANDS',
        'back': 'Terug',
        'go': 'Go!',
        'enter_house': 'HUIS BETREDEN',
        'to_world': 'NAAR WERELDKAART',
        'ip_settings': 'IP Instellingen',
        'web_browsing': 'Web Browsing',
        'terminal': 'Terminal',
        'wifi': 'WiFi',
        'restart': 'Herstarten',
        'reset': 'Factory Reset',
        'save': 'Opslaan',
        'select_cable': 'Kies Kabel:',
        'cat_straight': 'Straight-Through',
        'cat_cross': 'Crossover',
        'cat5e_label': 'Cat 5e Kabel',
        'wan_label': 'WAN Fiber',
        'error_len': 'Kabel te lang!',
        'error_ip': 'Fout: Router IP of Subnet incorrect.',
        'error_route': 'Fout: Geen route naar een Router.',
        'error_no_ip': 'Fout: PC heeft geen IP-adres.',
        'error_404': 'Fout: 404 Website niet gevonden.',
        'connecting': 'Verbinding maken...',
        'free_mode': 'Vrij Spel / Sandbox Mode',
        'extra_info': 'EXTRA UITLEG',
        'intro_title': 'Welkom bij de Netwerk Simulator!',
        'intro_body': [
            "In deze game leer je de basisprincipes van netwerken stap voor stap.",
            "Je bouwt je eigen lokale netwerk (LAN), verbindt apparaten via fysieke",
            "kabels, en leert hoe Routers je naar het echte internet tillen.",
            "",
            "Wat kun je allemaal doen?",
            "- Plaats PC's, Laptops, Switches en Routers (linksboven).",
            "- Verbind apparaten met Cat 5 of snellere fiber kabels (rechts).",
            "- Configureer IP-adressen via het besturingssysteem van elk apparaat.",
            "- Test je netwerk door data-pakketjes of webverkeer te sturen!",
            "",
            "Klik hier ergens in het vak om aan Level 1 te beginnen!"
        ],
        'l1_exp_mouse': "TIP: Houd de linkermuisknop ingedrukt om kabels te trekken!",
        'trans_zoom_in': "Inzoomen op...",
        'trans_zoom_out': "Uitzoomen naar de buitenwereld...",
        'trans_back_world': "Terug naar het overzicht...",
        'spacebar': 'SPATIE',
        'isp_provider': 'Internet Provider',
        'levels': 'LEVELS'
    }
}

def get_text(key):
    return LANGS['nl'].get(key, key)

CABLES = {
    'Cat 5':    {'color': (100, 200, 100), 'max_dist': 400, 'max_m': 100},
    'Fiber':    {'color': YELLOW,          'max_dist': 10000,'max_m': 5000},
    'Straight': {'color': GREEN,           'max_dist': 4000, 'max_m': 1000},
    'Crossover':{'color': (255, 128, 0),   'max_dist': 4000, 'max_m': 1000}, # Orange
    'WAN Fiber':{'color': YELLOW,          'max_dist': 2000,'max_m': 10000},
    'Wi-Fi':    {'color': CYAN,            'max_dist': 250, 'max_m': 30}
}

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Network Simulation")
font = pygame.font.SysFont("Arial", 20, bold=True)
mission_font = pygame.font.SysFont("lato", 30, bold=False)
small_font = pygame.font.SysFont("lato", 16)

bg_road = None
try:
    bg_road = pygame.image.load(os.path.join(BASE_DIR, "Background", "background.png")).convert()
    bg_road = pygame.transform.smoothscale(bg_road, (WIDTH, HEIGHT))
except Exception as e:
    pass

bg_level = None
try:
    bg_level = pygame.image.load(os.path.join(BASE_DIR, "Background", "background.png")).convert()
    bg_level = pygame.transform.smoothscale(bg_level, (WIDTH, HEIGHT))
except Exception as e:
    pass

logo_img = None
try:
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Logo", "logo2.png")
    # We laden het logo nu 1-op-1 in. Voor het beste resultaat: maak logo2.png exact 500px breed.
    logo_img = pygame.image.load(logo_path).convert_alpha()
except Exception as e:
    print(f"Logo load error: {e}")

gc_img = None
try:
    gc_img = pygame.image.load(os.path.join(BASE_DIR, "Icons", "GreenCircle.png")).convert_alpha()
except Exception as e:
    pass

arrow_img = None
try:
    img = pygame.image.load(os.path.join(BASE_DIR, "Icons", "arrow.png")).convert_alpha()
    arrow_img = pygame.transform.smoothscale(img, (80, 80))
except Exception as e:
    pass

# Global Game State
devices = []
connections = []
packets = []
packet_flash_timer = 0
mission_sys = None
current_mode = 'PC' 
current_cable = 'Straight'
sm = None

data_img = None
try:
    img = pygame.image.load(os.path.join(BASE_DIR, "Icons", "data.png")).convert_alpha()
    data_img = pygame.transform.smoothscale(img, (35, 35))
except Exception as e:
    pass

tm_img = None
try:
    img = pygame.image.load(os.path.join(BASE_DIR, "WebPages", "thomasmore.png")).convert_alpha()
    tm_img = pygame.transform.smoothscale(img, (500, 270))
except Exception as e:
    print(f"ERROR loading thomasmore.png: {e}")
    pass

def load_icon(folder, filename, size=(50, 50)):
    if '.' not in filename:
        for ext in ['.png', '.jpg', '.jpeg', '.webp']:
            filepath = os.path.join(BASE_DIR, folder, filename + ext)
            if os.path.exists(filepath):
                filename += ext
                break
                
    filepath = os.path.join(BASE_DIR, folder, filename)
    try:
        img = pygame.image.load(filepath).convert_alpha()
        return pygame.transform.smoothscale(img, size)
    except Exception as e:
        print(f"ERROR loading {filepath}: {e}")
        surf = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.circle(surf, WHITE, (size[0]//2, size[1]//2), size[0]//2)
        return surf

# --- GELUIDSSYSTEEM ---
pygame.mixer.init()
SOUND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")

snd_cable = None
snd_delete = None
snd_enter = None
snd_place = None

try:
    snd_cable = pygame.mixer.Sound(os.path.join(SOUND_DIR, "Cable.wav"))
    snd_delete = pygame.mixer.Sound(os.path.join(SOUND_DIR, "Delete.mp3"))
    snd_enter = pygame.mixer.Sound(os.path.join(SOUND_DIR, "EnteringHouse.mp3"))
    snd_place = pygame.mixer.Sound(os.path.join(SOUND_DIR, "PlaceItem.mp3"))
except Exception as e:
    print(f"ERROR loading sounds: {e}")

def play_sound(snd):
    if snd:
        snd.play()

ICONS = {
    'PC': load_icon("Gear", "pc.png"),
    'Laptop': load_icon("Gear", "laptop.png"),
    'Switch': load_icon("Gear", "switch.png"),
    'Router': load_icon("Gear", "router.png"),
    'Hub': load_icon("Gear", "hub.png"),
    'Converter': load_icon("Gear", "converter.png"),
    'DELETE': load_icon("Icons", "delete.png"),
    'House1': load_icon("Houses", "huis1.png", size=(80, 80)),
    'House2': load_icon("Houses", "huis2.png", size=(80, 80)),
    'House3': load_icon("Houses", "huis3.png", size=(80, 80)),
    'House4': load_icon("Houses", "huis4.png", size=(80, 80)),
    'WIFI': load_icon("Icons", "wifi.png", size=(130, 130)),
}

# --- GLOBAL UI BUTTONS ---
btn_modi = {
    'PC': pygame.Rect(10, 10, 80, 80),
    'Laptop': pygame.Rect(100, 10, 80, 80),
    'Switch': pygame.Rect(190, 10, 80, 80),
    'Hub': pygame.Rect(280, 10, 80, 80),
    'Router': pygame.Rect(370, 10, 80, 80),
    'Converter': pygame.Rect(460, 10, 80, 80),
    'DELETE': pygame.Rect(550, 10, 80, 80)
}
btn_data = pygame.Rect(640, 10, 80, 80)
btn_straight = pygame.Rect(820, 100, 170, 40)
btn_cross = pygame.Rect(820, 150, 170, 40)
btn_wan = pygame.Rect(820, 200, 170, 40)
btn_enter_house = pygame.Rect(10, 110, 180, 45) 
btn_to_world = pygame.Rect(20, HEIGHT//2 - 20, 220, 40)

EXT_ICONS = {}
def get_ext_icon(name):
    if name not in EXT_ICONS:
        filename = name
        if '.' not in filename:
            for ext in ['.png', '.jpg', '.webp']:
                if os.path.exists(os.path.join(BASE_DIR, "Icons", filename + ext)):
                    filename += ext
                    break
        try:
            img = pygame.image.load(os.path.join(BASE_DIR, "Icons", filename)).convert_alpha()
            EXT_ICONS[name] = pygame.transform.smoothscale(img, (60, 60))
        except Exception as e:
            print(f"ERROR loading ext icon {name}: {e}")
            surf = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.rect(surf, GRAY, (0,0,60,60))
            EXT_ICONS[name] = surf
    return EXT_ICONS[name]

class Device:
    counts = {"PC": 0, "Laptop": 0, "Switch": 0, "Router": 0, "Hub": 0, "House": 0}
    
    @classmethod
    def reset_counts(cls):
        cls.counts = {"PC": 0, "Laptop": 0, "Switch": 0, "Router": 0, "Hub": 0, "House": 0}

    def __init__(self, x, y, device_type, decorative=False):
        self.x = x
        self.y = y
        self.type = device_type
        self.decorative = decorative
        self.dhcp = False # DHCP state
        self.collision_timer = 0
        if not decorative:
            # Type-specifiek nummeren (PC1, RT1, etc)
            key = "House" if device_type.startswith("House") else device_type
            Device.counts[key] = Device.counts.get(key, 0) + 1
            self.name_idx = Device.counts[key]
        else:
            # Ook decoratieve huizen een nummer geven
            if device_type.startswith("House"):
                Device.counts["House"] = Device.counts.get("House", 0) + 1
                self.name_idx = Device.counts["House"]
            else:
                self.name_idx = 0
            
        self.id = random.randint(1000, 9999) # Unique ID for internal logic
        self.radius = 25
        self.ip = ""
        self.subnet = ""
        self.gateway = ""
        self.dns = ""

    @property
    def cable_c(self):
        # Return a slightly offset visual center point for cables to originate from
        if self.type == 'Router':
            return (self.x, self.y + 10)
        return (self.x, self.y)
        
    def cable_dist(self, angle):
        # Return the bounding intersection distance based on device type
        if self.type == 'Router':
            return 17 / max(abs(math.cos(angle)), abs(math.sin(angle)))
        elif self.type == 'PC':
            return 18 / max(abs(math.cos(angle)), abs(math.sin(angle)))
        elif self.type in ('House1', 'House2'):
            return 40 / max(abs(math.cos(angle)), abs(math.sin(angle))) + 2
        else:
            return 25 / max(abs(math.cos(angle)), abs(math.sin(angle))) + 2

    def draw(self, surface, current_scene='Level1'):
        if self.type == 'PC': label = f"PC {self.name_idx}"
        elif self.type == 'Laptop': label = f"LAP {self.name_idx}"
        elif self.type == 'Switch': label = f"SW {self.name_idx}"
        elif self.type == 'Router': label = f"RT {self.name_idx}"
        elif self.type == 'Hub': label = f"HB {self.name_idx}"
        elif self.type.startswith('House'):
            # Geef alle huizen namen gebaseerd op hun positie (met int() voor robuustheid)
            ix, iy = int(self.x), int(self.y)
            if ix == 100: label = "Huis 4"
            elif ix == 300: label = "Huis 1"
            elif ix == 500: label = "Huis 2"
            elif ix == 700: label = "Huis 5"
            elif ix == 900: label = "Huis 3"
            else: label = f"Huis {self.name_idx}"
            
            # Specifieke overschrijving voor Missie-huizen op top rij
            if iy == 280:
                if ix == 300: label = "Huis 1"
                elif ix == 500: label = "Huis 2"
        else: label = f"DEV {self.name_idx}"
            
        icon = ICONS.get(self.type)
        if icon:
            rect = icon.get_rect(center=(self.x, self.y))
            surface.blit(icon, rect.topleft)
        else:
            pygame.draw.circle(surface, GRAY, (self.x, self.y), self.radius)
            pygame.draw.circle(surface, WHITE, (self.x, self.y), self.radius, 2)
            
        # Collision effect (red flash)
        if self.collision_timer > 0:
            self.collision_timer -= 1
            s = pygame.Surface((60, 60), pygame.SRCALPHA)
            alpha = min(255, self.collision_timer * 4)
            pygame.draw.circle(s, (255, 0, 0, alpha), (30, 30), 25 + math.sin(pygame.time.get_ticks()*0.05)*5)
            surface.blit(s, (self.x - 30, self.y - 30))
            
            coll_text = small_font.render("COLLISION!", True, RED)
            surface.blit(coll_text, (self.x - coll_text.get_width()//2, self.y - 45))
        
        text = font.render(label, True, WHITE)
        # Bovenste rij (y=280) label boven, onderste rij (y=415) label beneden om de weg te ontwijken
        if int(self.y) == 280:
            surface.blit(text, (self.x - text.get_width()//2, self.y - self.radius - 25))
        else:
            surface.blit(text, (self.x - text.get_width()//2, self.y + self.radius + 10))
        
        # Wi-Fi connecting animation (blinking arcs to the LEFT of laptop)
        if self.type == 'Laptop' and mission_sys.wifi_timer > 0:
            if (pygame.time.get_ticks() // 250) % 2 == 0:
                for i in range(3):
                    r = 15 + i*8
                    rect = pygame.Rect(self.x - self.radius - 40 - r, self.y - r, r*2, r*2)
                    pygame.draw.arc(surface, CYAN, rect, 3*math.pi/4, 5*math.pi/4, 3) 
        
        # Highlight Huis 1 & 2 in World Map for mission
        if current_scene == 'World' and self.type in ['House1', 'House2'] and not self.decorative:
            # Check if mission is active and NO WAN connection yet
            m = mission_sys.get_current() if mission_sys else None
            if m and m.type in ["L3_CONNECT_WAN", "L3_SEND_P_WAN"]:
                # Check for WAN connection
                connected = False
                for c in connections:
                    if (c.d1.type == 'House1' and c.d2.type == 'House2') or (c.d1.type == 'House2' and c.d1.type == 'House1'):
                        if c.cable_type == 'WAN Fiber':
                            connected = True
                            break
                if not connected:
                    s = abs(math.sin(pygame.time.get_ticks() * 0.005))
                    pygame.draw.circle(surface, YELLOW, (self.x, self.y), self.radius + 10 + s*5, 3)
                    # Arrow above
                    ay = self.y - self.radius - 50 - s*10
                    pygame.draw.polygon(surface, YELLOW, [(self.x, ay+20), (self.x-10, ay), (self.x+10, ay)])
                    t = font.render("HUIS 2 (Target)", True, YELLOW)
                    surface.blit(t, (self.x - t.get_width()//2, ay - 25))
        
        if self.ip:
            ip_txt = small_font.render(self.ip, True, CYAN)
            surface.blit(ip_txt, (self.x - ip_txt.get_width()//2, self.y + self.radius + 5))

class TextInput:
    def __init__(self, x, y, w, h, default=""):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.rect = pygame.Rect(x, y, w, h)
        self.text = default
        self.active = False
        self.password_mode = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                pass
            else:
                if len(self.text) < 30:
                    self.text += event.unicode

    def draw(self, surface):
        self.rect.x = self.x
        self.rect.y = self.y
        pygame.draw.rect(surface, WHITE, self.rect)
        pygame.draw.rect(surface, BLACK if not self.active else BLUE, self.rect, 2)
        display_text = self.text if not self.password_mode else "*" * len(self.text)
        t = font.render(display_text, True, BLACK)
        surface.blit(t, (self.rect.x + 5, self.rect.y + 5))

class Connection:
    def __init__(self, d1, d2, cable_type='Cat 5'):
        self.d1 = d1
        self.d2 = d2
        self.cable_type = cable_type
        self.update_validity()

    def update_validity(self):
        c1x, c1y = self.d1.cable_c
        c2x, c2y = self.d2.cable_c
        self.distance = math.hypot(c1x - c2x, c1y - c2y)
        self.is_valid = self.distance <= CABLES[self.cable_type]['max_dist']

    def draw(self, surface):
        # Don't draw Wi-Fi line while connecting animation is playing
        if self.cable_type == 'Wi-Fi' and mission_sys.wifi_timer > 0:
            return

        color = CABLES[self.cable_type]['color'] if self.is_valid else RED
        
        c1x, c1y = self.d1.cable_c
        c2x, c2y = self.d2.cable_c
        
        angle = math.atan2(c2y - c1y, c2x - c1x)
        d1_dist = self.d1.cable_dist(angle)
        d2_dist = self.d2.cable_dist(angle)
        
        if self.distance > (d1_dist + d2_dist):
            start_x = c1x + math.cos(angle) * d1_dist
            start_y = c1y + math.sin(angle) * d1_dist
            end_x = c2x - math.cos(angle) * d2_dist
            end_y = c2y - math.sin(angle) * d2_dist
            
            if self.cable_type == 'Wi-Fi':
                # Draw 3-4 arcs (radio waves) centered on the midpoint
                mid_x, mid_y = (start_x + end_x) / 2, (start_y + end_y) / 2
                angle = math.atan2(end_y - start_y, end_x - start_x)
                
                # Draw small circles or arcs repeating along the line
                # Let's draw 3 arcs in the middle of the connection
                for i in range(1, 4):
                    r = i * 8
                    # Draw arc segment
                    points = []
                    for a in range(-30, 31, 10):
                        rad = math.radians(a)
                        px = mid_x + math.cos(angle + rad) * r
                        py = mid_y + math.sin(angle + rad) * r
                        points.append((px, py))
                    if len(points) > 1:
                        pygame.draw.lines(surface, color, False, points, 2)
                
                # Also a small dot in the center
                pygame.draw.circle(surface, color, (int(mid_x), int(mid_y)), 3)
            else:
                pygame.draw.line(surface, color, (start_x, start_y), (end_x, end_y), 4)

class PacketPath:
    def __init__(self, path, speed=4.0):
        self.path = path
        self.target_pc = path[-1]
        self.curr_idx = 0
        self.progress = 0.0
        self.speed = speed
        self.reached = False
        self.dist = 0
        self.pause_frames = 0
        self.just_reached_node = False
        self.status = 'OK' # 'OK' or 'COLLIDED'
        self.update_dist()

    def update_dist(self):
        if self.curr_idx < len(self.path) - 1:
            c1x, c1y = self.path[self.curr_idx].cable_c
            c2x, c2y = self.path[self.curr_idx+1].cable_c
            self.dist = math.hypot(c1x - c2x, c1y - c2y)
        else:
            self.dist = 0

    def update(self):
        if self.reached: return
        
        if self.pause_frames > 0:
            self.pause_frames -= 1
            return
            
        if self.dist == 0:
            self.progress = 1.0
        else:
            self.progress += self.speed / self.dist
            
        if self.progress >= 1.0:
            self.progress = 0.0
            self.curr_idx += 1
            if self.curr_idx >= len(self.path) - 1:
                self.reached = True
            else:
                self.just_reached_node = True
                self.pause_frames = 12 # 0.2s at 60fps
                self.update_dist()

    def draw(self, surface):
        if self.reached or self.curr_idx >= len(self.path) - 1 or self.status == 'COLLIDED': return
        
        c1x, c1y = self.path[self.curr_idx].cable_c
        c2x, c2y = self.path[self.curr_idx+1].cable_c
        
        x = c1x + (c2x - c1x) * self.progress
        y = c1y + (c2y - c1y) * self.progress
        
        # Wi-Fi pulse effect: check if current segment uses Wi-Fi
        alpha = 255
        from_dev = self.path[self.curr_idx]
        to_dev = self.path[self.curr_idx + 1]
        for c in connections:
            if ((c.d1 == from_dev and c.d2 == to_dev) or
                (c.d2 == from_dev and c.d1 == to_dev)):
                if c.cable_type == 'Wi-Fi':
                    # Sharp blinking effect for wireless (5 blinks per second)
                    alpha = 255 if (pygame.time.get_ticks() // 150) % 2 == 0 else 50
                break
        
        if data_img:
            tmp = data_img.copy()
            tmp.set_alpha(alpha)
            rect = tmp.get_rect(center=(int(x), int(y)))
            surface.blit(tmp, rect.topleft)
        else:
            s = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 220, 0, alpha), (10, 10), 10)
            surface.blit(s, (int(x)-10, int(y)-10))

class SceneManager:
    def __init__(self):
        self.scenes = {
            'Start': {'devices': [], 'connections': [], 'packets': []},
            'Level1': {'devices': [], 'connections': [], 'packets': [], 'bg_img': 'lab_bg.png'},
            'House1': {'devices': [], 'connections': [], 'packets': [], 'bg_img': 'lab_bg.png'},
            'House2': {'devices': [], 'connections': [], 'packets': [], 'bg_img': 'lab_bg.png'},
            'House3': {'devices': [], 'connections': [], 'packets': [], 'bg_img': 'lab_bg.png'},
            'House4': {'devices': [], 'connections': [], 'packets': [], 'bg_img': 'lab_bg.png'},
            'World': {'devices': [], 'connections': [], 'packets': [], 'bg_img': 'wereldkaart_bg.png'},
            'Uitleg_Menu': {'devices': [], 'connections': [], 'packets': []},
            'Level_Select': {'devices': [], 'connections': [], 'packets': []}
        }
        self.current = 'Start'
        self.transition_alpha = 0
        self.transition_state = "NONE" # NONE, FADE_OUT, FADE_IN
        self.target_scene = None
        self.trans_text = ""
        self.uitleg_page = 0
        self.uitleg_pages = [
            ("Eindapparaten (End Devices)", "PC", [
                "PC & Laptop zijn de werkstations van gebruikers.",
                "Hier begint en eindigt het meeste dataverkeer.",
                "Laptops kunnen ook draadloos verbinden via Wi-Fi."
            ]),
            ("De Switch", "Switch", [
                "Verbindt apparaten binnen hetzelfde netwerk (LAN).",
                "Is 'slim': onthoudt welk apparaat op welke poort zit.",
                "Dit gebeurt op basis van unieke MAC-adressen."
            ]),
            ("De Router", "Router", [
                "Is de 'poortwachter' tussen verschillende netwerken.",
                "Verbindt jouw thuisnetwerk met het grote internet.",
                "Gebruikt IP-adressen om data de juiste weg te wijzen."
            ]),
            ("De Hub", "Hub", [
                "Een Hub is een dom apparaat dat alles doorstuurt naar iedereen.",
                "Het verdeelt de bandbreedte en veroorzaakt meer botsingen.",
                "Wordt tegenwoordig bijna niet meer gebruikt, we gebruiken nu Switches."
            ]),
            ("Kabels (Straight-Through)", "cat5e_straight", [
                "Straight-Through (Recht) gebruik je voor VERSCHILLENDE types.",
                "Bijvoorbeeld: PC naar Switch of Switch naar Router.",
                "Kleur in de game: Groen."
            ]),
            ("Kabels (Crossover)", "cat5_cross", [
                "Crossover (Gekruist) gebruik je voor DEZELFDE types.",
                "Bijvoorbeeld: Switch naar Switch of Router naar Router.",
                "Kleur in de game: Oranje."
            ]),
            ("Data Pakketten", "data", [
                "De 'envelop' waarin jouw digitale bericht zit.",
                "Bevat o.a. de IP-adressen van verzender en ontvanger.",
                "Netwerkapparatuur leest dit om te weten waar het heen moet."
            ]),
            ("Broadcast", "broadcast", [
                "Een bericht dat naar ALLE apparaten wordt gestuurd.",
                "Nodig om onbekende apparaten te vinden in het netwerk.",
                "Een Switch stuurt dit door naar elke actieve poort."
            ]),
            ("Topologie (Ster vs Boom)", "topologie", [
                "Ster (Star): Alles zit op één centrale Switch.",
                "Boom (Tree): Meerdere Switches onderling verbonden.",
                "Boom-structuur kan veel meer apparaten aan."
            ]),
            ("IP Adres", "ip", [
                "Een unieke identificatie voor elk apparaat.",
                "Voorbeeld: 192.168.1.5",
                "Zonder IP kan een apparaat niet communiceren op internet."
            ]),
            ("Subnet Mask", "subnet", [
                "Bepaalt welk deel van het IP het netwerk is.",
                "Apparaten in hetzelfde subnet kunnen elkaar direct zien.",
                "Voorbeeld: 255.255.255.0"
            ]),
            ("Web Browsing", "web", [
                "Het bezoeken van websites via een browser.",
                "Werkt via URL's zoals www.thomasmore.be",
                "De router zorgt dat je de weg naar de website vindt."
            ])
        ]
        
    def start_transition(self, target, text):
        self.transition_state = "FADE_OUT"
        self.target_scene = target
        self.trans_text = text

    def get_current(self):
        return self.scenes[self.current]

    def draw_start_screen(self, surface):
        surface.fill((30, 30, 40))
        # Logo as Title
        if logo_img:
            surface.blit(logo_img, (WIDTH//2 - logo_img.get_width()//2, 60))
            y_slogan = 60 + logo_img.get_height() + 20
        else:
            title_font = pygame.font.SysFont('urbanist', 80, bold=True)
            t_surf = title_font.render("Packetry", True, (52, 50, 199))
            surface.blit(t_surf, (WIDTH//2 - t_surf.get_width()//2, 80))
            y_slogan = 170
        
        # Slogan
        slogan_font = pygame.font.SysFont('urbanist', 32, italic=True)
        s_surf = slogan_font.render("Engineering the flow", True, (0, 255, 148))
        surface.blit(s_surf, (WIDTH//2 - s_surf.get_width()//2, y_slogan))
        
        # Play / Quit / Extra Info Buttons (Vertically stacked)
        btn_play = pygame.Rect(WIDTH//2 - 100, 280, 200, 60)
        pygame.draw.rect(surface, (100, 200, 100), btn_play, border_radius=10)
        pygame.draw.rect(surface, WHITE, btn_play, 3, border_radius=10)
        p_txt = font.render(get_text('play'), True, WHITE)
        surface.blit(p_txt, (btn_play.centerx - p_txt.get_width()//2, btn_play.centery - p_txt.get_height()//2))
        
        btn_quit = pygame.Rect(WIDTH//2 - 100, 360, 200, 60)
        pygame.draw.rect(surface, (200, 100, 100), btn_quit, border_radius=10)
        pygame.draw.rect(surface, WHITE, btn_quit, 3, border_radius=10)
        q_txt = font.render(get_text('quit'), True, WHITE)
        surface.blit(q_txt, (btn_quit.centerx - q_txt.get_width()//2, btn_quit.centery - q_txt.get_height()//2))

        # Extra Uitleg Button
        btn_uitleg = pygame.Rect(WIDTH//2 - 100, 440, 200, 60)
        pygame.draw.rect(surface, (100, 100, 200), btn_uitleg, border_radius=10)
        pygame.draw.rect(surface, WHITE, btn_uitleg, 3, border_radius=10)
        u_txt = font.render(get_text('extra_info'), True, WHITE)
        surface.blit(u_txt, (btn_uitleg.centerx - u_txt.get_width()//2, btn_uitleg.centery - u_txt.get_height()//2))

        # Levels Button
        btn_levels = pygame.Rect(WIDTH//2 - 100, 520, 200, 60)
        pygame.draw.rect(surface, (200, 150, 50), btn_levels, border_radius=10)
        pygame.draw.rect(surface, WHITE, btn_levels, 3, border_radius=10)
        l_txt = font.render(get_text('levels'), True, WHITE)
        surface.blit(l_txt, (btn_levels.centerx - l_txt.get_width()//2, btn_levels.centery - l_txt.get_height()//2))

    def update(self):
        if self.transition_state == "FADE_OUT":
            self.transition_alpha += 5
            if self.transition_alpha >= 255:
                self.current = self.target_scene
                self.transition_state = "FADE_IN"
        elif self.transition_state == "FADE_IN":
            self.transition_alpha -= 5
            if self.transition_alpha <= 0:
                self.transition_state = "NONE"

    def draw(self, surface):
        if self.current == 'Start':
            self.draw_start_screen(surface)
            
        if self.current == 'Uitleg_Menu':
            surface.fill((20, 20, 30))
            box = pygame.Rect(WIDTH//2 - 400, HEIGHT//2 - 250, 800, 500)
            # Tablet look
            pygame.draw.rect(surface, (40, 40, 60), box, border_radius=20)
            pygame.draw.rect(surface, (150, 150, 180), box, 8, border_radius=20) # Frame
            
            # Close button (top right of tablet)
            close_btn = pygame.Rect(box.right - 50, box.top + 20, 30, 30)
            pygame.draw.circle(surface, RED, close_btn.center, 15)
            pygame.draw.circle(surface, WHITE, close_btn.center, 15, 2)
            cross = font.render("X", True, WHITE)
            surface.blit(cross, (close_btn.centerx - cross.get_width()//2, close_btn.centery - cross.get_height()//2))

            if self.uitleg_page >= len(self.uitleg_pages): self.uitleg_page = 0
            page_title, icon_key, page_lines = self.uitleg_pages[self.uitleg_page]
            
            # Title
            t_surf = pygame.font.SysFont('Arial', 36, bold=True).render(page_title, True, CYAN)
            surface.blit(t_surf, (WIDTH//2 - t_surf.get_width()//2, box.top + 40))
            
            # Icon
            icon = None
            if icon_key in ICONS:
                icon = ICONS[icon_key]
            elif icon_key == "data" and data_img:
                icon = pygame.transform.smoothscale(data_img, (80, 80))
            elif icon_key == "cat5e_straight":
                # Draw procedural straight cable
                cx, cy = WIDTH//2, box.top + 130
                pygame.draw.line(surface, GREEN, (cx - 40, cy), (cx + 40, cy), 8)
                pygame.draw.rect(surface, GRAY, (cx - 45, cy - 8, 10, 16))
                pygame.draw.rect(surface, GRAY, (cx + 35, cy - 8, 10, 16))
            elif icon_key == "cat5_cross":
                # Draw procedural crossover cable
                cx, cy = WIDTH//2, box.top + 130
                pygame.draw.line(surface, (255, 128, 0), (cx - 40, cy - 10), (cx + 40, cy + 10), 6)
                pygame.draw.line(surface, (255, 128, 0), (cx - 40, cy + 10), (cx + 40, cy - 10), 6)
                pygame.draw.rect(surface, GRAY, (cx - 45, cy - 15, 10, 10))
                pygame.draw.rect(surface, GRAY, (cx - 45, cy + 5, 10, 10))
                pygame.draw.rect(surface, GRAY, (cx + 35, cy - 15, 10, 10))
                pygame.draw.rect(surface, GRAY, (cx + 35, cy + 5, 10, 10))
            elif icon_key in ["ip", "subnet"]:
                 icon = load_icon("Icons", "ip_instellingen.png", (80, 80))
            elif icon_key == "web":
                 icon = load_icon("Icons", "web_browsing.png", (80, 80))
            elif icon_key == "topologie":
                 # Fallback for topology: draw a simple star?
                 pygame.draw.circle(surface, CYAN, (WIDTH//2, box.top + 130), 20, 2)
                 for angle in range(0, 360, 72):
                     rad = math.radians(angle)
                     pygame.draw.line(surface, CYAN, (WIDTH//2, box.top + 130), (WIDTH//2 + math.cos(rad)*40, box.top + 130 + math.sin(rad)*40), 2)
            elif icon_key == "broadcast":
                 pygame.draw.circle(surface, YELLOW, (WIDTH//2, box.top + 130), 10)
                 pygame.draw.circle(surface, YELLOW, (WIDTH//2, box.top + 130), 25, 2)
                 pygame.draw.circle(surface, YELLOW, (WIDTH//2, box.top + 130), 40, 1)

            if icon:
                surface.blit(icon, (WIDTH//2 - icon.get_width()//2, box.top + 90))

            # Lines - Centered
            y = box.top + 200
            for line in page_lines:
                rend = font.render(line, True, WHITE)
                surface.blit(rend, (WIDTH//2 - rend.get_width()//2, y))
                y += 50
                
            # Navigation Arrows
            left_arrow = pygame.Rect(box.left + 20, box.centery - 30, 40, 60)
            right_arrow = pygame.Rect(box.right - 60, box.centery - 30, 40, 60)
            
            if self.uitleg_page > 0:
                pygame.draw.polygon(surface, WHITE, [(left_arrow.right, left_arrow.top), (left_arrow.left, left_arrow.centery), (left_arrow.right, left_arrow.bottom)])
            if self.uitleg_page < len(self.uitleg_pages) - 1:
                pygame.draw.polygon(surface, WHITE, [(right_arrow.left, right_arrow.top), (right_arrow.right, right_arrow.centery), (right_arrow.left, right_arrow.bottom)])
                
            # Page Indicator
            ind = font.render(f"Pagina {self.uitleg_page + 1} / {len(self.uitleg_pages)}", True, GRAY)
            surface.blit(ind, (WIDTH//2 - ind.get_width()//2, box.bottom - 40))
            
        if self.current == 'Level_Select':
            # Background (World map style)
            if bg_road: 
                surface.blit(bg_road, (0, 0))
            else:
                surface.fill((40, 80, 40))
                pygame.draw.rect(surface, (60, 60, 60), (0, 300, 1000, 100))
                pygame.draw.line(surface, YELLOW, (0, 350), (1000, 350), 2)
            
            box = pygame.Rect(WIDTH//2 - 450, HEIGHT//2 - 250, 900, 500)
            # Glass effect box
            glass = pygame.Surface((box.width, box.height), pygame.SRCALPHA)
            glass.fill((20, 20, 40, 200))
            surface.blit(glass, box.topleft)
            pygame.draw.rect(surface, CYAN, box, 4, border_radius=15)
            
            title_font = pygame.font.SysFont('Arial', 40, bold=True)
            t_surf = title_font.render("KIES JE BESTEMMING (LEVELS)", True, YELLOW)
            surface.blit(t_surf, (WIDTH//2 - t_surf.get_width()//2, box.top + 30))
            
            # Level Houses
            house_types = ['House1', 'House2', 'House3', 'House4']
            start_x = box.left + 115
            for i in range(4):
                hx, hy = start_x + i * 220, box.centery
                # House Icon
                icon_key = house_types[i]
                icon = ICONS.get(icon_key)
                if icon:
                    # Scaled up house for menu
                    large_icon = pygame.transform.smoothscale(icon, (130, 130))
                    rect = large_icon.get_rect(center=(hx, hy))
                    surface.blit(large_icon, rect.topleft)
                    
                    # Selection circle (hover effect simulation)
                    mouse_pos = pygame.mouse.get_pos()
                    if math.hypot(mouse_pos[0] - hx, mouse_pos[1] - hy) < 70:
                        pygame.draw.circle(surface, WHITE, (hx, hy), 75, 3)
                    
                    # Label
                    l_text = f"LEVEL {i+1}"
                    l_surf = mission_font.render(l_text, True, YELLOW)
                    surface.blit(l_surf, (hx - l_surf.get_width()//2, hy + 80))
                    
                    # Small desc
                    descs = ["Kabels & Hubs", "Internet Basics", "DHCP & Redundantie", "WiFi & Routing"]
                    d_surf = small_font.render(descs[i], True, CYAN)
                    surface.blit(d_surf, (hx - d_surf.get_width()//2, hy + 110))

            # Close button
            close_btn = pygame.Rect(box.right - 50, box.top + 20, 30, 30)
            pygame.draw.circle(surface, RED, close_btn.center, 15)
            pygame.draw.circle(surface, WHITE, close_btn.center, 15, 2)
            cross = font.render("X", True, WHITE)
            surface.blit(cross, (close_btn.centerx - cross.get_width()//2, close_btn.centery - cross.get_height()//2))
            
            # Vrij Spel (Free Mode) Knop
            btn_freemode = pygame.Rect(box.centerx - 150, box.bottom - 80, 300, 50)
            pygame.draw.rect(surface, (100, 200, 100), btn_freemode, border_radius=10)
            pygame.draw.rect(surface, WHITE, btn_freemode, 3, border_radius=10)
            f_txt = font.render("VRIJ SPEL (FREE MODE)", True, WHITE)
            surface.blit(f_txt, (btn_freemode.centerx - f_txt.get_width()//2, btn_freemode.centery - f_txt.get_height()//2))
            
        if self.transition_alpha > 0:
            s = pygame.Surface((1000, 700), pygame.SRCALPHA)
            s.fill((0,0,0, min(255, max(0, self.transition_alpha))))
            if self.transition_alpha > 100:
                t = font.render(self.trans_text, True, (255,255,255))
                s.blit(t, (500 - t.get_width()//2, 350))
            surface.blit(s, (0,0))

class Mission:
    def __init__(self, text, m_type, target_pos=None, dev_type=None, radius=50, target_count=1):
        self.text = text
        self.type = m_type 
        self.target_pos = target_pos
        self.dev_type = dev_type
        self.radius = radius
        self.target_count = target_count

class MissionSystem:
    def __init__(self):
        self.level = 1
        self.fail_msg = ""
        self.fail_timer = 0
        self.surf_success = False
        self.popup_text = ""
        self.packets_delivered = 0
        self.packets_sent = 0  # counts every SPACE press attempt
        self.overlay_alpha = 0
        self.wifi_timer = 0
        self.wait_timer = 0
        self.collision_seen = False
        self.setup_level()
        
    def setup_level(self):
        global current_cable, sm
        Device.reset_counts()
        L = current_lang
        # Automatisch de juiste kabel selecteren voor het level
        if self.level == 1:
            current_cable = 'Cat 5'
        elif self.level == 2:
            current_cable = 'Cat 5'
        else:
            current_cable = 'Straight'

        if self.level == 1:
            self.missions = [
                Mission("Lees de start-introductie op het scherm.", "INTRO"),
                Mission("Uitleg PC/Laptop/Switch/Hub/Router.\nKlik om door te gaan.", "L1_EXP_ALL"),
                Mission("Missie 1: Plaats een Hub in de cirkel (midden).", "PLACE", target_pos=(500, 350), dev_type="Hub"),
                Mission("Missie 2: Plaats PC 1 (links boven).", "PLACE", target_pos=(350, 250), dev_type="PC", target_count=1),
                Mission("Missie 3: Plaats PC 2 (links midden).", "PLACE", target_pos=(350, 350), dev_type="PC", target_count=2),
                Mission("Missie 4: Plaats PC 3 (links onder).", "PLACE", target_pos=(350, 450), dev_type="PC", target_count=3),
                Mission("Missie 5: Verbind de 3 PC's met de Hub (Cat 5).", "CONNECT_3_PCS"),
                Mission("Missie 6: Druk op SPATIE om vanaf 2 PC's tegelijk data te sturen!", "L1_COLLISION_TEST"),
                Mission("Oeps! Een botsing (Collision). Lees de uitleg.", "EXPLANATION_COLLISION"),
                Mission("Missie 7: Verwijder de Hub (D-toets) en plaats een Switch in de cirkel (links).", "PLACE", target_pos=(200, 350), dev_type="Switch"),
                Mission("Missie 8: Verbind de PC's nu met de Switch.", "CONNECT_3_PCS_SW"),
                Mission("Lees waarom een Switch 'slim' is.", "EXPLANATION_SWITCH_SMART"),
                Mission("Missie 9: Druk op SPATIE. Geen botsingen meer!", "L1_TEST_SWITCH"),
                Mission("Missie 10: Plaats een 4e PC ver weg aan de rechterkant.", "PLACE", target_pos=(900, 550), dev_type="PC", target_count=4),
                Mission("Missie 11: Probeer PC4 met de Switch te verbinden.", "TRY_CONNECT"),
                Mission("Kabel te kort! Lees de uitleg.", "EXPLANATION_CAT5"),
                Mission("Missie 12: Pak de Fiber kabel aan de rechterkant.", "PICK_FIBER"),
                Mission("Hoe werkt Fiber? Bekijk de uitleg over Converters.", "EXPLANATION_FIBER_CHAIN"),
                Mission("Missie 13: Gebruik Converters om PC4 met de Switch te verbinden via Fiber.", "L1_FIBER_CHALLENGE"),
                Mission("Missie 14: Druk op SPATIE om data naar PC 4 te sturen!", "L1_TEST_FIBER"),
                Mission("Level 1 voltooid! Je begrijpt nu Hubs, Switches en Fiber.", "EXPLANATION_1")
            ]
        elif self.level == 2:
            self.packets_sent = 0
            self.packets_delivered = 0
            self.missions = [
                Mission("Intro: We gaan nu met Internet werken!\nKlik om door te gaan.", "INTRO_L2"),
                Mission("Plaats een Router om als poort naar buiten te dienen.", "PLACE", target_pos=(500, 200), dev_type="Router"),
                Mission("Een router krijgt een public IP van jouw ISP (internet provider).\nKlik Router -> IP Instellingen -> Klik op ISP Instellingen.", "CONF_ISP"),
                Mission("Lees de uitleg over ISP gegevens.", "L2_EXPLAIN_ISP"),
                Mission("Vul de Publieke IP gegevens in: 84.197.10.15", "L2_ISP_IP"),
                Mission("Vul het Subnet Masker in: 255.255.255.0", "L2_ISP_SUB"),
                Mission("Vul de Default Gateway in: 84.197.10.1", "L2_ISP_GW"),
                Mission("Vul de Primary DNS in: 8.8.8.8", "L2_ISP_DNS1"),
                Mission("Vul de Secondary DNS in: 8.8.4.4", "L2_ISP_DNS2"),
                Mission("Klik nu op Opslaan om de ISP configuratie te voltooien.", "L2_ISP_SAVE"),
                Mission("Lees de uitleg over Default Gateway en DNS.", "L2_EXPLAIN_GW_DNS"),
                Mission("Stel nu de lokale IP in: 192.168.1.1, Subnet Mask: 255.255.255.0\nKlik op Opslaan.", "CONF_ROUTER"),
                Mission("Mooi! Sluit het venster met de rode bol linksboven.", "CLOSE_WINDOW"),
                Mission("Plaats een PC in het lokale netwerk.", "PLACE", target_pos=(300, 400), dev_type="PC"),
                Mission("Verbind de PC met de Router middels een Cat 5 kabel.", "CONNECT_R"),
                Mission("Stel PC IP in: 192.168.1.2, Subnet Mask: 255.255.255.0\nGateway: 192.168.1.1, DNS: 8.8.8.8", "CONF_PC"),
                Mission("Testen: Terug -> Web Browsing -> Typ 'www.thomasmore.be' -> Go!", "SURF"),
                Mission("Sluit het browservenster met het rode bolletje.", "CLOSE_WINDOW"),
                Mission("Bonus: Plaats een extra PC maar geef hem GEEN IP.", "PLACE", dev_type="PC", target_count=2),
                Mission("Verbind de nieuwe PC ook met de Router.", "CONNECT_R2"),
                Mission("Stuur een pakketje (SPATIE). Hij bereikt de PC zonder IP NIET!", "L2_TEST_IP_FAIL"),
                Mission("Lees waarom een IP-adres essentieel is.", "L2_IP_WHY_POPUP"),
                Mission("Geef de nieuwe PC nu ook een IP (192.168.1.3), Subnet (255.255.255.0),\nGateway (192.168.1.1) en DNS (8.8.8.8).", "CONF_3_PCS"),
                Mission("Stuur nu opnieuw een pakketje (SPATIE). Nu komt het WEL aan!", "L2_FINAL_PACKET_CHECK"),
                Mission("Level 2 voltooid! Je begrijpt nu ISP, Gateways en IP-beveiliging.", "EXPLANATION_2")
            ]
        elif self.level == 3:
            if 'sm' in globals() and sm is not None:
                sm.current = 'World'
                # Reset all scenes for a clean Level 3 start
                for s in sm.scenes.values():
                    s['devices'].clear()
                    s['connections'].clear()
                    s['packets'].clear()
                
                # Setup World Map with Houses (Bovenste rij zijn Huis 1 en Huis 3)
                w_sc = sm.scenes['World']
                house_types = ['House1', 'House2', 'House3']
                w_sc['devices'].append(Device(100, 415, random.choice(house_types), decorative=True))
                w_sc['devices'].append(Device(300, 280, 'House1')) # Huis 1 (Interactief)
                w_sc['devices'].append(Device(500, 280, 'House2')) # Huis 3 (Interactief, type House2 voor mission)
                w_sc['devices'].append(Device(700, 415, random.choice(house_types), decorative=True))
                w_sc['devices'].append(Device(900, 415, random.choice(house_types), decorative=True))
            
            self.missions = [
                Mission("Welkom bij Level 3: Dit is de wereldkaart\nKlik op Huis 1 en daarna op de knipperende 'HUIS BETREDEN' knop.", "L3_START_WORLD"),
                Mission("Plaats de eerste Router in Server Ruimte A (links).", "PLACE", target_pos=(200, 230), dev_type="Router"),
                Mission("Plaats de tweede Router in Server Ruimte B (rechts).", "PLACE", target_pos=(780, 230), dev_type="Router"),
                Mission("Verbind de 2 Routers eerst met een Straight kabel.", "L3_TRY_STRAIGHT"),
                Mission("Foutmelding: Klik op de rode box voor uitleg.", "EXPLANATION_CROSS"),
                Mission("Verbind de 2 Routers nu met de Crossover kabel.", "L3_CONNECT_CROSS"),
                Mission("Top! Plaats nu een Switch in het kantoor.", "PLACE", dev_type="Switch"),
                Mission("Plaats 2 PC's rondom de Switch.", "PLACE", dev_type="PC", target_count=2),
                Mission("Verbind: Router 1->Switch (Straight) en Switch->2x PC.", "L3_CONNECT_LAN"),
                Mission("Klik Router 1 -> ISP Instellingen.", "CONF_ISP"),
                Mission("Lees de uitleg over ISP gegevens voor Huis 1.", "L3_EXPLAIN_ISP_H1"),
                Mission("Vul de ISP IP gegevens in: 193.191.1.20", "L3_H1_ISP_IP"),
                Mission("Vul het Subnet Masker in: 255.255.255.0", "L3_H1_ISP_SUB"),
                Mission("Vul de Default Gateway in: 193.191.1.1", "L3_H1_ISP_GW"),
                Mission("Vul de Primary DNS in: 8.8.8.8", "L3_H1_ISP_DNS1"),
                Mission("Vul de Secondary DNS in: 8.8.4.4", "L3_H1_ISP_DNS2"),
                Mission("Klik nu op Opslaan.", "L3_H1_ISP_SAVE"),
                Mission("Stel Router 1 LAN IP in: 192.168.1.1, Subnet Mask: 255.255.255.0", "CONF_ROUTER"),
                Mission("Klik voor uitleg over DHCP (Dynamic Host Configuration Protocol).", "L3_EXPLAIN_DHCP"),
                Mission("Zet de DHCP Server 'AAN' in de instellingen van Router 1.", "L3_ENABLE_DHCP_SRV"),
                Mission("Zet DHCP aan op BEIDE PC's in hun IP-instellingen.", "L3_USE_DHCP"),
                Mission("Stel Router 2 LAN IP in: 192.168.1.254, Subnet Mask: 255.255.255.0", "L3_H1_R2_LAN"),
                Mission("Zet ook de DHCP Server 'AAN' op Router 2.", "L3_ENABLE_DHCP_SRV_R2"),
                Mission("Plaats een derde PC bij Router 2 en verbind deze (Straight).", "L3_H1_PC3"),
                Mission("Zet PC 3 op DHCP in zijn IP-instellingen.", "L3_H1_DHCP_PC3"),
                Mission("Stuur een pakketje (SPATIE) van PC 1 naar PC 2 en PC 3 door beide routers!", "L3_H1_FINAL_PACKET"),
                Mission("Huis 1 is klaar! We gaan nu terug naar de kaart...", "L3_TO_WORLD_1"),
                Mission("Level 3 voltooid! Selecteer Huis 2 en klik op 'HUIS BETREDEN' voor Level 4.", "L3_END")
            ]
        elif self.level == 4:
            if 'sm' in globals() and sm is not None:
                sm.current = 'World'
                w_sc = sm.scenes['World']
                w_sc['devices'].clear()
                house_types = ['House1', 'House2', 'House3', 'House4']
                w_sc['devices'].append(Device(100, 415, random.choice(house_types), decorative=True))
                w_sc['devices'].append(Device(300, 280, 'House1'))
                w_sc['devices'].append(Device(500, 280, 'House2'))
                w_sc['devices'].append(Device(700, 415, random.choice(house_types), decorative=True))
                w_sc['devices'].append(Device(900, 415, random.choice(house_types), decorative=True))

            self.missions = [
                Mission("Wereldkaart: Selecteer Huis 2 en klik op 'HUIS BETREDEN'.", "L4_START"),
                Mission("Huis 2: Plaats een PC, Switch en de eerste Router.", "L3_H2_START"),
                Mission("Verbind: Router 1 -> Switch -> PC (Straight).", "L3_H2_CONNECT_P1"),
                Mission("Plaats een tweede Router en verbind deze met Router 1 (Crossover).", "L3_H2_R2"),
                Mission("Configureer de LAN IPs van de Routers: R1 (192.168.2.1) en R2 (192.168.3.1) met subnet 255.255.255.0.", "L3_H2_IPS"),
                Mission("Zet de DHCP Server 'AAN' in de instellingen van Router 1.", "L3_ENABLE_DHCP_SRV"),
                Mission("Zet de PC op DHCP in zijn IP-instellingen.", "L3_USE_DHCP"),
                Mission("Plaats een Laptop bij Router 2 en verbind via het WiFi menu (SSID: TM_intern, wachtwoord: iloveITF).", "L3_H2_LAP"),
                Mission("Lees de uitleg over Wi-Fi frequenties.", "EXPLANATION_WIFI"),
                Mission("Stuur een pakketje (SPATIE) van de PC naar de Laptop door beide routers!", "L3_H2_FINAL"),
                Mission("Huis 2 voltooid! Terug naar de Wereldkaart...", "L3_TO_WORLD_2"),
                Mission("Gefeliciteerd! Je hebt alle netwerken afgerond en Level 4 voltooid!\nKlik om door te gaan.", "EXPLANATION_FIN"),
                Mission("Je bent nu in Free Mode. Alle huizen zijn leeggemaakt voor maximale speelruimte. Veel plezier!", "DONE")
            ]
        else:
            # Free Mode (level 99) or any unknown level — no missions, just sandbox
            self.missions = [
                Mission("Vrij Spel — bouw je eigen netwerk! Alle huizen zijn leeggemaakt.", "DONE")
            ]
        self.current_idx = 0
        self.packets_delivered = 0
        self.surf_success = False
        
    def get_current(self):
        if self.current_idx < len(self.missions):
            return self.missions[self.current_idx]
        return None

    def advance(self):
        self.current_idx += 1
        self.overlay_alpha = 0
        self.wifi_timer = 0 # Reset timer on every mission advance to avoid sticky text
        self.packets_sent = 0
        self.packets_delivered = 0

    def draw_mission_text(self, surface, devices, isp_inputs=None):
        mission = self.get_current()
        if not mission or mission.type == "DONE":
            text = get_text('free_mode') if not mission else mission.text
            t_surf = mission_font.render(text, True, WHITE)
            # Display at the bottom instead of top
            surface.blit(t_surf, (WIDTH//2 - t_surf.get_width()//2, HEIGHT - 60))
            return

        # Special guidance for ISP mission
        if mission.type == "FILL_ISP" and isp_inputs:
            ip, sub, gw, dp, ds = isp_inputs
            guidance = "Vul Public IP in (193.190.124.107)"
            if ip.text.strip() == "193.190.124.107":
                guidance = "Vul Subnet Mask in (255.255.255.0)"
                if sub.text.strip() == "255.255.255.0":
                    guidance = "Vul Default Gateway in (193.190.124.1)"
                    if gw.text.strip() == "193.190.124.1":
                         guidance = "Vul Primary DNS in (8.8.8.8)"
                         if dp.text.strip() == "8.8.8.8":
                              guidance = "Vul Secondary DNS in (8.8.4.4)"
                              if ds.text.strip() == "8.8.4.4":
                                   guidance = "Klik nu op Opslaan!"
            
            # Draw guidance at the bottom
            g_surf = font.render(guidance, True, WHITE)
            pygame.draw.rect(surface, (0,0,0,150), (WIDTH//2 - g_surf.get_width()//2 - 10, HEIGHT - 50, g_surf.get_width() + 20, 35))
            surface.blit(g_surf, (WIDTH//2 - g_surf.get_width()//2, HEIGHT - 45))
            return # Don't draw the other redundant texts

        # Redundant cyan text removed as per user request

        lines = mission.text.split('\n')
        if mission.type == "L3_BUILD_H2" and sm.current != "House2":
            lines = ["Klik op 'HUIS BETREDEN' en selecteer Huis 2", "om daar apparatuur te plaatsen."]
            
        y = HEIGHT - 80 # Mission info at bottom
        for l in lines:
            t_surf = mission_font.render(l, True, (239, 233, 244))
            surface.blit(t_surf, (WIDTH//2 - t_surf.get_width()//2, y))
            y += 35

        if mission.type == "L1_EXP_MOUSE":
            # Ghost cable animation between PC1 and Hub
            pcs = [d for d in devices if d.type == 'PC']
            hubs = [d for d in devices if d.type == 'Hub']
            pc1 = next((d for d in pcs if d.name_idx == 1), None)
            hub = hubs[0] if hubs else None
            if pc1 and hub:
                s = abs(math.sin(pygame.time.get_ticks() * 0.005))
                alpha = int(100 + s * 155)
                temp_s = pygame.Surface((1000, 700), pygame.SRCALPHA)
                pygame.draw.line(temp_s, (255, 255, 0, alpha), (pc1.x, pc1.y), (hub.x, hub.y), 5)
                surface.blit(temp_s, (0,0))

        if mission.type == "PLACE" and mission.target_pos:
            if gc_img:
                scaled_gc = pygame.transform.smoothscale(gc_img, (mission.radius*2, mission.radius*2))
                rect = scaled_gc.get_rect(center=mission.target_pos)
                surface.blit(scaled_gc, rect.topleft)
            else:
                pygame.draw.circle(surface, (100, 255, 100), mission.target_pos, mission.radius, 3)

        if mission.type == "PICK_FIBER":
            s = abs(math.sin(pygame.time.get_ticks() * 0.008)) # Blinking effect
            alpha = int(100 + s * 155)
            if arrow_img:
                flipped = pygame.transform.rotate(arrow_img, 180)
                # Drawing with blinking alpha (Surface needed)
                arrow_surf = pygame.Surface(flipped.get_size(), pygame.SRCALPHA)
                arrow_surf.blit(flipped, (0,0))
                arrow_surf.set_alpha(alpha)
                surface.blit(arrow_surf, (720, 130))
            else:
                color = (255, 255, 0, alpha)
                temp_arr = pygame.Surface((1000, 700), pygame.SRCALPHA)
                pygame.draw.line(temp_arr, color, (790, 170), (700, 170), 6)
                pygame.draw.polygon(temp_arr, color, [(700, 170), (720, 150), (720, 190)])
                surface.blit(temp_arr, (0,0))

        # Icon explanations in Level 1 (Dynamic arrow positioning)
        if mission.type.startswith("L1_EXP_"):
            key = mission.type[7:] # Extract 'PC', 'LAP', 'SW', 'HUB', 'RT'
            # Map shorthand to dict keys
            m_key = {'PC': 'PC', 'LAP': 'Laptop', 'SW': 'Switch', 'HUB': 'Hub', 'RT': 'Router'}.get(key)
            if m_key and m_key in btn_modi:
                rb = btn_modi[m_key]
                px, py = rb.centerx, rb.bottom + 10
                s = abs(math.sin(pygame.time.get_ticks() * 0.01))
                pygame.draw.polygon(surface, YELLOW, [(px, py + s*10), (px-10, py+20+s*10), (px+10, py+20+s*10)])
                return # Don't draw the hardcoded one if we found the button
                
        if mission.type.startswith("L1_EXP_") and mission.target_pos:
             px, py = mission.target_pos
             s = abs(math.sin(pygame.time.get_ticks() * 0.01))
             pygame.draw.polygon(surface, YELLOW, [(px, py + 35 + s*10), (px-10, py+55+s*10), (px+10, py+55+s*10)])

        # Blinking arrow for Crossover or Router placement in Level 3
        if mission.type in ("EXPLANATION_CROSS", "L3_CONNECT_CROSS"):
            s = abs(math.sin(pygame.time.get_ticks() * 0.01))
            px, py = btn_cross.x - 40 - s*10, btn_cross.y + 15
            pygame.draw.polygon(surface, YELLOW, [(px, py), (px-20, py-10), (px-20, py+10)])
            pygame.draw.rect(surface, YELLOW, (px-40, py-5, 20, 10))
        elif mission and "PLACE" in mission.type and getattr(mission, 'dev_type', '') == "Router":
            # Point to Router icon
            rb = btn_modi['Router']
            s = abs(math.sin(pygame.time.get_ticks() * 0.01))
            px, py = rb.x + 35, rb.y + 100 + s*10
            pygame.draw.polygon(surface, YELLOW, [(px, py), (px-10, py+20), (px+10, py+20)])
            pygame.draw.rect(surface, YELLOW, (px-5, py+20, 10, 20))

    def draw_overlays(self, surface, devices):
        if self.fail_timer > 0:
            surf = mission_font.render(self.fail_msg, True, RED, BLACK)
            surface.blit(surf, (WIDTH//2 - surf.get_width()//2, 110))
            self.fail_timer -= 1

        mission = self.get_current()
        
        if mission and mission.type == "INTRO":
            if self.overlay_alpha < 255: self.overlay_alpha = min(255, self.overlay_alpha + 15)
            ov_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            box = pygame.Rect(WIDTH//2 - 400, HEIGHT//2 - 200, 800, 400)
            pygame.draw.rect(ov_surf, (40, 40, 50), box)
            pygame.draw.rect(ov_surf, CYAN, box, 3)
            
            lines = [get_text('intro_title'), ""] + LANGS[current_lang]['intro_body']
            y = box.y + 20
            for l in lines:
                surf = font.render(l, True, WHITE)
                ov_surf.blit(surf, (box.x + 400 - surf.get_width()//2, y))
                y += 25
                
            ov_surf.set_alpha(self.overlay_alpha)
            surface.blit(ov_surf, (0,0))
            
        elif mission and mission.type == "EXPLANATION_CAT5":
            if self.overlay_alpha < 255: self.overlay_alpha = min(255, self.overlay_alpha + 15)
            ov_surf = pygame.Surface((1000, 700), pygame.SRCALPHA)
            box = pygame.Rect(500 - 350, 350 - 180, 700, 360)
            pygame.draw.rect(ov_surf, (40, 40, 50), box)
            pygame.draw.rect(ov_surf, RED, box, 3)
            
            text_lines = {
                'nl': ["Oeps! De verbinding is mislukt...", "", "Je probeert data over een te grote afstand te sturen met een Cat 5 kabel.", "Een standaard Cat 5 (koper)kabel is maar geschikt voor maximaal 100 meter.", "Hoe langer de kabel, hoe zwakker je signaal wordt. Dit noemt men 'attenuatie'.", "", "Gelukkig is er fiber! Fiber kan data veel beter en sneller", "sturen doordat dit gebruik maakt van lichtsignalen.", "", "Klik hier ergens in dit vak om verder te gaan"],
                'en': ["Oops! The connection failed...", "", "You are trying to send data over too long a distance with a Cat 5 cable.", "A standard Cat 5 (copper) cable is only suitable for a maximum of 100 meters.", "The longer the cable, the weaker your signal becomes. This is called 'attenuation'.", "", "Fortunately, there is the Cat 5e (enhanced) cable! It can send data better and faster", "because the copper wires are twisted tighter against interference.", "", "Click anywhere in this box to continue"],
                'fr': ["Oups ! La connexion a échoué...", "", "Vous essayez d'envoyer des données sur une trop longue distance avec un câble Cat 5.", "Un câble Cat 5 standard n'est adapté que pour un maximum de 100 mètres.", "Plus le câble est long, plus le signal s'affaibit. C'est ce qu'on appelle 'l'atténuation'.", "", "Heureusement, il existe le câble Cat 5e ! Il envoie les données mieux et plus vite", "car les fils de cuivre sont torsadés plus serrés contre les interférences.", "", "Cliquez ici pour continuer"]
            }
            lines = text_lines.get(current_lang, text_lines['nl'])
            y = box.y + 20
            for l in lines:
                surf = font.render(l, True, WHITE)
                ov_surf.blit(surf, (box.x + 350 - surf.get_width()//2, y))
                y += 28
                
            ov_surf.set_alpha(self.overlay_alpha)
            surface.blit(ov_surf, (0,0))
            
        elif mission and mission.type == "INTRO_L2":
            if self.overlay_alpha < 255: self.overlay_alpha = min(255, self.overlay_alpha + 15)
            ov_surf = pygame.Surface((1000, 700), pygame.SRCALPHA)
            box = pygame.Rect(500 - 350, 350 - 150, 700, 300)
            pygame.draw.rect(ov_surf, (40, 40, 50), box)
            pygame.draw.rect(ov_surf, GREEN, box, 3)
            
            lines = ["WELKOM BIJ LEVEL 2: HET INTERNET", "", "In dit level leer je hoe we een lokaal netwerk verbinden", "met de buitenwereld middels een Internet Service Provider (ISP).", "Denk aan Belgische providers zoals Proximus of Telenet.", "", "Je gaat een Router plaatsen en deze de juiste poort instellen.", "", "Klik in dit vak om te beginnen!"]
            y = box.y + 25
            for l in lines:
                surf = font.render(l, True, WHITE)
                ov_surf.blit(surf, (box.x + 350 - surf.get_width()//2, y))
                y += 28
                
            ov_surf.set_alpha(self.overlay_alpha)
            surface.blit(ov_surf, (0,0))
            
        elif mission and mission.type == "EXPLANATION_2":
            if self.overlay_alpha < 255: self.overlay_alpha = min(255, self.overlay_alpha + 15)
            ov_surf = pygame.Surface((1000, 700), pygame.SRCALPHA)
            box = pygame.Rect(500 - 350, 350 - 180, 700, 360)
            pygame.draw.rect(ov_surf, (20, 20, 40), box)
            pygame.draw.rect(ov_surf, CYAN, box, 3)
            
            lines = ["GEWELDIG! Level 2 succesvol afgerond.", "", "Je hebt nu een PC verbonden met een Router (Gateway).", "Je hebt ook een router ingesteld. Nu kan de PC", "data versturen naar 'www.thomasmore.be' en terug.", "", "Dit is de basis van hoe internet bij jou thuis werkt!", "", "Klik hier om naar Level 3 (Wereldkaart) te gaan!"]
            y = box.y + 25
            for l in lines:
                surf = font.render(l, True, WHITE)
                ov_surf.blit(surf, (box.x + 350 - surf.get_width()//2, y))
                y += 32
                
            ov_surf.set_alpha(self.overlay_alpha)
            surface.blit(ov_surf, (0,0))
            
        elif mission and mission.type == "L3_TO_WORLD_1":
            if self.overlay_alpha < 255: self.overlay_alpha = min(255, self.overlay_alpha + 15)
            ov_surf = pygame.Surface((1000, 700), pygame.SRCALPHA)
            box = pygame.Rect(500 - 350, 350 - 100, 700, 200)
            pygame.draw.rect(ov_surf, (40, 40, 50), box)
            pygame.draw.rect(ov_surf, GREEN, box, 3)
            
            lines = ["Huis 1 is nu lokaal volledig verbonden!", "", "Klik hier om uit te zoomen naar de buitenwereld..."]
            y = box.y + 50
            for l in lines:
                surf = font.render(l, True, WHITE)
                ov_surf.blit(surf, (box.x + 350 - surf.get_width()//2, y))
                y += 35
                
            ov_surf.set_alpha(self.overlay_alpha)
            surface.blit(ov_surf, (0,0))

        elif mission and mission.type == "L3_WORLD_1":
            if sm and sm.transition_state != "NONE": return
            if self.overlay_alpha < 255: self.overlay_alpha = min(255, self.overlay_alpha + 15)
            ov_surf = pygame.Surface((1000, 700), pygame.SRCALPHA)
            box = pygame.Rect(500 - 400, 350 - 150, 800, 300)
            pygame.draw.rect(ov_surf, (40, 40, 50), box)
            pygame.draw.rect(ov_surf, CYAN, box, 3)
            
            lines = ["Je bevindt je nu op de Wereldkaart!", "", "Hier zie je de buitenkant van de lokale netwerken die je bouwt.", "In de verte staat een tweede huis (Huis 2) met een leeg netwerk.", "", "Klik eerst in dit vak om door te gaan", "Klik daarna op de knop 'HUIS BETREDEN' links om in te gaan!"]
            y = box.y + 30
            for l in lines:
                surf = font.render(l, True, WHITE)
                ov_surf.blit(surf, (WIDTH//2 - surf.get_width()//2, y))
                y += 30
                
            ov_surf.set_alpha(self.overlay_alpha)
            surface.blit(ov_surf, (0,0))

        elif mission and mission.type == "L3_TO_WORLD_2":
            if self.overlay_alpha < 255: self.overlay_alpha = min(255, self.overlay_alpha + 15)
            ov_surf = pygame.Surface((1000, 700), pygame.SRCALPHA)
            box = pygame.Rect(500 - 350, 350 - 100, 700, 200)
            pygame.draw.rect(ov_surf, (40, 40, 50), box)
            pygame.draw.rect(ov_surf, GREEN, box, 3)
            
            lines = [
                "Ook Huis 2 is nu klaar!",
                "",
                "Klik hier om terug te keren naar de wereldkaart."
            ]
            y = box.y + 50
            for l in lines:
                surf = font.render(l, True, WHITE)
                ov_surf.blit(surf, (WIDTH//2 - surf.get_width()//2, y))
                y += 35
                
            ov_surf.set_alpha(self.overlay_alpha)
            surface.blit(ov_surf, (0,0))

        elif mission and mission.type == "EXPLANATION_1":
            if self.overlay_alpha < 255: self.overlay_alpha = min(255, self.overlay_alpha + 15)
            ov_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            box = pygame.Rect(WIDTH//2 - 350, HEIGHT//2 - 200, 700, 400)
            pygame.draw.rect(ov_surf, (40, 40, 50), box)
            pygame.draw.rect(ov_surf, CYAN, box, 3)
            
            lines = [
                "GEWELDIG GEDAAN!",
                "",
                "Je hebt geleerd dat koperkabels (Cat 5) beperkt zijn in afstand.",
                "Fiber (glasvezel) is de standaard voor lange afstanden",
                "omdat het kilometers overbrugt zonder signaalverlies.",
                "",
                "Bovendien werkt fiber met licht in plaats van elektriciteit.",
                "Hierdoor is het ongevoelig voor elektronische storingen!",
                "Onthoud wel: je hebt altijd een Media Converter nodig",
                "om glasvezel aan te sluiten op normale koperpoorten.",
                "",
                "Klik ergens om naar Level 2 te gaan."
            ]
            y = box.y + 25
            for l in lines:
                surf = font.render(l, True, WHITE)
                ov_surf.blit(surf, (WIDTH//2 - surf.get_width()//2, y))
                y += 28
                
            ov_surf.set_alpha(self.overlay_alpha)
            surface.blit(ov_surf, (0,0))

        elif mission and mission.type == "EXPLANATION_FIBER_ERROR":
            if self.overlay_alpha < 255: self.overlay_alpha = min(255, self.overlay_alpha + 15)
            ov_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            box = pygame.Rect(WIDTH//2 - 350, HEIGHT//2 - 180, 700, 360)
            pygame.draw.rect(ov_surf, (50, 30, 30), box)
            pygame.draw.rect(ov_surf, RED, box, 4)
            
            lines = [
                "[FIBER CONNECTIE FOUT]",
                "",
                "Wacht even! Je probeert glasvezel in een koperpoort te steken.",
                "Glasvezel werkt met licht en heeft een speciale",
                "Media Converter nodig om de fiber connector om te zetten",
                "naar een RJ45 poort.",
                "",
                "Gebruik de Converter uit het menu. Steek daar de Fiber in,",
                "en trek dan een koperkabel (Cat 5) naar de PC of Hub.",
                "",
                "Klik hier om het opnieuw te proberen."
            ]
            y = box.y + 20
            for l in lines:
                surf = font.render(l, True, WHITE)
                ov_surf.blit(surf, (WIDTH//2 - surf.get_width()//2, y))
                y += 28
                
            ov_surf.set_alpha(self.overlay_alpha)
            surface.blit(ov_surf, (0,0))

        elif mission and mission.type == "EXPLANATION_FIBER_CHAIN":
            if self.overlay_alpha < 255: self.overlay_alpha = min(255, self.overlay_alpha + 15)
            ov_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            box = pygame.Rect(WIDTH//2 - 400, HEIGHT//2 - 200, 800, 420)
            pygame.draw.rect(ov_surf, (40, 40, 60), box)
            pygame.draw.rect(ov_surf, YELLOW, box, 3)
            
            lines = [
                "HOE VERBIND JE GLASVEZEL?",
                "",
                "Je hebt altijd TWEE Media Converters nodig om een gat te overbruggen.",
                "De volgorde is als volgt:",
                "",
                "1. [Switch] --(Cat 5)--> [Converter 1]",
                "2. [Converter 1] --(Fiber)--> [Converter 2]",
                "3. [Converter 2] --(Cat 5)--> [Verre PC]",
                "",
                "Onthoud: Koper (Cat 5) gaat in de RJ45 poort, Fiber in de optische poort.",
                "Een converter heeft beide! Je bouwt dus een 'brug' van licht.",
                "",
                "Klik hier om het zelf te proberen!"
            ]
            y = box.y + 25
            for l in lines:
                surf = font.render(l, True, WHITE)
                ov_surf.blit(surf, (WIDTH//2 - surf.get_width()//2, y))
                y += 28
                
            ov_surf.set_alpha(self.overlay_alpha)
            surface.blit(ov_surf, (0,0))

        elif mission and mission.type == "EXPLANATION_CROSS":
            if self.overlay_alpha < 255: self.overlay_alpha = min(255, self.overlay_alpha + 15)
            ov_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            box = pygame.Rect(WIDTH//2 - 350, HEIGHT//2 - 180, 700, 360)
            pygame.draw.rect(ov_surf, (30, 30, 40), box)
            pygame.draw.rect(ov_surf, (200, 50, 50), box, 4)
            
            lines = [
                "FOUT: Je probeert twee routers te verbinden met een Straight kabel!",
                "",
                "Het belangrijkste verschil zit in de interne draden en de apparatuur:",
                "",
                "1. Straight-through: Draden aan beide kanten in DEZELFDE volgorde.",
                "   GEBRUIK: Verschillende apparaten (PC naar Switch, Router naar Switch).",
                "",
                "2. Crossover: Verzend- en ontvangstlijnen (TX/RX) aan één kant omgedraaid.",
                "   GEBRUIK: Zelfde apparaten (Router naar Router, Switch naar Switch).",
                "",
                "Klik hier om het opnieuw te proberen met de Crossover kabel."
            ]
            y = box.y + 15
            for l in lines:
                surf = font.render(l, True, WHITE)
                ov_surf.blit(surf, (box.x + 350 - surf.get_width()//2, y))
                y += 26
                
            ov_surf.set_alpha(self.overlay_alpha)
            surface.blit(ov_surf, (0,0))

        elif mission and mission.type == "L3_EXPLAIN_DHCP":
            if self.overlay_alpha < 255: self.overlay_alpha = min(255, self.overlay_alpha + 15)
            ov_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            box = pygame.Rect(WIDTH//2 - 350, HEIGHT//2 - 190, 700, 380)
            pygame.draw.rect(ov_surf, (30, 45, 60), box)
            pygame.draw.rect(ov_surf, CYAN, box, 4)
            
            lines = [
                "NIEUW CONCEPT: DHCP",
                "",
                "Handmatig IP-adressen invullen voor honderden PC's is veel werk.",
                "DHCP (Dynamic Host Configuration Protocol) lost dit op!",
                "",
                "- Een Router met DHCP-server deelt automatisch IP's uit aan apparaten.",
                "- Het bespaart tijd en voorkomt fouten (zoals dubbele IP's).",
                "",
                "In deze missie hoef je alleen DHCP 'AAN' te zetten op de PC's.",
                "De Router (die al een IP heeft) doet de rest van het werk!",
                "",
                "Klik hier om verder te gaan."
            ]
            y = box.y + 20
            for l in lines:
                surf = font.render(l, True, WHITE)
                ov_surf.blit(surf, (box.x + 350 - surf.get_width()//2, y))
                y += 28
            ov_surf.set_alpha(self.overlay_alpha)
            surface.blit(ov_surf, (0,0))

        elif mission and mission.type in ("L2_EXPLAIN_ISP", "L3_EXPLAIN_ISP_H1"):
            if self.overlay_alpha < 255: self.overlay_alpha = min(255, self.overlay_alpha + 15)
            ov_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            box = pygame.Rect(WIDTH//2 - 350, HEIGHT//2 - 220, 700, 440)
            pygame.draw.rect(ov_surf, (40, 50, 70), box)
            pygame.draw.rect(ov_surf, YELLOW, box, 4)
            
            if mission.type == "L2_EXPLAIN_ISP":
                target_ip, target_sub, target_gw = "84.197.10.15", "255.255.255.0", "84.197.10.1"
                title = "Level 2 ISP: Telenet Thuisnetwerk"
            else:
                target_ip, target_sub, target_gw = "193.191.1.20", "255.255.255.0", "193.191.1.1"
                title = "Level 3 ISP: Thomas More Campus"

            lines = [
                f"UITLEG: {title}",
                "",
                "De service provider is vergeten jouw router in te stellen dus moeten wij het doen",
                "Vul de volgende gegevens in bij de ISP instellingen:",
                "",
                f"- Public IP: {target_ip}",
                f"- Subnet Mask: {target_sub}",
                f"- Default Gateway: {target_gw}",
                "- Primary DNS: 8.8.8.8",
                "- Secondary DNS: 8.8.4.4",
                "",
                "deze zijn voor iedere router uniek! Elke aansluiting heeft zijn eigen IP.",
                "",
                "Klik hier om de gegevens in te vullen."
            ]
            y = box.y + 20
            for l in lines:
                surf = font.render(l, True, WHITE)
                ov_surf.blit(surf, (box.x + 350 - surf.get_width()//2, y))
                y += 28
            ov_surf.set_alpha(self.overlay_alpha)
            surface.blit(ov_surf, (0,0))

        elif mission and mission.type == "L2_EXPLAIN_GW_DNS":
            if self.overlay_alpha < 255: self.overlay_alpha = min(255, self.overlay_alpha + 15)
            ov_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            box = pygame.Rect(WIDTH//2 - 350, HEIGHT//2 - 220, 700, 440)
            pygame.draw.rect(ov_surf, (30, 50, 60), box)
            pygame.draw.rect(ov_surf, CYAN, box, 4)
            
            lines = [
                "UITLEG: Default Gateway & DNS",
                "",
                "DEFAULT GATEWAY:",
                "Dit is het adres van de 'voordeur' van jouw netwerk.",
                "Als een apparaat data wil sturen naar het internet,",
                "stuurt het alles eerst naar de Gateway (jouw router).",
                "De router weet dan hoe het verder moet naar buiten.",
                "",
                "DNS (Domain Name System):",
                "DNS vertaalt domeinnamen (zoals www.google.com)",
                "naar IP-adressen (zoals 142.250.179.110).",
                "Zonder DNS moet je elk IP-adres uit je hoofd kennen!",
                "",
                "Primary DNS: 8.8.8.8 (Google's hoofd DNS-server)",
                "Secondary DNS: 8.8.4.4 (backup als de primary uitvalt)",
                "",
                "Klik hier om verder te gaan."
            ]
            y = box.y + 15
            for l in lines:
                surf = font.render(l, True, WHITE)
                ov_surf.blit(surf, (box.x + 350 - surf.get_width()//2, y))
                y += 24
            ov_surf.set_alpha(self.overlay_alpha)
            surface.blit(ov_surf, (0,0))

        elif mission and mission.type == "L2_IP_WHY_POPUP":
            if self.overlay_alpha < 255: self.overlay_alpha = min(255, self.overlay_alpha + 15)
            ov_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            box = pygame.Rect(WIDTH//2 - 350, HEIGHT//2 - 180, 700, 360)
            pygame.draw.rect(ov_surf, (40, 50, 70), box)
            pygame.draw.rect(ov_surf, CYAN, box, 4)
            
            lines = [
                "WAAROM IS EEN IP-ADRES BELANGRIJK?",
                "",
                "Zoals je zag, kwam het pakketje NIET aan bij de nieuwe PC.",
                "Zonder IP-adres is een apparaat onzichtbaar op het netwerk.",
                "",
                "Vergelijk het met een huis zonder huisnummer:",
                "De postbode (het pakketje) weet wel waar de straat is,",
                "maar kan de brief niet afleveren omdat het adres ontbreekt!",
                "",
                "Een IP-adres zorgt ervoor dat data de juiste bestemming vindt.",
                "",
                "Klik hier om de nieuwe PC ook een adres te geven."
            ]
            y = box.y + 30
            for l in lines:
                surf = font.render(l, True, WHITE)
                ov_surf.blit(surf, (box.x + 350 - surf.get_width()//2, y))
                y += 26
            ov_surf.set_alpha(self.overlay_alpha)
            surface.blit(ov_surf, (0,0))

            ov_surf.set_alpha(self.overlay_alpha)
            surface.blit(ov_surf, (0,0))

        elif mission and mission.type == "L1_EXP_ALL":
            if self.overlay_alpha < 255: self.overlay_alpha = min(255, self.overlay_alpha + 15)
            ov_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            box = pygame.Rect(WIDTH//2 - 400, HEIGHT//2 - 250, 800, 500)
            pygame.draw.rect(ov_surf, (30, 30, 40), box)
            pygame.draw.rect(ov_surf, CYAN, box, 3)
            
            lines = [
                "BASIS APPARATUUR",
                "",
                "PC: Je vaste werkstation.Gebruikt kabels om te verbinden met andere.",
                "LAPTOP: Flexibel werkstation. Kan kabel of Wi-Fi gebruiken.",
                "HUB: Een verdeeldoos. Stuurt data naar iedereen er op aangesloten.",
                "SWITCH: Een slimme Hub. Stuurt data alleen naar de juiste poort.",
                "ROUTER: De poort naar de rest van de wereld (Internet).",
                "CONVERTER: Vertaalt lichtsignalen uit glasvezel naar elektrische signalen voor koperkabels (Cat5).",
                "",
                "Klik hier om te beginnen met je eerste netwerk!"
            ]
            y = box.y + 30
            for l in lines:
                surf = font.render(l, True, WHITE)
                ov_surf.blit(surf, (WIDTH//2 - surf.get_width()//2, y))
                y += 45
            ov_surf.set_alpha(self.overlay_alpha)
            surface.blit(ov_surf, (0,0))

        elif mission and mission.type == "EXPLANATION_COLLISION":
            if self.overlay_alpha < 255: self.overlay_alpha = min(255, self.overlay_alpha + 15)
            ov_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            box = pygame.Rect(WIDTH//2 - 350, HEIGHT//2 - 200, 700, 400)
            pygame.draw.rect(ov_surf, (40, 30, 30), box)
            pygame.draw.rect(ov_surf, RED, box, 4)
            
            lines = [
                "COLLISION: De Hub is te 'dom'!",
                "",
                "Een Hub begrijpt niet wie de ontvanger is.",
                "Hij stuurt alle binnenkomende data naar IEDEREEN tegelijk.",
                "",
                "Als twee PC's tegelijk praten, botsen de elektrische signalen",
                "in de Hub. De data raakt beschadigd en gaat verloren.",
                "Dit noemen we een 'Collision'.",
                "",
                "Klik hier om te leren hoe we dit oplossen met een Switch."
            ]
            y = box.y + 30
            for l in lines:
                surf = font.render(l, True, WHITE)
                ov_surf.blit(surf, (WIDTH//2 - surf.get_width()//2, y))
                y += 28
            ov_surf.set_alpha(self.overlay_alpha)
            surface.blit(ov_surf, (0,0))

        elif mission and mission.type == "EXPLANATION_SWITCH_SMART":
            if self.overlay_alpha < 255: self.overlay_alpha = min(255, self.overlay_alpha + 15)
            ov_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            box = pygame.Rect(WIDTH//2 - 350, HEIGHT//2 - 200, 700, 400)
            pygame.draw.rect(ov_surf, (30, 40, 50), box)
            pygame.draw.rect(ov_surf, GREEN, box, 4)
            
            lines = [
                "DE SWITCH: Het 'slimme' apparaat",
                "",
                "Een Switch is veel slimmer dan een Hub.",
                "Het onthoudt welk apparaat op welke poort zit.",
                "",
                "Als PC 1 data stuurt naar PC 2, stuurt de Switch dit",
                "ALLEEN naar PC 2. Andere poorten blijven vrij.",
                "",
                "Hierdoor kunnen meerdere PC's tegelijk communiceren",
                "zonder dat er botsingen ontstaan. Veel efficiënter!",
                "",
                "Klik hier om het te testen!"
            ]
            y = box.y + 30
            for l in lines:
                surf = font.render(l, True, WHITE)
                ov_surf.blit(surf, (WIDTH//2 - surf.get_width()//2, y))
                y += 28
            ov_surf.set_alpha(self.overlay_alpha)
            surface.blit(ov_surf, (0,0))

        elif mission and mission.type == "EXPLANATION_WIFI":
            if self.overlay_alpha < 255: self.overlay_alpha = min(255, self.overlay_alpha + 15)
            ov_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            box = pygame.Rect(WIDTH//2 - 350, HEIGHT//2 - 200, 700, 400)
            pygame.draw.rect(ov_surf, (30, 40, 60), box)
            pygame.draw.rect(ov_surf, YELLOW, box, 4)
            
            lines = [
                "UITLEG: Wi-Fi Frequenties",
                "Wi-Fi werkt op verschillende frequenties.",
                "",
                "2.4GHz is de 'vrachtwagen':",
                "Hij komt overal doorheen (muren, plafonds) en gaat ver,",
                "maar is niet zo snel.",
                "",
                "5GHz is de 'sportwagen':",
                "Hij is supersnel, maar heeft moeite met muren",
                "en verliest snel zijn bereik.",
                "",
                "Als jouw device beide frequentie banden ondersteunt",
                "dan kiest het automatisch de beste band voor het beste signaal",
                "",
                "Klik hier om verder te gaan."
            ]
            y = box.y + 20
            for l in lines:
                surf = font.render(l, True, WHITE)
                ov_surf.blit(surf, (box.x + 350 - surf.get_width()//2, y))
                y += 24
            ov_surf.set_alpha(self.overlay_alpha)
            surface.blit(ov_surf, (0,0))

    def check_conditions(self, devices, connections, packets, sm=None, active_window=None, active_device=None, isp_inputs=None):
        if self.wifi_timer > 0:
            self.wifi_timer -= 1
            
        mission = self.get_current()
        if not mission: return

        if mission.type == "PLACE":
            # Count the existing devices of this type
            existing_count = sum(1 for d in devices if d.type == mission.dev_type)
            target_count = getattr(mission, 'target_count', 1)
            
            if existing_count >= target_count:
                # If target_pos is specified, we must check if THEY are inside. 
                # (Simple check: if at least target_count are in their zones)
                if hasattr(mission, 'target_pos') and mission.target_pos:
                    # Specific spot placement logic
                    in_zone_count = 0
                    for d in devices:
                        if d.type == mission.dev_type:
                            dist = math.hypot(d.x - mission.target_pos[0], d.y - mission.target_pos[1])
                            if dist <= mission.radius:
                                in_zone_count += 1
                    if in_zone_count >= 1: # At least one must be in the zone (the newly placed one)
                        self.advance()
                        return
                else:
                    # Free placement mission - just check the count
                    self.advance()
                    return
                        
        elif mission.type == "CONNECT_3_PCS":
            # Check if 3 PCs are connected to a Hub
            pc_hub_count = 0
            for c in connections:
                if c.is_valid and {c.d1.type, c.d2.type} == {'PC', 'Hub'}:
                    pc_hub_count += 1
            if pc_hub_count >= 3:
                self.advance()
                return
        elif mission.type == "L1_COLLISION_TEST":
            # Wait until collision starts
            if any(d.type == 'Hub' and d.collision_timer > 0 for d in devices):
                self.collision_seen = True
            
            # Advance only after packets are gone and collision was witnessed
            if getattr(self, 'collision_seen', False) and not packets:
                self.advance()
                self.collision_seen = False # reset for future
                return
        elif mission.type == "L1_REPLACE_HUB":
            # Check if Hub is gone and Switch is present
            hub_exists = any(d.type == 'Hub' for d in devices)
            sw_exists = any(d.type == 'Switch' for d in devices)
            if not hub_exists and sw_exists:
                self.advance()
                return
        elif mission.type == "CONNECT_3_PCS_SW":
            # Check if 3 PCs are connected to a Switch
            pc_sw_count = 0
            for c in connections:
                if c.is_valid and {c.d1.type, c.d2.type} == {'PC', 'Switch'}:
                    pc_sw_count += 1
            if pc_sw_count >= 3:
                self.packets_delivered = 0 
                self.advance()
                return
        elif mission.type == "L1_TEST_SWITCH":
            # Advance when player presses SPACE and packets are delivered
            if self.packets_delivered >= 2:
                self.advance()
                return
        elif mission.type == "L1_FIBER_CHALLENGE":
            # Switch -> Cat5 -> Conv1 -> Fiber -> Conv2 -> Cat5 -> PC4
            sw = next((d for d in devices if d.type == 'Switch'), None)
            pc4 = next((d for d in devices if d.type == 'PC' and d.name_idx == 4), None)
            if sw and pc4:
                p = find_path(devices, connections, sw, pc4)
                if p and len(p) == 4:
                    # p[0]=Switch, p[1]=Conv, p[2]=Conv, p[3]=PC4
                    if p[1].type == 'Converter' and p[2].type == 'Converter':
                        c1 = next((c for c in connections if c.is_valid and {c.d1, c.d2} == {p[0], p[1]}), None)
                        c2 = next((c for c in connections if c.is_valid and {c.d1, c.d2} == {p[1], p[2]}), None)
                        c3 = next((c for c in connections if c.is_valid and {c.d1, c.d2} == {p[2], p[3]}), None)
                        
                        if c1 and c2 and c3:
                            if c1.cable_type == 'Cat 5' and c2.cable_type == 'Fiber' and c3.cable_type == 'Cat 5':
                                self.packets_delivered = 0
                                self.advance()
                                return
        
        elif mission.type == "L1_TEST_FIBER":
            # End level when data reaches PC4
            if self.packets_delivered >= 1:
                self.advance()
                return

        elif mission.type == "TRY_CONNECT":
            # Check if any connection attempt was made to the far PC
            for c in connections:
                if {c.d1.type, c.d2.type} == {'PC', 'Switch'} and c.distance > 400:
                    self.advance()
                    return
                    
        elif mission.type == "PICK_FIBER":
            if current_cable == 'Fiber':
                self.advance()
                return
        elif mission.type == "PLACE_CONVERTERS":
            if sum(1 for d in devices if d.type == 'Converter') >= 2:
                self.advance()
                return
        elif mission.type == "CONNECT_CONV_RJ45":
            c1 = any(c.is_valid and {c.d1.type, c.d2.type} == {'PC', 'Converter'} for c in connections)
            c2 = any(c.is_valid and {c.d1.type, c.d2.type} in ({'Hub', 'Converter'}, {'Switch', 'Converter'}) for c in connections)
            if c1 and c2:
                self.advance()
                return
        elif mission.type == "CONNECT_FIBER_MAIN":
            if any(c.is_valid and c.d1.type == 'Converter' and c.d2.type == 'Converter' and c.cable_type == 'Fiber' for c in connections):
                self.advance()
                return
        elif mission.type == "L2_LEAVE_EMPTY":
            p4 = next((d for d in devices if d.type == 'PC' and d.name_idx == 3), None)
            if p4 and not p4.ip:
                self.advance()
                return
        elif mission.type == "L2_TEST_IP_FAIL":
            # Wait until at least one packet was sent AND all packets have finished moving
            if mission_sys.packets_sent > 0 and not packets:
                self.advance()
                return
        elif mission.type == "L2_FINAL_PACKET_CHECK":
            # Check if at least one packet successfully reached its destination
            if self.packets_delivered > 0 and not packets:
                self.advance()
                return
        elif mission.type == "CONF_3_PCS":
            count = sum(1 for d in devices if d.type == 'PC' and d.ip and d.subnet and d.gateway and d.dns == "8.8.8.8")
            if count >= 2:
                self.packets_delivered = 0  # Reset zodat L2_FINAL_PACKET_CHECK niet meteen doorskipt
                self.packets_sent = 0
                self.advance()
        elif mission.type == "L2_FINAL_PACKET":
            if self.packets_delivered >= 2: self.advance() # 1 from start, 1 now
            for d in devices:
                if d.type == 'Router' and getattr(d, 'isp', None) in ("Proximus", "Telenet"):
                    self.advance()
                    return
        elif mission.type == "CONF_ISP":
            pass # Wordt afgehandeld in de klik van de knop
        elif mission.type == "L2_ISP_IP":
            if active_window == "ISP" and isp_inputs[0].text.strip() == "84.197.10.15":
                self.advance()
        elif mission.type == "L2_ISP_SUB":
            if active_window == "ISP" and isp_inputs[1].text.strip() == "255.255.255.0":
                self.advance()
        elif mission.type == "L2_ISP_GW":
            if active_window == "ISP" and isp_inputs[2].text.strip() == "84.197.10.1":
                self.advance()
        elif mission.type == "L2_ISP_DNS1":
            if active_window == "ISP" and isp_inputs[3].text.strip() == "8.8.8.8":
                self.advance()
        elif mission.type == "L2_ISP_DNS2":
            if active_window == "ISP" and isp_inputs[4].text.strip() == "8.8.4.4":
                self.advance()
        elif mission.type == "L2_ISP_SAVE":
            for d in devices:
                if d.type == 'Router' and getattr(d, 'isp', None) == "Manual":
                    if (d.public_ip == "84.197.10.15" and 
                        d.public_subnet == "255.255.255.0" and 
                        d.public_gw == "84.197.10.1"):
                        self.advance()
                        return

        elif mission.type == "L3_H1_ISP_IP":
            if active_window == "ISP" and isp_inputs[0].text.strip() == "193.191.1.20":
                self.advance()
        elif mission.type == "L3_H1_ISP_SUB":
            if active_window == "ISP" and isp_inputs[1].text.strip() == "255.255.255.0":
                self.advance()
        elif mission.type == "L3_H1_ISP_GW":
            if active_window == "ISP" and isp_inputs[2].text.strip() == "193.191.1.1":
                self.advance()
        elif mission.type == "L3_H1_ISP_DNS1":
            if active_window == "ISP" and isp_inputs[3].text.strip() == "8.8.8.8":
                self.advance()
        elif mission.type == "L3_H1_ISP_DNS2":
            if active_window == "ISP" and isp_inputs[4].text.strip() == "8.8.4.4":
                self.advance()
        elif mission.type == "L3_H1_ISP_SAVE":
            for d in devices:
                if d.type == 'Router' and getattr(d, 'isp', None) == "Manual":
                    if (d.public_ip == "193.191.1.20" and 
                        d.public_subnet == "255.255.255.0" and 
                        d.public_gw == "193.191.1.1"):
                        self.advance()
                        return
        elif mission.type == "L2_PING_TEST":
            # Wordt afgehandeld in terminal logic
            pass
                        
        elif mission.type == "CONNECT_R":
            for c in connections:
                if c.is_valid and ((c.d1.type == 'PC' and c.d2.type == 'Router') or (c.d1.type == 'Router' and c.d2.type == 'PC')):
                    self.advance()
                    return

        elif mission.type == "CONNECT_R2":
            # Count all PC<->Router connections (need at least 2 for the bonus PC)
            pc_router_count = sum(
                1 for c in connections
                if c.is_valid and {c.d1.type, c.d2.type} == {'PC', 'Router'}
            )
            if pc_router_count >= 2:
                self.advance()
                return
                    
        elif mission.type == "CONF_ROUTER":
            for d in devices:
                if d.type == 'Router' and d.ip == "192.168.1.1" and d.subnet in ("255.255.255.0", "24"):
                    self.advance()
                    return
                    
        elif mission.type == "CONF_PC":
            # Dit wordt nu afgehandeld in de Save knop logica voor betere controle
            return
        elif mission.type == "L3_CONNECT_CROSS":
            for c in connections:
                if c.is_valid and c.d1.type == 'Router' and c.d2.type == 'Router':
                    if c.cable_type == 'Crossover':
                        self.advance()
                        return
        elif mission.type == "L3_H1_R2_LAN":
            # Check for Router 2 LAN configuration
            for d in devices:
                if d.type == 'Router' and d.ip == "192.168.1.254" and d.subnet == "255.255.255.0":
                    self.advance()
                    return

        elif mission.type == "L3_H1_PC3":
            # Check if 3 PCs and 2 Routers are present and at least one PC is connected to a router
            pcs = [d for d in devices if d.type == 'PC']
            routers = [d for d in devices if d.type == 'Router']
            if len(pcs) >= 3 and len(routers) >= 2:
                for c in connections:
                    if c.is_valid and {c.d1.type, c.d2.type} == {'PC', 'Router'}:
                        self.advance()
                        return

        elif mission.type == "L3_H1_DHCP_PC3":
            pcs = [d for d in devices if d.type == 'PC']
            if len(pcs) >= 3 and all(p.dhcp for p in pcs):
                self.advance()
                self.packets_delivered = 0
                return

        elif mission.type == "L3_H1_FINAL_PACKET":
            # Wait for 2 packets delivered (to PC2 and PC3)
            if self.packets_delivered >= 2 and not packets:
                if self.wait_timer == 0:
                    self.wait_timer = 60 # ~1 second at 60 FPS
                
                self.wait_timer -= 1
                if self.wait_timer <= 1:
                    self.advance()
                    self.wait_timer = 0
                    return
        elif mission.type == "L3_START_WORLD":
            if sm.current == 'House1' and sm.transition_state == "NONE":
                self.advance()
                return
                
        elif mission.type == "L3_WORLD_2_IN":
             if sm.current == 'House2' and sm.transition_state == "NONE":
                 self.advance()
                 return
                        
        elif mission.type == "L3_PLACE_RS":
            has_r = sum(1 for d in devices if d.type == 'Router')
            has_s = sum(1 for d in devices if d.type == 'Switch')
            if has_r >= 1 and has_s >= 1: self.advance()
            
        elif mission.type == "L3_PLACE_PC":
            if sum(1 for d in devices if d.type == 'PC') >= 2: self.advance()
            
        elif mission.type == "L3_CONNECT_LAN":
            r_s = False
            s_p = 0
            for c in connections:
                if not c.is_valid: continue
                types = {c.d1.type, c.d2.type}
                if types == {'Router', 'Switch'}: r_s = True
                if types == {'Switch', 'PC'}: s_p += 1
            if r_s and s_p >= 2: self.advance()

        elif mission.type == "L3_EXPLAIN_DHCP":
             # Dismissed via click logic in loop (handled by overlay_alpha check)
             pass

        elif mission.type == "L3_USE_DHCP":
            pcs = [d for d in devices if d.type == 'PC']
            if len(pcs) >= 2 and all(d.dhcp for d in pcs):
                self.advance()
                return
            
        elif mission.type == "L3_WIFI_PLACE":
            connected = False
            for c in connections:
                if c.cable_type == 'Wi-Fi' and c.is_valid:
                    connected = True
                    break
            
            if connected:
                if self.wifi_timer <= 0:
                    self.wifi_timer = 270 # 4.5 seconds (requested)
                
                if self.wifi_timer <= 1: # 1 to avoid re-triggering 240 logic above next frame
                    self.advance()
                    self.wifi_timer = 0
            else:
                self.wifi_timer = 0
                    
        elif mission.type == "L3_H2_START":
            has_p = any(d.type == 'PC' for d in devices)
            has_s = any(d.type == 'Switch' for d in devices)
            has_r = any(d.type == 'Router' for d in devices)
            if has_p and has_s and has_r: self.advance()
            
        elif mission.type == "L3_H2_CONNECT_P1":
            # PC -> Switch -> Router 1
            p_s = any(c.is_valid and {c.d1.type, c.d2.type} == {'PC', 'Switch'} for c in connections)
            s_r = any(c.is_valid and {c.d1.type, c.d2.type} == {'Switch', 'Router'} for c in connections)
            if p_s and s_r: self.advance()

        elif mission.type == "L3_H2_R2":
            for c in connections:
                if c.is_valid and c.d1.type == 'Router' and c.d2.type == 'Router':
                    if c.cable_type == 'Crossover':
                        self.advance()
                        return

        elif mission.type == "L3_H2_IPS":
            # R1(192.168.2.1), R2(192.168.3.1)
            r1 = next((d for d in devices if d.type == 'Router' and d.name_idx == 1), None)
            r2 = next((d for d in devices if d.type == 'Router' and d.name_idx == 2), None)
            if r1 and r2:
                if r1.ip == "192.168.2.1" and r2.ip == "192.168.3.1":
                    self.advance()
                    return
                    
        elif mission.type == "L3_H2_LAP":
            lap = next((d for d in devices if d.type == 'Laptop'), None)
            if lap:
                # Check if connected via Wi-Fi
                is_wifi = any(c.cable_type == 'Wi-Fi' and (c.d1 == lap or c.d2 == lap) for c in connections)
                if is_wifi:
                    self.advance()
                    self.packets_delivered = 0
                    return
        
        elif mission.type == "L3_H2_FINAL":
            if self.packets_delivered >= 1 and not packets:
                self.advance()
                return

        elif mission.type == "L4_START":
            if sm.current == 'House2' and sm.transition_state == "NONE":
                self.advance()
                return
        
        elif mission.type == "L3_END":
            # Optional: Advance if they click House 2, but we handle that in main() clicks
            pass

        elif mission.type == "L3_TO_WORLD_2":
             # Transition handled by click logic in overlays
             pass

        elif mission.type == "L3_BUILD_H2":
            # Deprecated but kept for safety if any state refers to it
            has_r = sum(1 for d in devices if d.type == 'Router')
            has_s = sum(1 for d in devices if d.type == 'Switch')
            has_p = sum(1 for d in devices if d.type == 'PC')
            if has_r >= 1 and has_s >= 1 and has_p >= 1:
                r_s = False
                s_p = False
                for c in connections:
                    if not c.is_valid: continue
                    types = {c.d1.type, c.d2.type}
                    if types == {'Router', 'Switch'}: r_s = True
                    if types == {'Switch', 'PC'}: s_p = True
                if r_s and s_p:
                    self.advance()
                    
        elif mission.type == "L3_CONNECT_WAN":
            for c in connections:
                if c.is_valid and c.cable_type == 'WAN Fiber':
                    if {c.d1.type, c.d2.type} == {'House1', 'House2'}:
                        self.advance()
                        return
                        
        elif mission.type == "L3_SEND_P_WAN":
            # Check if a packet has travelled between House 1 and House 2
            # For simplicity, we can check delivered packets if they were across WAN
            if self.packets_delivered >= 1 and len(packets) == 0:
                self.advance()
                return
                        
        elif mission.type == "PACKET":
            if self.packets_delivered > 0 and len(packets) == 0:
                self.advance()
                return

def find_path(devices, connections, start_dev, target_dev):
    # Check if start and target themselves are valid (must have IP if they are L3 devices, but only Level 2+)
    if mission_sys.level >= 2:
        for d in [start_dev, target_dev]:
            if d.type in ('PC', 'Laptop', 'Router') and (not d.ip or not d.ip.strip()):
                return None

    adj = {d.id: [] for d in devices}
    for c in connections:
        if c.is_valid:
            # Only allow neighbor if it's a "pass-through" device (Switch/Hub) 
            # OR if it's a configured L3 device (PC/Laptop/Router with IP)
            for d1, d2 in [(c.d1, c.d2), (c.d2, c.d1)]:
                can_pass = True
                if mission_sys.level >= 2 and d2.type in ('PC', 'Laptop', 'Router'):
                    if not d2.ip or not d2.ip.strip():
                        can_pass = False
                
                if can_pass:
                    adj[d1.id].append(d2)
    
    queue = [[start_dev]]
    visited = set([start_dev.id])
    while queue:
        path = queue.pop(0)
        curr = path[-1]
        
        if curr.id == target_dev.id:
            return path
            
        for neighbor in adj[curr.id]:
            if neighbor.id not in visited:
                visited.add(neighbor.id)
                queue.append(path + [neighbor])
    return None

def find_path_to_type(devices, connections, start_dev, dev_type='Router'):
    # Start must have IP if it's L3
    if start_dev.type in ('PC', 'Laptop', 'Router') and (not start_dev.ip or not start_dev.ip.strip()):
        return None

    adj = {d.id: [] for d in devices}
    for c in connections:
        if c.is_valid:
            for d1, d2 in [(c.d1, c.d2), (c.d2, c.d1)]:
                can_pass = True
                if d2.type in ('PC', 'Laptop', 'Router'):
                    if not d2.ip or not d2.ip.strip():
                        can_pass = False
                if can_pass:
                    adj[d1.id].append(d2)
    
    queue = [[start_dev]]
    visited = set([start_dev.id])
    while queue:
        path = queue.pop(0)
        curr = path[-1]
        
        if curr.type == dev_type:
            return path
            
        for neighbor in adj[curr.id]:
            if neighbor.id not in visited:
                visited.add(neighbor.id)
                queue.append(path + [neighbor])
    return None

def main():
    global sm, mission_sys, devices, connections, packets, current_mode, current_cable, btn_modi, packet_flash_timer
    sm = SceneManager()
    mission_sys = MissionSystem()
    
    # OS Inputs
    ip_input = TextInput(WIDTH//2 - 95, HEIGHT//2 - 45, 200, 30)
    subnet_input = TextInput(WIDTH//2 - 95, HEIGHT//2 + 15, 200, 30)
    gw_input = TextInput(WIDTH//2 - 95, HEIGHT//2 + 75, 200, 30)
    dns_input = TextInput(WIDTH//2 - 95, HEIGHT//2 + 135, 200, 30)
    url_input = TextInput(WIDTH//2 - 100, HEIGHT//2, 250, 40, "www.")
    term_input = TextInput(WIDTH//2 - 240, HEIGHT//2 + 115, 480, 30, ">")
    wifi_pwd_input = TextInput(WIDTH//2 - 100, HEIGHT//2, 200, 30)
    wifi_pwd_input.password_mode = True
    
    # ISP Public Inputs
    isp_ip_input = TextInput(WIDTH//2 - 100, HEIGHT//2 - 100, 200, 30)
    isp_subnet_input = TextInput(WIDTH//2 - 100, HEIGHT//2 - 50, 200, 30)
    isp_gw_input = TextInput(WIDTH//2 - 100, HEIGHT//2, 200, 30)
    isp_dns_p_input = TextInput(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 30)
    isp_dns_s_input = TextInput(WIDTH//2 - 100, HEIGHT//2 + 100, 200, 30)
    
    term_input = TextInput(WIDTH//2 - 200, HEIGHT//2 + 100, 400, 30, default=">")
    term_output = ["Router Console v1.0", "Type 'help' for commands."]
    
    error_msg = ""
    error_timer = 0
    
    dragging = False
    drag_start_dev = None
    selected_house = None
    mouse_pos = (0, 0)
    mouse_press_tick = 0  # For hold-to-drag safety
    HOLD_THRESHOLD_MS = 700  # ms before it's considered a 'hold'
    
    active_device = None
    active_window = None # "MENU", "IP", "WEB"
    ui_alpha = 0
    
    debug_skip_timer = 0
    
    clock = pygame.time.Clock()
    
    while True:
        curr = sm.get_current()
        devices = curr['devices']
        connections = curr['connections']
        packets = curr['packets']
        
        # DEBUG SKIP (F + K for 2s)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_f] and keys[pygame.K_k]:
            debug_skip_timer += 1
            if debug_skip_timer >= 120:
                mission_sys.level = 3
                devices.clear()
                connections.clear()
                packets.clear()
                mission_sys.setup_level()
                sm.current = "House1"
                current_mode = "PC"
                debug_skip_timer = 0
        else:
            debug_skip_timer = 0
            
        sm.update()
        if sm.transition_state == "FADE_IN" and sm.target_scene == "World":
            current_mode = None
            current_cable = None # Reset kabel bij binnenkomst Wereldkaart voor 'Huis Betreden' modus
            selected_house = None # Reset selectie bij terugkomst op kaart
            
        m = mission_sys.get_current()
                
        # Scene drawing
        if sm.current == 'World':
            if bg_road: 
                screen.blit(bg_road, (0, 0))
            else:
                screen.fill((40, 80, 40))
                pygame.draw.rect(screen, (60, 60, 60), (0, 300, 1000, 100))
                pygame.draw.line(screen, YELLOW, (0, 350), (1000, 350), 2)
        elif sm.current == 'Start':
            sm.draw_start_screen(screen)
        else:
            # Alle andere scènes (Level 1, Level 2, Huizen) gebruiken de kamer-achtergrond
            if bg_level:
                screen.blit(bg_level, (0, 0))
            else:
                screen.fill(BLACK)
        
        # --- House 1 Special Layout: Ground Floor (Level 3) ---
        if sm.current == 'House1' and mission_sys.level == 3:
            # Blueprint-style ground floor
            wc = (100, 100, 110) # Wall color
            # Outer walls
            pygame.draw.rect(screen, wc, (40, 110, 920, 560), 5)
            
            # Internal partitions
            # Horizontal corridor wall
            pygame.draw.line(screen, wc, (40, 320), (960, 320), 4)
            
            # Vertical walls for Server Rooms (Top row)
            pygame.draw.line(screen, wc, (340, 110), (340, 320), 4)
            pygame.draw.line(screen, wc, (660, 110), (660, 320), 4)
            
            # Room Labels
            r_font = pygame.font.SysFont("Arial", 18, bold=True)
            
            # Server Rooms
            s1 = r_font.render("SERVER ROOM A (SECURE)", True, (130, 130, 150))
            screen.blit(s1, (190 - s1.get_width()//2, 130))
            
            s2 = r_font.render("SERVER ROOM B (BACKUP)", True, (130, 130, 150))
            screen.blit(s2, (500 - s2.get_width()//2, 130))
            
            s3 = r_font.render("OPSLAG / TECH ROOM", True, (130, 130, 150))
            screen.blit(s3, (810 - s3.get_width()//2, 130))
            
            # Main Area
            main_a = r_font.render("OPEN KANTOOR / WERKRUIMTE", True, (130, 130, 150))
            screen.blit(main_a, (500 - main_a.get_width()//2, 450))
            
            # Corridor label
            corr = small_font.render("GANG / CORRIDOR", True, (100, 100, 100))
            screen.blit(corr, (500 - corr.get_width()//2, 295))

            # Doors (Gaps)
            pygame.draw.rect(screen, (30, 30, 35), (140, 315, 60, 10)) # Door to Room A
            pygame.draw.rect(screen, (30, 30, 35), (470, 315, 60, 10)) # Door to Room B
            pygame.draw.rect(screen, (30, 30, 35), (780, 315, 60, 10)) # Door to Tech
        
        # --- Visual feedback for selected house (World Map) ---
        if sm.current == 'World' and selected_house:
            # Pulsing ring around selected house
            s = abs(math.sin(pygame.time.get_ticks() * 0.01))
            alpha = int(100 + s * 155)
            pulse_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(pulse_surf, (100, 255, 100, alpha), (60, 60), 55, 4)
            screen.blit(pulse_surf, (selected_house.x - 60, selected_house.y - 60))
            
            # Hint text near button
            hint = font.render(f"<<< KLIK HIER OM {selected_house.type.upper()} TE BETREDEN!", True, YELLOW)
            # Add blinking to hint
            if (pygame.time.get_ticks() // 500) % 2 == 0:
                screen.blit(hint, (200, 120))
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            elif event.type == pygame.KEYDOWN:
                if active_device and active_window == "IP":
                    # Only route to input boxes, not SPACE etc.
                    is_dhcp_on = active_device.type in ('PC', 'Laptop') and getattr(active_device, 'dhcp', False)
                    if not is_dhcp_on:
                        ip_input.handle_event(event)
                        subnet_input.handle_event(event)
                        gw_input.handle_event(event)
                        dns_input.handle_event(event)
                elif active_device and active_window == "ISP":
                    isp_ip_input.handle_event(event)
                    isp_subnet_input.handle_event(event)
                    isp_gw_input.handle_event(event)
                    isp_dns_p_input.handle_event(event)
                    isp_dns_s_input.handle_event(event)
                elif active_device and active_window == "WEB" and not mission_sys.surf_success:
                    url_input.handle_event(event)
                elif active_device and active_window == "WIFI_PWD":
                    wifi_pwd_input.handle_event(event)
                else:
                    if event.key == pygame.K_1: current_mode = 'PC'
                    elif event.key == pygame.K_2: current_mode = 'Laptop'
                    elif event.key == pygame.K_3: current_mode = 'Switch'
                    elif event.key == pygame.K_4: current_mode = 'Hub'
                    elif event.key == pygame.K_5: current_mode = 'Router'
                    elif event.key == pygame.K_6: current_mode = 'Converter'
                    elif event.key == pygame.K_d: current_mode = 'DELETE'
                    elif event.key == pygame.K_F3:
                        # DEBUG SKIP TO LEVEL 3
                        mission_sys.level = 3
                        mission_sys.setup_level()
                        sm.current = 'World'
                    elif event.key == pygame.K_SPACE:
                        mission_sys.packets_sent += 1
                        packet_flash_timer = 15
                        mission = mission_sys.get_current()
                        if sm.current == 'World':
                            # Send packet between House 1 and House 2
                            h1 = next((d for d in devices if d.type == 'House1'), None)
                            h2 = next((d for d in devices if d.type == 'House2'), None)
                            if h1 and h2:
                                path = find_path(devices, connections, h1, h2)
                                if path and len(path) > 1:
                                    packets.append(PacketPath(path))
                                    m = mission_sys.get_current()
                                    if m and m.type == "L3_SEND_P_WAN":
                                        mission_sys.advance()
                        else:
                            # --- LEVEL-SPECIFIC TESTS ---
                            mission = mission_sys.get_current()
                            pcs = [d for d in devices if d.type == 'PC']
                            endpoints = [d for d in devices if d.type in ('PC', 'Laptop', 'Server', 'House1', 'House2', 'House3', 'House4')]
                            routers = [d for d in devices if d.type == 'Router']

                            if mission_sys.level == 1 and mission:
                                if mission.type == "L1_COLLISION_TEST":
                                    hub = next((d for d in devices if d.type == 'Hub'), None)
                                    if hub and len(pcs) >= 3:
                                        p1 = find_path(devices, connections, pcs[0], pcs[1])
                                        p2 = find_path(devices, connections, pcs[2], pcs[1])
                                        if p1 and p2 and hub in p1 and hub in p2:
                                            packets.append(PacketPath(p1))
                                            packets.append(PacketPath(p2))
                                        else:
                                            mission_sys.fail_msg = "Zorg dat alle 3 de PC's met de Hub verbonden zijn!"
                                            mission_sys.fail_timer = 180
                                    continue
                                elif mission.type == "L1_TEST_SWITCH":
                                    sw = next((d for d in devices if d.type == 'Switch'), None)
                                    if sw and len(pcs) >= 3:
                                        p1 = find_path(devices, connections, pcs[0], pcs[1])
                                        p2 = find_path(devices, connections, pcs[2], pcs[1])
                                        if p1 and p2 and sw in p1 and sw in p2:
                                            packets.append(PacketPath(p1))
                                            packets.append(PacketPath(p2))
                                        else:
                                            mission_sys.fail_msg = "Zorg dat alle 3 de PC's met de Switch verbonden zijn!"
                                            mission_sys.fail_timer = 180
                                    continue
                                elif mission.type == "L1_TEST_FIBER":
                                    sw = next((d for d in devices if d.type == 'Switch'), None)
                                    pc4 = next((d for d in devices if d.type == 'PC' and d.name_idx == 4), None)
                                    if sw and pc4:
                                        path = find_path(devices, connections, sw, pc4)
                                        if path and len(path) > 1:
                                            packets.append(PacketPath(path))
                                        else:
                                            mission_sys.fail_msg = "PC 4 is nog niet (volledig) verbonden!"
                                            mission_sys.fail_timer = 180
                                    continue

                            # --- MISSION-SPECIFIC LOGIC (L3) ---
                            if mission:
                                if mission.type == "L3_H1_FINAL_PACKET":
                                    if len(endpoints) >= 3:
                                        start_pc = endpoints[0]
                                        for target_pc in endpoints[1:]:
                                            path = find_path(devices, connections, start_pc, target_pc)
                                            if path and len(path) > 1:
                                                packets.append(PacketPath(path))
                                    continue
                            
                            if mission and mission.type == "L3_H2_FINAL":
                                # Send specifically from PC to Laptop
                                pc = next((d for d in devices if d.type == 'PC'), None)
                                lap = next((d for d in devices if d.type == 'Laptop'), None)
                                if pc and lap:
                                    path = find_path(devices, connections, pc, lap)
                                    if path and len(path) > 1:
                                        packets.append(PacketPath(path))
                                        # mission_sys.packets_sent is now incremented at the start of SPACE handler
                                    else:
                                        mission_sys.fail_msg = "Geen verbinding gevonden tussen PC en Laptop!"
                                        mission_sys.fail_timer = 120
                                else:
                                    mission_sys.fail_msg = "PC of Laptop niet gevonden!"
                                    mission_sys.fail_timer = 120
                                continue

                            if mission_sys.level >= 2 and routers:
                                internet_source = routers[0]
                                for ep in endpoints:
                                    path = find_path(devices, connections, internet_source, ep)
                                    if path and len(path) > 1:
                                        packets.append(PacketPath(path))
                            elif len(endpoints) >= 2:
                                start_pc = endpoints[0]
                                target_pc = endpoints[-1]
                                for d in endpoints:
                                    if d.x > target_pc.x: target_pc = d
                                
                                if target_pc != start_pc:
                                    path = find_path(devices, connections, start_pc, target_pc)
                                    if path and len(path) > 1:
                                        packets.append(PacketPath(path))
                                        mission_sys.packets_sent += 1
                                        
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    # --- WORLD MAP SELECTION PRIORITY ---
                    if sm.current == 'World':
                        # 1. Confirm Enter
                        if btn_enter_house.collidepoint(event.pos):
                            if selected_house:
                                if selected_house.type == 'House2' and mission_sys.level == 3:
                                    # Jump to level 4
                                    mission_sys.level = 4
                                    mission_sys.setup_level()
                                
                                scene_name = selected_house.type
                                sm.start_transition(scene_name, f"Inzoomen op {scene_name}...")
                                play_sound(snd_enter)
                                current_cable = None 
                                selected_house = None 
                                continue
                        
                        # 2. Select House
                        clicked_house = False
                        for d in devices:
                            if d.type in ('House1', 'House2', 'House3', 'House4'):
                                if math.hypot(d.x - event.pos[0], d.y - event.pos[1]) < d.radius + 20:
                                    selected_house = d
                                    current_cable = None # Clear cable mode when selecting
                                    clicked_house = True
                                    break
                        if clicked_house:
                            continue

                    # START SCREEN CLICKS
                    if sm.current == 'Start':
                        # Play / Quit
                        btn_play = pygame.Rect(WIDTH//2 - 100, 280, 200, 60)
                        if btn_play.collidepoint(event.pos):
                            sm.start_transition("Level1", get_text('trans_zoom_in'))
                        
                        btn_quit = pygame.Rect(WIDTH//2 - 100, 360, 200, 60)
                        if btn_quit.collidepoint(event.pos):
                            pygame.quit()
                            sys.exit()
                            
                        btn_uitleg = pygame.Rect(WIDTH//2 - 100, 440, 200, 60)
                        if btn_uitleg.collidepoint(event.pos):
                            sm.start_transition("Uitleg_Menu", "")
                        
                        btn_levels = pygame.Rect(WIDTH//2 - 100, 520, 200, 60)
                        if btn_levels.collidepoint(event.pos):
                            sm.start_transition("Level_Select", "")
                        continue
                        
                    # UITLEG MENU CLICKS
                    if sm.current == 'Uitleg_Menu':
                        box = pygame.Rect(WIDTH//2 - 400, HEIGHT//2 - 250, 800, 500)
                        # Close Button
                        close_btn = pygame.Rect(box.right - 50, box.top + 20, 30, 30)
                        if close_btn.collidepoint(event.pos):
                            sm.start_transition("Start", "")
                            continue
                        
                        # Pagination Arrows
                        left_arrow = pygame.Rect(box.left + 20, box.centery - 30, 40, 60)
                        right_arrow = pygame.Rect(box.right - 60, box.centery - 30, 40, 60)
                        if left_arrow.collidepoint(event.pos) and sm.uitleg_page > 0:
                            sm.uitleg_page -= 1
                        if right_arrow.collidepoint(event.pos) and sm.uitleg_page < len(sm.uitleg_pages) - 1:
                            sm.uitleg_page += 1
                        continue
                        
                    # LEVEL SELECT CLICKS
                    if sm.current == 'Level_Select':
                        box = pygame.Rect(WIDTH//2 - 400, HEIGHT//2 - 250, 800, 500)
                        close_btn = pygame.Rect(box.right - 50, box.top + 20, 30, 30)
                        if close_btn.collidepoint(event.pos):
                            sm.start_transition("Start", "")
                            continue
                            
                        # Level Houses selection
                        start_x = box.left + 115
                        for i in range(4):
                            hx, hy = start_x + i * 220, box.centery
                            if math.hypot(event.pos[0] - hx, event.pos[1] - hy) < 70:
                                level_num = i + 1
                                mission_sys.level = level_num
                                # Reset everything
                                for s in sm.scenes.values():
                                    s['devices'].clear()
                                    s['connections'].clear()
                                    s['packets'].clear()
                                mission_sys.setup_level()
                                
                                target_scene = "Level1"
                                if level_num >= 3:
                                    target_scene = "World"
                                
                                sm.start_transition(target_scene, f"Laden van Level {level_num}...")
                                break
                        # Free Mode selection
                        btn_freemode = pygame.Rect(box.centerx - 150, box.bottom - 80, 300, 50)
                        if btn_freemode.collidepoint(event.pos):
                            mission_sys.level = 99
                            for s in sm.scenes.values():
                                s['devices'].clear()
                                s['connections'].clear()
                                s['packets'].clear()
                            mission_sys.setup_level()
                            
                            sm.scenes['World']['devices'].append(Device(100, 415, 'House3'))
                            sm.scenes['World']['devices'].append(Device(300, 280, 'House1'))
                            sm.scenes['World']['devices'].append(Device(500, 280, 'House2'))
                            sm.scenes['World']['devices'].append(Device(700, 415, 'House4'))
                            sm.scenes['World']['devices'].append(Device(900, 415, 'House3'))
                            
                            sm.start_transition("World", "Laden van Vrij Spel (Sandbox)...")
                            continue

                        continue
                        
                    # Educational Overlays dismissal (Highest Priority, above OS)
                    mission = mission_sys.get_current()
                    if mission and sm.transition_state == "NONE":
                        if mission.type in ("INTRO", "INTRO_L2", "L1_EXP_ALL", "L1_EXP_PC", "L1_EXP_LAP", "L1_EXP_SW", "L1_EXP_HUB", "L1_EXP_RT", "L1_EXP_MOUSE", "L2_EXPLAIN_ISP", "L3_EXPLAIN_ISP_H1", "L2_IP_WHY_POPUP", "L2_EXPLAIN_GW_DNS", "EXPLANATION_CAT5", "EXPLANATION_CROSS", "L3_EXPLAIN_DHCP", "EXPLANATION_WIFI", "EXPLANATION_FIBER_ERROR", "EXPLANATION_COLLISION", "EXPLANATION_SWITCH_SMART", "EXPLANATION_FIBER_CHAIN"):
                            box = pygame.Rect(WIDTH//2 - 400, HEIGHT//2 - 200, 800, 400)
                            if mission.type == "INTRO_L2":
                                box = pygame.Rect(500 - 350, 350 - 150, 700, 300)
                            elif mission.type == "L1_EXP_ALL":
                                box = pygame.Rect(WIDTH//2 - 400, HEIGHT//2 - 250, 800, 500)
                            elif mission.type == "L2_IP_WHY_POPUP":
                                box = pygame.Rect(WIDTH//2 - 350, HEIGHT//2 - 180, 700, 360)
                            elif mission.type in ("L2_EXPLAIN_ISP", "L3_EXPLAIN_ISP_H1", "L3_EXPLAIN_DHCP", "L2_EXPLAIN_GW_DNS"):
                                box = pygame.Rect(WIDTH//2 - 350, HEIGHT//2 - 220, 700, 440)
                            elif mission.type in ("EXPLANATION_CAT5", "EXPLANATION_CROSS", "EXPLANATION_WIFI", "EXPLANATION_FIBER_ERROR", "EXPLANATION_COLLISION", "EXPLANATION_SWITCH_SMART", "EXPLANATION_FIBER_CHAIN"):
                                box = pygame.Rect(WIDTH//2 - 400, HEIGHT//2 - 210, 800, 420) if mission.type == "EXPLANATION_FIBER_CHAIN" else (pygame.Rect(WIDTH//2 - 350, HEIGHT//2 - 200, 700, 400) if mission.type in ("EXPLANATION_WIFI", "EXPLANATION_FIBER_ERROR", "EXPLANATION_COLLISION", "EXPLANATION_SWITCH_SMART") else pygame.Rect(WIDTH//2 - 350, HEIGHT//2 - 180, 700, 360))
                            
                            if box.collidepoint(event.pos):
                                mission_sys.overlay_alpha = 0
                                mission_sys.advance()
                                continue
                                
                        if mission.type == "L3_WORLD_1":
                            box = pygame.Rect(100, 150, 800, 300)
                            if box.collidepoint(event.pos):
                                mission_sys.overlay_alpha
                                mission_sys.advance() # Advances to L3_BUILD_H2
                                continue
                        if mission.type == "L3_TO_WORLD_1":
                            box = pygame.Rect(150, 250, 700, 200)
                            if box.collidepoint(event.pos):
                                active_device = active_window = None
                                sm.start_transition("World", "Uitzoomen naar de Wereldkaart...")
                                if not any(d.type == 'House1' and not d.decorative for d in sm.scenes['World']['devices']):
                                    house_types = ['House1', 'House2', 'House3', 'House4']
                                    sm.scenes['World']['devices'].append(Device(100, 415, random.choice(house_types), decorative=True))
                                    sm.scenes['World']['devices'].append(Device(300, 280, 'House1'))
                                    sm.scenes['World']['devices'].append(Device(500, 280, 'House2'))
                                    sm.scenes['World']['devices'].append(Device(700, 415, random.choice(house_types), decorative=True))
                                    sm.scenes['World']['devices'].append(Device(900, 415, random.choice(house_types), decorative=True))
                                mission_sys.advance()
                                continue
                        if mission.type == "L3_TO_WORLD_2":
                            box = pygame.Rect(150, 250, 700, 200)
                            if box.collidepoint(event.pos):
                                active_device = active_window = None
                                sm.start_transition("World", "Uitzoomen naar de Wereldkaart...")
                                mission_sys.advance()
                                continue
                        if mission.type == "EXPLANATION_1":
                            box = pygame.Rect(WIDTH//2 - 350, HEIGHT//2 - 180, 700, 360)
                            if box.collidepoint(event.pos):
                                active_device = active_window = None
                                mission_sys.level = 2
                                devices.clear()
                                connections.clear()
                                packets.clear()
                                mission_sys.setup_level()
                                current_mode = 'Router'
                                continue
                        if mission.type == "EXPLANATION_2":
                            box = pygame.Rect(WIDTH//2 - 400, HEIGHT//2 - 200, 800, 400)
                            if box.collidepoint(event.pos):
                                active_device = active_window = None
                                mission_sys.level = 3
                                devices.clear()
                                connections.clear()
                                packets.clear()
                                mission_sys.setup_level()
                                current_mode = 'PC'
                                continue
                        
                        if mission.type == "EXPLANATION_FIN":
                            box = pygame.Rect(WIDTH//2 - 400, HEIGHT//2 - 200, 800, 400)
                            if box.collidepoint(event.pos):
                                active_device = active_window = None
                                # Clear all scenes for Free Mode
                                for s in sm.scenes.values():
                                    s['devices'].clear()
                                    s['connections'].clear()
                                    s['packets'].clear()
                                # Restore World Map houses since they were cleared too
                                sm.scenes['World']['devices'].append(Device(100, 415, 'House3'))
                                sm.scenes['World']['devices'].append(Device(300, 280, 'House1'))
                                sm.scenes['World']['devices'].append(Device(500, 280, 'House2'))
                                sm.scenes['World']['devices'].append(Device(700, 415, 'House4'))
                                sm.scenes['World']['devices'].append(Device(900, 415, 'House3'))
                                mission_sys.advance()
                                continue

                    # OS WINDOW CLICKS
                    if active_device:
                        box = pygame.Rect(WIDTH//2 - 250, HEIGHT//2 - 225, 500, 450)
                        dist_to_red = math.hypot(event.pos[0] - (box.x + 15), event.pos[1] - (box.y + 15))
                        if dist_to_red <= 12:
                            active_device = None
                            active_window = None
                            mission = mission_sys.get_current()
                            if mission and mission.type == "CLOSE_WINDOW": mission_sys.advance()
                            continue
                            
                        btn_back = pygame.Rect(box.x + 75, box.y + 4, 60, 22)
                        if active_window != "MENU" and btn_back.collidepoint(event.pos):
                            active_window = "MENU"
                            ui_alpha = 0
                            continue
                            
                        if active_window == "MENU":
                            bx, by = box.x + 50, box.y + 70
                            if active_device.type == 'Laptop':
                                options = [('wifi', "wifi.png"), ('web_browsing', "web_browsing.png"), ('terminal', "terminal.png")]
                            elif active_device.type == 'PC':
                                options = [('ip_settings', "ip_instellingen.png"), ('web_browsing', "web_browsing.png"), ('terminal', "terminal.png")]
                            else:
                                options = [('ip_settings', "ip_instellingen.png"), ('terminal', "terminal.png"), ('restart', "restart.png")]
                            
                            for key, icon_file in options:
                                r = pygame.Rect(bx, by, 130, 130) # Vergroten naar 130x130
                                if r.collidepoint(event.pos):
                                    if key == "ip_settings":
                                        active_window = "IP"
                                        ui_alpha = 0
                                        ip_input.text = active_device.ip
                                        subnet_input.text = active_device.subnet
                                        gw_input.text = active_device.gateway
                                        dns_input.text = active_device.dns
                                    elif key == "web_browsing" and active_device.type in ('PC', 'Laptop'):
                                        active_window = "WEB"
                                        ui_alpha = 0
                                        url_input.text = "www."
                                        mission_sys.surf_success, mission_sys.popup_text = False, ""
                                    elif key == "terminal":
                                        active_window = "TERM"
                                        ui_alpha = 0
                                        term_input.text = ">"
                                    elif key == "wifi":
                                        active_window = "WIFI_LIST"
                                        ui_alpha = 0
                                    elif key == "restart": active_device = active_window = None
                                    elif key == "reset": active_device.ip = active_device.subnet = ""
                                    break
                                bx += 145 # Grotere spacing
                        elif active_window == "IP":
                            if active_device.type == 'Router':
                                # --- Router ISP Instellingen button ---
                                btn_isp = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 115, 200, 32)
                                if btn_isp.collidepoint(event.pos):
                                    m = mission_sys.get_current()
                                    active_window = "ISP"
                                    ui_alpha = 0
                                    isp_ip_input.text = getattr(active_device, 'public_ip', '')
                                    isp_subnet_input.text = getattr(active_device, 'public_subnet', '')
                                    isp_gw_input.text = getattr(active_device, 'public_gw', '')
                                    isp_dns_p_input.text = getattr(active_device, 'dns_p', '')
                                    isp_dns_s_input.text = getattr(active_device, 'dns_s', '')
                                    if m and m.type == "CONF_ISP": mission_sys.advance()
                                    continue
                                
                                # --- Router DHCP Server toggle (Level 3+) ---
                                if mission_sys.level >= 3:
                                    dhcp_srv_btn = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 85, 140, 32)
                                    if dhcp_srv_btn.collidepoint(event.pos):
                                        active_device.dhcp_srv = not getattr(active_device, 'dhcp_srv', False)
                                        m = mission_sys.get_current()
                                        if m and m.type in ("L3_ENABLE_DHCP_SRV", "L3_ENABLE_DHCP_SRV_R2") and active_device.dhcp_srv:
                                            mission_sys.advance()
                                        continue

                                # --- Router LAN Save button ---
                                ip_input.handle_event(event)
                                subnet_input.handle_event(event)
                                btn_save = pygame.Rect(WIDTH//2 - 50, HEIGHT//2 + 130, 100, 30)
                                if btn_save.collidepoint(event.pos):
                                    active_device.ip = ip_input.text
                                    active_device.subnet = subnet_input.text
                                    m = mission_sys.get_current()
                                    if m and m.type == "CONF_ROUTER": mission_sys.advance()
                                    continue

                            elif active_device.type in ('PC', 'Laptop'):
                                # --- PC/Laptop DHCP toggle (Level 3+) ---
                                if mission_sys.level >= 3:
                                    pc_dhcp_btn = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 - 105, 140, 32)
                                    if pc_dhcp_btn.collidepoint(event.pos):
                                        active_device.dhcp = not getattr(active_device, 'dhcp', False)
                                        if active_device.dhcp:
                                            ip_input.text = ""
                                            subnet_input.text = ""
                                            m = mission_sys.get_current()
                                            if m and m.type == "L3_USE_DHCP":
                                                # Check if all targeted PCs are on
                                                all_on = True
                                                for d in devices:
                                                    if d.type in ('PC', 'Laptop') and not getattr(d, 'dhcp', False):
                                                        all_on = False
                                                if all_on: mission_sys.advance()
                                        else:
                                            ip_input.text = active_device.ip if active_device.ip else ""
                                            subnet_input.text = active_device.subnet if active_device.subnet else ""
                                            gw_input.text = active_device.gateway if active_device.gateway else ""
                                            dns_input.text = active_device.dns if active_device.dns else ""
                                        continue
                                
                                # --- PC/Laptop IP fields ---
                                if not getattr(active_device, 'dhcp', False):
                                    ip_input.handle_event(event)
                                    subnet_input.handle_event(event)
                                    gw_input.handle_event(event)
                                    dns_input.handle_event(event)
                                        
                                    save_y = HEIGHT//2 + 180 if mission_sys.level >= 2 else HEIGHT//2 + 130
                                    btn_save = pygame.Rect(WIDTH//2 - 50, save_y, 100, 30)
                                    if btn_save.collidepoint(event.pos):
                                        active_device.ip = ip_input.text
                                        active_device.subnet = subnet_input.text
                                        active_device.gateway = gw_input.text
                                        active_device.dns = dns_input.text
                                        
                                        m = mission_sys.get_current()
                                        if m and m.type == "CONF_PC":
                                            # Basic check for IP/Subnet
                                            if active_device.ip and active_device.subnet:
                                                if mission_sys.level < 2:
                                                    mission_sys.advance()
                                                else:
                                                    # In Level 2+ we need gateway and DNS (8.8.8.8)
                                                    if active_device.gateway and active_device.dns == "8.8.8.8":
                                                        mission_sys.advance()
                                        continue

                        elif active_window == "ISP":
                            isp_ip_input.handle_event(event)
                            isp_subnet_input.handle_event(event)
                            isp_gw_input.handle_event(event)
                            isp_dns_p_input.handle_event(event)
                            isp_dns_s_input.handle_event(event)
                            
                            # Sync with drawn button: box.x + box.width//2 - 75, box.y + 340, 150, 40
                            # where box.x = WIDTH//2 - 280, box.y = HEIGHT//2 - 200
                            btn_save_isp = pygame.Rect(WIDTH//2 - 75, HEIGHT//2 + 140, 150, 40)
                            if btn_save_isp.collidepoint(event.pos):
                                active_device.public_ip = isp_ip_input.text.strip()
                                active_device.public_subnet = isp_subnet_input.text.strip()
                                active_device.public_gw = isp_gw_input.text.strip()
                                active_device.dns_p = isp_dns_p_input.text.strip()
                                active_device.dns_s = isp_dns_s_input.text.strip()
                                active_device.isp = "Manual" # Mark as configured
                                
                                # Force immediate mission check for better UX
                                m = mission_sys.get_current()
                                if m and m.type == "FILL_ISP_L2":
                                    if (active_device.public_ip == "84.197.10.15" and 
                                        active_device.public_subnet == "255.255.255.0" and 
                                        active_device.public_gw == "84.197.10.1"):
                                        mission_sys.advance()
                                elif m and m.type == "FILL_ISP_L3_H1":
                                    if (active_device.public_ip == "193.191.1.20" and 
                                        active_device.public_subnet == "255.255.255.0" and 
                                        active_device.public_gw == "193.191.1.1"):
                                        mission_sys.advance()

                                active_window = "IP"
                                ui_alpha = 0
                                continue
                        elif active_window == "WEB":
                            if not mission_sys.surf_success:
                                url_input.handle_event(event)
                                btn_go = pygame.Rect(WIDTH//2 + 150, HEIGHT//2, 80, 40)
                                if btn_go.collidepoint(event.pos):
                                    if url_input.text == "www.thomasmore.be":
                                        if active_device.ip:
                                            path = find_path_to_type(devices, connections, active_device, 'Router')
                                            if path and path[-1].ip:
                                                mission_sys.surf_success, mission_sys.popup_text = True, ""
                                                m = mission_sys.get_current()
                                                if m and m.type == "SURF": mission_sys.advance()
                                            else: mission_sys.popup_text = get_text('error_route') if not path else get_text('error_ip')
                                        else: mission_sys.popup_text = get_text('error_no_ip')
                                    else: mission_sys.popup_text = get_text('error_404')
                        elif active_window == "TERM":
                            term_input.handle_event(event)
                            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                                cmd = term_input.text.strip('> ').lower()
                                term_output.append(term_input.text)
                                if cmd == "help":
                                    term_output.append("Beschikbare commands: help, ipconfig, ping")
                                elif cmd == "ipconfig":
                                    term_output.append(f"IP: {active_device.ip or '0.0.0.0'}")
                                    term_output.append(f"Public IP: {getattr(active_device, 'public_ip', '0.0.0.0')}")
                                elif cmd.startswith("ping"):
                                    target = cmd.split(" ")[-1] if " " in cmd else "unknown"
                                    term_output.append(f"Pingen naar {target}...")
                                    if target in ("www.google.com", "google.com", "8.8.8.8"):
                                        term_output.append("Antwoord van 8.8.8.8: bytes=32 tijd=12ms TTL=54")
                                        m = mission_sys.get_current()
                                        if m and m.type == "L2_PING_TEST": mission_sys.advance()
                                    else:
                                        term_output.append("Request timed out.")
                                else:
                                    term_output.append(f"Onbekend commando: {cmd}")
                                term_input.text = ">"
                                if len(term_output) > 10: term_output.pop(0)
                        
                        elif active_window == "WIFI_LIST":
                            nets = ["Free_WiFi_Station", "Telenet-ABCD", "TM_intern"]
                            ny = HEIGHT//2 - 225 + 90
                            for net in nets:
                                btn_net = pygame.Rect(WIDTH//2 - 250 + 50, ny, 300, 40)
                                if btn_net.collidepoint(event.pos):
                                    if net == "TM_intern":
                                        active_window = "WIFI_PWD"
                                        wifi_pwd_input.text = ""
                                        mission_sys.popup_text = ""
                                    else:
                                        mission_sys.popup_text = "Beveiligd netwerk. Toegang geweigerd."
                                    break
                                ny += 50
                        
                        elif active_window == "WIFI_PWD":
                            wifi_pwd_input.handle_event(event)
                            btn_conn = pygame.Rect(WIDTH//2 - 250 + 50, HEIGHT//2 - 225 + 150, 120, 40)
                            if btn_conn.collidepoint(event.pos):
                                if wifi_pwd_input.text == "iloveITF":
                                    # Succes! Connect laptop to nearest router
                                    router = None
                                    min_dist = float('inf')
                                    for d in devices:
                                        if d.type == 'Router':
                                            dist = math.hypot(d.x - active_device.x, d.y - active_device.y)
                                            if dist < min_dist:
                                                min_dist = dist
                                                router = d
                                                
                                    if router:
                                        # Check distance
                                        if min_dist < CABLES['Wi-Fi']['max_dist']:
                                            # Check if already connected
                                            exists = any(c.cable_type == 'Wi-Fi' and (c.d1 == active_device or c.d2 == active_device) for c in connections)
                                            if not exists:
                                                connections.append(Connection(active_device, router, 'Wi-Fi'))
                                                # DHCP simulatie voor Wi-Fi
                                                if mission_sys.level >= 3:
                                                    active_device.ip = "192.168.3.50" if mission_sys.level == 4 else "192.168.1.50"
                                                    active_device.subnet = "255.255.255.0"
                                            active_window = "MENU"
                                            mission_sys.popup_text = "Verbonden!"
                                        else:
                                            mission_sys.popup_text = "Signaal te zwak!"
                                    else:
                                        mission_sys.popup_text = "Geen router gevonden!"
                                else:
                                    mission_sys.popup_text = "Fout wachtwoord!"
                        
                        continue # Block all background interaction when OS is open
                        
                    # Terug naar Wereldknop
                    is_free_mode = mission_sys.get_current() is None or mission_sys.get_current().type == "DONE"
                    if (sm.current == 'House2' and mission_sys.level in (3, 4)) or (sm.current != 'World' and sm.current != 'Start' and is_free_mode):
                        btn_to_world = pygame.Rect(20, HEIGHT//2 - 20, 220, 40)
                        if btn_to_world.collidepoint(event.pos):
                            sm.start_transition("World", "Terug naar het overzicht...")
            
                    # UI Cables
                    if btn_straight.collidepoint(event.pos):
                        current_cable = 'Cat 5' if mission_sys.level == 1 else 'Straight'
                        continue
                    if btn_cross.collidepoint(event.pos):
                        current_cable = 'Fiber' if mission_sys.level <= 2 else 'Crossover'
                        mission = mission_sys.get_current()
                        if mission and mission.type in ("PICK_FIBER", "L1_FIBER_CHALLENGE"):
                            mission_sys.advance()
                        continue
                    if btn_wan.collidepoint(event.pos):
                        if is_free_mode:
                            current_cable = 'Fiber'
                        else:
                            current_cable = 'WAN Fiber'
                            mission = mission_sys.get_current()
                            if mission and mission.type == "L3_PICK_WAN":
                                mission_sys.advance()
                        continue
                                            
                    if btn_data.collidepoint(event.pos):
                        mission_sys.packets_sent += 1
                        packet_flash_timer = 15
                        # Trigger Spatie logic
                        if sm.current == 'World':
                            h1 = next((d for d in devices if d.type == 'House1'), None)
                            h2 = next((d for d in devices if d.type == 'House2'), None)
                            if h1 and h2:
                                path = find_path(devices, connections, h1, h2)
                                if path and len(path) > 1:
                                    packets.append(PacketPath(path))
                                    m = mission_sys.get_current()
                                    if m and m.type == "L3_SEND_P_WAN":
                                        mission_sys.advance()
                        else:
                            # Standard send packet logic
                            endpoints = [d for d in devices if d.type in ('PC', 'Laptop')]
                            routers = [d for d in devices if d.type == 'Router']
                            
                            mission = mission_sys.get_current()
                            if mission and mission.type == "L3_H1_FINAL_PACKET":
                                # Send from PC 1 to PC 2 and PC 3
                                if len(endpoints) >= 3:
                                    start_pc = endpoints[0]
                                    for target_pc in endpoints[1:]:
                                        path = find_path(devices, connections, start_pc, target_pc)
                                        if path and len(path) > 1:
                                            packets.append(PacketPath(path))
                                            mission_sys.packets_sent += 1
                                continue

                            if mission_sys.level >= 2 and routers:
                                internet_source = routers[0]
                                for ep in endpoints:
                                    path = find_path(devices, connections, internet_source, ep)
                                    if path and len(path) > 1:
                                        packets.append(PacketPath(path))
                                        mission_sys.packets_sent += 1
                                if m and m.type == "PACKET": pass
                            elif len(endpoints) >= 2:
                                start_pc = endpoints[0]
                                target_pc = endpoints[-1]
                                for d in endpoints:
                                    if d.x > target_pc.x: target_pc = d
                                if target_pc != start_pc:
                                    path = find_path(devices, connections, start_pc, target_pc)
                                    if path and len(path) > 1:
                                        packets.append(PacketPath(path))
                                        mission_sys.packets_sent += 1
                                        if m and m.type == "PACKET": pass
                        continue
                        
                    # Top Modes (Toolbar)
                    if sm.current != 'World':
                        clicked_menu = False
                        for m_t, r in btn_modi.items():
                            if r.collidepoint(event.pos):
                                current_mode = m_t
                                clicked_menu = True
                                break
                        if clicked_menu:
                            continue
                        
                        if event.pos[1] < 100: # Blokkering van bovenste balk
                            continue
                    else:
                        # Op de wereldkaart is alles behalve WAN Fiber geblokkeerd
                        if btn_enter_house.collidepoint(event.pos):
                            current_cable = None
                            current_mode = None
                            continue
                        
                        if btn_wan.collidepoint(event.pos):
                            current_cable = 'WAN Fiber'
                            current_mode = None
                            continue
                        
                        if event.pos[1] < 100 or (event.pos[0] > 800 and event.pos[1] < 300):
                            # Strikte blokkering van onzichtbare toolbar en kabels
                            continue

                    # UI Cables (Binnenshuis)
                    if sm.current != 'World':
                        if btn_straight.collidepoint(event.pos):
                            current_cable = 'Cat 5' if mission_sys.level == 1 else 'Straight'
                            continue
                        if btn_cross.collidepoint(event.pos):
                            current_cable = 'Fiber' if mission_sys.level <= 2 else 'Crossover'
                            continue
                    else:
                        # WAN Fiber al hierboven afgehandeld
                        pass
                        
                    # Track when mouse was pressed (for hold safety)
                    mouse_press_tick = pygame.time.get_ticks()
                    
                    # Devices — larger hit radius for easier selection
                    clicked_dev = None
                    for d in reversed(devices):
                        if math.hypot(d.x - event.pos[0], d.y - event.pos[1]) < d.radius + 15:
                            clicked_dev = d
                            break
                            
                    if current_mode == 'DELETE':
                        if clicked_dev:
                             # FIX: Huizen mogen niet verwijderd worden!
                             if clicked_dev.type not in ['House1', 'House2', 'House3', 'House4']:
                                 devices.remove(clicked_dev)
                                 play_sound(snd_delete)
                                 connections = [c for c in connections if c.d1 != clicked_dev and c.d2 != clicked_dev]
                                 packets = [p for p in packets if clicked_dev not in getattr(p, 'path', [])]
                                 curr['connections'] = connections
                                 curr['packets'] = packets
                        else:
                            for c in connections:
                                mx, my = (c.d1.x + c.d2.x) / 2, (c.d1.y + c.d2.y) / 2
                                if math.hypot(mx - event.pos[0], my - event.pos[1]) < 20:
                                    connections.remove(c)
                                    play_sound(snd_delete)
                                    break
                    else:
                        if clicked_dev:
                            drag_start_dev = clicked_dev
                            dragging = True
                            play_sound(snd_cable)
                        else:
                            # HOLD SAFETY: Only place device on short click (< HOLD_THRESHOLD_MS)
                            # Long holding = intending to drag a cable, not place a device.
                            # We set mouse_press_tick here but defer placement to MOUSEBUTTONUP.
                            pass  # device placement deferred to MOUSEBUTTONUP
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    held_ms = pygame.time.get_ticks() - mouse_press_tick
                    
                    # House selection on World Map (larger hit radius)
                    if sm.current == 'World' and not dragging and current_cable is None:
                        for d in devices:
                            if d.type in ('House1', 'House2', 'House3', 'House4'):
                                if math.hypot(d.x - event.pos[0], d.y - event.pos[1]) < d.radius + 20:
                                    selected_house = d
                                    break
                    
                    if btn_enter_house.collidepoint(event.pos) and selected_house and sm.current == 'World' and not dragging and current_cable is None:
                        sm.start_transition(selected_house.type, get_text('trans_zoom_in'))
                        play_sound(snd_enter)
                        Device.reset_counts()
                        current_cable = 'Cat 5'
                        continue

                    if dragging and drag_start_dev:
                        target_dev = None
                        for d in devices:
                            if math.hypot(d.x - event.pos[0], d.y - event.pos[1]) < d.radius + 20: # +20px extra margen
                                target_dev = d
                                break
                                
                        if target_dev == drag_start_dev:
                            # Opende het OS (NIET in Level 1!)
                            if sm.current != 'World' and mission_sys.level > 1:
                                active_device = drag_start_dev
                                active_window = "MENU"
                                ui_alpha = 0
                        elif target_dev:
                            # Verbinding
                            dist = math.hypot(drag_start_dev.cable_c[0] - target_dev.cable_c[0], drag_start_dev.cable_c[1] - target_dev.cable_c[1])
                            mission = mission_sys.get_current()
                            if mission and mission.type == "TRY_CONNECT":
                                if dist > CABLES['Straight']['max_dist'] and current_cable == 'Straight':
                                    mission_sys.advance() 
                                    
                            exists = False
                            for c in connections:
                                if (c.d1 == drag_start_dev and c.d2 == target_dev) or (c.d2 == drag_start_dev and c.d1 == target_dev):
                                    exists = True
                                    c.cable_type = current_cable
                                    c.update_validity()
                                    break

                            if not exists and current_cable in CABLES:
                                # Forgiving connection distance check
                                max_d = CABLES[current_cable]['max_dist']
                                if dist <= max_d + 10: # Extra bit of leeway
                                    valid_cable = True
                                    dev1 = drag_start_dev.type
                                    dev2 = target_dev.type
                                    
                                    # Fiber Check
                                    if current_cable == 'Fiber':
                                        if dev1 != 'Converter' or dev2 != 'Converter':
                                            valid_cable = False
                                            error_msg = "[FIBER FOUT] Glasvezel moet tussen twee Converters!"
                                            error_timer = 180
                                            m = mission_sys.get_current()
                                            if m and m.type == "TRY_FIBER_FAIL": mission_sys.advance()

                                    # Nieuw: Geen koper (Straight/Cross/Cat5) tussen twee Converters
                                    if current_cable in ('Straight', 'Crossover', 'Cat 5') and dev1 == 'Converter' and dev2 == 'Converter':
                                        valid_cable = False
                                        error_msg = "Koperkabels werken niet tussen twee Converters. Gebruik Fiber!"
                                        error_timer = 180

                                    # Alleen vanaf Level 3 controleren we op Straight vs Crossover
                                    if valid_cable and mission_sys.level >= 3 and current_cable in ('Straight', 'Crossover'):
                                        type1 = 'EndDevice' if dev1 in ('PC', 'Laptop', 'Server') else dev1
                                        type2 = 'EndDevice' if dev2 in ('PC', 'Laptop', 'Server') else dev2
                                        
                                        if type1 == type2:
                                            # Zelfde types -> Moet Crossover zijn
                                            if current_cable != 'Crossover':
                                                valid_cable = False
                                                error_msg = "Foute kabel! Gebruik CROSSOVER voor gelijke apparaten."
                                                error_timer = 240
                                                m = mission_sys.get_current()
                                                if m and m.type == "L3_TRY_STRAIGHT": mission_sys.advance()
                                        else:
                                            # Verschillende types -> Moet Straight zijn
                                            if current_cable != 'Straight':
                                                valid_cable = False
                                                error_msg = "Foute kabel! Gebruik STRAIGHT voor verschillende apparaten."
                                                error_timer = 240
                                    
                                    if valid_cable:
                                        connections.append(Connection(drag_start_dev, target_dev, current_cable))
                                        mission_sys.fail_timer = 0 
                                    
                                    if not valid_cable:
                                        # Show cable error via mission system
                                        mission_sys.fail_msg = error_msg
                                        mission_sys.fail_timer = 180
                                else:
                                    miss = mission_sys.get_current()
                                    if miss and miss.type == "TRY_CONNECT":
                                        mission_sys.advance()
                                    else:
                                        msg = get_text('error_len')
                                        mission_sys.fail_msg = f"{msg} {CABLES[current_cable]['max_m']}m"
                                        mission_sys.fail_timer = 180
                                
                    if dragging:
                        play_sound(snd_cable)
                    dragging = False
                    drag_start_dev = None
                    
                    # ====================================================
                    # DEFERRED DEVICE PLACEMENT (held < HOLD_THRESHOLD_MS)
                    # ====================================================
                    if not dragging and held_ms < HOLD_THRESHOLD_MS and sm.current not in ('World', 'Start', 'Uitleg_Menu') and current_mode and current_mode != 'DELETE':
                        # Check nothing was clicked and it wasn't a toolbar hit
                        clicked_anything = False
                        if active_device: clicked_anything = True
                        for r in btn_modi.values():
                            if r.collidepoint(event.pos): clicked_anything = True
                        if btn_data.collidepoint(event.pos): clicked_anything = True
                        if btn_straight.collidepoint(event.pos): clicked_anything = True
                        if btn_cross.collidepoint(event.pos): clicked_anything = True
                        if btn_wan.collidepoint(event.pos): clicked_anything = True
                        for d in devices:
                            if math.hypot(d.x - event.pos[0], d.y - event.pos[1]) < d.radius + 15:
                                clicked_anything = True
                                break
                        
                        if not clicked_anything and event.pos[1] > 100:
                            mission = mission_sys.get_current()
                            new_dev = None
                            # Placement safety check
                            if mission and ("PLACE" in mission.type or mission.type == "L1_FIBER_CHALLENGE"):
                                # If the mission type contains 'PLACE' (e.g., PLACE, L3_PLACE_2RT, L3_PLACE_PC) or is the fiber challenge
                                if mission.type != "L1_FIBER_CHALLENGE" and (hasattr(mission, 'dev_type') and mission.dev_type) and current_mode != mission.dev_type:
                                    mission_sys.fail_msg = f"FOUT: Plaats een {mission.dev_type}, geen {current_mode}."
                                    mission_sys.fail_timer = 180
                                else:
                                    # If it has a target radius, check it
                                    if hasattr(mission, 'target_pos') and mission.target_pos and hasattr(mission, 'radius'):
                                        dist_to_target = math.hypot(event.pos[0] - mission.target_pos[0], event.pos[1] - mission.target_pos[1])
                                        if dist_to_target > mission.radius:
                                            mission_sys.fail_msg = "Oeps verkeerd geklikt! Plaats het object IN de cirkel."
                                            mission_sys.fail_timer = 180
                                            new_dev = None
                                        else:
                                            new_dev = Device(event.pos[0], event.pos[1], current_mode)
                                            devices.append(new_dev)
                                            play_sound(snd_place)
                                    else:
                                        # Free placement (no specific circle) but restricted to correct type
                                        new_dev = Device(event.pos[0], event.pos[1], current_mode)
                                        devices.append(new_dev)
                                        play_sound(snd_place)
                            elif mission and mission.type not in ("DONE", "FREE", "L3_BUILD_H2", "L1_FIBER_CHALLENGE") and mission_sys.level < 3:
                                # If there is an active mission but it's NOT a placement mission
                                mission_sys.fail_msg = "Hellaaa dat was de opdracht niet! Eerst de huidige taak afmaken."
                                mission_sys.fail_timer = 180
                            else:
                                # Free mode or non-restrictive mission phases
                                new_dev = Device(event.pos[0], event.pos[1], current_mode)
                                devices.append(new_dev)
                                play_sound(snd_place)
                                
                            # Check Wi-Fi connection (Disabled for Manual Wi-Fi mission in Level 3)
                            if new_dev and new_dev.type == 'Laptop' and mission_sys.level < 3:
                                for d in devices:
                                    if d.type == 'Router':
                                        dist = math.hypot(d.x - new_dev.x, d.y - new_dev.y)
                                        if dist < CABLES['Wi-Fi']['max_dist']:
                                            connections.append(Connection(new_dev, d, 'Wi-Fi'))
                                            mission_sys.wifi_timer = 90
                                            break
                    
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                
            
        # --- RENDERING ---
        
        # 1. Connections & Dragging Line
        for c in connections: c.draw(screen)
        
        if dragging and drag_start_dev and current_cable in CABLES:
            c1x, c1y = drag_start_dev.cable_c
            drag_dist = math.hypot(c1x - mouse_pos[0], c1y - mouse_pos[1])
            if drag_dist > drag_start_dev.radius:
                max_dist = CABLES[current_cable]['max_dist']
                max_m = CABLES[current_cable]['max_m']
                dist_m = int(drag_dist / 4)
                color = CABLES[current_cable]['color'] if drag_dist <= max_dist else RED
                angle = math.atan2(mouse_pos[1] - c1y, mouse_pos[0] - c1x)
                d1_dist = drag_start_dev.cable_dist(angle)
                start_x, start_y = c1x + math.cos(angle) * d1_dist, c1y + math.sin(angle) * d1_dist
                pygame.draw.line(screen, color, (start_x, start_y), mouse_pos, 4)
                msg_too_long = "Too long!" if current_lang == 'en' else "Trop long!" if current_lang == 'fr' else "Te lang!"
                msg_max = "Max" if current_lang != 'nl' else "Max"
                
                # Als de kabel een enorme limiet heeft (1000m+), toon geen Max label
                if max_m >= 1000:
                    text_str = f"{dist_m}m"
                else:
                    text_str = f"{msg_too_long} {dist_m}m / {max_m}m" if drag_dist > max_dist else f"{dist_m}m ({msg_max} {max_m}m)"
                
                text = small_font.render(text_str, True, RED if drag_dist > max_dist else WHITE)
                screen.blit(text, (mouse_pos[0] + 10, mouse_pos[1] + 10))

        # 2. Packets
        new_packets = []
        pending_broadcasts = []
        for p in packets:
            p.update()
            
            # --- Collision Check (Hub) ---
            if p.curr_idx < len(p.path):
                cur_dev = p.path[p.curr_idx]
                if cur_dev.type == 'Hub' and p.status != 'COLLIDED':
                    # Check if another packet is at the same hub
                    for other in packets:
                        if other != p and other.status != 'COLLIDED' and not other.reached:
                            if other.path[other.curr_idx] == cur_dev:
                                cur_dev.collision_timer = 90
                                p.status = 'COLLIDED'
                                other.status = 'COLLIDED'
                                break

            
            # --- IP Security Check (Level 2+) ---
            # Packet dropt als het DOEL-apparaat geen IP heeft
            if mission_sys.level >= 2:
                dest = p.path[-1]
                if not dest.ip and dest.type in ('PC', 'Laptop'):
                    p.reached = True  # silently drop packet
                    continue
            
            p.draw(screen)
            
            if p.just_reached_node:
                p.just_reached_node = False
                reached_dev = p.path[p.curr_idx]
                if reached_dev.type == 'Hub':
                    # Hub Broadcast Logic
                    prev_dev = p.path[p.curr_idx - 1]
                    next_dev = p.path[p.curr_idx + 1] if p.curr_idx < len(p.path)-1 else None
                    
                    # Find all connected neighbors
                    for c in connections:
                        if c.is_valid:
                            other = None
                            if c.d1 == reached_dev: other = c.d2
                            elif c.d2 == reached_dev: other = c.d1
                            
                            if other and other != prev_dev and other != next_dev:
                                # Send a ghost/side packet to this neighbor
                                # If it's a 1-hop path, it just reaches it and dies
                                side_p = PacketPath([reached_dev, other])
                                pending_broadcasts.append(side_p)

            if not p.reached:
                new_packets.append(p)
            else:
                mission_sys.packets_delivered += 1
        
        packets = new_packets + pending_broadcasts
        curr['packets'] = packets

        for d in devices: d.draw(screen, sm.current)
        
        # World Map extra visuals (Road & Street)
        if sm.current == 'World':
            # Draw the road itself
            pygame.draw.rect(screen, (50, 50, 55), (0, 320, WIDTH, 60)) # Asphalt
            pygame.draw.rect(screen, (70, 70, 75), (0, 315, WIDTH, 5))  # Top shoulder
            pygame.draw.rect(screen, (70, 70, 75), (0, 380, WIDTH, 5))  # Bottom shoulder
            # Lane marking (dashed)
            for x in range(0, WIDTH, 60):
                pygame.draw.line(screen, WHITE, (x, 350), (x + 30, 350), 2)
            
            # Label
            st_font = pygame.font.SysFont(None, 45, bold=True)
            st_shad = st_font.render("Stationsstraat", True, BLACK)
            screen.blit(st_shad, (32, 282))
            st_txt = st_font.render("Stationsstraat", True, YELLOW)
            screen.blit(st_txt, (30, 280))
            
            # Highlight selected house
            if selected_house:
                pygame.draw.circle(screen, YELLOW, (selected_house.x, selected_house.y), selected_house.radius + 15, 3)
                # Pulse highlight shadow
                s = abs(math.sin(pygame.time.get_ticks() * 0.005))
                pygame.draw.circle(screen, YELLOW, (selected_house.x, selected_house.y), selected_house.radius + 15 + s*5, 1)

        # Laptop Wi-Fi Placement Guide
        if current_mode == 'Laptop' and sm.current != 'World' and sm.current != 'Start':
            for d in devices:
                if d.type == 'Router':
                    # Best placement zone (80px to 200px)
                    # Use transparency
                    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                    pygame.draw.circle(s, (0, 255, 255, 30), (d.x, d.y), 200)
                    pygame.draw.circle(s, (0, 0, 0, 0), (d.x, d.y), 80)
                    screen.blit(s, (0,0))
                    pygame.draw.circle(screen, CYAN, (d.x, d.y), 200, 1)
                    pygame.draw.circle(screen, CYAN, (d.x, d.y), 80, 1)

        # UI overlays
        show_main_ui = sm.current != 'Start'
        curr_m = mission_sys.get_current()
        # Only hide UI during full-screen overlays/intros
        if curr_m and (curr_m.type == 'INTRO' or curr_m.type.startswith('EXPLANATION') or curr_m.type in ('L3_TO_WORLD_1', 'L3_WORLD_1', 'L3_TO_WORLD_2')):
            show_main_ui = False
            
        if show_main_ui:
            for m_t, r in btn_modi.items():
                # Restriction: No devices placement or delete on World Map
                if sm.current == 'World':
                    continue
                    
                bgcolor = (0, 255, 148) if current_mode == m_t else (60, 60, 60)
                if m_t == 'DELETE':
                    bgcolor = RED if current_mode == 'DELETE' else (60, 60, 60)
                pygame.draw.rect(screen, bgcolor, r)
                pygame.draw.rect(screen, (52, 50, 199), r, 2)
                
                icon = ICONS.get(m_t)
                if icon:
                    scaled_icon = pygame.transform.smoothscale(icon, (30, 30))
                    icon_x = r.x + 25 if m_t == 'DELETE' else r.x + 15
                    screen.blit(scaled_icon, (icon_x, r.y + 25))
                
                if m_t == 'DELETE':
                    dt2 = small_font.render("[D]", True, WHITE)
                    screen.blit(dt2, (r.x + 5, r.y + 2))
                else:
                    num_map = {'PC': '1', 'Laptop': '2', 'Switch': '3', 'Hub': '4', 'Router': '5', 'Converter': '6'}
                    num_text = num_map.get(m_t, '')
                    if num_text:
                        t = font.render(num_text, True, WHITE)
                        screen.blit(t, (r.x + 5, r.y + 2))
                
                # Labels under icons
                labels_map = {'PC': 'PC', 'Laptop': 'Laptop', 'Switch': 'Switch', 'Hub': 'Hub', 'Router': 'Router', 'Converter': 'Converter', 'DELETE': 'Delete'}
                lbl_text = labels_map.get(m_t, '')
                if lbl_text:
                    l_surf = small_font.render(lbl_text, True, WHITE)
                    screen.blit(l_surf, (r.x + r.width//2 - l_surf.get_width()//2, r.y + 60))
                    
            if sm.current != 'World':
                # Space button (only show/enable in appropriate phases)
                p_color = (135, 246, 255) if packet_flash_timer > 0 else (60, 60, 60)
                pygame.draw.rect(screen, p_color, btn_data)
                pygame.draw.rect(screen, (52, 50, 199), btn_data, 2)
                
                # Label ABOVE icon
                dt = small_font.render(f"[{get_text('spacebar')}]", True, WHITE)
                screen.blit(dt, (btn_data.x + 5, btn_data.y + 2))
                
                if data_img:
                    scaled_data = pygame.transform.smoothscale(data_img, (30, 30))
                    screen.blit(scaled_data, (btn_data.x + 25, btn_data.y + 30))
                
                # Label BELOW icon for consistency
                p_lbl = small_font.render("Pakket", True, WHITE)
                screen.blit(p_lbl, (btn_data.x + btn_data.width//2 - p_lbl.get_width()//2, btn_data.y + 60))

                menu_title = font.render(get_text('select_cable') if 'select_cable' in LANGS[current_lang] else ("Choose Cable:" if current_lang == 'en' else "Choisir Câble:" if current_lang == 'fr' else "Kies Kabel:"), True, WHITE)
                screen.blit(menu_title, (810, 50))
                
                # Level 1 & 2: Show Cat 5 + Cat 5e; Level 3+: Show Straight + Crossover; Free Mode: Show 3 options
                is_free_mode = mission_sys.get_current() is None or mission_sys.get_current().type == "DONE"
                if is_free_mode:
                    cable_btns = [(btn_straight, 'Straight'), (btn_cross, 'Crossover'), (btn_wan, 'Fiber')]
                elif mission_sys.level <= 2:
                    cable_btns = [(btn_straight, 'Cat 5'), (btn_cross, 'Fiber')]
                else:
                    cable_btns = [(btn_straight, 'Straight'), (btn_cross, 'Crossover')]
                
                for btn, name in cable_btns:
                    btn_color = (0, 255, 148) if current_cable == name else (60, 60, 60)
                    pygame.draw.rect(screen, btn_color, btn)
                    pygame.draw.rect(screen, (52, 50, 199), btn, 2)
                    lbl_key = 'cat_straight' if name in ('Straight', 'Cat 5') else 'cat_cross' if name in ('Crossover', 'Fiber') else 'wan_label'
                    label = 'Cat 5' if name == 'Cat 5' else 'Fiber' if name == 'Fiber' else get_text(lbl_key)
                    t = font.render(label, True, WHITE)
                    screen.blit(t, (btn.x + 10, btn.y + 10))
            # Terug naar Wereldknop tekenen
            is_free_mode = mission_sys.get_current() is None or mission_sys.get_current().type == "DONE"
            if (sm.current == 'House2' and mission_sys.level in (3, 4)) or (sm.current != 'World' and sm.current != 'Start' and is_free_mode):
                btn_w = pygame.Rect(20, HEIGHT//2 - 20, 220, 40)
                pygame.draw.rect(screen, (70, 70, 90), btn_w)
                pygame.draw.rect(screen, CYAN, btn_w, 2)
                tw = font.render(get_text('to_world'), True, WHITE)
                screen.blit(tw, (btn_w.x + btn_w.width//2 - tw.get_width()//2, btn_w.y + 10))

            # Huis Betreden Knop op Wereldkaart
            if sm.current == 'World':
                # Blinking logic for the button if a house is selected
                if selected_house:
                    s_blink = abs(math.sin(pygame.time.get_ticks() * 0.01))
                    btn_alpha = int(100 + s_blink * 155)
                    color = (100, 255, 100, btn_alpha)
                    # Support for transparent rectangle drawing
                    btn_s = pygame.Surface((btn_enter_house.width, btn_enter_house.height), pygame.SRCALPHA)
                    pygame.draw.rect(btn_s, color, (0, 0, btn_enter_house.width, btn_enter_house.height), 0, 5)
                    screen.blit(btn_s, (btn_enter_house.x, btn_enter_house.y))
                else:
                    pygame.draw.rect(screen, (60, 60, 80), btn_enter_house, 0, 5)
                
                pygame.draw.rect(screen, WHITE, btn_enter_house, 2, 5)
                tt = font.render(get_text('enter_house'), True, WHITE)
                screen.blit(tt, (btn_enter_house.x + btn_enter_house.width//2 - tt.get_width()//2, btn_enter_house.y + 15))
                
                # Pijl naar knop bij missie naar H2 (PAS ALS POPUP WEG IS)
                m = mission_sys.get_current()
        if active_device:
            if ui_alpha < 255:
                ui_alpha = min(255, ui_alpha + 25)
                
            os_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            box = pygame.Rect(WIDTH//2 - 250, HEIGHT//2 - 225, 500, 450)
            
            if active_window == "WEB" and mission_sys.surf_success and tm_img:
                pygame.draw.rect(os_surf, (230, 230, 230), box)
                os_surf.blit(tm_img, (box.x, box.y + 30))
            else:
                pygame.draw.rect(os_surf, (40, 40, 50), box)
            
            pygame.draw.rect(os_surf, (30, 30, 40), (box.x, box.y, box.width, 30))
            pygame.draw.line(os_surf, (52, 50, 199), (box.x, box.y + 30), (box.x + box.width, box.y + 30), 2)
            pygame.draw.rect(os_surf, (52, 50, 199), box, 3)
            
            pygame.draw.circle(os_surf, RED, (box.x + 15, box.y + 15), 6)
            pygame.draw.circle(os_surf, YELLOW, (box.x + 35, box.y + 15), 6)
            pygame.draw.circle(os_surf, GREEN, (box.x + 55, box.y + 15), 6)
            
            if active_window != "MENU":
                btn_back = pygame.Rect(box.x + 75, box.y + 4, 60, 22)
                pygame.draw.rect(os_surf, GRAY, btn_back)
                t = small_font.render(get_text('back'), True, WHITE)
                os_surf.blit(t, (btn_back.x + 10, btn_back.y + 2))
                
            title_text = ""
            if active_window == "MENU":
                title_text = f"Console - {active_device.type} {active_device.id}"
            elif active_window == "IP":
                title_text = f"{get_text('ip_settings')} - {active_device.type}"
            elif active_window == "WEB":
                title_text = f"{get_text('web_browsing')} - {active_device.type}"
                
            tx = box.x + 150 if active_window != "MENU" else box.x + 80
            t = font.render(title_text, True, WHITE)
            os_surf.blit(t, (tx, box.y + 3))

            # Inner content
            if active_window == "MENU":
                bx, by = box.x + 50, box.y + 70
                if active_device.type == 'Laptop':
                    options = [('wifi', "wifi.png"), ('web_browsing', "web_browsing.png"), ('terminal', "terminal.png")]
                elif active_device.type == 'PC':
                    options = [('ip_settings', "ip_instellingen.png"), ('web_browsing', "web_browsing.png"), ('terminal', "terminal.png")]
                else:
                    options = [('ip_settings', "ip_instellingen.png"), ('terminal', "terminal.png"), ('restart', "restart.png")]
                
                for key, icon_file in options:
                    r = pygame.Rect(bx, by, 130, 130)
                    pygame.draw.rect(os_surf, (220, 220, 220), r)
                    pygame.draw.rect(os_surf, GRAY, r, 2)
                    
                    icon = get_ext_icon(icon_file)
                    if icon:
                        os_surf.blit(icon, (bx + 35, by + 15))
                    
                    # Label (Localized)
                    lbl = font.render(get_text(key), True, WHITE)
                    os_surf.blit(lbl, (bx + 65 - lbl.get_width()//2, by + 90))
                    
                    bx += 145
                    
            elif active_window == "IP":
                cy = HEIGHT//2  # center Y of the box

                # --- PC/Laptop: DHCP toggle ABOVE IP inputs ---
                if mission_sys.level >= 3 and active_device.type in ('PC', 'Laptop'):
                    is_dhcp = getattr(active_device, 'dhcp', False)
                    dhcp_lbl = font.render("DHCP:", True, WHITE)
                    os_surf.blit(dhcp_lbl, (WIDTH//2 - 200, cy - 100))
                    btn_dhcp = pygame.Rect(WIDTH//2 + 20, cy - 105, 140, 32)
                    pygame.draw.rect(os_surf, (0, 180, 0) if is_dhcp else (160, 50, 50), btn_dhcp, 0, 6)
                    pygame.draw.rect(os_surf, BLACK, btn_dhcp, 2, 6)
                    dhcp_st = font.render("Actief" if is_dhcp else "Niet Actief", True, WHITE)
                    os_surf.blit(dhcp_st, (btn_dhcp.x + btn_dhcp.width//2 - dhcp_st.get_width()//2, btn_dhcp.y + 6))

                # --- Router ISP Button ---
                if active_device.type == 'Router' and active_window == "IP":
                    btn_isp_sett = pygame.Rect(WIDTH//2 - 100, cy - 105, 200, 32)
                    pygame.draw.rect(os_surf, (150, 150, 180), btn_isp_sett, 0, 5)
                    pygame.draw.rect(os_surf, BLACK, btn_isp_sett, 2, 5)
                    isp_t = font.render("ISP Instellingen", True, WHITE)
                    os_surf.blit(isp_t, (btn_isp_sett.x + btn_isp_sett.width//2 - isp_t.get_width()//2, btn_isp_sett.y + 6))

                # --- IP Address input ---
                t1 = font.render("IP Adres:", True, WHITE)
                os_surf.blit(t1, (WIDTH//2 - 200, cy - 40))

                # Gray out inputs if PC DHCP is active
                is_dhcp_on = active_device.type in ('PC', 'Laptop') and getattr(active_device, 'dhcp', False)
                if is_dhcp_on:
                    pygame.draw.rect(os_surf, (210, 210, 210), (WIDTH//2 - 95, cy - 45, 200, 30))
                    auto_txt = small_font.render("Automatisch via DHCP", True, (100, 100, 100))
                    os_surf.blit(auto_txt, (WIDTH//2 - 95, cy - 37))
                    
                    pygame.draw.rect(os_surf, (210, 210, 210), (WIDTH//2 - 95, cy + 15, 200, 30))
                    os_surf.blit(auto_txt.copy(), (WIDTH//2 - 95, cy + 23))
                    
                    if mission_sys.level >= 2:
                        pygame.draw.rect(os_surf, (210, 210, 210), (WIDTH//2 - 95, cy + 75, 200, 30))
                        os_surf.blit(auto_txt.copy(), (WIDTH//2 - 95, cy + 83))
                        pygame.draw.rect(os_surf, (210, 210, 210), (WIDTH//2 - 95, cy + 135, 200, 30))
                        os_surf.blit(auto_txt.copy(), (WIDTH//2 - 95, cy + 143))
                else:
                    ip_input.draw(os_surf)

                # --- Subnet mask input ---
                t2 = font.render("Subnet Mask:", True, WHITE)
                os_surf.blit(t2, (WIDTH//2 - 200, cy + 20))
                if not is_dhcp_on:
                    subnet_input.draw(os_surf)

                # --- Level 2+ Gateway & DNS ---
                if mission_sys.level >= 2 and active_device.type in ('PC', 'Laptop'):
                    t3 = font.render("Default GW:", True, WHITE)
                    os_surf.blit(t3, (WIDTH//2 - 200, cy + 80))
                    if not is_dhcp_on: gw_input.draw(os_surf)
                    
                    t4 = font.render("DNS Server:", True, WHITE)
                    os_surf.blit(t4, (WIDTH//2 - 200, cy + 140))
                    if not is_dhcp_on: dns_input.draw(os_surf)

                # --- Router: DHCP Server toggle BELOW subnet (Level 3+) ---
                if mission_sys.level >= 3 and active_device.type == 'Router':
                    is_srv = getattr(active_device, 'dhcp_srv', False)
                    srv_lbl = font.render("DHCP Server:", True, WHITE)
                    os_surf.blit(srv_lbl, (WIDTH//2 - 200, cy + 85))
                    btn_srv = pygame.Rect(WIDTH//2 + 20, cy + 80, 140, 32)
                    pygame.draw.rect(os_surf, (0, 120, 200) if is_srv else (160, 50, 50), btn_srv, 0, 6)
                    pygame.draw.rect(os_surf, BLACK, btn_srv, 2, 6)
                    srv_st = font.render("Actief" if is_srv else "Niet Actief", True, WHITE)
                    os_surf.blit(srv_st, (btn_srv.x + btn_srv.width//2 - srv_st.get_width()//2, btn_srv.y + 6))

                # --- Save button ---
                save_y = cy + 180 if (mission_sys.level >= 2 and active_device.type in ('PC', 'Laptop')) else cy + 130
                btn_save = pygame.Rect(WIDTH//2 - 50, save_y, 100, 30)
                if not is_dhcp_on:
                    pygame.draw.rect(os_surf, (100, 200, 100), btn_save)
                    pygame.draw.rect(os_surf, (52, 50, 199), btn_save, 2)
                    st = font.render(get_text('save'), True, WHITE)
                    os_surf.blit(st, (btn_save.x + btn_save.width//2 - st.get_width()//2, btn_save.y + 5))

            elif active_window == "ISP":
                # Vergroten van de box voor ISP instellingen om overlap te voorkomen
                box = pygame.Rect(WIDTH//2 - 280, HEIGHT//2 - 200, 560, 400)
                pygame.draw.rect(os_surf, (240, 240, 240), box)
                pygame.draw.rect(os_surf, (200, 200, 200), (box.x, box.y, box.width, 30))
                pygame.draw.rect(os_surf, GRAY, box, 3)
                
                # Header buttons
                pygame.draw.circle(os_surf, RED, (box.x + 15, box.y + 15), 6)
                pygame.draw.circle(os_surf, YELLOW, (box.x + 35, box.y + 15), 6)
                pygame.draw.circle(os_surf, GREEN, (box.x + 55, box.y + 15), 6)
                
                btn_back = pygame.Rect(box.x + 75, box.y + 4, 60, 22)
                pygame.draw.rect(os_surf, GRAY, btn_back)
                pygame.draw.rect(os_surf, BLACK, btn_back, 1)
                t = small_font.render(get_text('back'), True, BLACK)
                os_surf.blit(t, (btn_back.x + 10, btn_back.y + 2))

                cy = box.y + 45
                title = font.render("WAN / ISP Instellingen", True, BLUE)
                os_surf.blit(title, (box.x + box.width//2 - title.get_width()//2, box.y + 5))
                
                inputs = [
                    ("Public IP:", isp_ip_input, cy),
                    ("Subnet Mask:", isp_subnet_input, cy + 50),
                    ("Default Gateway:", isp_gw_input, cy + 100),
                    ("Primary DNS:", isp_dns_p_input, cy + 150),
                    ("Secondary DNS:", isp_dns_s_input, cy + 200)
                ]
                
                for label, inp, y in inputs:
                    lbl = small_font.render(label, True, WHITE)
                    os_surf.blit(lbl, (box.x + 50, y))
                    # Align input boxes nicely
                    inp.x = box.x + 220
                    inp.y = y - 7
                    inp.draw(os_surf)
                    
                # Save button for ISP - repositioned to avoid overlap
                btn_save_isp = pygame.Rect(box.x + box.width//2 - 75, box.y + 340, 150, 40)
                pygame.draw.rect(os_surf, (100, 200, 100), btn_save_isp)
                pygame.draw.rect(os_surf, (52, 50, 199), btn_save_isp, 2)
                st = font.render("Opslaan", True, WHITE)
                os_surf.blit(st, (btn_save_isp.x + btn_save_isp.width//2 - st.get_width()//2, btn_save_isp.y + 8))

            elif active_window == "WEB":
                if not mission_sys.surf_success:
                    t = font.render("URL:", True, BLACK)
                    os_surf.blit(t, (WIDTH//2 - 200, HEIGHT//2 + 5))
                    url_input.draw(os_surf)
                    
                    btn_go = pygame.Rect(WIDTH//2 + 150, HEIGHT//2, 80, 40)
                    pygame.draw.rect(os_surf, BLUE, btn_go)
                    pygame.draw.rect(os_surf, BLACK, btn_go, 2)
                    gt = font.render(get_text('go'), True, WHITE)
                    os_surf.blit(gt, (btn_go.x + 25, btn_go.y + 10))
                    
                    if mission_sys.popup_text:
                        color = (0, 150, 0) if mission_sys.surf_success else RED
                        txt = font.render(mission_sys.popup_text, True, color)
                        os_surf.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 + 70))
                
            elif active_window == "TERM":
                    # Draw Terminal background
                    pygame.draw.rect(os_surf, (10, 10, 10), (box.x + 20, box.y + 40, box.width - 40, box.height - 80))
                    y_off = box.y + 50
                    for line in term_output:
                        t = small_font.render(line, True, (0, 255, 0))
                        os_surf.blit(t, (box.x + 30, y_off))
                        y_off += 20
                    term_input.draw(os_surf)
                
            elif active_window == "WIFI_LIST":
                    title = font.render("Beschikbare netwerken:", True, BLUE)
                    os_surf.blit(title, (box.x + 50, box.y + 50))
                    
                    nets = ["Free_WiFi_Station", "Telenet-ABCD", "TM_intern"]
                    ny = box.y + 90
                    for net in nets:
                        btn_net = pygame.Rect(box.x + 50, ny, 300, 40)
                        pygame.draw.rect(os_surf, (220, 220, 220), btn_net)
                        pygame.draw.rect(os_surf, BLACK, btn_net, 1)
                        nt = font.render(net, True, BLACK)
                        os_surf.blit(nt, (btn_net.x + 10, btn_net.y + 10))
                        ny += 50
                
            elif active_window == "WIFI_PWD":
                    title = font.render("Wachtwoord voor TM_intern:", True, BLUE)
                    os_surf.blit(title, (box.x + 50, box.y + 50))
                    wifi_pwd_input.x = box.x + 50
                    wifi_pwd_input.y = box.y + 90
                    wifi_pwd_input.draw(os_surf)
                    
                    btn_conn = pygame.Rect(box.x + 50, box.y + 150, 120, 40)
                    pygame.draw.rect(os_surf, GREEN, btn_conn)
                    pygame.draw.rect(os_surf, BLACK, btn_conn, 2)
                    ct = font.render("Verbinden", True, BLACK)
                    os_surf.blit(ct, (btn_conn.x + 15, btn_conn.y + 10))
                    
                    if mission_sys.popup_text:
                        pt = font.render(mission_sys.popup_text, True, RED)
                        os_surf.blit(pt, (box.x + 50, box.y + 210))
            
            os_surf.set_alpha(ui_alpha)
            screen.blit(os_surf, (0, 0))
        
        if sm.current != 'Start':
            # --- DHCP Background Logic (Level 3+) ---
            if mission_sys.level >= 3:
                for d in devices:
                    if d.type in ('PC', 'Laptop') and d.dhcp:
                        # Zoek verbinding met een Router
                        path = find_path_to_type(devices, connections, d, 'Router')
                        if path and path[-1].ip:
                             # Gevonden! Geef automatisch een IP (gebaseerd op index voor uniekheid)
                             d.ip = f"192.168.1.{10 + d.name_idx}"
                             d.subnet = "255.255.255.0"
                        else:
                             # Geen DHCP server (Router) gevonden
                             d.ip = "Searching..."
                             d.subnet = "---"
            
            mission_sys.check_conditions(devices, connections, packets, sm, active_window, active_device, (isp_ip_input, isp_subnet_input, isp_gw_input, isp_dns_p_input, isp_dns_s_input))
            mission_sys.draw_mission_text(screen, devices, (isp_ip_input, isp_subnet_input, isp_gw_input, isp_dns_p_input, isp_dns_s_input))
            mission_sys.draw_overlays(screen, devices)
        sm.draw(screen)
        
        if packet_flash_timer > 0:
            packet_flash_timer -= 1
            
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()


