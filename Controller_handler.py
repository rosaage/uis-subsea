import multiprocessing
from Threadwatch import Threadwatcher
import threading
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
import time
import sys
DPAD = 1538
BUTTON_DOWN = 1539
BUTTON_UP = 1540
JOYSTICK = 1536

BUTTON_A = 0
BUTTON_B = 1
BUTTON_X = 2
BUTTON_Y = 3


def clear_screen():
    pass
    os.system("cls")


class Controller:
    def __init__(self, queue_to_rov: multiprocessing.Queue, t_watch: Threadwatcher, id, joystick_deadzone=15) -> None:
        self.queue_to_rov = queue_to_rov
        self.t_watch = t_watch
        self.id = id
        self.joystick_deadzone = joystick_deadzone  # deadzone in percent
        self.buttons = [0]*10
        self.joysticks = [0]*7
        self.dpad = (0, 0)
        self.controller_stop_point = 1.000030518509476

        self.camera_motor = 0

        self.boyancy = 0
        self.first_run = True
        self.button_names = {0: "A", 1: "B", 2: "X", 3: "Y", 4: "Left button back", 5: "Right button back", 6: "Back", 7: "Start", 8: "Thumb button left", 9: "Thumb button right"}
        self.duration = -1
        pygame.init()
        self.wait_for_controller()
        self.clock = pygame.time.Clock()

    def pack_controller_values(self):
        values = {"joysticks": self.joysticks, "camera_movement": self.joysticks[3],  "buttons": self.buttons, "dpad": self.dpad, "camera_to_control": self.camera_motor, "time_between_updates": self.duration}
        # print(values)
        return values

    def reset_button(self, event) -> None:
        self.buttons[event.button] = 0 


    def wait_for_controller(self):
        """wait_for_controller will attempt to connect until it finds a controller."""
        while self.t_watch.should_run(self.id):    
            try:
                if not self.first_run:
                    pygame.joystick.quit()
                else:
                    # clear_screen()
                    print("Attempting to Connect to controller")
                pygame.joystick.init()
                global joystick
                if pygame.joystick.get_count() > 1:
                    print("Found several controllers. Connecting to controller 0 only")
                joystick = pygame.joystick.Joystick(0)
                print(f"Connected to {joystick.get_name()}")
                break
            except:
                self.first_run = False
                for sec in range(5,0,-1):
                        sys.stdout.write("\r" + f"Could not find controller. if it is already connected, try reconnecting it! retrying in {sec} seconds")
                        time.sleep(1)
                        sys.stdout.flush()
        joystick.init()

    def get_new_range(self, value, min, max, scale=100):
        return((value-min)/(max-min))*scale

    def normalize_joysticks(self, event):
        # (x-min)/(max-min)
        if event.axis == 1:
            return self.deadzone_adjustment(-round((2*(event.value--self.controller_stop_point)/(self.controller_stop_point--self.controller_stop_point)-1)*100))

        if event.axis == 3:
            return self.deadzone_adjustment(-round((2*(event.value--self.controller_stop_point)/(self.controller_stop_point--self.controller_stop_point)-1)*100))


        if event.axis == 4:
            return self.deadzone_adjustment(-round(self.get_new_range(event.value,-self.controller_stop_point, self.controller_stop_point))) # opp og ned på roboten har range fra 0 til 100 og 0 til -100
            # return round((event.value--self.controller_stop_point)/(self.controller_stop_point--self.controller_stop_point)*100)
        if event.axis == 5:
            return self.deadzone_adjustment(round(self.get_new_range(event.value,-self.controller_stop_point, self.controller_stop_point))) # opp og ned på roboten har range fra 0 til 100 og 0 til -100
            # return round((event.value--self.controller_stop_point)/(self.controller_stop_point--self.controller_stop_point)*100)

        return self.deadzone_adjustment(round((2*(event.value--self.controller_stop_point)/(self.controller_stop_point--self.controller_stop_point)-1)*100))

        # return round(self.get_new_range(event.value,-self.controller_stop_point, self.controller_stop_point))

    def deadzone_adjustment(self, value) -> int:
        if abs(value) < self.joystick_deadzone+1:
            return 0
        return value

    def write_controller_values(self, local=False):
        # writestring = self.joysticks
        writestring = f"{self.buttons} - {self.dpad} - {self.joysticks}"
        if not local:
            return writestring
        
        # for i in range(len(self.joysticks)):
        #     writestring += f"axis {i} : {self.joysticks}%"
        sys.stdout.write("\r" + f"{writestring}                                     ")
        sys.stdout.flush()
        # sys.stdout.write("\r" + f"{self.buttons} - {self.joysticks}                     ")
        # sys.stdout.flush()


    def lekkasje(self, duration=250, loops=3, pause_duration=500):
        for i in range(loops):
            joystick.rumble(1,1,duration)
            time.sleep((duration+pause_duration)/1000)

    def get_events_loop(self, t_watch: Threadwatcher, id: int, debug=False, debug_all=False):
        while t_watch.should_run(id):
            if pygame.joystick.get_count() < 1:
                self.wait_for_controller()
            self.duration = self.clock.tick(20)
            # print(duration)
            for event in pygame.event.get():
                # print("entered event check")
                if event.type == DPAD: #dpad (both up and down)
                    self.dpad = event.value
                    # self.dpad = [val*100 for val in event.value]

                if event.type == BUTTON_DOWN: #button down
                    self.buttons[event.button] = 1

                    if self.buttons[BUTTON_Y] == 1:
                        self.camera_motor = (self.camera_motor+1)%2
                        # threading.Thread(target=self.lekkasje).start()

                    if debug_all:
                        if event.button == BUTTON_A:
                            print("A")

                        if event.button == BUTTON_B:
                            print("B")
                        if event.button == BUTTON_X:
                            print("X")
                        if event.button == BUTTON_Y:
                            print("Y")
                        if event.button == 4:
                            print("Left button")
                        if event.button == 5:
                            print("Right button")
                        if event.button == 6:
                            print("Back")
                        if event.button == 7:
                            print("Start")
                        if event.button == 8:
                            print("Thumb button left")
                        if event.button == 9:
                            print("Thumb button right")


                    # print(event.button)
                if event.type == BUTTON_UP: #button up
                    self.reset_button(event)

                    if debug_all:
                        if event.button == 0:
                            # pygame.joystick.Joystick.stop_rumble()
                            print("A up")
                        if event.button == 1:
                            print("B up")
                        if event.button == 2:
                            print("X up")
                        if event.button == 3:
                            print("Y up")
                        if event.button == 4:
                            print("Left button up")
                        if event.button == 5:
                            print("Right button up")
                        if event.button == 6:
                            print("Back up")
                        if event.button == 7:
                            print("Start up")
                        if event.button == 8:
                            print("Thumb button left up")
                        if event.button == 9:
                            print("Thumb button right up")
                    self.reset_button(event)

                # There is a bug where only one joystick is registered if the program has been started, but no buttons or dpad has been pressed yet.
                # this is "solved" by the fact that the other joystick reduces the value of the first joystick that was pressed. Since we add up the
                # joystick values to get total trust. Example: axis 4: -50, axis 5: 100. Value we get is 50. With bug: axis 4: 0, axis 5: 50.
                if event.type == JOYSTICK: #joystick movement
                    self.joysticks[event.axis] = self.normalize_joysticks(event)
                    self.joysticks[6] = self.joysticks[4] + self.joysticks[5]

                    
                    if debug_all:
                        if event.axis == 0:
                            if event.value > 0:
                                print(f"Roboten kjører mot høyre med {self.normalize_joysticks(event)}% kraft")
                            else:
                                print(f"Roboten kjører mot venstre med {self.normalize_joysticks(event)}% kraft")
                        if event.axis == 4 or event.axis == 5:
                            print(f"{event.axis} signal: {event.value}, normalized: {self.normalize_joysticks(event)}")
                            if event.value > 0:
                                print(f"Roboten kjører framover med {self.normalize_joysticks(event)}% kraft")
                            else:
                                print(f"Roboten kjører bakover med {self.normalize_joysticks(event)}% kraft")
                        elif event.axis == 2:
                            if event.value > 0:
                                print(f"Roboten roterer mot klokka med {self.normalize_joysticks(event)}% kraft")
                            else:
                                print(f"Roboten roterer med klokka med {self.normalize_joysticks(event)}% kraft")
                        elif event.axis == 3:
                            if event.value > 0:
                                print(f"Roboten tilter kamera med {self.normalize_joysticks(event)}% kraft")
                            else:
                                print(f"Roboten tilter kamera med {self.normalize_joysticks(event)}% kraft")
                        elif event.axis == 4:
                                print(f"Roboten går ned med {self.normalize_joysticks(event)}% kraft")
                        elif event.axis == 5:
                                print(f"Roboten går opp med {self.normalize_joysticks(event)}% kraft")
            if self.queue_to_rov is not None:
                # print("sending to main")
                self.queue_to_rov.put((1, self.pack_controller_values()))
                # print(self.buttons)
            elif debug and self.connection is None: 
                self.write_controller_values(local=True)
        print("closed connection")
        # self.connection.close()            


def run(queue_to_rov, t_watch: Threadwatcher, id, debug=True, debug_all=False):
    debug_all = False
    c = Controller(queue_to_rov, t_watch, id)
    c.get_events_loop(t_watch, id, debug=debug, debug_all=debug_all)

if __name__ == "__main__":
    pass
    # c = Controller(None)
    # run(None, True, False)
    # c.get_events_loop(debug=True, debug_all=False)