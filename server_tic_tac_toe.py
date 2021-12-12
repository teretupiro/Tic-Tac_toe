#== server_tic_tac_toe.py     R.R.Sonkin 10.02.2020
##-- сервер для сетевого варианта игры "Крестики-нолики"
##-- вариант 0 игровой сервер


#== подключить библиотеки
# import threading
from socket import *

# from random import randint                ////0////

#                                           ////0////
flag_test = 0               # тестовый режим для одного игрока
mode = 'регистрация'        # режим регистрации
# mode = 'игра'             # режим игры
play_table = []             # таблица игроков [name, ip, ch]             ////0////
player_count = 2            # число игроков для игры
player_num = 0              # номер текущего игрока
ch_table = ['z', 'k']       # список значков (z - нолик, k - крестик)
x_count = 22
y_count = 22


# массив результатов ходов
cells = []
for y_num in range(y_count):
    row = []
    for x_num in range(x_count):
        row.append(' ')
    cells.append(row)


# secret_num = 100            # задуманное число               ////0////


# ///////// ФУНКЦИИ /////////
def clear_cells():          # очистить таблицу ходов
    global cells
    for row in range(y_count):
        for col in range(x_count):
            cells[row][col] = ''


# проверяет есть ли 5 элементов в одну линию подряд (горизонт, вертик и диагональ)
def count_dir(row, col, d_row, d_col):          # сосчитать число ch в заданном направлении
    ch_beg = cells[row][col]
    if not ch_beg: return 0                     # защита от ошибки
    row_cur = row + d_row; col_cur = col + d_col; res = 0

    while 0 <= row_cur < y_count and 0 <= col_cur < x_count:
        if cells[row_cur][col_cur] != ch_beg: break
        res += 1
        row_cur += d_row; col_cur += d_col
    return res


# Проверка игры на окончание (нет ли победителя?)
def test_end(row, col):
    ch_mid = cells[row][col]
    print('ch_mid =', ch_mid)

    # проверить по вертикали,
    # сосчитать по вертикали вверх
    num_up = count_dir(row, col, -1, 0)
    # сосчитать по вертикали вниз
    num_down = count_dir(row, col, 1, 0)
    print('vert', num_up + num_down + 1)
    if num_up + num_down + 1 >= 5: return 1

    # проверить по горизонтали,
    # сосчитать по горизонтали влево
    num_left = count_dir(row, col, 0, -1)
    # сосчитать по горизонтали вправо
    num_right = count_dir(row, col, 0, 1)
    print('horiz', num_left + num_right + 1)
    if num_left + num_right + 1 >= 5: return 1

    # проверить по одной диагонали,
    # сосчитать по диагонали влево вверх
    num_lu = count_dir(row, col, -1, -1)
    # сосчитать по диагонали вправо вниз
    num_rd = count_dir(row, col, 1, 1)
    print('dia_1', num_lu + num_rd + 1)
    if num_lu + num_rd + 1 >= 5: return 1

    # проверить по второй диагонали,
    # сосчитать по диагонали влево вниз
    num_ld = count_dir(row, col, 1, -1)
    # сосчитать по диагонали вправо вверх
    num_ru = count_dir(row, col, -1, 1)
    print('dia_2', num_ld + num_ru + 1)
    if num_ld + num_ru + 1 >= 5: return 1

    return 0


def str_playcount():        # склонение слова игроки
    if player_count == 1:
        return '1 игрок'
    elif player_count < 5:
        return str(player_count) + ' игрока'
    else:
        return str(player_count) + ' игроков'


def send_to_all(msg):       # отправить строку всем игрокам
    for el in play_table:
        ip_el = el[1]
        res = send_answ(ip_el, msg)


mainserv_addr = ('', 5403)  # порт сервера ивеличен на 2
main_sock = socket(AF_INET, SOCK_STREAM)
main_sock.bind(mainserv_addr)                # связать с номером порта локального сервера
main_sock.listen(5)                         # не более 5 ожидающих запросов
print('main server works')


# отправить строку сообщения по заданному адресу
def send_answ(ip, msg):
    client = socket(AF_INET, SOCK_STREAM)
    bin_msg = bytes(msg, 'UTF-8')
    try:
        client.connect((ip, 5402))      # порт клиента увеличен на 2
        client.send(bin_msg)
        res = 'OK'
    except:
        res = 'not connected'
    finally:
        client.close()
    return res


# Главный цикл
while True:

    print('ready')
    connection, address = main_sock.accept()          # ждать и получить сообщение от игрока
    print('connected by', address)
    bin_data = connection.recv(1024)
    str_data = bin_data.decode('utf-8')
    print(str_data)
    connection.close()

    # обработка принятого сообщения          //// 0 ////

    # выделить адрес клиента
    ip_client = address[0]
    print(ip_client)

    # выделить команду и параметр
    lst_data = str_data.split('|')
    command = lst_data[0]
    print(command)
    try:
        param = lst_data[1]
    except:
        param = ''
    print('command = ' + command +', param = '+ param + ', mode = '+ mode)

    # отработать команду
    if command == 'get_info':
        str_answer = 'состояние сервера\n режим:  ' + mode
        str_answer += '\n список игроков: '
        for el in play_table:
            str_answer += '\n' + el[0] + ', ip = ' + el[1]
        if mode == 'игра':
            str_answer += '\n ходит: ' + play_table[player_num][0]
        elif mode == 'регистрация':
            str_answer += '\n необходимо: ' + str_playcount()
        res = send_answ(ip_client, str_answer)

    elif command == 'registr':
        if mode == 'игра':
            str_answer = '\n во время игры регистрация запрещена '
            res = send_answ(ip_client, str_answer)
            continue
        # зарегистрировать игрока
        # проверить игрока по ip адресу в таблице
        flag_find = 0
        for el in play_table:
            if el[1] == ip_client:
                el[0] = param
                flag_find = 1
                break

        # добавить игрока в таблицу, если его там нет (flag_find==0)
        if flag_find == 0:
            ch = ch_table[len(play_table)]                  # ////0////
            play_table.append([param, ip_client, ch])

            if flag_test:       # в тестовом режиме сдублировать игрока    ////0////
                ch = ch_table[len(play_table)]
                play_table.append([param, ip_client, ch])
        clear_cells()                                       # ////0////
        player_num = 0

        # подтвердить регистрацию
        str_answer = str_data + '|' + ch                    # ////0////
        res = send_answ(ip_client, str_answer)

        # сообщить всем о регистрации игрока
        str_answer = '\n Зарегистрирован игрок: ' + param
        send_to_all(str_answer)

        # начать игру, если игроков достаточно
        if len(play_table) >= player_count:
            # начальные установки в игре
            # secret_num = randint(1, secret_num)           # ////0////
            clear_cells()
            player_num = 0

            # сообщить всем о начале игры                   # ////0////
            gamer_name = play_table[player_num][0]
            str_answer = 'begin|' + str(y_count) + '|' + \
                         str(x_count) + '|' + ' игра началась!\nходит: ' + gamer_name + '\n'
            # str_answer = '\n Игра началась \n задумано число от 1 до {}'.format(secret_num)
            send_to_all(str_answer)

            # дать ход первому зарегистрированному
            ip_el = play_table[player_num][1]
            res = send_answ(ip_el, '\n Ваш ход')

            # переключиться в режим игры
            mode = 'игра'
            continue

    elif command == 'step':
        if mode == 'регистрация':
            str_answer = '\n во время регистрации запрещено ходить '
            res = send_answ(ip_client, str_answer)
            continue

        # проверить игрока по ip адресу
        el = play_table[player_num]
        if el[1] != ip_client:
            str_answer = '\n сейчас не Ваш ход =)'
            res = send_answ(ip_client, str_answer)
            continue

        # обработать ход
        '''
        # проверить корректность хода
        if not param.isnumeric():
            str_answer = '\n ваш ход не корректен, \n нужно отправить целое число'
            res = send_answ(ip_client, str_answer)
            continue

        # извлечь значение хода
        try:
            int_param = int(param)
        except:
            int_param = 0

        # сравнить с задуманным числом
        if secret_num > int_param:
            str_res = 'больше'
        elif secret_num < int_param:
            str_res = 'меньше'
        else:
            str_res = 'угадал'
        '''

        try:
            str_row, str_col = param.split(',')
            row = int(str_row)
            col = int(str_col)
        except:
            row, col = 0, 0

        if row >= y_count: row = y_count - 1
        if col >= x_count: col = x_count - 1
        ch = play_table[player_num][2]
        if cells[row][col] != '':
            str_answer = 'Ваш ход некорректен \n'
            res = send_answ(ip_client, str_answer)
            continue

        # сообщишь всем о ходе                  # ////0////
        cells[row][col] = ch
        gamer = play_table[player_num]
        gamer_name = gamer[0]
        gamer_ip = gamer[1]
        # str_answer = '\n ' + gamer_name + ': ' + param + ' - ' + str_res
        str_answer = str_data + ',' + ch + '|' + gamer_name + '\n'

        send_to_all(str_answer)

        # закончить игру, если число угадано
        '''
        if str_res == 'угадал':
            str_answer = '\n ' + gamer_name + ' выиграл, \n Игра окончена!'
            send_to_all(str_answer)
            mode = 'регистрация'
            continue
        '''

        # проверяем ...
        res = test_end(row, col)
        if res == 1:
            str_answer = 'end|' + gamer_name + ' выиграл, \n игра окончена'
            send_to_all(str_answer)
            mode = 'регистрация'
            continue

        # передать ход при неправильном ответе
        player_num += 1
        if player_num >= len(play_table): player_num = 0

        ip_el = play_table[player_num][1]
        res = send_answ(ip_el, '\n Ваш ход')

    elif command == 'restart':
        if mode == 'игра':
            str_answer = 'во время игры restart запрещен'
            res = send_answ(ip_client, str_answer)
            continue

        str_answer = 'таблица игроков очищена. \n Перерегистрируйтесь'
        send_to_all(str_answer)

        # очистить таблицу игроков и массив ходов
        play_table = []
        clear_cells()
        player_num = 0

        continue



    else:                                           # недопустимая команда
        str_answer = '\n ошибочная команда серверу '
        res = send_answ(ip_client, str_answer)






