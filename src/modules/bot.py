"""An interpreter that reads and executes user-created routines."""

import threading
import time
import git
import cv2
import inspect
import importlib
import traceback
from os.path import splitext, basename
from src.common import config, utils, settings
from src.detection import detection
from src.routine import components
from src.routine.routine import Routine
from src.command_book.command_book import CommandBook
from src.routine.components import Point
from src.common.vkeys import press, click, key_up
from src.common.interfaces import Configurable


# The rune's buff icon
RUNE_BUFF_TEMPLATE = cv2.imread('assets/rune_buff_template.jpg', 0)


class Bot(Configurable):
    """A class that interprets and executes user-defined routines."""

    DEFAULT_CONFIG = {
        'Interact': 'space',
        'Feed pet': '9'
    }

    def __init__(self):
        """Loads a user-defined routine on start up and initializes this Bot's main thread."""

        super().__init__('keybindings')
        config.bot = self

        self.rune_active = False
        self.in_rune_buff = False
        self.rune_pos = (0, 0)
        self.rune_closest_pos = (0, 0)      # Location of the Point closest to rune
        self.submodules = []
        self.command_book = None            # CommandBook instance
        # self.module_name = None
        # self.model = None
        # self.buff = components.Buff()

        # self.command_book = {}
        # for c in (components.Wait, components.Walk, components.Fall,
        #           components.Move, components.Adjust, components.Buff):
        #     self.command_book[c.__name__.lower()] = c

        config.routine = Routine()

        self.ready = False
        self.thread = threading.Thread(target=self._main)
        self.thread.daemon = True

    def start(self):
        """
        Starts this Bot object's thread.
        :return:    None
        """

        self.update_submodules()
        print('\n[~] Started main bot loop')
        self.thread.start()

    def _main(self):
        """
        The main body of Bot that executes the user's routine.
        :return:    None
        """

        print('\n[~] Initializing detection algorithm:\n')
        model = detection.load_model()
        print('\n[~] Initialized detection algorithm')

        self.ready = True
        self.solve_rune_fail_count = 0

        config.listener.enabled = True
        last_fed = time.time()
        while True:
            if config.enabled and len(config.routine) > 0:
                # Buff and feed pets
                self.command_book.buff.main()
                pet_settings = config.gui.settings.pets
                auto_feed = pet_settings.auto_feed.get()
                num_pets = pet_settings.num_pets.get()
                now = time.time()
                if auto_feed and now - last_fed > 1200 / num_pets:
                    press(self.config['Feed pet'], 1)
                    last_fed = now

                # Highlight the current Point
                config.gui.view.routine.select(config.routine.index)
                config.gui.view.details.display_info(config.routine.index)

                # Execute next Point in the routine
                element = config.routine[config.routine.index]
                if self.rune_active and (isinstance(element, Point) \
                        # and element.location == self.rune_closest_pos:
                        and (element.location == self.rune_closest_pos or utils.distance(config.bot.rune_pos, element.location) <= 40) \
                        and time.time() - float(config.latest_solved_rune) >= (int(settings.rune_cd_min) * 60) \
                        or config.should_solve_rune \
                        or not self.in_rune_buff):
                    if not self.model:
                        self.model = detection.load_model()
                    if self._solve_rune(self.model):
                        self.solve_rune_fail_count = 0
                    else:
                        self.solve_rune_fail_count = self.solve_rune_fail_count + 1
                    if self.solve_rune_fail_count >= 2 and settings.auto_change_channel:
                        print("max try, auto change channel")
                        change_action = components.ChangeChannel(max_rand=40)
                        change_action.execute()
                    elif self.solve_rune_fail_count >= 2:
                        pass
                config.routine.next_step()
            else:
                time.sleep(0.03)

    @utils.run_if_enabled
    def _solve_rune(self, model):
        """
        Moves to the position of the rune and solves the arrow-key puzzle.
        :param model:   The TensorFlow model to classify with.
        :param sct:     The mss instance object with which to take screenshots.
        :return:        None
        """
        key_up("a") # TODO: temporary hack, fix this with better solution

        if self.in_rune_buff:
            print('in rune buff, quit solve rune')
            return True
        for _ in range(2):
            move = self.command_book['move']
            move(*self.rune_pos).execute()
            adjust = self.command_book['adjust']
            adjust(*self.rune_pos).execute()
        time.sleep(0.5)   
        for ii in range(2):
            if ii == 1:
                press("left", 1, down_time=0.1,up_time=0.3) 
            elif ii == 2:
                press("right", 1, down_time=0.2,up_time=0.3) 
            press(self.config['Interact'], 1, down_time=0.15,up_time=0.1) # Inherited from Configurable
            print('\nSolving rune:')
            time.sleep(1.5)
            for _ in range(5):
                if self.rune_active == False:
                    break
                frame = config.capture.frame
                # height, width, _n = frame.shape
                # solution_frame = frame[height//2-300:height//2+30, width //2-500:width//2+500]
                cv2.imwrite('./recording/s_' + str(time.time()) + '.png',frame)
                solution = detection.merge_detection(model, frame)
                if solution:
                    print(', '.join(solution))
                    if len(solution) == 4:
                        print('Solution found, entering result')
                        for arrow in solution:
                            press(arrow, 1, down_time=0.1)
                        time.sleep(1)
                        find_rune_buff = False
                        for _ in range(2):
                            time.sleep(0.2)
                            frame = config.capture.frame
                            rune_buff = utils.multi_match(frame[:95, :],
                                                        RUNE_BUFF_TEMPLATE,
                                                        threshold=0.93)
                            print('rune_buff matched : ',len(rune_buff))
                            if len(rune_buff) >= 2:
                                config.latest_solved_rune = time.time()
                                config.should_solve_rune = False
                                self.rune_active = False
                                self.in_rune_buff = True
                                find_rune_buff = True
                            if len(rune_buff) >= 3:
                                rune_buff_pos = min(rune_buff, key=lambda p: p[0])
                                print('rune_buff_pos : ', rune_buff_pos)
                                target = (
                                    round(rune_buff_pos[0]),
                                    round(rune_buff_pos[1])
                                )
                                utils.game_window_click(target, button='right')
                                config.latest_solved_rune = time.time()
                                config.should_solve_rune = False
                                self.rune_active = False
                                self.in_rune_buff = True
                                find_rune_buff = True
                                utils.game_window_click((700,120), button='right')
                        if find_rune_buff:
                            return True
            press("left", 1, down_time=0.05,up_time=0.1)
            press("right", 1, down_time=0.05,up_time=0.1)
            if self.rune_active == False:
                break
            time.sleep(2.8) 
        return False
    
    def load_commands(self, file):
        try:
            self.command_book = CommandBook(file)
            config.gui.settings.update_class_bindings()
        except ValueError:
            pass    # TODO: UI warning popup, say check cmd for errors
        #
        # utils.print_separator()
        # print(f"[~] Loading command book '{basename(file)}':")
        #
        # ext = splitext(file)[1]
        # if ext != '.py':
        #     print(f" !  '{ext}' is not a supported file extension.")
        #     return False
        #
        # new_step = components.step
        # new_cb = {}
        # for c in (components.Wait, components.Walk, components.Fall):
        #     new_cb[c.__name__.lower()] = c
        #
        # # Import the desired command book file
        # module_name = splitext(basename(file))[0]
        # target = '.'.join(['resources', 'command_books', module_name])
        # try:
        #     module = importlib.import_module(target)
        #     module = importlib.reload(module)
        # except ImportError:     # Display errors in the target Command Book
        #     print(' !  Errors during compilation:\n')
        #     for line in traceback.format_exc().split('\n'):
        #         line = line.rstrip()
        #         if line:
        #             print(' ' * 4 + line)
        #     print(f"\n !  Command book '{module_name}' was not loaded")
        #     return
        #
        # # Check if the 'step' function has been implemented
        # step_found = False
        # for name, func in inspect.getmembers(module, inspect.isfunction):
        #     if name.lower() == 'step':
        #         step_found = True
        #         new_step = func
        #
        # # Populate the new command book
        # for name, command in inspect.getmembers(module, inspect.isclass):
        #     new_cb[name.lower()] = command
        #
        # # Check if required commands have been implemented and overridden
        # required_found = True
        # for command in [components.Buff]:
        #     name = command.__name__.lower()
        #     if name not in new_cb:
        #         required_found = False
        #         new_cb[name] = command
        #         print(f" !  Error: Must implement required command '{name}'.")
        #
        # # Look for overridden movement commands
        # movement_found = True
        # for command in (components.Move, components.Adjust):
        #     name = command.__name__.lower()
        #     if name not in new_cb:
        #         movement_found = False
        #         new_cb[name] = command
        #
        # if not step_found and not movement_found:
        #     print(f" !  Error: Must either implement both 'Move' and 'Adjust' commands, "
        #           f"or the function 'step'")
        # if required_found and (step_found or movement_found):
        #     self.module_name = module_name
        #     self.command_book = new_cb
        #     self.buff = new_cb['buff']()
        #     components.step = new_step
        #     config.gui.menu.file.enable_routine_state()
        #     config.gui.view.status.set_cb(basename(file))
        #     config.routine.clear()
        #     print(f" ~  Successfully loaded command book '{module_name}'")
        # else:
        #     print(f" !  Command book '{module_name}' was not loaded")

    def update_submodules(self, force=False):
        """
        Pulls updates from the submodule repositories. If FORCE is True,
        rebuilds submodules by overwriting all local changes.
        """

        utils.print_separator()
        print('[~] Retrieving latest submodules:')
        self.submodules = []
        repo = git.Repo.init()
        with open('.gitmodules', 'r') as file:
            lines = file.readlines()
            i = 0
            while i < len(lines):
                if lines[i].startswith('[') and i < len(lines) - 2:
                    path = lines[i + 1].split('=')[1].strip()
                    url = lines[i + 2].split('=')[1].strip()
                    self.submodules.append(path)
                    try:
                        repo.git.clone(url, path)       # First time loading submodule
                        print(f" -  Initialized submodule '{path}'")
                    except git.exc.GitCommandError:
                        sub_repo = git.Repo(path)
                        if not force:
                            sub_repo.git.stash()        # Save modified content
                        sub_repo.git.fetch('origin', 'main')
                        sub_repo.git.reset('--hard', 'FETCH_HEAD')
                        if not force:
                            try:                # Restore modified content
                                sub_repo.git.checkout('stash', '--', '.')
                                print(f" -  Updated submodule '{path}', restored local changes")
                            except git.exc.GitCommandError:
                                print(f" -  Updated submodule '{path}'")
                        else:
                            print(f" -  Rebuilt submodule '{path}'")
                        sub_repo.git.stash('clear')
                    i += 3
                else:
                    i += 1
