import win32api
from math import radians
from struct import unpack, pack
from filewrappers import PSPRAMFileDescriptor as PSPRam
from time import sleep


mariana = unpack('f', b'\x83\xf9\x22\x4a')[0]


def angletoyaw(i):
    if i >= 90:
        yaw = (180 - (i-15))*500/90
        height = 4
    elif i <= 50:
        yaw = max(1, (i*10))
        height = 0
    elif i < 70:
        yaw = max(1, (i*10))
        height = 1
    elif i < 80:
        yaw = max(1, (i*10))
        height = 2
    elif i < 90:
        yaw = max(1, (i*10))
        height = 3
    return max(0.1, yaw), height


class P3rdCam:
    def __init__(self, psp_ram, symbols):
        self.ram = psp_ram
        self.pitch_add = symbols["pitch"]
        self.yaw_add = symbols["yaw"]
    
    @property
    def yaw(self):
        self.ram.seek(self.yaw_add)
        return unpack("f", self.ram.read(4))[0]

    @yaw.setter
    def yaw(self, value):
        yaw, height = angletoyaw(value)
        self.ram.seek(self.yaw_add)
        self.ram.write(pack("f", yaw))
        self.ram.seek(0x09B477A4)
        self.ram.write(pack("b", height))
    
    @property
    def pitch(self):
        self.ram.seek(self.pitch_add)
        return self.ram.read(4) 
    
    @pitch.setter
    def pitch(self, angle):
        ang = round(radians(angle)*mariana)
        self.ram.seek(self.pitch_add)
        self.ram.write(ang.to_bytes(4, "big"))
    
    @property
    def height(self):
        self.ram.seek(0x09B477A4)
        return unpack("b", self.ram.read(1))[0]

    @height.setter
    def height(self, value):
        self.ram.seek(0x09B477A4)
        self.ram.write(pack("b", value))


def install_patch(pspram):
    patches = {"main.bin": "yawmain", "fixd.bin": "fixdown", "fixu.bin": "fixup", "yaw_hook.bin": "yaw_h", "pitch_hook.bin": "pitch_h"}
    with open("symfile") as file:
        symbols = { x.split(" ")[1].replace("\n", ""): int(x.split(" ")[0], 16) for x in file.readlines()[1:] if ":" not in x and " " in x}
    for file, symbol in patches.items():
        with open(file, "rb") as fd:
            pspram.seek(symbols[symbol])
            pspram.write(fd.read())
    return P3rdCam(pspram, symbols)
    





if __name__ == "__main__":
    CENTER = (win32api.GetSystemMetrics(0) // 2, win32api.GetSystemMetrics(1) // 2)

    last_pos = CENTER
    win32api.SetCursorPos(CENTER)

    curr_pos = win32api.GetCursorPos()
    movement = (curr_pos[0] - last_pos[0], curr_pos[1] - last_pos[1])
    last_pos = curr_pos

    sensibility = [.2, 0.20]

    pitch = 0
    yaw = 90

    psp_ram = PSPRam()

    cam = install_patch(psp_ram)

    while True:
        curr_pos = win32api.GetCursorPos()
        win32api.SetCursorPos(CENTER)
        movement = (curr_pos[0] - CENTER[0], curr_pos[1] - CENTER[1])
        yaw = min(140, max(0.1, yaw - (movement[1]*sensibility[1])))
        pitch = pitch - (movement[0]*sensibility[0])
        if pitch < 0:
            pitch += 360
        elif pitch > 360:
            pitch -= 360
        
        cam.yaw, cam.pitch = yaw, pitch
        print(movement, yaw, pitch)

        sleep(1/60)
