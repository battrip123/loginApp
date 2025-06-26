# -*- coding: utf-8 -*-
import csv  # Do ładowania plików csv.
import yaml  # Do ładowania plików yaml.
import random  # Do losowania liczb (przy numerze badanego).
import atexit  # Do pobierania danych z procedury do pliku.
import codecs  # Do pobrania polskich znaków.
from typing import List, Dict # Do używania listy i słownika.
from os.path import join # Do łączenia plików i danych.
from psychopy import visual, event, logging, gui, core # Do ładowania potrzebnych rzeczy z psychopy.


@atexit.register

# Dzięki atexit ta funkcja zawsze zostanie wykonana:
# Wyniki badanego będą z awsze zapisane, nawet jak coś przerwie działanie kodu.

def save_beh_results() -> None:
   """
   Tworzenie w pliku results notatkę do zapisania danych badanego.
   """
   file_name = PART_ID + '_' + str(random.choice(range(100, 1000))) + '_beh.csv' # Nadawanie nazwy notatce z wynikami badanego.
   with open(join('results', file_name), 'w', encoding='utf-8') as beh_file: # Zaspisywanie danych w pliku.
       beh_writer = csv.writer(beh_file)
       beh_writer.writerows(RESULTS)
   logging.flush()



def show_image(win: visual.Window, file_name: str, size: List[int], key: str = 'f7') -> None:
    """
    Pokazywanie tesktu w formie obrazu.
    Zakończenie procedury jeśli zostanie naciśnięty klawisz "f7".
    Przejście dalej jeśli zostanie naciśnięty "enter" lub "spacja".
    """
    image = visual.ImageStim(win=win, image=file_name, interpolate=True, size=size)
    image.draw()
    win.flip()
    clicked = event.waitKeys(keyList=[key, 'return', 'space'])
    if clicked == [key]:
        logging.critical('Experiment finished by user! {} pressed.'.format(key[0]))
        exit(0)
    win.flip()


def read_text_from_file(file_name: str, insert: str = '') -> str:
    """
    Zczytywanie danych z plików:
    Tytuł pliku musi być ciągiem znaków;
    Otwieranie i czytanie pliku, z pominięciem komentarzy;
    Wstawianie tekstu z pliku.
    """
    if not isinstance(file_name, str):
        logging.error('Problem with file reading, filename must be a string')
        raise TypeError('file_name must be a string')
    msg = list()
    with codecs.open(file_name, encoding='utf-8', mode='r') as data_file:
        for line in data_file:
            if not line.startswith('#'):
                if line.startswith('<--insert-->'):
                    if insert:
                        msg.append(insert)
                else:
                    msg.append(line)
    return ''.join(msg)


def check_exit(key: str = 'f7') -> None:
    """
    Zakończenie całej procedury przez wciśnięcie klawisza "f7".
    """
    stop = event.getKeys(keyList=[key])
    if stop:
        abort_with_error('Experiment finished by user! {} pressed.'.format(key))


def show_info(win: visual.Window, file_name: str, insert: str = '') -> None:
    """
    Wyświetlanie intstrukcji na ekranie.
    Formatowanie instrukcji.
    Wciśnięcie klawisza "spacja" lub "enter" w celu prześcia dalej.
    """
    msg = read_text_from_file(file_name, insert=insert)
    msg = visual.TextStim(win, color='black', text=msg, height=20, wrapWidth=1000)
    msg.draw()
    win.flip()
    key = event.waitKeys(keyList=['f7', 'return', 'space'])
    if key == ['f7']:
        abort_with_error('Experiment finished by user on info screen! F7 pressed.')
    win.flip()


def abort_with_error(err: str) -> None:
    """
    Zakończenie całej procedury.
    Uruchamiane po wciśnięciu klawisza "f7".
    """
    logging.critical(err)
    win.close()  # zamyka okno
    raise SystemExit(err)


def run_trial(win, conf, clock, target_stim, cue_stim, fix_cross, reminder_stim, previous_cue, no_switch_count, training=False):
    """
    Przebieg pojedynczej sekwencji
    Prepare and present single trial of procedure.
    Input (params) should consist all data need for presenting stimuli.
    If some stimulus (eg. text, label, button) will be presented across many trials.
    Should be prepared outside this function and passed for .draw() or .setAutoDraw().
    Returns:
        All behavioral data (reaction time, answer, etc. should be returned from this function).
    """

    if previous_cue is None: # Losowanie pierwszej wskazówki - LITERA lub CYFRA.
        cue = random.choice(conf['STIM_CUE'])
        no_switch_count = 0
    else:
        if no_switch_count >= 5: # Zmiana wskazówki, jeśli nie było zmiany przez ostatnie 5 sekwencji.
            cue = "CYFRA" if previous_cue == "LITERA" else "LITERA"
            no_switch_count = 0
        else:
            if random.random() < 0.25: # Prawdopodobieństwo zmienienia wskazówki.
                cue = "CYFRA" if previous_cue == "LITERA" else "LITERA"
                no_switch_count = 0
            else:
                cue = previous_cue
                no_switch_count += 1 # Liczenie ile razy powtarzała się dana wskazówka.

    if cue == previous_cue or previous_cue == None: # Zebranie informacji czy zadanie było "switch", czy "no-switch".
        switch_status = "no-switch"
    else:
        switch_status = "switch"

    litera = random.choice(conf['STIM_LETTERS']) # Wybranie ze zbioru liter losowej litery do bodźca docelowego.
    cyfra = random.choice(conf['STIM_NUMBERS']) # Wybranie ze zbioru cyfr losowej cyfry do bodźca docelowego.
    cue_stim.text = cue # Przechowywanie tekstu wskazówki.

    for _ in range(conf['STIM_TIME']): # Wyświetlenie wskazówki.
        check_exit() # Sprawdzenie, czy nie został wciśnięty klawisz F7.
        cue_stim.draw()
        reminder_stim.draw()
        win.flip()

    for _ in range(conf['FIX_CROSS_TIME']): # Wyświetlenie punktu fiksacji.
        check_exit() # Sprawdzenie, czy nie został wciśnięty klawisz F7.
        fix_cross.draw()
        reminder_stim.draw()
        win.flip()

    target_stim.text = f"{litera} {cyfra}" # Przechowywanie bodźców docelowych w formie tekstu.
    event.clearEvents() # Zresetowanie każdego wcześniejszego wciśnięcia klawiszu.
    win.callOnFlip(clock.reset) # Dokładne rozpoczęcie czasu pomiaru od momentu wyświetlenia bodźca.

    for _ in range(conf['REACTION_TIME']):  # Wyświetlenie bodźca docelowego.
        check_exit() # Sprawdzenie, czy nie został wciśnięty klawisz F7.
        reaction = event.getKeys(keyList=list(conf['REACTION_KEYS']), timeStamped=clock) # Zarejestrowanie wciśnięcia klawisza i przypisanie czasu reakcji.
        if reaction:  # Zatrzymanie po wciśnięciu klawisza.
            break
        target_stim.draw() # Wyświetlanie bodźca docelowego.
        reminder_stim.draw() # Wyświetlanie przypomnienia o przypisaniu klawiszy do bodźców.
        win.flip()

    if not training: # Maska w sesji eksperymentalnej pojawia się po pokazaniu bodźców, zaś w treningu po feedbacku.
        for _ in range(conf['MASK_TIME']):
            check_exit() # Sprawdzenie, czy nie został wciśnięty klawisz F7.
            reminder_stim.draw()
            win.flip()

    if reaction:
        key_pressed, rt = reaction[0]  # 0 to krotka: (pierwszy przycisk który został wciśnięty, czas wciśnięcia).
    else:  # Po upłynięciu czasu na reakcję na bodziec zapisujemy czas reakcji jako -1, aby wyróżniał się z rzeczywistych czasów reakcji.
        key_pressed = 'no_key'
        rt = -1

    correct_key = None  # Wprowadzenie prawidłowej reakcji (klawiszu) na dane bodźce (domyślnie żaden klawisz).
    if cue == "LITERA": # Jeśli wskazówką była LITERA, poprawnym klawiszem w odpowiedzi na samogłoskę jest "z", a na spółgłoskę "m".
        correct_key = 'z' if litera in ['A', 'E', 'I', 'U'] else 'm'
    elif cue == "CYFRA": # Jeśli wskazówką była CYFRA, poprawnym klawiszem w odpowiedzi na cyfry nieparzyste jest "z", a na cyfry parzyste "m".
        correct_key = 'z' if cyfra in ['3', '5', '7', '9'] else 'm'

    correctness = 1 if key_pressed == correct_key else 0 #Poprawna odpowiedź zapisana jako 1, a niepoprawna jako 0.

    return key_pressed, rt, switch_status, correctness, cue  # Zwracanie wszystkich danych zebranych podczas sekwencji.



# Ustawienia zmiennych globalnych:

RESULTS = list()  # Lista, w której będą zbierane dane.
RESULTS.append(['PART_ID', 'Block', 'Trial', 'Cue', 'Correctness', 'Switch_status', 'RT'])  # Nadanie tytułów nagłówkom kolumn.
PART_ID = '' # ID badanego.
SCREEN_RES = [] # Rozdzielczość ekranu

# Storzenie okna do zbierania danych badanego.
info: Dict = {'ID': '', 'Sex': ['M', "F"], 'Age': ''} # Słownik, który zapisuje ID, płeć i wiek.
dict_dlg = gui.DlgFromDict(dictionary=info, title='Experiment title, fill by your name!')
if not dict_dlg.OK:
    abort_with_error('Info dialog terminated.')

clock = core.Clock() # Ustawienie zegara.

conf: Dict = yaml.load(open('config.yaml', encoding='utf-8'), Loader=yaml.SafeLoader)
frame_rate: int = conf['FRAME_RATE']
SCREEN_RES: List[int] = conf['SCREEN_RES']
# === Scene init ===
# zmiana: wielkość okna
win = visual.Window(SCREEN_RES, monitor='testMonitor', units='pix', color=conf['BACKGROUND_COLOR'])
event.Mouse(visible=False, newPos=None, win=win)  # Make mouse invisible

PART_ID = info['ID'] + info['Sex'] + info['Age']
logging.LogFile(join('results', f'{PART_ID}.log'), level=logging.INFO)  # errors logging
logging.info('FRAME RATE: {}'.format(frame_rate))
logging.info('SCREEN RES: {}'.format(SCREEN_RES))

# === Prepare stimulus here ===
# Stworzenia bodźców

fix_cross = visual.TextStim(win, text='+', height=100, color=conf['FIX_CROSS_COLOR'])
cue_stim = visual.TextStim(win, text="", height=conf['STIM_SIZE'], color=conf['STIM_COLOR'])
target_stim = visual.TextStim(win, text="", height=conf['STIM_SIZE'], color=conf['STIM_COLOR'])
reminder_text = read_text_from_file(join('.', 'messages', 'przypomnienie.txt'))
reminder_stim = visual.TextStim(win, text=reminder_text, pos=(0, -SCREEN_RES[1] // 2 + 100), height=20, color='black', wrapWidth=SCREEN_RES[0] - 100)



# === Training ===
show_info(win, join('.', 'messages', 'instrukcja.txt'))
show_info(win, join('.', 'messages', 'komunikattrening.txt'))
show_info(win, join('.', 'messages', 'start.txt'))
previous_cue = None
no_switch_count = 0
for trial_no in range(conf['TRAINING_TRIALS']):
    key_pressed, rt, switch_status, correctness, cue = run_trial(win, conf, clock, target_stim, cue_stim, fix_cross, reminder_stim, previous_cue, no_switch_count, training=True)
    previous_cue = cue
    corr = correctness
    RESULTS.append([PART_ID, 'training', trial_no, cue, corr, switch_status, rt])
    feedb = "Poprawnie" if corr else "Niepoprawnie"
    feedb = visual.TextStim(win, text=feedb, height=50, color=conf['STIM_COLOR'])
    for _ in range(int(frame_rate * 1)):  # 1 sekunda (zamiana core.wait(1) na pętlę)
        check_exit()
        feedb.draw()
        reminder_stim.draw()
        win.flip()

    for _ in range(conf['MASK_TIME']): # maska jako pusty ekran pojawia się po feedbacku
        check_exit()
        reminder_stim.draw()
        win.flip()

# === Experiment ===
show_info(win, join('.', 'messages', 'komunikateksperyment.txt'))
show_info(win, join('.', 'messages', 'start.txt'))
trial_no = 0
for block_no in range(conf['NO_BLOCKS']):
    for _ in range(conf['TRIALS_IN_BLOCK']):
        key_pressed, rt, switch_status, corr, cue = run_trial(win, conf, clock, target_stim, cue_stim, fix_cross, reminder_stim, previous_cue, no_switch_count, training=False)
        previous_cue = "LITERA"
        RESULTS.append([PART_ID, block_no, trial_no, cue, corr, switch_status, rt])
        trial_no += 1
        for _ in range(int(frame_rate * 1)):  # przypomnienie jest widoczne przez 1s między próbami, aby znikało i nie rozpraszało badanego
            check_exit()
            reminder_stim.draw()
            win.flip()
    show_image(win, join('.', 'images', 'przerwa.jpg'), size=SCREEN_RES)

# === Cleaning time ===
save_beh_results()
logging.flush()
show_info(win, join('.', 'messages', 'end.txt'))
win.close()
