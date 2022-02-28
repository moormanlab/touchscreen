#!/usr/bin/python3
import pygame, pygame_menu
import logging
import os, subprocess
from importlib import import_module
from importlib import reload as reload_module
import inspect
import datetime
import time
import tinydb

# import showip
from keyboard import keyboard
#from return_to_menu import return_to_menu
from hal import isRaspberryPI, LiqReward, IRSensor, Sound, Battery
from utils import SCREENWIDTH, SCREENHEIGHT

from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import smtplib
import re
import functools

# Email Variables
SMTP_SERVER = 'smtp.gmail.com'  # Email Server (don’t change!)
SMTP_PORT = 587  # Server Port (don’t change!)
GMAIL_USERNAME = 'moormanlabtouchscreen@gmail.com'
GMAIL_PASSWORD = 'moormanlabTC'

logger = logging.getLogger('TouchMenu')

logPath = os.path.abspath('logs')
# print(logPath)
protocolsPath = 'protocols'
userLogHdlr = None
touchDBFile = 'touchDB.json'
touchDB = tinydb.TinyDB(touchDBFile)

EMAIL=""
SELECTED_FILE_PATH = [""]
FILE_LIST = []
FILE_NAMES = []

def update_list():
    """
    Updates email list to choose from in send_data menu
    """
    FILE_NAMES.clear()
    i = 0
    for filename in os.listdir(logPath):
        if filename.endswith('.log'):
            i += 1
            FILE_NAMES.append((filename, i))
    FILE_NAMES.sort()
    #print(FILE_NAMES[0][0])
    SELECTED_FILE_PATH[0] = os.path.join(logPath, FILE_NAMES[0][0])


# hardware_initialized = False


def add_back_button(menu):
    menu.add.vertical_margin(30)
    menu.add.button('Back', pygame_menu.events.BACK)


def add_close_button(menu):
    menu.add.vertical_margin(30)
    menu.add.button('Back', pygame_menu.events.CLOSE)


def initialize_menu(title):
    # Creates menu, adding title, and enabling touchscreen mode
    menu = pygame_menu.Menu(title, SCREENWIDTH, SCREENHEIGHT,
                            theme=pygame_menu.themes.THEME_DARK,
                            onclose=pygame_menu.events.RESET,
                            touchscreen=True if isRaspberryPI() else False,
                            joystick_enabled=False,
                            mouse_enabled=False if isRaspberryPI() else True,
                            )

    logger.debug('Menu created: {}'.format(title))

    return menu


def window_message(surface, message):
    menu = pygame_menu.Menu('Warning', int(SCREENWIDTH * .75), int(SCREENHEIGHT * .75),
                            theme=pygame_menu.themes.THEME_ORANGE,
                            onclose=pygame_menu.events.RESET,
                            touchscreen=True if isRaspberryPI() else False,
                            joystick_enabled=False,
                            mouse_enabled=False if isRaspberryPI() else True,
                            )

    menu.add.label(message)
    add_close_button(menu)

    menu.mainloop(surface, fps_limit=30)
    return

def list_view(surface, message):
    menu = pygame_menu.Menu('Attached Files', int(SCREENWIDTH * .75), int(SCREENHEIGHT * .75),
                            theme=pygame_menu.themes.THEME_DARK,
                            onclose=pygame_menu.events.RESET,
                            touchscreen=True if isRaspberryPI() else False,
                            joystick_enabled=False,
                            mouse_enabled=False if isRaspberryPI() else True,
                            )

    menu.add.label(message)
    add_close_button(menu)

    menu.mainloop(surface, fps_limit=30)
    return


def import_protocols(filename, surface):
    # Imports file as a module (excludes .py extension)
    try:
        module = import_module(protocolsPath + '.' + filename[:-3])
        # reload_module in case the functions changes while the system is running
        reload_module(module)
        # Retrieves classes from module
        classes = inspect.getmembers(module, inspect.isclass)
    except Exception:
        msg = 'Exception when importing file: \n\{}.\nCheck logfile to see details'.format(filename)
        logger.exception('Exception when importing file {}'.format(filename))
        window_message(surface, msg)
        classes = []

    return classes


def protocol_run(protocol, surface, data):
    global userLogHdlr

    logger.debug('Starting protocol {}'.format(protocol.__name__))

    # initialize hardware if is not has been before
    initialize_hardware()

    try:
        protoc = protocol(surface, subject=data[0], experimenter=data[1])

        # create new log file for protocol running
        now = datetime.datetime.now().strftime('%Y%m%d-%H%M')
        userLogHdlr.baseFilename = os.path.join(logPath, protocol.__name__ + '_' + now + '.log')

        protoc._init(userLogHdlr)
        protoc._run()
        protoc._end()
        # close protocol logfile
        #userLogHdlr.close()
    except Exception:
        msg = 'Exception running protocol  \n\t \'{}\'.\nCheck logfile to see details'.format(protocol.__name__)
        logger.exception('Exception running protocol {}'.format(protocol.__name__))
        window_message(surface, msg)

    return


def function_menu(filename, data, surface):
    # New function menu
    fMenu = initialize_menu(filename)

    base_classes = ['BaseProtocol', 'Protocol']

    # Get functions from test_file
    protocols = import_protocols(filename, surface)

    # Creates a button for each function
    fMenu.add.label('Subject: {} | Experimenter: {}'.format(data[0], data[1]))
    fMenu.add.vertical_margin(20)
    for protocol in protocols:
        protocol_name, protocol_call = protocol

        if protocol_name in base_classes:
            continue
        else:
            for b in protocol_call.__bases__:
                if b.__name__ in base_classes:
                    fMenu.add.button(protocol_name, protocol_run, protocol_call, surface, data)
                    break

    add_close_button(fMenu)

    fMenu.mainloop(surface, fps_limit=30)


def scan_directory(dirPath):
    # Scans directory for relevent python files and returns the file names as an array
    # List of file names in directory
    files = []

    # Goes through each file and checks if they are python files
    for filename in os.listdir(dirPath):
        if filename.endswith('.py'):
            files.append(filename)

    files.sort()

    return files


def files_menu(data, surface):
    # Retrieves test files
    files = scan_directory(protocolsPath)
    # Creates new sub menu
    pMenu = initialize_menu('Programs')
    subject = data['subject'][0][0]
    experimenter = data['experimenter'][0][0]

    pMenu.add.label('Subject: {} | Experimenter: {}'.format(subject, experimenter))
    pMenu.add.vertical_margin(20)
    for filename in files:
        pMenu.add.button(filename, function_menu, filename, (subject, experimenter), surface)

    add_close_button(pMenu)

    pMenu.mainloop(surface, fps_limit=30)


def shutdown_pi_menu():
    def shutdown_pi():
        logger.info('Shutting down Raspberry pi')
        subprocess.call(['sudo', 'sync'])
        time.sleep(1)
        subprocess.call(['sudo', 'shutdown', 'now'])
        # sys.exit()

    confirm_menu = initialize_menu('Shutdown Device')

    if isRaspberryPI():
        confirm_msg = "Are you sure you want to shutdown your device?"
        confirm_menu.add.label(confirm_msg)
        confirm_menu.add.button('No', pygame_menu.events.BACK)
        confirm_menu.add.button('Yes', shutdown_pi)
    else:
        msg = "Device is not a Raspberry Pi. Cannot shut down."
        confirm_menu.add.label(msg)

    add_back_button(confirm_menu)

    return confirm_menu


def liquid_reward_menu(liqrewdev):
    lr_menu = initialize_menu('Liquid Reward')
    logger.debug('variant selected = {}'.format(liqrewdev))

    liqrew = LiqReward(variant=liqrewdev)

    def control(stateVal):
        if stateVal == False:
            liqrew.close()
        else:
            liqrew.open()

    def increase_drop(Label):
        drop_amount = liqrew.get_drop_amount()
        drop_amount += 1
        liqrew.set_drop_amount(drop_amount)
        Label.set_title(liqrew)

    def decrease_drop(Label):
        drop_amount = liqrew.get_drop_amount()
        drop_amount -= 1
        if drop_amount > 0:
            liqrew.set_drop_amount(drop_amount)
            Label.set_title(liqrew)

    def valveDrop(switch):
        liqrew.drop()
        logger.info('set switch status')
        switch.set_value(False)

    logger.debug('liqrew {}'.format(liqrew))
    T1 = lr_menu.add.toggle_switch('Valve State:', False, state_text=('Closed', 'Open'), onchange=control,
                                   single_click=True)
    lr_menu.add.vertical_margin(30)
    lr_menu.add.button('Give Drop', valveDrop, T1)
    lr_menu.add.vertical_margin(20)
    labelT = lr_menu.add.label(liqrew)
    frame = lr_menu.add.frame_h(700, 58)
    frame.pack(labelT, align=pygame_menu.locals.ALIGN_CENTER)
    frame.pack(lr_menu.add._horizontal_margin(20), align=pygame_menu.locals.ALIGN_CENTER)
    frame.pack(lr_menu.add.button(' + ', increase_drop, labelT, border_width=2), align=pygame_menu.locals.ALIGN_CENTER)
    frame.pack(lr_menu.add._horizontal_margin(20), align=pygame_menu.locals.ALIGN_CENTER)
    frame.pack(lr_menu.add.button('  -  ', decrease_drop, labelT, border_width=2),
               align=pygame_menu.locals.ALIGN_CENTER)

    add_back_button(lr_menu)

    return lr_menu


def ir_menu(sensor):
    irMenu = initialize_menu('Infrared Sensor')

    irSensor = IRSensor(variant=sensor)

    def updateIRsensor(label, menu):
        state = irSensor.is_activated()
        if state == True:
            msg = 'Activated'
        else:
            msg = 'Not Activated'
        label.set_title('IR Sensor state: {: <15}'.format(msg))

    irL1 = irMenu.add.label('Status')
    irL1.add_draw_callback(updateIRsensor)

    irL2 = irMenu.add.label('Last Trigger In : {: <8}'.format(''))
    irL3 = irMenu.add.label('Last Trigger Out: {: <8}'.format(''))

    def sensorTestHandlerIn():
        logger.info('Test Ir Sensor Trigger In')
        now = datetime.datetime.now().strftime('%H:%M:%S')
        irL2.set_title('Last Trigger In : {: <8}'.format(now))

    def sensorTestHandlerOut():
        logger.info('Test Ir Sensor Trigger Out')
        now = datetime.datetime.now().strftime('%H:%M:%S')
        irL3.set_title('Last Trigger Out: {: <8}'.format(now))

    irSensor.set_handler_in(sensorTestHandlerIn)
    irSensor.set_handler_out(sensorTestHandlerOut)

    add_back_button(irMenu)

    return irMenu


def sound_menu(audio):
    class Params:
        def __init__(self, frequency: int, duration: float, amplitude: float):
            self.frequency = int(frequency)
            self.duration = float(duration)
            self.amplitude = float(amplitude)

    params = Params(440, 1.0, 1.0)
    sndMenu = initialize_menu('Sound')

    sounddev = Sound(audio)

    def change_frequency(label, amount: int, inc: bool):
        params.frequency += (amount if inc else -amount)
        if params.frequency <= 10:
            params.frequency = 10
        if params.frequency > 1000:
            label.set_title('{:>3.2f} kHz'.format(params.frequency / 1000.0))
        else:
            label.set_title('{:>5d} Hz'.format(params.frequency))

    def change_amplitude(label, inc: bool, big: bool):
        amount = 0.1 if big else 0.01
        params.amplitude += (amount if inc else -amount)
        if params.amplitude > 1.0:
            params.amplitude = 1.0
        elif params.amplitude < 0.01:
            params.amplitude = 0.01
        label.set_title('     {:3.2f}  '.format(params.amplitude))

    def change_duration(label, inc: bool):
        params.duration += (0.1 if inc else -0.1)
        if params.duration < 0.1:
            params.duration = 0.1
        label.set_title('     {:2.1f} s'.format(params.duration))

    def playsnd():
        sounddev.play(frequency=params.frequency, duration=params.duration, amplitude=params.amplitude)

    labelF = sndMenu.add.label('{:>5d} Hz'.format(params.frequency))
    frameF = sndMenu.add.frame_h(700, 58)
    frameF.pack(sndMenu.add.label('Frequency: '), align=pygame_menu.locals.ALIGN_CENTER)
    frameF.pack(labelF, align=pygame_menu.locals.ALIGN_CENTER)
    frameF.pack(sndMenu.add._horizontal_margin(20), align=pygame_menu.locals.ALIGN_CENTER)
    frameF.pack(sndMenu.add.button(' ++ ', change_frequency, labelF, 100, True, border_width=2),
                align=pygame_menu.locals.ALIGN_CENTER)
    frameF.pack(sndMenu.add._horizontal_margin(5), align=pygame_menu.locals.ALIGN_CENTER)
    frameF.pack(sndMenu.add.button(' + ', change_frequency, labelF, 10, True, border_width=2),
                align=pygame_menu.locals.ALIGN_CENTER)
    frameF.pack(sndMenu.add._horizontal_margin(20), align=pygame_menu.locals.ALIGN_CENTER)
    frameF.pack(sndMenu.add.button('  -  ', change_frequency, labelF, 10, False, border_width=2),
                align=pygame_menu.locals.ALIGN_CENTER)
    frameF.pack(sndMenu.add._horizontal_margin(5), align=pygame_menu.locals.ALIGN_CENTER)
    frameF.pack(sndMenu.add.button('  --  ', change_frequency, labelF, 100, False, border_width=2),
                align=pygame_menu.locals.ALIGN_CENTER)

    labelA = sndMenu.add.label('     {:3.2f}  '.format(params.amplitude))
    frameA = sndMenu.add.frame_h(700, 58)
    frameA.pack(sndMenu.add.label('   Amplitude:'), align=pygame_menu.locals.ALIGN_CENTER)
    frameA.pack(labelA, align=pygame_menu.locals.ALIGN_CENTER)
    frameA.pack(sndMenu.add._horizontal_margin(20), align=pygame_menu.locals.ALIGN_CENTER)
    frameA.pack(sndMenu.add.button(' ++ ', change_amplitude, labelA, True, True, border_width=2),
                align=pygame_menu.locals.ALIGN_CENTER)
    frameA.pack(sndMenu.add._horizontal_margin(5), align=pygame_menu.locals.ALIGN_CENTER)
    frameA.pack(sndMenu.add.button(' + ', change_amplitude, labelA, True, False, border_width=2),
                align=pygame_menu.locals.ALIGN_CENTER)  # \u2795
    frameA.pack(sndMenu.add._horizontal_margin(20), align=pygame_menu.locals.ALIGN_CENTER)
    frameA.pack(sndMenu.add.button('  -  ', change_amplitude, labelA, False, False, border_width=2),
                align=pygame_menu.locals.ALIGN_CENTER)  # \u2796
    frameA.pack(sndMenu.add._horizontal_margin(5), align=pygame_menu.locals.ALIGN_CENTER)
    frameA.pack(sndMenu.add.button('  --  ', change_amplitude, labelA, False, True, border_width=2),
                align=pygame_menu.locals.ALIGN_CENTER)

    labelT = sndMenu.add.label('     {:2.1f} s'.format(params.duration))
    frameT = sndMenu.add.frame_h(600, 58)
    frameT.pack(sndMenu.add.label('   Duration:'), align=pygame_menu.locals.ALIGN_CENTER)
    frameT.pack(labelT, align=pygame_menu.locals.ALIGN_CENTER)
    frameT.pack(sndMenu.add._horizontal_margin(20), align=pygame_menu.locals.ALIGN_CENTER)
    frameT.pack(sndMenu.add.button(' + ', change_duration, labelT, True, border_width=2),
                align=pygame_menu.locals.ALIGN_CENTER)  # \u2795
    frameT.pack(sndMenu.add._horizontal_margin(20), align=pygame_menu.locals.ALIGN_CENTER)
    frameT.pack(sndMenu.add.button('  -  ', change_duration, labelT, False, border_width=2),
                align=pygame_menu.locals.ALIGN_CENTER)  # \u2796

    sndMenu.add.button('Play Sound', playsnd)

    add_back_button(sndMenu)

    return sndMenu


def special_settings_menu(surface):
    spMenu = initialize_menu('Special Settings')

    table = touchDB.table('settings')

    ## Logging level
    current_level = logging.getLogger().level
    current_logDebug = True if current_level == logging.DEBUG else False

    def change_loglevel(level):
        logOpt = table.get(tinydb.Query().logDebugOn.exists())

        table.update({'logDebugOn': level}, doc_ids=[logOpt.doc_id])
        if level:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.debug('Debug logging mode activated')
        else:
            logger.debug('Debug logging mode deactivated')
            logging.getLogger().setLevel(logging.INFO)

    spMenu.add.toggle_switch('Logging Level ', current_logDebug, state_text=('Regular', 'Debug'),
                             onchange=change_loglevel, single_click=True, width=180)

    ## Syncing
    current_sync = table.get(tinydb.Query().syncOn.exists())['syncOn']

    def change_sync(stateval):
        syncOpt = table.get(tinydb.Query().syncOn.exists())
        table.update({'syncOn': stateval}, doc_ids=[syncOpt.doc_id])
        logger.debug('Synchronize time {}'.format('enabled' if stateval else 'disabled'))

    spMenu.add.toggle_switch('Synchronize time on start: ', current_sync, state_text=('Disabled', 'Enabled'),
                             onchange=change_sync, single_click=True, width=180)

    ## Battery
    batteryObj = table.get(tinydb.Query().battery.exists())
    battery = batteryObj['battery']

    def change_battery(state):
        bat = Battery()
        if state:
            if bat.detect_battery():
                table.update({'battery': state}, doc_ids=[batteryObj.doc_id])
                logger.debug('Battery connected')
            else:
                msg = 'Battery not detected'
                logger.debug(msg)
                window_message(surface, msg)
                T1.set_value(False)
        else:
            bat.disconnect()
            logger.debug('Battery not connected')

            table.update({'battery': state}, doc_ids=[batteryObj.doc_id])

    T1 = spMenu.add.toggle_switch('Battery: ', battery, state_text=('Disconnected', 'Connected'),
                                  onchange=change_battery, single_click=True, width=230)
    if battery:
        change_battery(True)

    # Sounds
    audioObj = table.get(tinydb.Query().audio.exists())
    current_audio = audioObj['audio']

    audio_items = Sound.get_items()
    current_audio_index = 0
    for i in range(len(audio_items)):
        if audio_items[i][1] == current_audio:
            current_audio_index = i
            break

    def change_audio(item, value):
        global new_audio_index
        audioObj = table.get(tinydb.Query().audio.exists())

        for i in range(len(audio_items)):
            if audio_items[i][1] == value:
                new_audio_index = i
                break

        logger.debug('Audio system changed to: "{}"'.format(audio_items[new_audio_index][0]))
        table.update({'audio': value}, doc_ids=[audioObj.doc_id])

    spMenu.add.selector('Audio System: ', audio_items, onchange=change_audio, default=current_audio_index)

    # Reward sensor
    sensor = table.get(tinydb.Query().rSensor.exists())
    current_sensor = sensor['rSensor']

    sensor_items = IRSensor.get_items()
    current_sensor_index = 0
    for i in range(len(sensor_items)):
        if sensor_items[i][1] == current_sensor:
            current_sensor_index = i
            break

    def change_sensor(item, sensorval):
        global new_sensor_index
        sensorObj = table.get(tinydb.Query().rSensor.exists())

        for i in range(len(sensor_items)):
            if sensor_items[i][1] == sensorval:
                new_sensor_index = i
                break

        logger.debug('Reward sensor changed to {}'.format(sensor_items[new_sensor_index][0]))
        table.update({'rSensor': sensorval}, doc_ids=[sensorObj.doc_id])

    spMenu.add.selector('IR Reward Sensor: ', sensor_items, onchange=change_sensor, default=current_sensor_index)

    # Liquid Reward
    liquid_reward = table.get(tinydb.Query().lReward.exists())
    current_liquid_reward = liquid_reward['lReward']

    liquid_reward_items = LiqReward.get_items()
    current_liquid_reward_index = 0
    for i in range(len(liquid_reward_items)):
        if liquid_reward_items[i][1] == current_liquid_reward:
            current_liquid_reward_index = i
            break

    def change_liquid_reward(item, reward_value):
        global new_liquid_reward_index
        liquid_rewardObj = table.get(tinydb.Query().lReward.exists())

        for i in range(len(liquid_reward_items)):
            if liquid_reward_items[i][1] == reward_value:
                new_liquid_reward_index = i
                break

        logger.debug('Liquid Reward changed to {}'.format(liquid_reward_items[new_liquid_reward_index][0]))
        table.update({'lReward': reward_value}, doc_ids=[liquid_rewardObj.doc_id])

    spMenu.add.selector('Liquid Reward System: ', liquid_reward_items, onchange=change_liquid_reward,
                        default=current_liquid_reward_index)

    # Food Reward
    food_reward = table.get(tinydb.Query().fReward.exists())
    current_food_reward = food_reward['fReward']

    food_reward_items = [('No food Reward', 'None')]
    current_food_reward_index = 0
    for i in range(len(food_reward_items)):
        if food_reward_items[i][1] == current_food_reward:
            current_food_reward_index = i
            break

    def change_food_reward(item, value):
        global new_food_reward_index
        food_rewardObj = table.get(tinydb.Query().fReward.exists())

        for i in range(len(food_reward_items)):
            if food_reward_items[i][1] == value:
                new_food_reward_index = i
                break

        logger.debug('Food Reward changed to {}'.format(food_reward_items[new_food_reward_index][0]))
        table.update({'fReward': value}, doc_ids=[food_rewardObj.doc_id])

    spMenu.add.selector('Food Reward System: ', food_reward_items, onchange=change_food_reward,
                        default=current_food_reward_index)

    def update_software():
        logger.info('Updating software')
        if isRaspberryPI():
            ret = subprocess.call(['scripts/update.sh'])
            if ret == 0:
                msg = 'Software updated successfully.\nA system restart is needed'
            else:
                msg = 'Software update was unsuccessful.\nCheck system log file'
        else:
            msg = 'Running in PC, manual update required.\nRun "git pull"'

        logger.debug(msg)
        window_message(surface, msg)

    spMenu.add.vertical_margin(5)
    spMenu.add.button('Update Software', update_software)

    add_close_button(spMenu)

    spMenu.mainloop(surface, fps_limit=30)


def settings_menu(surface):
    sMenu = initialize_menu('Settings')

    table = touchDB.table('settings')

    # def updateIP(Label, menu):
    #     Label.set_title('Ip : {}'.format(showip.getip()))

    # IPLabel = sMenu.add.label('Ip')
    # IPLabel.add_draw_callback(updateIP)

    def updateBatt(label, menu):
        battery_msg = 'Battery  {:d} %,  Charging: {}'.format(battery.get_capacity(), battery.get_powered())
        label.set_title(battery_msg)

    battObj = table.get(tinydb.Query().battery.exists())['battery']
    if battObj:
        battery = Battery()
        if battery.detect_battery():
            BattLabel = sMenu.add.label('Battery')
            BattLabel.add_draw_callback(updateBatt)
        else:
            ## mssg no battery detected
            ## change state in database
            pass

    sMenu.add.vertical_margin(20)

    liquid_reward = table.get(tinydb.Query().lReward.exists())['lReward']
    if liquid_reward != 'None':
        lr_menu = liquid_reward_menu(liquid_reward)
        sMenu.add.button(lr_menu.get_title(), lr_menu)

    #    food_reward = table.get(tinydb.Query().lReward.exists())['fReward']
    #    if food_reward != 'None':
    #        frMenu = foodReward_menu(food_reward)
    #        sMenu.add.button(frMenu.get_title(),frMenu)

    sensor = table.get(tinydb.Query().rSensor.exists())['rSensor']
    if sensor != 'None':
        irMenu = ir_menu(sensor)
        sMenu.add.button(irMenu.get_title(), irMenu)

    audio = table.get(tinydb.Query().audio.exists())['audio']
    if audio != 'None':
        sndMenu = sound_menu(audio)
        sMenu.add.button(sndMenu.get_title(), sndMenu)

    sMenu.add.vertical_margin(10)
    confirm_menu = shutdown_pi_menu()
    sMenu.add.button(confirm_menu.get_title(), confirm_menu)

    add_close_button(sMenu)

    sMenu.mainloop(surface, fps_limit=30)



def set_file(selected, value):
    """
    Sets the File selected by the item selector to be attatched to the email
    :param selected: Filename.log
    :return:
    """
    SELECTED_FILE_PATH[0] = os.path.join(logPath, selected[0][0])
    pass

def view_file_list(surface):
    if len(FILE_LIST) != 0:
        ToDisplay = ""
        counter = 1
        for file_name in FILE_LIST:
            ToDisplay += str(counter) + ". " + str(file_name).lstrip(logPath) + "\n"
            counter += 1
        list_view(surface, ToDisplay)
    else:
        list_view(surface, "No files attached")

def add_file():
    if SELECTED_FILE_PATH[0] not in FILE_LIST:
        FILE_LIST.append(SELECTED_FILE_PATH[0])
        print(FILE_LIST)

def set_email(recipt):
    """
    Sets the recipient of the email
    :param text: email@email.com
    :return:
    """
    global EMAIL
    EMAIL = recipt
    pass

def validate_email(func):
    """
    Wrapper that checks the email is valid before executing the function
    Function needs to have a surface variable
    """
    @functools.wraps(func)
    def wrapper(surface):
        if not re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', EMAIL.lower()):
            window_message(surface, 'Email address is invalid')
            return
        func(surface)
        return

    return wrapper

@validate_email
def send_email(surface):
    if len(FILE_LIST) != 0:
        """
        Uses smtplib to email a file from moormanlabtouchscreen@gmail.com
        Can change subject/body messages using MIME
        Converts .log file to CSV using @@ as delimiters
        Attach file using MIME (Currently only sends one file)
        :return:
        """
        # Create Headers
        recipient = EMAIL
        print(recipient)
        msg = MIMEMultipart()
        msg['Subject'] = "Your Touchscreen Data"
        msg['From'] = GMAIL_USERNAME
        msg['To'] = recipient
        body_part = MIMEText("Here is your data:", 'plain')
        msg.attach(body_part)

        for path_to_file in FILE_LIST:
            path_to_csv = path_to_file[:-3] + "csv"
            # convert log file to csv
            with open(path_to_file, 'r') as file:
                lines = file.readlines()
                with open(path_to_csv, 'w+') as csvfile:
                    for line in lines:
                        line = line.replace("@@", ",")
                        # assume first two fields are 24 chars, add quotes to third field
                        # not robust, must fix
                        line = line[:24] + "\"" + line[24:-1] + "\"\n"
                        print(line)
                        csvfile.write(line)
                csvfile.close()
            file.close()

            # Attach the file with filename to the email
            with open(path_to_csv, 'rb') as csvfile:
                msg.attach(MIMEApplication(csvfile.read(), Name=os.path.basename(path_to_csv)))


        # Connect to Gmail Server
        session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        session.ehlo()
        session.starttls()
        session.ehlo()
        # Login to Gmail
        session.login(GMAIL_USERNAME, GMAIL_PASSWORD)
        # Send Email & Exit
        session.sendmail(GMAIL_USERNAME, recipient, msg.as_string())
        session.quit()
        window_message(surface, 'Email Sent')
    else:
        window_message(surface, 'No file selected')

def send_data_menu(surface):
    update_list()
    FILE_LIST.clear()
    sdMenu = initialize_menu('Email Data')
    sdMenu.add.text_input('Email Address: ', maxwidth=19, default=EMAIL, input_underline='_', onchange=set_email)
    sdMenu.add.selector('File: ', FILE_NAMES, onchange=set_file)
    sdMenu.add.button('Add file', add_file)
    sdMenu.add.button('View attached files', view_file_list, surface)
    sdMenu.add.button('Send', send_email, surface)

    add_close_button(sdMenu)
    sdMenu.mainloop(surface, fps_limit=30)


def create_surface():
    # Creates surface
    # make fullscreen on touchscreen
    if isRaspberryPI():
        surface = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT), pygame.FULLSCREEN)
        pygame.mouse.set_cursor((8, 8), (0, 0), (0, 0, 0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0))
    else:
        surface = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))

    return surface

def piSynchronizeTime():
    delayLinkInit = 10
    delaySyncInit = 25

    delayLink = delayLinkInit
    delaySync = delaySyncInit
    if isRaspberryPI():
        while delayLink:
            time.sleep(1)
            if showip.isLinkUp():
                break
            delayLink -= 1

        # once there is a connection, usually takes 20 seconds to synchronize the clock
        if showip.isLinkUp():
            while delaySync:
                a = datetime.datetime.now()
                time.sleep(1)
                b = datetime.datetime.now()
                c = b - a
                if c.seconds > 2:
                    msg = 'System time correctly updated. LinkDelay {}, SyncDelay {}'.format(delayLinkInit-delayLink,delaySyncInit-delaySync)
                    break
                delaySync -=1

            if delaySync == 0:
                msg = 'Exceeded sync delay, System time was not updated. LinkDelay {} SyncTimeAwaited {}'.format(delayLinkInit-delayLink,delaySyncInit)
        else:
            msg = 'Exceeded connection delay, Internet connection was not established. LinkDelayAwaited {}'.format(delayLinkInit)
    else:
        msg = 'Working on computer, no need to synchronize time'

    return msg


def initialize_hardware() -> None:
    table = touchDB.table('settings')

    batteryObj = table.get(tinydb.Query().battery.exists())
    batt = batteryObj['battery']
    if batt:
        battery = Battery()
        if not battery.detect_battery():
            table.update({'battery': False}, doc_ids=[batteryObj.doc_id])

    sensor = table.get(tinydb.Query().rSensor.exists())['rSensor']
    if sensor != 'None':
        irSensor = IRSensor(variant=sensor)

    audio = table.get(tinydb.Query().audio.exists())['audio']
    if audio != 'None':
        sounddev = Sound(audio)

    liquid_reward = table.get(tinydb.Query().lReward.exists())['lReward']
    if liquid_reward != 'None':
        liqrew = LiqReward(variant=liquid_reward)

    hardware_initialized = True


#    food_reward = table.get(tinydb.Query().lReward.exists())['fReward']
#    if food_reward != 'None':
#        foodrew = FoodReward(variant=food_reward)


def initialize_logging():
    table = touchDB.table('settings')
    syncOpt = table.get(tinydb.Query().syncOn.exists())['syncOn']

    # if syncOpt:
    #     # wait for time synchronization
    #     msg = piSynchronizeTime()
    # else:
    #     msg = 'Synchronizing time disabled'
    msg = 'Synchronizing time disabled'

    # Initialize logging
    formatDate = '%Y/%m/%d@@%H:%M:%S'
    sysFormatStr = '%(asctime)s.%(msecs)03d@@%(name)s@@%(levelname)s@@%(message)s'
    sysFormatter = logging.Formatter(fmt=sysFormatStr, datefmt=formatDate)
    userFormatStr = '%(asctime)s.%(msecs)03d@@%(message)s'
    userFormatter = logging.Formatter(fmt=userFormatStr, datefmt=formatDate)

    log = logging.getLogger()
    logOpt = table.get(tinydb.Query().logDebugOn.exists())['logDebugOn']

    if logOpt:
        level = logging.DEBUG
    else:
        level = logging.INFO

    log.setLevel(level)

    now = datetime.datetime.now().strftime('%Y%m%d-%H%M')
    os.makedirs(logPath, exist_ok=True)

    # the delay=1 should prevent the file from being opened until used.
    systemLogFile = os.path.join(logPath, now + '-system.log')
    systemLogHdlr = logging.FileHandler(systemLogFile, mode='w')
    systemLogHdlr.setFormatter(sysFormatter)
    log.addHandler(systemLogHdlr)

    global userLogHdlr
    # prepare userLog Handler with dummy log file
    userLogFile = os.path.join(logPath, now + '-userprotocol.log')
    userLogHdlr = logging.FileHandler(userLogFile, mode='w')
    userLogHdlr.setLevel(logging.INFO)
    userLogHdlr.setFormatter(userFormatter)
    userLogHdlr.close()
    logger.info('Logging initialized')
    logger.debug(msg)
    # logger.debug('{}'.format(showip.getip()))


def dbGetAll(subjectType):
    table = touchDB.table(subjectType)

    A = table.all()
    nameList = [('No Name',)]
    for item in A:
        nameList.append((item['name'],))

    return nameList


def database_init():
    table = touchDB.table('settings')
    initOpt = table.get(tinydb.Query().init.exists())

    if not initOpt:
        table.insert({'init': True})
        table.insert({'syncOn': True})
        table.insert({'logDebugOn': True})
        table.insert({'battery': False})
        table.insert({'audio': 'None'})
        table.insert({'rSensor': 'None'})
        table.insert({'lReward': 'None'})
        table.insert({'fReward': 'None'})


def main_menu():
    # Initializes pygame and logging
    update_list()
    pygame.init()
    database_init()

    initialize_logging()

    logger.debug('Running in Raspberry PI = {}'.format(isRaspberryPI()))

    # Creates surface based on machine
    surface = create_surface()

    menu = initialize_menu('Mouse Touchscreen Menu')

    def addItems(selector, surface):
        subject = keyboard(surface)
        sType = selector.get_id()

        if subject != '':
            table = touchDB.table(sType)
            if table.search(tinydb.Query().name == subject):
                items = selector.get_items()
                for i in range(len(items)):
                    if items[i][0] == subject:
                        selector._index = i
                logger.debug('Name already in database')
            else:
                table.insert({'name': subject})
                items = selector.get_items()
                items.append((subject,))
                selector.update_items(items)
                selector._index = len(items) - 1

    def delItems(selector):
        sType = selector.get_id()
        table = touchDB.table(sType)
        sIdx = selector.get_index()
        if sIdx > 0:  # idx == 0 -> 'No Name'
            subject = selector.get_value()[0][0]
            logger.info('to remove {}'.format(subject))
            table.remove(tinydb.Query().name == subject)
            items = selector.get_items()
            items.pop(sIdx)
            selector.update_items(items)
            selector._index = 0

    def clearItems(selector):
        sType = selector.get_id()
        table = touchDB.table(sType)
        table.truncate()
        items = [('No Name',)]
        selector.update_items(items)
        selector._index = 0

    def run_files_menu(menu, surface):
        data = menu.get_input_data()
        files_menu(data, surface)

    # Creates initial buttons
    frameS = menu.add.frame_h(760, 58)
    S1 = menu.add.dropselect('Subject Id', items=dbGetAll('subject'), default=0, dropselect_id='subject',
                             placeholder='Select             ', placeholder_add_to_selection_box=False)
    frameS.pack(menu.add.button('Clear', clearItems, S1), align='align-right')
    frameS.pack(menu.add.button('Del', delItems, S1), align='align-right')
    frameS.pack(menu.add.button('Add', addItems, S1, surface), align='align-right')
    frameS.pack(S1, align='align-right')

    frameE = menu.add.frame_h(760, 58)
    S2 = menu.add.dropselect('Experimenter Id', items=dbGetAll('experimenter'), default=0, dropselect_id='experimenter',
                             placeholder='Select             ', placeholder_add_to_selection_box=False)
    frameE.pack(menu.add.button('Clear', clearItems, S2), align='align-right')
    frameE.pack(menu.add.button('Del', delItems, S2), align='align-right')
    frameE.pack(menu.add.button('Add', addItems, S2, surface), align='align-right')
    frameE.pack(S2, align='align-right')

    menu.add.vertical_margin(20)
    menu.add.button('Protocols', run_files_menu, menu, surface)
    menu.add.button('Send Data', send_data_menu, surface)
    menu.add.button('Settings', settings_menu, surface)
    menu.add.vertical_margin(10)
    menu.add.button('Special Settings', special_settings_menu, surface)
    menu.add.button('Exit', pygame_menu.events.EXIT)

    # Allows menu to be run
    try:
        menu.mainloop(surface, fps_limit=30)
    except Exception:
        logger.exception('Exception running mainloop')

    logger.info('Exiting Menu')

    return


if __name__ == "__main__":
    main_menu()
