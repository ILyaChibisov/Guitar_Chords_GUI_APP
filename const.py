from dotenv import load_dotenv
import os
import re
import itertools
from datetime import datetime
from babel.dates import format_datetime
from functools import wraps
import time

import database.db_scripts as db

########################################################
# Ссылки на графики
File_link1 = 'scr/statistics/users_hours_today.png'
File_link2 = 'scr/statistics/users_months.png'
File_link3 = 'scr/statistics/users_years.png'

File_link4 = 'scr/statistics/views_today.png'
File_link5 = 'scr/statistics/views_month.png'
File_link6 = 'scr/statistics/views_year.png'


def get_time():
    now = datetime.now()
    f_date = format_datetime(now, "d MMMM yyyy", locale='ru')
    date = f_date.split(' ')
    day, year = " ".join(date[:2]) + " " + date[2] + " года", date[2] + " год"
    month = format_datetime(now, "LLLL", locale='ru') + ' ' + year
    return day,month,year

KEYBOARD_CALL = ['',' ','next_page_let_','prev_page_let_','prev_page_','up_let_','next_page_','prevsong_page_','up_let2_',
                 'nextsong_page_','prev_ch_','chord_','next_ch_','dell_song_','w_','z_']


load_dotenv()
GENERAL_ADMIN = int(os.getenv('GENERAL_ADMIN'))
DBNAME, USER, PASSWORD, HOST = os.getenv('DBNAME'), os.getenv('USER'), os.getenv('PASSWORD'),os.getenv('HOST')
MAIN_DIRECTORY = os.getenv('MAIN_SONGS_DIRECTORY')
SENDER_LINK = os.getenv('SENDER_LINK')
SENDER_TITLE = os.getenv('SENDER_TITLE')
REDIRECT_SERVER = os.getenv('REDIRECT_SERVER')
TOKEN = os.getenv('TOKKEN')
donate_url  = os.getenv('DONATE_URL')
TOKEN_SDK = os.getenv('TOKEN_SDK')

admin_ids_str = os.getenv('ADMIN_ID', '')
ADMIN_ID = [int(admin_id.strip()) for admin_id in admin_ids_str.split(',') if admin_id.strip()]
PARTNER_LINK = os.getenv('PARTNER_LINK').replace('\\n', '\n')

MONTH_NAME = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май',
                     'Июнь', 'Июль', 'Август', 'Сентябрь',
                     'Октябрь', 'Ноябрь', 'Декабрь']

MENU_BAR = ['Аккорды🎼','Поиск 🔍','Песни 🎸','Статьи🎓','Избранное ⭐','FAQ📚']

VIEWS_DICT = {3: '🎓', 2: '🎸', 4: '🔍', 5: '🔍🎸', 6: '⭐'}

TYPE = ['','m','7','m7','+','dim','dim7','sus2','sus4','7sus2','7sus4','6','m6','9','m9','maj','maj7','7/6','5','add9']

CHORDS_TYPE = ['A', 'A#', 'Bb', 'B', 'H', 'C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab']

CHORDS_1 = ['A', 'Am', 'A7', 'Am7', 'A+', 'Adim', 'Adim7', 'Asus2', 'Asus4', 'A7sus2', 'A7sus4', 'A6', 'Am6', 'A9',
            'Am9', 'Amaj', 'Amaj7', 'A7/6','A5','Aadd9']

CHORDS_2 = ['A#', 'A#m', 'A#7', 'A#m7', 'A#+', 'A#dim', 'A#dim7', 'A#sus2', 'A#sus4', 'A#7sus2', 'A#7sus4', 'A#6', 'A#m6',
            'A#9', 'A#m9', 'A#maj', 'A#maj7', 'A#7/6','A#5','A#add9']

CHORDS_3 = ['Bb', 'Bbm', 'Bb7', 'Bbm7', 'Bb+', 'Bbdim', 'Bbdim7', 'Bbsus2', 'Bbsus4', 'Bb7sus2', 'Bb7sus4', 'Bb6', 'Bbm6', 'Bb9',
            'Bbm9', 'Bbmaj', 'Bbmaj7', 'Bb7/6','Bb5','Bbadd9']

CHORDS_4 = ['B', 'Bm', 'B7', 'Bm7', 'B+', 'Bdim', 'Bdim7', 'Bsus2', 'Bsus4', 'B7sus2', 'B7sus4', 'B6', 'Bm6', 'B9',
            'Bm9', 'Bmaj', 'Bmaj7', 'B7/6','B5','Badd9']

CHORDS_5 = ['H', 'Hm', 'H7', 'Hm7', 'H+', 'Hdim', 'Hdim7', 'Hsus2', 'Hsus4', 'H7sus2', 'H7sus4', 'H6', 'Hm6', 'H9',
            'Hm9', 'Hmaj', 'Hmaj7', 'H7/6','H5','Hadd9']


CHORDS_6 = ['C', 'Cm', 'C7', 'Cm7', 'C+', 'Cdim', 'Cdim7', 'Csus2', 'Csus4', 'C7sus2', 'C7sus4', 'C6', 'Cm6',
            'C9', 'Cm9', 'Cmaj', 'Cmaj7', 'C7/6','C5','Cadd9']


CHORDS_7 = ['C#', 'C#m', 'C#7', 'C#m7', 'C#+', 'C#dim', 'C#dim7', 'C#sus2', 'C#sus4', 'C#7sus2', 'C#7sus4', 'C#6', 'C#m6',
            'C#9', 'C#m9', 'C#maj', 'C#maj7', 'C#7/6','C#5','C#add9']

CHORDS_8 = ['Db', 'Dbm', 'Db7', 'Dbm7', 'Db+', 'Dbdim', 'Dbdim7', 'Dbsus2', 'Dbsus4', 'Db7sus2', 'Db7sus4', 'Db6', 'Dbm6',
            'Db9', 'Dbm9','Dbmaj', 'Dbmaj7', 'Db7/6','Db5','Dbadd9']

CHORDS_9 = ['D', 'Dm', 'D7', 'Dm7', 'D+', 'Ddim', 'Ddim7', 'Dsus2', 'Dsus4', 'D7sus2', 'D7sus4', 'D6', 'Dm6', 'D9', 'Dm9',
            'Dmaj', 'Dmaj7', 'D7/6','D5','Dadd9']

CHORDS_10 = ['D#', 'D#m', 'D#7', 'D#m7', 'D#+', 'D#dim', 'D#dim7', 'D#sus2', 'D#sus4', 'D#7sus2', 'D#7sus4', 'D#6', 'D#m6',
            'D#9', 'D#m9', 'D#maj', 'D#maj7', 'D#7/6','D#5','D#add9']

CHORDS_11 = ['Eb', 'Ebm', 'Eb7', 'Ebm7', 'Eb+', 'Ebdim', 'Ebdim7', 'Ebsus2', 'Ebsus4', 'Eb7sus2', 'Eb7sus4', 'Eb6', 'Ebm6',
             'Eb9', 'Ebm9','Ebmaj', 'Ebmaj7', 'Eb7/6','Eb5','Ebadd9']

CHORDS_12 = ['E', 'Em', 'E7', 'Em7', 'E+', 'Edim', 'Edim7', 'Esus2', 'Esus4', 'E7sus2', 'E7sus4', 'E6', 'Em6', 'E9', 'Em9',
            'Emaj', 'Emaj7', 'E7/6','E5','Eadd9']

CHORDS_13 = ['F', 'Fm', 'F7', 'Fm7', 'F+', 'Fdim', 'Fdim7', 'Fsus2', 'Fsus4', 'F7sus2', 'F7sus4', 'F6', 'Fm6', 'F9', 'Fm9',
            'Fmaj', 'Fmaj7', 'F7/6','F5','Fadd9']

CHORDS_14 = ['F#', 'F#m', 'F#7', 'F#m7', 'F#+', 'F#dim', 'F#dim7', 'F#sus2', 'F#sus4', 'F#7sus2', 'F#7sus4', 'F#6', 'F#m6',
             'F#9', 'F#m9', 'F#maj', 'F#maj7', 'F#7/6','F#5','F#add9']

CHORDS_15 = ['Gb', 'Gbm', 'Gb7', 'Gbm7', 'Gb+', 'Gbdim', 'Gbdim7', 'Gbsus2', 'Gbsus4', 'Gb7sus2', 'Gb7sus4', 'Gb6', 'Gbm6', 'Gb9', 'Gbm9',
             'Gbmaj', 'Gbmaj7', 'Gb7/6','Gb5','Gbadd9']

CHORDS_16 = ['G', 'Gm', 'G7', 'Gm7', 'G+', 'Gdim', 'Gdim7', 'Gsus2', 'Gsus4', 'G7sus2', 'G7sus4', 'G6', 'Gm6', 'G9', 'Gm9',
             'Gmaj', 'Gmaj7', 'G7/6','G5','Gadd9']

CHORDS_17 = ['G#', 'G#m', 'G#7', 'G#m7', 'G#+', 'G#dim', 'G#dim7', 'G#sus2', 'G#sus4', 'G#7sus2', 'G#7sus4', 'G#6', 'G#m6',
             'G#9', 'G#m9', 'G#maj', 'G#maj7', 'G#7/6','G#5','G#add9']

CHORDS_18 = ['Ab', 'Abm', 'Ab7', 'Abm7', 'Ab+', 'Abdim', 'Abdim7', 'Absus2', 'Absus4', 'Ab7sus2', 'Ab7sus4', 'Ab6', 'Abm6',
             'Ab9','Abm9', 'Abmaj', 'Abmaj7', 'Ab7/6', 'Ab5', 'Abadd9']


CHORDS_TYPE_NAME_LIST = ['CHORDS_1', 'CHORDS_2', 'CHORDS_3', 'CHORDS_4', 'CHORDS_5', 'CHORDS_6', 'CHORDS_7',
                         'CHORDS_8', 'CHORDS_9', 'CHORDS_10', 'CHORDS_11', 'CHORDS_12', 'CHORDS_13','CHORDS_14',
                         'CHORDS_15','CHORDS_16','CHORDS_17','CHORDS_18']

CHORDS_TYPE_LIST = [CHORDS_1, CHORDS_2, CHORDS_3, CHORDS_4, CHORDS_5, CHORDS_6, CHORDS_7,
                    CHORDS_8, CHORDS_9, CHORDS_10, CHORDS_11, CHORDS_12, CHORDS_13,CHORDS_14,CHORDS_15,
                    CHORDS_16,CHORDS_17,CHORDS_18]

LETTERS = ['0-9', 'А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И', 'Й', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т',
           'У', 'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ы', 'Э', 'Ю', 'Я']

LETTERS2 = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
            'V', 'W', 'X', 'Y', 'Z']

# A
CHORDS_1DSR = ['Ля мажор', 'Ля минор', 'Доминантсептаккорд (мажорный септаккорд) от ноты Ля', 'Минорный септаккорд от ноты Ля',
               'Ля мажор увеличенный', 'Уменьшенный аккорд от ноты Ля', 'Уменьшенный септаккорд от ноты Ля',
               'Ля мажор с большой секундой вместо терции', 'Ля мажор с квартой вместо терции',
               'Мажорный септаккорд с большой секундой от ноты Ля', 'Мажорный септаккорд с квартой от ноты Ля',
               'Мажорный секстаккорд от ноты Ля', 'Минорный секстаккорд от ноты Ля', 'Мажорный нонаккорд от ноты Ля',
               'Минорный нонаккорд от ноты Ля', 'Ля мажор', 'Большой мажорный септаккорд от ноты Ля', 'Мажорный септаккорд с секстой от ноты Ля',
               'Ля мажор с уменьшенной квинтой','Ля мажор с большой ноной']

# A#
CHORDS_2DSR = ['Ля-диез мажор', 'Ля-диез минор', 'Доминантсептаккорд (мажорный септаккорд) от ноты Ля-диез',
               'Минорный септаккорд от ноты Ля-диез', 'Ля-диез мажор увеличенный', 'Уменьшенный аккорд от ноты Ля-диез',
               'Уменьшенный септаккорд от ноты Ля-диез', 'Ля-диез мажор с большой секундой вместо терции',
               'Ля-диез мажор с квартой вместо терции', 'Мажорный септаккорд с большой секундой от ноты Ля-диез',
               'Мажорный септаккорд с квартой от ноты Ля-диез', 'Мажорный секстаккорд от ноты Ля-диез',
               'Минорный секстаккорд от ноты Ля-диез', 'Мажорный нонаккорд от ноты Ля-диез', 'Минорный нонаккорд от ноты Ля-диез',
               'Ля-диез мажор', 'Большой мажорный септаккорд от ноты Ля-диез', 'Мажорный септаккорд с секстой от ноты Ля-диез',
               'Ля-диез мажор с уменьшенной квинтой','Ля-диез мажор с большой ноной']

# Bb
CHORDS_3DSR = ['Си-бемоль мажор', 'Cи-бемоль-минорный аккорд', 'Cи-бемоль-доминантсептаккорд', 'Cи-бемоль-минорный септаккорд', 'Увеличенный аккорд от ноты Си-бемоль',
               'Cи-бемоль-уменьшенный аккорд', 'Cи-бемоль-уменьшенный септаккорд', 'Си-бемоль-аккорд с задержанной секундой',
               'Си-бемоль-аккорд с задержанной квартой', 'Мажорный септаккорд с большой секундой от ноты Си-бемоль', 'Си-бемоль-доминантсептаккорд с задержанной квартой',
               'Си-бемоль-мажорный секстаккорд', 'Си-бемоль-минорный секстаккорд', ' Си-бемоль-доминантнонаккорд',
               'Cи-бемоль-минорный нонаккорд', 'Cи-бемоль мажор, большая септима', 'Cи-бемоль-мажорный септаккорд', 'Мажорный септаккорд с секстой от ноты Си-бемоль',
               'Си-бемоль мажор с уменьшенной квинтой','Си-бемоль мажор с большой ноной']
# B
CHORDS_4DSR = ['Си мажор', 'Си минор', 'Доминантсептаккорд от ноты Си', 'Минорный септаккорд от ноты Си', 'Си мажор увеличенный',
               'Уменьшенный аккорд от ноты Си', 'Уменьшенный септаккорд от ноты Си', 'Си мажор с большой секундой вместо терции',
               'Си мажор с квартой вместо терции', 'Мажорный септаккорд с большой секундой от ноты Си', 'Мажорный септаккорд с квартой от ноты Си',
               'Мажорный секстаккорд от ноты Си', 'Минорный секстаккорд от ноты Си', 'Мажорный нонаккорд от ноты Си',
               'Минорный нонаккорд от ноты Си', 'Си мажор', 'Большой мажорный септаккорд от ноты Си', 'Мажорный септаккорд с секстой от ноты Си',
               'Си мажор с уменьшенной квинтой','Си мажор с большой ноной']

# H
CHORDS_5DSR = ['Си мажор', 'Си минор', 'Доминантсептаккорд от ноты Си', 'Минорный септаккорд от ноты Си', 'Си мажор увеличенный',
               'Уменьшенный аккорд от ноты Си', 'Уменьшенный септаккорд от ноты Си', 'Си мажор с большой секундой вместо терции',
               'Си мажор с квартой вместо терции', 'Мажорный септаккорд с большой секундой от ноты Си', 'Мажорный септаккорд с квартой от ноты Си',
               'Мажорный секстаккорд от ноты Си', 'Минорный секстаккорд от ноты Си', 'Мажорный нонаккорд от ноты Си',
               'Минорный нонаккорд от ноты Си', 'Си мажор', 'Большой мажорный септаккорд от ноты Си', 'Мажорный септаккорд с секстой от ноты Си',
               'Си мажор с уменьшенной квинтой','Си мажор с большой ноной']


# C
CHORDS_6DSR = ['До мажор', 'До минор', 'Доминантсептаккорд от ноты До', 'Минорный септаккорд от ноты До', 'До мажор увеличенный',
               'Уменьшенный аккорд от ноты До', 'Уменьшенный септаккорд от ноты До', 'До мажор с большой секундой вместо терции',
               'До мажор с квартой вместо терции', 'Мажорный септаккорд с большой секундой от ноты До', 'Мажорный септаккорд с квартой от ноты До',
               'Мажорный секстаккорд от ноты До', 'Минорный секстаккорд от ноты До', 'Мажорный нонаккорд от ноты До',
               'Минорный нонаккорд от ноты До', 'До мажор', 'Большой мажорный септаккорд от ноты До', 'Мажорный септаккорд с секстой от ноты До',
               'До мажор с уменьшенной квинтой','До мажор с большой ноной']

# C#
CHORDS_7DSR = ['До-диез мажор', 'До-диез минор', 'Доминантсептаккорд от ноты До-диез', 'Минорный септаккорд от ноты До-диез',
               'До-диез мажор увеличенный', 'Уменьшенный аккорд от ноты До-диез', 'Уменьшенный септаккорд от ноты До-диез',
               'До-диез мажор с большой секундой вместо терции', 'До-диез мажор с квартой вместо терции',
               'Мажорный септаккорд с большой секундой от ноты До-диез', 'Мажорный септаккорд с квартой от ноты До-диез',
               'Мажорный секстаккорд от ноты До-диез', 'Минорный секстаккорд от ноты До-диез', 'Мажорный нонаккорд от ноты До-диез',
               'Минорный нонаккорд от ноты До-диез', 'До-диез мажор', 'Большой мажорный септаккорд от ноты До-диез',
               'Мажорный септаккорд с секстой от ноты До-диез','До-диез мажор с уменьшенной квинтой','До-диез мажор с большой ноной']


# Db
CHORDS_8DSR = ['До-бемоль мажор', 'До-бемоль-минорный аккорд', 'До-бемоль-доминантсептаккорд', 'До-бемоль-минорный септаккорд', 'Увеличенный аккорд от ноты До-бемоль',
               'До-бемоль-уменьшенный аккорд', 'До-бемоль-уменьшенный септаккорд', 'До-бемоль-аккорд с задержанной секундой',
               'До-бемоль-аккорд с задержанной квартой', 'Мажорный септаккорд с большой секундой от ноты До-бемоль', 'До-бемоль-доминантсептаккорд с задержанной квартой',
               'До-бемоль-мажорный секстаккорд', 'До-бемоль-минорный секстаккорд', ' До-бемоль-доминантнонаккорд',
               'До-бемоль-минорный нонаккорд', 'До-бемоль мажор, большая септима', 'До-бемоль-мажорный септаккорд', 'Мажорный септаккорд с секстой от ноты До-бемоль',
               'До-бемоль мажор с уменьшенной квинтой','До-бемоль мажор с большой ноной']

# D
CHORDS_9DSR = ['Ре мажор', 'Ре минор', 'Доминантсептаккорд от ноты Ре', 'Минорный септаккорд от ноты Ре', 'Ре мажор увеличенный',
               'Уменьшенный аккорд от ноты Ре', 'Уменьшенный септаккорд от ноты Ре', 'Ре мажор с большой секундой вместо терции',
               'Ре мажор с квартой вместо терции', 'Мажорный септаккорд с большой секундой от ноты Ре', 'Мажорный септаккорд с квартой от ноты Ре',
               'Мажорный секстаккорд от ноты Ре', 'Минорный секстаккорд от ноты Ре', 'Мажорный нонаккорд от ноты Ре',
               'Минорный нонаккорд от ноты Ре', 'Ре мажор', 'Большой мажорный септаккорд от ноты Ре', 'Мажорный септаккорд с секстой от ноты Ре',
               'Ре мажор с уменьшенной квинтой','Ре мажор с большой ноной']

# D#
CHORDS_10DSR = ['Ре-диез мажор', 'Ре-диез минор', 'Доминантсептаккорд от ноты Ре-диез', 'Минорный септаккорд от ноты Ре-диез',
               'Ре-диез мажор увеличенный', 'Уменьшенный аккорд от ноты Ре-диез', 'Уменьшенный септаккорд от ноты Ре-диез',
               'Ре-диез мажор с большой секундой вместо терции', 'Ре-диез мажор с квартой вместо терции',
               'Мажорный септаккорд с большой секундой от ноты Ре-диез', 'Мажорный септаккорд с квартой от ноты Ре-диез',
               'Мажорный секстаккорд от ноты Ре-диез', 'Минорный секстаккорд от ноты Ре-диез', 'Мажорный нонаккорд от ноты Ре-диез',
               'Минорный нонаккорд от ноты Ре-диез', 'Ре-диез мажор', 'Большой мажорный септаккорд от ноты Ре-диез',
               'Мажорный септаккорд с секстой от ноты Ре-диез','Ре-диез мажор с уменьшенной квинтой','Ре-диез мажор с большой ноной']


# Eb
CHORDS_11DSR = ['Ми-бемоль мажор', 'Ми-бемоль минор', 'Доминантсептаккорд от ноты Ми-бемоль', 'Минорный септаккорд от ноты Ми-бемоль',
               'Ми-бемоль мажор увеличенный', 'Уменьшенный аккорд от ноты Ми-бемоль', 'Уменьшенный септаккорд от ноты Ми-бемоль',
               'Ми-бемоль мажор с большой секундой вместо терции', 'Ми-бемоль мажор с квартой вместо терции',
               'Мажорный септаккорд с большой секундой от ноты Ми-бемоль', 'Мажорный септаккорд с квартой от ноты Ми-бемоль',
               'Мажорный секстаккорд от ноты Ми-бемоль', 'Минорный секстаккорд от ноты Ми-бемоль', 'Мажорный нонаккорд от ноты Ми-бемоль',
               'Минорный нонаккорд от ноты Ми-бемоль', 'Ми-бемоль мажор', 'Большой мажорный септаккорд от ноты Ми-бемоль',
               'Мажорный септаккорд с секстой от ноты Ми-бемоль','Ми-бемоль мажор с уменьшенной квинтой','Ми-бемоль мажор с большой ноной']


# E
CHORDS_12DSR = ['Ми мажор', 'Ми минор', 'Доминантсептаккорд от ноты Ми', 'Минорный септаккорд от ноты Ми', 'Ми мажор увеличенный',
               'Уменьшенный аккорд от ноты Ми', 'Уменьшенный септаккорд от ноты Ми', 'Ми мажор с большой секундой вместо терции',
               'Ми мажор с квартой вместо терции', 'Мажорный септаккорд с большой секундой от ноты Ми', 'Мажорный септаккорд с квартой от ноты Ми',
               'Мажорный секстаккорд от ноты Ми', 'Минорный секстаккорд от ноты Ми', 'Мажорный нонаккорд от ноты Ми',
               'Минорный нонаккорд от ноты Ми', 'Ми мажор', 'Большой мажорный септаккорд от ноты Ми', 'Мажорный септаккорд с секстой от ноты Ми',
                'Ми мажор с уменьшенной квинтой','Ми мажор с большой ноной']


# F
CHORDS_13DSR = ['Фа мажор', 'Фа минор', 'Доминантсептаккорд от ноты Фа', 'Минорный септаккорд от ноты Фа', 'Фа мажор увеличенный',
               'Уменьшенный аккорд от ноты Фа', 'Уменьшенный септаккорд от ноты Фа', 'Фа мажор с большой секундой вместо терции',
               'Фа мажор с квартой вместо терции', 'Мажорный септаккорд с большой секундой от ноты Фа', 'Мажорный септаккорд с квартой от ноты Фа',
               'Мажорный секстаккорд от ноты Фа', 'Минорный секстаккорд от ноты Фа', 'Мажорный нонаккорд от ноты Фа',
               'Минорный нонаккорд от ноты Фа', 'Фа мажор', 'Большой мажорный септаккорд от ноты Фа', 'Мажорный септаккорд с секстой от ноты Фа',
                'Фа мажор с уменьшенной квинтой','Фа мажор с большой ноной']

# F#
CHORDS_14DSR = ['Фа-диез мажор', 'Фа-диез минор', 'Доминантсептаккорд от ноты Фа-диез', 'Минорный септаккорд от ноты Фа-диез',
                'Фа-диез мажор увеличенный', 'Уменьшенный аккорд от ноты Фа-диез', 'Уменьшенный септаккорд от ноты Фа-диез',
                'Фа-диез мажор с большой секундой вместо терции', 'Фа-диез мажор с квартой вместо терции',
                'Мажорный септаккорд с большой секундой от ноты Фа-диез', 'Мажорный септаккорд с квартой от ноты Фа-диез',
                'Мажорный секстаккорд от ноты Фа-диез', 'Минорный секстаккорд от ноты Фа-диез', 'Мажорный нонаккорд от ноты Фа-диез',
                'Минорный нонаккорд от ноты Фа-диез', 'Фа-диез мажор', 'Большой мажорный септаккорд от ноты Фа-диез',
                'Мажорный септаккорд с секстой от ноты Фа-диез','Фа-диез мажор с уменьшенной квинтой','Фа-диез мажор с большой ноной']

# Gb 15
CHORDS_15DSR = ['Соль-бемоль мажор', 'Соль-бемоль минор', 'Доминантсептаккорд от ноты Соль-бемоль', 'Минорный септаккорд от ноты Соль-бемоль',
               'Соль-бемоль мажор увеличенный', 'Уменьшенный аккорд от ноты Соль-бемоль', 'Уменьшенный септаккорд от ноты Соль-бемоль',
               'Соль-бемоль мажор с большой секундой вместо терции', 'Соль-бемоль мажор с квартой вместо терции',
               'Мажорный септаккорд с большой секундой от ноты Соль-бемоль', 'Мажорный септаккорд с квартой от ноты Соль-бемоль',
               'Мажорный секстаккорд от ноты Соль-бемоль', 'Минорный секстаккорд от ноты Соль-бемоль', 'Мажорный нонаккорд от ноты Соль-бемоль',
               'Минорный нонаккорд от ноты Соль-бемоль', 'Соль-бемоль мажор', 'Большой мажорный септаккорд от ноты Соль-бемоль',
               'Мажорный септаккорд с секстой от ноты Соль-бемоль','Соль-бемоль мажор с уменьшенной квинтой','Соль-бемоль мажор с большой ноной']


# G
CHORDS_16DSR = ['Соль мажор', 'Соль минор', 'Доминантсептаккорд от ноты Соль', 'Минорный септаккорд от ноты Соль', 'Соль мажор увеличенный',
                'Уменьшенный аккорд от ноты Соль', 'Уменьшенный септаккорд от ноты Соль', 'Соль мажор с большой секундой вместо терции',
                'Соль мажор с квартой вместо терции', 'Мажорный септаккорд с большой секундой от ноты Соль', 'Мажорный септаккорд с квартой от ноты Соль',
                'Мажорный секстаккорд от ноты Соль', 'Минорный секстаккорд от ноты Соль', 'Мажорный нонаккорд от ноты Соль',
                'Минорный нонаккорд от ноты Соль', 'Соль мажор', 'Большой мажорный септаккорд от ноты Соль', 'Мажорный септаккорд с секстой от ноты Соль',
                'Соль мажор с уменьшенной квинтой','Соль мажор с большой ноной']

# G#
CHORDS_17DSR = ['Соль-диез мажор', 'Соль-диез минор', 'Доминантсептаккорд от ноты Соль-диез', 'Минорный септаккорд от ноты Соль-диез',
                'Соль-диез мажор увеличенный', 'Уменьшенный аккорд от ноты Соль-диез', 'Уменьшенный септаккорд от ноты Соль-диез',
                'Соль-диез мажор с большой секундой вместо терции', 'Соль-диез мажор с квартой вместо терции',
                'Мажорный септаккорд с большой секундой от ноты Соль-диез', 'Мажорный септаккорд с квартой от ноты Соль-диез',
                'Мажорный секстаккорд от ноты Соль-диез', 'Минорный секстаккорд от ноты Соль-диез', 'Мажорный нонаккорд от ноты Соль-диез',
                'Минорный нонаккорд от ноты Соль-диез', 'Соль-диез мажор', 'Большой мажорный септаккорд от ноты Соль-диез',
                'Мажорный септаккорд с секстой от ноты Соль-диез','Соль-диез мажор с уменьшенной квинтой','Соль-диез мажор с большой ноной']

# Ab 18
CHORDS_18DSR = ['Ля-бемоль мажор', 'Ля-бемоль минор', 'Доминантсептаккорд от ноты Ля-бемоль', 'Минорный септаккорд от ноты Ля-бемоль',
               'Ля-бемоль мажор увеличенный', 'Уменьшенный аккорд от ноты Ля-бемоль', 'Уменьшенный септаккорд от ноты Ля-бемоль',
               'Ля-бемоль мажор с большой секундой вместо терции', 'Ля-бемоль мажор с квартой вместо терции',
               'Мажорный септаккорд с большой секундой от ноты Ля-бемоль', 'Мажорный септаккорд с квартой от ноты Ля-бемоль',
               'Мажорный секстаккорд от ноты Ля-бемоль', 'Минорный секстаккорд от ноты Ля-бемоль', 'Мажорный нонаккорд от ноты Ля-бемоль',
               'Минорный нонаккорд от ноты Ля-бемоль', 'Ля-бемоль мажор', 'Большой мажорный септаккорд от ноты Ля-бемоль',
               'Мажорный септаккорд с секстой от ноты Ля-бемоль','Ля-бемоль мажор с уменьшенной квинтой','Ля-бемоль мажор с большой ноной']


CHORDS_TYPE_NAME_LIST_DSR = [CHORDS_1DSR, CHORDS_2DSR, CHORDS_3DSR, CHORDS_4DSR, CHORDS_5DSR, CHORDS_6DSR, CHORDS_7DSR,
CHORDS_8DSR, CHORDS_9DSR, CHORDS_10DSR, CHORDS_11DSR, CHORDS_12DSR, CHORDS_13DSR,CHORDS_14DSR,CHORDS_15DSR,
                             CHORDS_16DSR,CHORDS_17DSR,CHORDS_18DSR]


TR_TYPE_1_B = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
TR_TYPE_2_B = ['A', 'Bb', 'B', 'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab']

TR_TYPE_1_H = ['A', 'A#', 'H', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
TR_TYPE_2_H = ['A', 'Bb', 'H', 'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab']


def trans_chord(chord_type, ton:int = 0, b = 0 , h = 0 ):
    if len(chord_type) > 1:
        if chord_type[1] != 'b' and chord_type[1] != '#':
            chord = chord_type[0]
            chord_syf = chord_type.replace(chord,'')
        else:
            chord = chord_type[0] + chord_type[1]
            chord_syf = chord_type.replace(chord,'')
    else:
        chord = chord_type[0]
        chord_syf = ''

    # если в песне нет h и b
    if h == 0 and b == 0:
        index = TR_TYPE_1_B.index(chord)
        if ton == 1:
            if index + 1 == len(TR_TYPE_1_B):
                tr_chord = TR_TYPE_1_B[0] + chord_syf
                return tr_chord
            else:
                tr_chord = TR_TYPE_1_B[index + 1] + chord_syf
                return tr_chord
        else:
            if index - 1 < 0:
                tr_chord = TR_TYPE_1_B[-1] + chord_syf
                return tr_chord
            else:
                tr_chord = TR_TYPE_1_B[index - 1] + chord_syf
                return tr_chord

    # транспонируем по третьему списку c H без бемолей
    elif h == 1 and b == 0:
        index = TR_TYPE_1_H.index(chord)
        if ton == 1:
            if index + 1 == len(TR_TYPE_1_H):
                tr_chord = TR_TYPE_1_H[0] + chord_syf
                return tr_chord
            else:
                tr_chord = TR_TYPE_1_H[index + 1] + chord_syf
                return tr_chord
        else:
            if index - 1 < 0:
                tr_chord = TR_TYPE_1_H[-1] + chord_syf
                return tr_chord
            else:
                tr_chord = TR_TYPE_1_H[index - 1] + chord_syf
                return tr_chord

    # транспонируем по второму списку с без h c бемолем
    elif h == 0 and b == 1:
        index = TR_TYPE_2_B.index(chord)
        if ton == 1:
            if index + 1 == len(TR_TYPE_2_B):
                tr_chord = TR_TYPE_2_B[0] + chord_syf
                return tr_chord
            else:
                tr_chord = TR_TYPE_2_B[index + 1] + chord_syf
                return tr_chord
        else:
            if index - 1 < 0:
                tr_chord = TR_TYPE_2_B[-1] + chord_syf
                return tr_chord
            else:
                tr_chord = TR_TYPE_2_B[index - 1] + chord_syf
                return tr_chord


    # транспонируем по второму списку с бемолями (сли в композиции есть бемоль)
    elif h == 1 and b == 1:
        index = TR_TYPE_2_H.index(chord)
        if ton == 1:
            if index + 1 == len(TR_TYPE_2_H):
                tr_chord = TR_TYPE_2_H[0] + chord_syf
                return tr_chord
            else:
                tr_chord = TR_TYPE_2_H[index + 1] + chord_syf
                return tr_chord
        else:
            if index - 1 < 0:
                tr_chord = TR_TYPE_2_H[-1] + chord_syf
                return tr_chord
            else:
                tr_chord = TR_TYPE_2_H[index - 1] + chord_syf
                return tr_chord

########################################################################################################################
# транспонирование текста
def transponire_song(song_link, ton,user):
    def find_all_chords(text):
        """Находит все аккорды в тексте по спискам."""
        chords_found = set()
        for word in text.split():
            if (word in CHORDS_1 or word in CHORDS_2 or word in CHORDS_3 or word in CHORDS_4 or word in CHORDS_5
                    or word in CHORDS_6 or word in CHORDS_7 or word in CHORDS_8 or word in CHORDS_9 or word in CHORDS_10
                    or word in CHORDS_11 or word in CHORDS_12 or word in CHORDS_13 or word in CHORDS_14 or word in CHORDS_15
                    or word in CHORDS_16 or word in CHORDS_17 or word in CHORDS_18):
                chords_found.add(word)
        return list(chords_found)

    def replace_chords_in_text(text, chord_map):
        def replacer(match):
            chord = match.group(0)
            return chord_map.get(chord, chord)

        pattern = r'(' + '|'.join(re.escape(c) for c in chord_map.keys()) + r')'
        return re.sub(pattern, replacer, text)

    def replace_markdown_symbols(text):
        replacements = {
            '*': '⨉',
            '_': '⎯',
            '[': '［',
            ']': '］',
            '(': '（',
            ')': '）',
            '`': '｀',
            '{': '｛',
            '}': '｝',
            '+': '＋',
            '-': '－',
            '!': '！',
            '|': '｜',
            '>': '＞'
        }
        for symbol, replacement in replacements.items():
            text = text.replace(symbol, replacement)
        return text

    def get_transpose_params(chord):
        if any(n in chord for n in ['Ab', 'Bb', 'Db', 'Eb', 'Gb']):
            return {'b': 1, 'h': 0}
        elif chord in CHORDS_5:
            return {'b': 0, 'h': 1}
        else:
            return {'b': 0, 'h': 0}

    # Основная логика:
    with open(song_link, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()

    # Обработка первых двух строк
    if len(lines) >= 3:
        lines[0] = f"🎸 *{lines[0].strip()}*🤘🎶😎\n"
        lines[2] = f"🎵 _{lines[2].strip()}_\n"
        print(f'Текущие аккорды: {lines[2]}')

    # Объединяем весь текст для поиска аккордов
    full_text = ''.join(lines)

    # Находим все аккорды в тексте
    all_chords = find_all_chords(full_text)
    print(f'найдены{all_chords}')

    # Теперь применяем транспонирование для каждого аккорда с индивидуальными параметрами
    chord_map = {}
    for ch in all_chords:
        params = get_transpose_params(ch)
        b = params['b']
        h = params['h']

        trans_ch = ch
        if ton > 0:
            for _ in range(ton):
                trans_ch = trans_chord(trans_ch, 1, b, h)
                # print(f'{ch} транспонирован в тексте {trans_ch}')
        elif ton < 0:
            for _ in range(-ton):
                trans_ch = trans_chord(trans_ch, -1, b, h)
                # print(f'{ch} транспонирован в тексте {trans_ch}')

        chord_map[ch] = trans_ch

    # Перед заменой третьей строки — заменяем спец символы в остальных строках (кроме первой и третьей)
    for i in range(len(lines)):
        if i != 0 and i != 2:
            lines[i] = replace_markdown_symbols(lines[i])

    # Заменяем все найденные аккорды в полном тексте на транспонированные
    full_text_transposed = replace_chords_in_text(full_text, chord_map)
    # Обновляем строки с учетом замены аккордов
    for i in range(len(lines)):
        lines[i] = replace_chords_in_text(lines[i], chord_map)
    # Заменяем третью строку на слово "Аккорды" и список
    sorted_chords = sorted(set(chord_map.values()))
    lines[2] = f"🎵 _Аккорды({','.join(sorted_chords)})_\n"

    if PARTNER_LINK:
        lines.append(replace_markdown_symbols(f'\n\n'))
        lines.append(PARTNER_LINK)


    # Итоговый текст
    file_link = ''.join(lines)

    return file_link, ','.join(sorted_chords)

# строка до последнего пробела
def get_substring(s, max_length=25):
    # Если длина строки меньше или равна max_length, возвращаем всю строку
    if len(s) <= max_length:
        return s

    # Обрезаем строку до max_length
    truncated = s[:max_length]

    # Ищем последний пробел в обрезанной части
    last_space = truncated.rfind(' ')

    # Если есть пробел, возвращаем строку до него
    if last_space != -1:
        return truncated[:last_space]
    else:
        # Если пробелов нет, возвращаем обрезанную строку полностью
        return truncated


# оформление топов
def escape_markdown_v2(text):
    special_chars = r'\_*[]()~`>#+-=|{}.!'
    for char in special_chars:
        text = text.replace(char, '\\' + char)
    return text

def escape_markdown(text):
    special_chars = r'\_*[]()~`>#+-=|{}.!'
    for char in special_chars:
        text = text.replace(char, '\\' + char)
    return text

def format_top_songs_for_telegram(songs_list,text,type: int = 0):
    message_lines = []
    numbers = ['🥇','🥈','🥉','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟',]
    for name, views in songs_list:
        index = songs_list.index([name, views])
        idx = numbers[index]
        if len(name) > 30:
            safe_name = escape_markdown_v2(name[:30] + '...')
        else:
            safe_name = escape_markdown_v2(name)


        message_lines.append(f"{idx} *{safe_name}*")
        if views == 1:
            if type == 0:
                message_lines.append(" ".ljust(6, ' ') + f"{views} 👁️ _просмотр_\n")
            elif type == 1:
                message_lines.append(" ".ljust(6, ' ') + f"{views} ⭐ _песня_\n")
        elif views in [2,3,4]:
            if type == 0:
                message_lines.append(" ".ljust(6, ' ') + f"{views} 👁️ _просмотра_\n")
            elif type == 1:
                message_lines.append(" ".ljust(6, ' ') + f"{views} ⭐ _песни_\n")
        else:
            if type == 0:
                message_lines.append(" ".ljust(6, ' ') + f"{views} 👁️ _просмотров_\n")
            elif type == 1:
                message_lines.append(" ".ljust(6, ' ') + f"{views} ⭐ _песен_\n")

    return f"*ТОП10 {text}*\n\n" + "\n".join(message_lines)

# группировка песен по названию
def group_songs(songs):
    grouped = {}
    for song in songs:
        # Разделяем название по первому нижнему подчеркиванию
        if '_' in song:
            base_name = song.split('_')[0]
        else:
            base_name = song
        # Приводим к нижнему регистру и заменяем 'ё' на 'е'
        base_name_processed = base_name.lower().replace('ё', 'е')
        # Добавляем песню в соответствующую группу
        if base_name_processed not in grouped:
            grouped[base_name_processed] = []
        grouped[base_name_processed].append(song)
    return list(grouped.values())


# декоратор таймер выполнения операций

# декоратор для вывода времени выполнения функций
def measure_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        seconds = int(elapsed_time % 60)
        print(f"⏱ Время выполнения: {hours:02d}:{minutes:02d}:{seconds:02d}")
        return result
    return wrapper


# поиск идентичных файлов в папке
def get_files_in_folder(initial_file_path):
    # Получаем абсолютный путь к файлу
    initial_file_abs = os.path.abspath(initial_file_path)
    # Определяем папку файла
    folder_path = os.path.dirname(initial_file_abs)

    # Получаем все файлы в папке
    all_files = []
    for filename in os.listdir(folder_path):
        full_path = os.path.join(folder_path, filename)
        if os.path.isfile(full_path):
            all_files.append(full_path)

    # Фильтруем по расширениям
    extensions = ['.jpg', '.png']
    filtered_files = [f for f in all_files if os.path.splitext(f)[1].lower() in extensions]

    # Включаем начальный файл первым элементом
    if initial_file_abs not in filtered_files:
        filtered_files.insert(0, initial_file_abs)
    else:
        filtered_files.remove(initial_file_abs)
        filtered_files.insert(0, initial_file_abs)

    # Функция для извлечения числа из имени файла
    def extract_number(file_path):
        filename = os.path.basename(file_path)
        match = re.search(r'_(\d+)', filename)
        if match:
            return int(match.group(1))
        else:
            return -1  # файлы без суффикса идут в начало при сортировке

    # Сортируем файлы по числовому суффиксу, при этом файлы без суффикса получат -1 и будут в начале
    sorted_files = sorted(filtered_files, key=extract_number)
    print(sorted_files)
    return sorted_files


def replace_markdown_symbols(text):
    replacements = {
        '*': '⨉',
        '_': '⎯',
        '[': '［',
        ']': '］',
        '(': '（',
        ')': '）',
        '`': '｀',
        '{': '｛',
        '}': '｝',
        '+': '＋',
        '-': '－',
        '!': '！',
        '|': '｜',
        '>': '＞'
    }
    for symbol, replacement in replacements.items():
        text = text.replace(symbol, replacement)
    return text


# разбивка длинного текста
def split_text(text, max_length=4000):
    """
    Разбивает текст на части не длиннее max_length символов.
    Разбиение происходит по переносам строк (\n), чтобы не резать строки посередине.

    Возвращает список строк.
    """
    lines = text.split('\n')
    parts = []
    current_part = []

    current_length = 0
    for line in lines:
        # +1 для учёта символа переноса строки, который будет добавлен обратно
        line_length = len(line) + 1

        if current_length + line_length > max_length:
            # Если текущая часть не пустая, добавляем её в результат
            if current_part:
                parts.append('\n'.join(current_part))
                current_part = []
                current_length = 0

            # Если одна строка длиннее max_length, нужно её разбить принудительно
            if line_length > max_length:
                # Разбиваем длинную строку на куски по max_length
                for i in range(0, len(line), max_length):
                    parts.append(line[i:i + max_length])
            else:
                current_part.append(line)
                current_length = line_length
        else:
            current_part.append(line)
            current_length += line_length

    # Добавляем последнюю часть
    if current_part:
        parts.append('\n'.join(current_part))

    return parts

if __name__ == "__main__":
    print(DBNAME)






