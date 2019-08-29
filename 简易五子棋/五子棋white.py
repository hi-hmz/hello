# 思路
# 1. 画两个棋盘
# 2. 点哪里就在哪里画棋子
# 3. 一方下完等待另一方落子
# 4. 判断输赢

from tkinter import *
from tkinter.messagebox import *
from json import *
from socket import *
from threading import Thread


# 画棋盘横线
def drawline():
    for i in range(1, 17):
        canvas1.create_line(0, 40 * i, 600, 40 * i)  # 画横线
        canvas1.create_line(40 * i, 0, 40 * i, 640)  # 画竖线


# 画棋子
def draw_chess(event, x1, y1, x2, y2, i, j):
    canvas1.create_oval(x1, y1, x2, y2, fill='white')
    canvas1['state'] = 'disabled'
    game_map[i][j] = 'white'
    judge_winning_losing(i, j, x1, y1, x2, y2)
    list1 = [x1, y1, x2, y2, i, j]
    message = dumps(list1)
    send_coordinate(message)
    label1 = Label(win, text='请黑方走棋', fg='red', font=('', 20)).place(x=80, y=620)


# 函数转接器
def draw_chess_adaptor(fun, *args):
    return lambda event, fun=fun, args=args: fun(event, *args)


# 画小圆,用于点击时落子
def draw_circle():
    x = 1
    for i in range(0, 14):
        for j in range(0, 14):
            canvas1.create_oval(35 + 40 * j, 35 + 40 * i, 45 + 40 * j, 45 + 40 * i, fill='#eeb766', tags='r' + str(x))
            canvas1.tag_bind('r' + str(x), '<Button-1>',
                             draw_chess_adaptor(draw_chess, 20 + 40 * j, 20 + 40 * i, 60 + 40 * j, 60 + 40 * i, i, j))
            x += 1


# 接收传来的信息
def receive_coordinate():
    while True:
        res, send_address = udp_client_socket.recvfrom(1024)
        res = res.decode('utf8')
        if res == 'exit':
            break
        rres = loads(res)
        canvas1['state'] = 'normal'
        canvas1.create_oval(rres[0], rres[1], rres[2], rres[3], fill='black')
        if len(rres) == 5:
            showinfo(title='提示', message='黑方胜利,游戏结束')
            win.destroy()
        game_map[rres[4]][rres[5]] = 'black'
        label1 = Label(win, text='请白方走棋', fg='red', font=('', 20)).place(x=80, y=620)
    udp_client_socket.close()
    showinfo(title='提示', message='对方退出游戏,你获得胜利')
    win.destroy()


# 发送消息
def send_coordinate(message):
    udp_client_socket.sendto(message.encode('utf8'), ('192.168.1.8', 3766))


# 胜利后关闭窗口
def close_window(x1, y1, x2, y2):
    showinfo(title='提示', message='白方胜利,游戏结束')
    hint = '你输了'
    list1 = [x1, y1, x2, y2, hint]
    message = dumps(list1)
    send_coordinate(message)
    # win.destroy()
    os._exit(1)


# 判断输赢
def judge_winning_losing(i, j, x1, y1, x2, y2):
    # 横向判断
    count = 1
    for x in range(1, 6):
        if j + x > 13:
            break
        else:
            if game_map[i][j] == game_map[i][j + x]:
                count += 1
                if count >= 5:
                    close_window(x1, y1, x2, y2)
    for x in range(1, 6):
        if j - x < 0:
            break
        else:
            if game_map[i][j] == game_map[i][j - x]:
                count += 1
                if count >= 5:
                    close_window(x1, y1, x2, y2)
    # 纵向判断
    count = 1
    for x in range(1, 6):
        if i + x > 13:
            break
        else:
            if game_map[i][j] == game_map[i + x][j]:
                count += 1
                if count >= 5:
                    close_window(x1, y1, x2, y2)
    for x in range(1, 6):
        if i - x < 0:
            break
        else:
            if game_map[i][j] == game_map[i - x][j]:
                count += 1
                if count >= 5:
                    close_window(x1, y1, x2, y2)
    # 斜向判断
    count = 1
    for x in range(1, 6):
        if i + x > 13 or j + x > 13:
            break
        else:
            if game_map[i][j] == game_map[i + x][j + x]:
                count += 1
                if count >= 5:
                    close_window(x1, y1, x2, y2)
    for x in range(1, 6):
        if i - x < 0 or j - x < 0:
            break
        else:
            if game_map[i][j] == game_map[i - x][j - x]:
                count += 1
                if count >= 5:
                    close_window(x1, y1, x2, y2)
    # 反斜判断
    count = 1
    for x in range(1, 6):
        if i + x > 13 or j - x < 0:
            break
        else:
            if game_map[i][j] == game_map[i + x][j - x]:
                count += 1
                if count >= 5:
                    close_window(x1, y1, x2, y2)
    for x in range(1, 6):
        if i - x < 0 or j + x > 13:
            break
        else:
            if game_map[i][j] == game_map[i - x][j + x]:
                count += 1
                if count >= 5:
                    close_window(x1, y1, x2, y2)


# 创建线程用来接收消息
def start_new_thread():
    t1 = Thread(target=receive_coordinate)
    t1.setDaemon(True)
    t1.start()


if __name__ == '__main__':
    # 创建游戏地图列表
    game_map = [['' for i in range(14)] for j in range(14)]
    # 创建套接字
    udp_client_socket = socket(AF_INET, SOCK_DGRAM)
    udp_client_socket.bind(('192.168.1.8', 3765))
    #  生成对弈窗口
    win = Tk()
    win.title('五子棋白')
    win.geometry('600x680')
    win.resizable(0, 0)
    canvas1 = Canvas(win, width=600, height=600, bg='#eeb766')
    canvas1.pack()
    drawline()
    draw_circle()
    canvas1['state'] = 'disabled'
    label1 = Label(win, text='请黑方走棋', fg='red', font=('', 20)).place(x=80, y=620)
    button1 = Button(win, text='关闭游戏', font=('', 12), command=lambda: [send_coordinate('exit'),
                                                                       win.destroy()]).place(x=350, y=625)
    start_new_thread()
    win.protocol("WM_DELETE_WINDOW", lambda: showinfo(message='退出请点击关闭游戏'))
    win.mainloop()
