#! /usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import time

from multiprocessing import Process, Pipe
import platform
import multiprocessing

import pygame


# Define some colors.
BLACK = pygame.Color('black')
WHITE = pygame.Color('white')


# This is a simple class that will help us print to the screen.
# It has nothing to do with the joysticks, just outputting the
# information. Set verbose to True for testing
class TextPrint(object):
    def __init__(self, verbose=True):
        self.reset()
        self.font = pygame.font.Font(None, 20)
        self.verbose = verbose

    def tprint(self, screen, textString):
        if self.verbose:
            textBitmap = self.font.render(textString, True, BLACK)
            screen.blit(textBitmap, (self.x, self.y))
            self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15

    def indent(self):
        self.x += 10

    def unindent(self):
        self.x -= 10

def joystick_capture(save_path):
    pygame.init()

    # Set the width and height of the screen (width, height).
    screen = pygame.display.set_mode((500, 700))

    pygame.display.set_caption("Joystick")

    # Loop until the user clicks the close button.
    done = False

    # Used to manage how fast the screen updates.
    clock = pygame.time.Clock()

    # Initialize the joysticks.
    pygame.joystick.init()

    # Get ready to print.
    verbose = True
    textPrint = TextPrint(verbose)

    # -------- Main Program Loop -----------
    joystick_annotations_X = []
    joystick_annotations_Y = []
    joystick_annotations_ROLL = []

    while not done:
        #
        # EVENT PROCESSING STEP
        #
        # Possible joystick actions: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
        # JOYBUTTONUP, JOYHATMOTION
        for event in pygame.event.get(): # User did something.
            if event.type == pygame.QUIT: # If user clicked close.
                done = True # Flag that we are done so we exit this loop.
            elif event.type == pygame.JOYBUTTONDOWN:
                print("Joystick button pressed.")
            elif event.type == pygame.JOYBUTTONUP:
                print("Joystick button released.")

        #
        # DRAWING STEP
        #
        # First, clear the screen to white. Don't put other drawing commands
        # above this, or they will be erased with this command.
        screen.fill(WHITE)
        textPrint.reset()

        # Get count of joysticks.
        joystick_count = pygame.joystick.get_count()

        textPrint.tprint(screen, "Number of joysticks: {}".format(joystick_count))
        textPrint.indent()

        # For each joystick:
        for i in range(joystick_count):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()

            try:
                jid = joystick.get_instance_id()
            except AttributeError:
                # get_instance_id() is an SDL2 method
                jid = joystick.get_id()
            textPrint.tprint(screen, "Joystick {}".format(jid))
            textPrint.indent()

            # Get the name from the OS for the controller/joystick.
            name = joystick.get_name()
            textPrint.tprint(screen, "Joystick name: {}".format(name))

            try:
                guid = joystick.get_guid()
            except AttributeError:
                # get_guid() is an SDL2 method
                pass
            else:
                textPrint.tprint(screen, "GUID: {}".format(guid))

            # Usually axis run in pairs, up/down for one, and left/right for
            # the other.
            axes = joystick.get_numaxes()
            textPrint.tprint(screen, "Number of axes: {}".format(axes))
            textPrint.indent()

            # Axis 0 is Left/Right
            # Axis 1 is Up/Down
            # Axis 2 is Roll
            for i in range(axes):
                axis = joystick.get_axis(i)
                if i == 0:
                    joystick_annotations_X.append(axis)
                elif i == 1:
                    joystick_annotations_Y.append(axis)
                elif i == 2:
                    joystick_annotations_ROLL.append(axis)
                textPrint.tprint(screen, "Axis {} value: {:>6.3f}".format(i, axis))

        

            textPrint.unindent()

            buttons = joystick.get_numbuttons()
            textPrint.tprint(screen, "Number of buttons: {}".format(buttons))
            textPrint.indent()

            for i in range(buttons):
                button = joystick.get_button(i)
                textPrint.tprint(screen,
                                 "Button {:>2} value: {}".format(i, button))
            textPrint.unindent()

            hats = joystick.get_numhats()
            textPrint.tprint(screen, "Number of hats: {}".format(hats))
            textPrint.indent()

            # Hat position. All or nothing for direction, not a float like
            # get_axis(). Position is a tuple of int values (x, y).
            for i in range(hats):
                hat = joystick.get_hat(i)
                textPrint.tprint(screen, "Hat {} value: {}".format(i, str(hat)))
            textPrint.unindent()

            textPrint.unindent()

        # Update the screen
        pygame.display.flip()


        # Limit to 30 frames per second.
        clock.tick(30)

    # Save the anbnotations
    #np.save(save_path + '_X.npy', np.array(joystick_annotations_X))
    #np.save(save_path + '_Y.npy', np.array(joystick_annotations_Y))
    #np.save(save_path + '_ROLL.npy', np.array(joystick_annotations_ROLL))

    # Close the window and quit.
    # If you forget this line, the program will 'hang'
    # on exit if running from IDLE.
    pygame.quit()



# set up the pipes for the processes to communicate with each other

parent, child = Pipe()
save_path = "test3"
joystick_capture(save_path)

#joystick_thread = Process(target=joystick_capture, args=(child,save_path))
#joystick_thread.start()

time.sleep(5)
parent.send(True)
time.sleep(5)
print("Complete")

