#env/Scripts/activate
#env/Scripts/python.exe

import os
import sys
import vlc
import pygame
import numpy as np
import pandas as pd
import argparse
import time

from audio_wrap import wrap_audio

# Define some colors.
BLACK = pygame.Color('black')
WHITE = pygame.Color('white')

def callback(self, player):

	print('FPS =',  player.get_fps())
	print('time =', player.get_time(), '(ms)')
	print('FRAME =', .001 * player.get_time() * player.get_fps())

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
            textBitmap = self.font.render(textString, True, WHITE)
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



def main(save_path, FPS=30):
    # Enable in Windows to use directx renderer instead of windib
    #os.environ["SDL_VIDEODRIVER"] = "directx"
    X=800
    Y=600

    pygame.init()
    screen = pygame.display.set_mode((X,Y),pygame.RESIZABLE)
    pygame.display.get_wm_info()
    pygame.display.set_caption("Annotation")


    print("Using %s renderer" % pygame.display.get_driver())
    # Used to manage how fast the screen updates.
    clock = pygame.time.Clock()

    # Initialize the joysticks.
    pygame.joystick.init()

    # CONNECT THE AUDIO
    font = pygame.font.Font('freesansbold.ttf', 24)
    text = font.render('Formatting capture...', True, (255, 255, 255), (0,0,0))
    textRect = text.get_rect()
    # set the center of the rectangular object.
    textRect.center = (X // 2, Y // 2)
    # Write to the interface
    screen.blit(text, textRect)
    pygame.display.update()

    print("SAVE PATH:", save_path)

    vid_path = wrap_audio(save_path)
    print(vid_path)
    time.sleep(0.1)

    print("AUDIO WRAPPED")

    # Get path to movie specified as command line argument
    movie = os.path.expanduser(vid_path)
    # Check if movie is accessible
    if not os.access(movie, os.R_OK):
        print('Error: %s file not readable' % movie)
        sys.exit(1)

    # Create instane of VLC and create reference to movie.
    vlcInstance = vlc.Instance()
    media = vlcInstance.media_new(movie)

    print("NEW VLC INSTANCE")

    # Create new instance of vlc player
    player = vlcInstance.media_player_new()

    print("NEW VLC INSTANCE 2")

    # Add a callback
    em = player.event_manager()
    em.event_attach(vlc.EventType.MediaPlayerTimeChanged, \
	    callback, player)

    print("CALLBACK ATTACHED")

    # PRINT INSTRUCTIONS TO SCREEN
    # create a text surface object,
    # on which text is drawn on it.
    text = font.render('Press spacebar to begin annotation.', True, (255, 255, 255), (0,0,0))
    # create a rectangular object for the
    # text surface object
    textRect = text.get_rect()
    # set the center of the rectangular object.
    textRect.center = (X // 2, Y // 2)
    # Write to the interface
    screen.blit(text, textRect)
    pygame.display.update()

    # Pass pygame window id to vlc player, so it can render its contents there.
    win_id = pygame.display.get_wm_info()['window']
    if sys.platform == "linux2": # for Linux using the X Server
        player.set_xwindow(win_id)
    elif sys.platform == "win32": # for Windows
        player.set_hwnd(win_id)
    elif sys.platform == "darwin": # for MacOS
        player.set_agl(win_id)

    # Load movie into vlc player instance
    player.set_media(media)

    # Quit pygame mixer to allow vlc full access to audio device (REINIT AFTER MOVIE PLAYBACK IS FINISHED!)
    pygame.mixer.quit()

    # Start movie playback on spacebar pull

    vid_off=True
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    while vid_off:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == 32:
                    print("Spacebar Pressed")
                    player.play()
                    vid_off=False
                    break
                else:
                    print("Press the spacebar to start annotations")
        clock.tick(FPS)

    # Get ready to print.
    verbose = True
    textPrint = TextPrint(verbose)

    # -------- Main Program Loop -----------
    joystick_annotations_X = []
    joystick_annotations_Y = []
    joystick_annotations_ROLL = []
    timestamps = []

    done=False

    while not done and (player.get_state() != vlc.State.Ended):
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

        # Keep a list of the Frame nums for reference
        timestamps.append(.001 * player.get_time() * player.get_fps())

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
        clock.tick(FPS)

    # Save the anbnotations
    #np.save(save_path.split('.')[0] + '_X.npy', np.array(joystick_annotations_X))
    #np.save(save_path.split('.')[0] + '_Y.npy', np.array(joystick_annotations_Y))
    #np.save(save_path.split('.')[0] + '_ROLL.npy', np.array(joystick_annotations_ROLL))
    #np.save(save_path.split('.')[0] + '_timestamp.npy', np.array(timestamps))

    pd.DataFrame({"frame": timestamps,
                  "X": joystick_annotations_X,
                  "Y": joystick_annotations_Y,
                  "Roll":joystick_annotations_ROLL
                  }).to_csv(save_path.split('.')[0] + "_annotations.csv")

    print("ANNOTATIONS SAVED TO ",save_path.split('.')[0])
    # Close the window and quit.
    # If you forget this line, the program will 'hang'
    # on exit if running from IDLE.
    player.stop()
    print("Player Stopped")
    pygame.quit()
    print("EXITING")




#if __name__ == "__main__":
#    # NEED TO UPDATE THE ARG PARER AND REFACTOR
#    parser = argparse.ArgumentParser()
#    parser.add_argument('--FPS', type=int, default=30,
#                        help='video playback FPS')
#    parser.add_argument('--save_path', default='test.mkv',
#                        help='The path to the MKV file to be annotated')

#    args = parser.parse_args()


#    main(args.save_path, args.FPS)
