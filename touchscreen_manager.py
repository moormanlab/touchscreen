#!/usr/bin/python3
import tinydb
import logging
from utils.utils import touchDBFile, initialize_logging, database_init, get_database, close_IRSensor_thread
import Touchscreen_Menu, Touchscreen_Client
logger = logging.getLogger('TouchManager')

def run_touchscreen():
    source = get_source().get('isClient')
    if source:
        logger.debug('running client')
        change = Touchscreen_Client.main_menu()
        logger.debug('exiting client')
    else:
        logger.debug('running menu')
        change = Touchscreen_Menu.main_menu()
        logger.debug('exit menu')
    return change


def source_change():
    set_source(not get_source().get('isClient')) # toggle source before running
    logger.debug('source changed to {}'.format('client' if get_source().get('isClient') else 'menu'))



def get_source():
    with get_database() as db:
        source = db.table('settings').get(tinydb.Query().isClient.exists())
    return source

def set_source(source: bool):
    with get_database() as db: 
        db.table('settings').update({'isClient': source}, doc_ids=[get_source().doc_id])


def main():
    ret = run_touchscreen()
    while ret:
        source_change()
        ret = run_touchscreen()












if __name__ == '__main__':
    database_init()
    initialize_logging()
    main()
    close_IRSensor_thread()