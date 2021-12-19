#== client_tic_tac_toe.py     R.R.Sonkin 10.02.2020
##-- клиент для сетевого варианта игры "Крестики-Нолики"
##-- часть 0 - интерфейс


#== подключить библиотеки
from tkinter import *
from tkinter import ttk

# библиотеки для связи
import threading
from time import *
from socket import *


#== параметры и функции

#== вывести строку в текстовое поле
def disp_msg(msg):
    txt_serv.insert(END, msg + '\n')
    txt_serv.yview(END)


# Параметры и функции работы с сетью
server_address = ('25.39.54.57', 5403)
# server_address = ('192.168.0.101', 5401)
mode = 'disconnect'                 # режим работы клиента
main_tau = 20                       # время цикла главной программы в мс
lst_in = []                         # очередь для принятых сообщений
busy_in = 0                         # признак занятости очереди
ch_name = {'z': 'нолик', 'k': 'крестик'}        # имя значка

# Отправить сообщение по TCP
def send_msg(msg):
    client = socket(AF_INET, SOCK_STREAM)
    bin_msg = bytes(msg, 'UTF-8')
    try:
        client.connect(server_address)
        client.sendall(bin_msg)
        # res = 'OK'
        res = ''
    except:
        # res = 'not connected'
        res = 'Сервер выключен'
    finally:
        client.close()
    return res


# Аккуратно записать сообщ в очередь сообщений
def put_msg(msg):
    global lst_in
    global busy_in
    while busy_in:
        sleep(0.001)
    busy_in = 1
    lst_in.append(msg)
    busy_in = 0


# Функция приема сообщ. (один пакет за раз)
def work_in():
    global lst_in
    global busy_in
    locserv_addr = ('', 5402)
    lock_sock = socket(AF_INET, SOCK_STREAM)
    lock_sock.bind(locserv_addr)                # связать с номером порта локального с
    lock_sock.listen(5)                         # не более 5 ожидающих запросов

    while True:
        # ждать и получить сообщ. от игрового сервера...
        # print('ready')
        connection, address = lock_sock.accept()
        # print('connected by', address)
        bin_data = connection.recv(1024)
        str_data = bin_data.decode('utf-8')
        # print(str_data)
        connection.close()

        # ...записать его в очередь сообщ...
        put_msg(str_data)

        # ...задержка потока
        sleep(0.001)


# поток приема сообщений
tr_in = threading.Thread(target=work_in)
tr_in.daemon = True
tr_in.start()


#== создание интерфейса
root = Tk()
root.title('Tic_Tac_Toe')
frm_color = '#ffd800'                   #-- цвет форма
btn_width = 20                          #-- ширина кнопок


# Новая левая панель                                        ////0////
pn_game = Frame(root, bg='cyan')
pn_game.pack(side='left')

# параметры поля                                        ////0////
cell_size = 24
x_count = 22
y_count = 22

# сформировать канву                                        ////0////
canv_width = x_count * cell_size
canv_height = y_count * cell_size

canv = Canvas(pn_game, width=canv_width, height=canv_height)
canv.pack()

# очистка канвы
def init_canv():
    canv['bg'] = 'black'
    canv.delete(ALL)
    canv.create_rectangle(0, 0, canv_width, canv_height)
    # клетки
    for x_num in range(x_count):
        for y_num in range(y_count):
            canv.create_line(0, y_num*cell_size, canv_width, y_num*cell_size)
            canv.create_line(x_num*cell_size, 0, x_num*cell_size, canv_height)


# вывести на канву значек (крести при ch='k', или нолик при ch=='z')
def draw_canv(row, col, ch):
    x_left = col * cell_size + 3; x_right = x_left + cell_size - 6
    y_top = row * cell_size + 3; y_bottom = y_top + cell_size - 6
    if ch == 'z':
        canv.create_oval(x_left, y_top, x_right, y_bottom, outline='#050', )
    elif ch == 'k':
        canv.create_line(x_left, y_top, x_right, y_bottom, fill='blue', )
        canv.create_line(x_left, y_bottom, x_right, y_top, fill='blue', )


# привязать к канве отправку хода
def send_step(event):
    # определить координаты
    col = event.x // cell_size
    row = event.y // cell_size
    # сформировать и отправить сообщение о ходе
    res = send_msg('step|' + str(row) + ',' + str(col))
    disp_msg(res)


canv.bind('<Button-1>', send_step)


# правая панель с элементами управления
pnl_right = Frame(root, width=150, bg=frm_color)
pnl_right.pack(side='right', fill='both', expand=1)

lbl_head = Label(pnl_right, text='Сетевая игра \n "Крестики Нолики"', bg=frm_color, fg='white')
lbl_head.grid(row=0, column=0, sticky=W)

lbl_empty = Label(pnl_right, text='   ', bg=frm_color, fg='white')
lbl_empty.grid(row=1, column=0, sticky=W, padx=10)

lbl_mode = Label(pnl_right, text='Незарегистрирован', bg=frm_color, fg='white')
lbl_mode.grid(row=2, column=0, sticky=W, padx=10)


# Кнопка регистрации
def fnc_registr():
    name = edt_strout.get().strip()
    if len(name) < 1:
        put_msg('регистрация невозможна \n введите имя в строке ввода.')
        return
    str_out = 'registr|' + name
    res = send_msg(str_out)
    # print(res)
    disp_msg(res)


btn_reg = ttk.Button(pnl_right, text='Зарегистрировать', width=btn_width, command=fnc_registr)
btn_reg.grid(row=3, column=0, sticky=E+W, padx=5, pady=5)


# Кнопка информации
def fnc_info():
    str_out = 'get_info'
    res = send_msg(str_out)
    # print(res)
    disp_msg(res)


btn_info = ttk.Button(pnl_right, text='Информация', width=btn_width, command=fnc_info)
btn_info.grid(row=4, column=0, sticky=E+N, padx=5, pady=5)


# метка и поле отправляемой строки
# lbl_step = Label(pnl_right, text='Ваше число:', bg=frm_color, fg='white')     # ////0////
lbl_step = Label(pnl_right, text='Ваше имя:', bg=frm_color, fg='white')
lbl_step.grid(row=7, column=0, sticky=W, padx=10)


'''                                                     # ////0////
def fnc_step(event):
    str_out = edt_strout.get()
    if not str_out.isnumeric():
        put_msg('некорректный ход \n должны быть только цифры')
        return
    res = send_msg('step|' + str_out)
    # print(res)
    disp_msg(res)
'''


edt_strout = Entry(pnl_right, width=btn_width)
edt_strout.grid(row=8, column=0, padx=10)
# edt_strout.bind('<Return>', fnc_step)                 # ////0////


'''                                                 # ////0////
# кнопка отправки хода
btn_step = ttk.Button(pnl_right, text='Отправить', width=btn_width)
btn_step.grid(row=9, column=0, sticky=E+N, padx=5, pady=5)
btn_step.bind('<Button-1>', fnc_step)
'''


# кнопка очистки таблицы игроков                 # ////0////
def fnc_restart(event):
    str_out = 'restart'
    res = send_msg(str_out)
    disp_msg(res)

btn_restart = ttk.Button(pnl_right, text='Новая игра', width=btn_width)
btn_restart.grid(row=9, column=0, sticky=E+N, padx=5, pady=5)
btn_restart.bind('<Button-1>', fnc_restart)


#-- панель с сообщениями от сервера
pnl_bottom = Frame(pnl_right, bg=frm_color)
# pnl_bottom.pack(side='left', fill='y')
pnl_bottom.grid(row=10, column=0, sticky=E+N, padx=5, pady=5)

txt_serv = Text(pnl_bottom, width=30, height=20, wrap='word', )
txt_serv.pack(side='left', fill='y')

sbr_serv = Scrollbar(pnl_bottom, orient='vertical')
sbr_serv.pack(side='right', fill='y')

sbr_serv.config(command=txt_serv.yview)
txt_serv.config(yscrollcommand=sbr_serv.set, wrap='word')


# главная функция, запускаемая в цикле
def main():
    global lst_in
    global busy_in
    global mode
    global x_count                      # ////0////
    global y_count

    # Проверить и вывести данные из очереди строк
    if len(lst_in) > 0:
        while busy_in:
            sleep(0.001)
        busy_in = 1
        str_in = lst_in.pop(0)
        busy_in = 0

        disp_msg(str_in)

        # Обработать регистрацию
        lst_loc = str_in.split('|')
        if lst_loc[0] == 'registr':
            lbl_mode['text'] = lst_loc[1] + ' ( ' + ch_name[lst_loc[2]] + ' )'

        # Обработать ход                ////0////
        if lst_loc[0] == 'step':
            row, col, ch = lst_loc[1].split(',')
            draw_canv(int(row), int(col), ch)

        # Обработать начало игры        ////0////
        if lst_loc[0] == 'begin':
            y_count = int(lst_loc[1])
            x_count = int(lst_loc[2])
            init_canv()

        # Обработать окончание игры     ////0////
        if lst_loc[0] == 'end':
            canv['bg'] = '#009900'

    # Перезапуститься после задержки
    root.after(main_tau, main)


# запустить главную функцию
# очистить канву
canv['bg'] = 'white'
canv.delete('all')
canv.create_rectangle(0, 0, canv_width, canv_height)

main()

root.mainloop()
