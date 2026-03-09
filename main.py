import threading
import time
from random import randint
import ctypes

import pymem
import pymem.process

import glfw
import imgui
from imgui.integrations.glfw import GlfwRenderer
from OpenGL import GL

from pynput import keyboard, mouse

from Classes.PlayerVars import *
from Classes.Vector3 import Vec3
from MatFunctions.MathPy import GetBestTarget

from Utils.junkcode import *
from Utils.Autostrafe import AutoStrafe
from Utils.Bhop import Bhop
from Utils.Chams import Chams, ResetChams
from Utils.Utilities import GetWindowText, GetForegroundWindow, is_pressed
from Utils.WallhackFunctions import SetEntityGlow, GetEntityVars
from Utils.rcs import rcse

junkcode()

class UI:
    def __init__(self):
        self.Trigger = False
        self.TriggerKey = "mouse5"
        self.TriggerMode = "Hold"
        self.TriggerToggledOn = False
        self.changing_keybind = False

        self.temp_kb_listener = None
        self.temp_mouse_listener = None
        self.active_kb_listener = None
        self.active_mouse_listener = None

        self.TriggerDelayMs = 0
        self.RandomizeDelay = False
        self.DelayMinMs = 30
        self.DelayMaxMs = 90

        self.Wallhack = False
        self.Radar = False
        self.Chams = False

        self.Bhop = False
        self.auto_strafe = False
        self.Noflash = False
        self.RCS = False

        self.FovChanger = False
        self.FovValue = 120

        self.WRGB = [1.0, 0.0, 0.0]
        self.Ergb = [1.0, 0.2, 0.2]
        self.Argb = [0.2, 1.0, 0.2]


ui = UI()


def triggerbot(pm, crosshairid, client, localTeam, crosshairTeam):
    if crosshairid <= 0 or crosshairid > 64:
        return
    if localTeam == crosshairTeam:
        return

    if ui.RandomizeDelay and ui.DelayMinMs <= ui.DelayMaxMs:
        delay_ms = randint(ui.DelayMinMs, ui.DelayMaxMs)
    else:
        delay_ms = ui.TriggerDelayMs

    if delay_ms > 0:
        time.sleep(delay_ms / 1000.0)

    pm.write_int(client + dwForceAttack, 6)
    time.sleep(0.012)
    pm.write_int(client + dwForceAttack, 4)


def should_trigger():
    if ui.TriggerMode == "Hold":
        return ui.Trigger and better_is_pressed(ui.TriggerKey)
    elif ui.TriggerMode == "Toggle":
        return ui.Trigger and ui.TriggerToggledOn
    return False


def main():
    try:
        pm = pymem.Pymem("csgo.exe")
    except Exception:
        ctypes.windll.user32.MessageBoxW(None, "Could not find csgo.exe", "Error", 16)
        return

    client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
    engine = pymem.process.module_from_name(pm.process_handle, "engine.dll").lpBaseOfDll

    engine_pointer = pm.read_uint(engine + dwClientState)

    oldpunch = Vec3(0, 0, 0)
    newrcs = Vec3(0, 0, 0)
    punch = Vec3(0, 0, 0)
    rcs = Vec3(0, 0, 0)

    oldviewangle = 0.0

    print("CHEAT STARTED")

    while True:
        time.sleep(0.002)

        try:
            if "Counter-Strike" not in GetWindowText(GetForegroundWindow()).decode("cp1252"):
                time.sleep(1)
                continue

            player = pm.read_uint(client + dwLocalPlayer)

            (
                player,
                engine_pointer,
                glow_manager,
                crosshairid,
                getcrosshairTarget,
                immunitygunganme,
                localTeam,
                crosshairTeam,
                y_angle,
            ) = GetPlayerVars(pm, client, engine, engine_pointer)

            if should_trigger():
                triggerbot(pm, crosshairid, client, localTeam, crosshairTeam)

            if ui.FovChanger and player:
                try:
                    is_scoped = pm.read_bool(player + 0x9974)
                    if not is_scoped:
                        pm.write_int(player + m_iDefaultFOV, ui.FovValue)
                        pm.write_int(player + m_iFOV, ui.FovValue)
                        time.sleep(0.001)
                        pm.write_int(player + m_iDefaultFOV, ui.FovValue)
                        pm.write_int(player + m_iFOV, ui.FovValue)
                except:
                    pass

            if ui.Noflash:
                pm.write_float(player + m_flFlashMaxAlpha, 0.0)

            if ui.RCS:
                oldpunch = rcse(pm, player, engine_pointer, oldpunch, newrcs, punch, rcs)

            if ui.Bhop and better_is_pressed("space"):
                Bhop(pm, client, player)

            if ui.auto_strafe and y_angle:
                y_angle = AutoStrafe(pm, client, player, y_angle, oldviewangle)
                oldviewangle = y_angle

            for i in range(64):
                entity = pm.read_uint(client + dwEntityList + i * 0x10)
                if not entity:
                    continue

                (
                    entity_glow,
                    entity_team_id,
                    entity_isdefusing,
                    entity_hp,
                    entity_dormant,
                ) = GetEntityVars(pm, entity)

                if entity_dormant:
                    continue

                if ui.Wallhack:
                    SetEntityGlow(
                        pm, entity_hp, entity_team_id, entity_dormant, localTeam,
                        glow_manager, entity_glow, False, False, ui.WRGB
                    )

                if ui.Radar:
                    pm.write_int(entity + m_bSpotted, 1)

                if ui.Chams:
                    Chams(
                        pm, engine, entity, False, ui.Ergb, ui.Argb,
                        False, True, entity_team_id, entity_hp, True, player
                    )

        except:
            continue

KEY_ALIASES = {
    "alt gr":      "right alt",
    "alt_gr":      "right alt",
    "altgr":       "right alt",
    "right alt":   "right alt",
    "alt_r":       "right alt",
    "alt_l":       "left alt",
}


def normalize_key_name(name: str) -> str:
    name = name.lower().strip()
    return KEY_ALIASES.get(name, name)

user32 = ctypes.windll.user32

VK_CODES = {

    "mouse1": 0x01,
    "mouse2": 0x02,
    "mouse3": 0x04,
    "mouse4": 0x05,
    "mouse5": 0x06,

    "space": 0x20,
    "shift": 0x10,
    "ctrl": 0x11,
    "alt": 0x12,
    "left alt": 0xA4,
    "right alt": 0xA5,
}


def get_vk(key: str) -> int:
    key = normalize_key_name(key)
    if len(key) == 1 and key.isalnum():
        return ord(key.upper())
    return VK_CODES.get(key, 0)


def better_is_pressed(key: str) -> bool:
    vk = get_vk(key)
    if vk == 0:
        return False
    return (user32.GetAsyncKeyState(vk) & 0x8000) != 0

def start_temp_listeners():
    def on_press(key):
        if not ui.changing_keybind:
            return
        try:
            name = key.char if hasattr(key, 'char') and key.char else key.name
            normalized = normalize_key_name(name)
            finish_binding(normalized)
        except:
            pass

    def on_click(x, y, button, pressed):
        if not ui.changing_keybind or not pressed:
            return
        name_map = {
            mouse.Button.left:   "mouse1",
            mouse.Button.right:  "mouse2",
            mouse.Button.middle: "mouse3",
            mouse.Button.x1:     "mouse4",
            mouse.Button.x2:     "mouse5",
        }
        if button in name_map:
            finish_binding(name_map[button])

    ui.temp_kb_listener = keyboard.Listener(on_press=on_press)
    ui.temp_mouse_listener = mouse.Listener(on_click=on_click)
    ui.temp_kb_listener.start()
    ui.temp_mouse_listener.start()


def finish_binding(key_name: str):
    normalized = normalize_key_name(key_name)
    ui.TriggerKey = normalized
    ui.changing_keybind = False
    stop_temp_listeners()
    setup_active_listener()


def stop_temp_listeners():
    if ui.temp_kb_listener:
        ui.temp_kb_listener.stop()
        ui.temp_kb_listener = None
    if ui.temp_mouse_listener:
        ui.temp_mouse_listener.stop()
        ui.temp_mouse_listener = None


def setup_active_listener():
    stop_active_listener()

    key = normalize_key_name(ui.TriggerKey)

    if key.startswith("mouse"):
        btn_map = {
            "mouse1": mouse.Button.left,
            "mouse2": mouse.Button.right,
            "mouse3": mouse.Button.middle,
            "mouse4": mouse.Button.x1,
            "mouse5": mouse.Button.x2,
        }
        btn = btn_map.get(key)
        if btn:
            def on_click(x, y, button, pressed):
                if button == btn and pressed:
                    handle_trigger_input()
            ui.active_mouse_listener = mouse.Listener(on_click=on_click)
            ui.active_mouse_listener.start()
    else:
        acceptable_names = {key}
        # Also accept the most common AltGr variants during listening
        if key == "right alt":
            acceptable_names.update({"alt gr", "alt_gr", "altgr", "alt_r"})
        if key == "left alt":
            acceptable_names.update({"alt_l"})

        def on_press(k):
            try:
                name = k.char if hasattr(k, 'char') and k.char else k.name
                norm = normalize_key_name(name)
                if norm in acceptable_names:
                    handle_trigger_input()
            except:
                pass

        ui.active_kb_listener = keyboard.Listener(on_press=on_press)
        ui.active_kb_listener.start()


def stop_active_listener():
    if ui.active_kb_listener:
        ui.active_kb_listener.stop()
        ui.active_kb_listener = None
    if ui.active_mouse_listener:
        ui.active_mouse_listener.stop()
        ui.active_mouse_listener = None


def handle_trigger_input():
    if ui.TriggerMode == "Hold":
        pass
    elif ui.TriggerMode == "Toggle":
        # Only toggle if CS is foreground
        try:
            fg = GetForegroundWindow()
            txt = GetWindowText(fg).decode("cp1252")
            if "Counter-Strike" not in txt:
                return
        except:
            return
        ui.TriggerToggledOn = not ui.TriggerToggledOn


def imgui_menu():
    glfw.init()

    window = glfw.create_window(540, 580, "Python CSGO External", None, None)
    glfw.make_context_current(window)

    imgui.create_context()
    impl = GlfwRenderer(window)

    trigger_modes = ["Hold", "Toggle"]

    setup_active_listener()

    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()

        imgui.new_frame()

        imgui.begin("Python External")

        if imgui.begin_tab_bar("MainTabs"):

            if imgui.begin_tab_item("Triggerbot")[0]:

                _, ui.Trigger = imgui.checkbox("Enable Triggerbot", ui.Trigger)

                if ui.Trigger:

                    changed, idx = imgui.combo(
                        "Mode",
                        trigger_modes.index(ui.TriggerMode),
                        trigger_modes
                    )
                    if changed:
                        ui.TriggerMode = trigger_modes[idx]

                    imgui.text("Keybind:")
                    imgui.same_line()

                    display_key = ui.TriggerKey.upper()
                    if display_key == "RIGHT ALT":
                        display_key = "RIGHT ALT / ALT GR"

                    btn_text = "Set Key" if not ui.changing_keybind else "Listening..."
                    if imgui.button(btn_text):
                        ui.changing_keybind = not ui.changing_keybind
                        if ui.changing_keybind:
                            start_temp_listeners()
                        else:
                            stop_temp_listeners()

                    imgui.same_line()
                    if ui.changing_keybind:
                        imgui.text_colored("Press any key or mouse button...", 1.0, 0.3, 0.3, 1.0)
                    else:
                        imgui.text(f"[{display_key}]")

                    if ui.TriggerMode == "Toggle":
                        imgui.text(f"Status: {'ON' if ui.TriggerToggledOn else 'OFF'}")
                        imgui.same_line()
                        if imgui.button("Toggle Now"):
                            ui.TriggerToggledOn = not ui.TriggerToggledOn

                    imgui.separator()
                    imgui.text("Reaction Delay")

                    _, ui.TriggerDelayMs = imgui.slider_int(
                        "Fixed delay (ms)", ui.TriggerDelayMs, 0, 200, format="%d ms"
                    )

                    _, ui.RandomizeDelay = imgui.checkbox("Randomize", ui.RandomizeDelay)

                    if ui.RandomizeDelay:
                        imgui.indent()
                        _, ui.DelayMinMs = imgui.slider_int(
                            "Min (ms)", ui.DelayMinMs, 0, 150, format="%d ms"
                        )
                        _, ui.DelayMaxMs = imgui.slider_int(
                            "Max (ms)", ui.DelayMaxMs, ui.DelayMinMs, 250, format="%d ms"
                        )
                        imgui.unindent()
                        if ui.DelayMinMs > ui.DelayMaxMs:
                            ui.DelayMaxMs = ui.DelayMinMs

                imgui.end_tab_item()

            if imgui.begin_tab_item("Visuals")[0]:
                _, ui.Wallhack = imgui.checkbox("Glow", ui.Wallhack)
                _, ui.Radar = imgui.checkbox("Radar", ui.Radar)
                _, ui.Chams = imgui.checkbox("Chams", ui.Chams)
                imgui.end_tab_item()

            if imgui.begin_tab_item("Misc")[0]:
                _, ui.Bhop = imgui.checkbox("Bunnyhop", ui.Bhop)
                _, ui.auto_strafe = imgui.checkbox("Auto Strafe", ui.auto_strafe)
                _, ui.Noflash = imgui.checkbox("No Flash", ui.Noflash)
                _, ui.RCS = imgui.checkbox("RCS", ui.RCS)

                imgui.separator()

                _, ui.FovChanger = imgui.checkbox("FOV Changer", ui.FovChanger)
                if ui.FovChanger:
                    _, ui.FovValue = imgui.slider_int("FOV", ui.FovValue, 90, 140)

                imgui.end_tab_item()

            imgui.end_tab_bar()

        imgui.end()

        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)

    stop_temp_listeners()
    stop_active_listener()

    impl.shutdown()
    glfw.terminate()


if __name__ == "__main__":
    threading.Thread(target=main, daemon=True).start()
    imgui_menu()

