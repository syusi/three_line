import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox
import inspect
import random

# ゲームに必要なパラメーター
EMPTY = -9999

## 今のターン、0だと○、1は×
nowTurn = 0
## [[EMPTY]*3]*3だと同じリストを参照してしまう
board_status = [[EMPTY]*3,[EMPTY]*3,[EMPTY]*3]

## CPUモードにするか
CPU_MODE = True

#表示に必要なもの
##各盤面
cells = []
##テキストボックス
text_box = None

# 強化学習に必要な奴
## テーブルの初期化、期待値なので0-1?サイズは各マスに○×無しの3通りが8個、その時にどこに置くかで8個
qtable = np.random.randint(low = 0,high = 1,size=(3**8,8))


def init_figure():
    fig = plt.figure()
    for y in range(3):
        for x in range(3):
            cell = fig.add_subplot(3, 3, xy_to_row(x,y)+1)
            cell.tick_params(labelbottom=False,labelleft=False)
            cell.tick_params(bottom=False,left=False)
            viewText = (xy_to_row(x,y)+1)
            cell.text(0.35,0.35,viewText,size = 40,color="blue")
            cells.append(cell)
    axbox = plt.axes([0.4, 0.01, 0.4, 0.075])
    global text_box
    text_box = TextBox(axbox, 'Trun ○ input number!')
    text_box.on_submit(submit)
    # print(type(text_box))
    # for x in inspect.getmembers(text_box):
    #     print(x)
    plt.show()

def submit(text):
    global nowTurn
    input_num = 0
    try:
        input_num = int(text)-1
    except ValueError as e:
        print("error input")
        return
    
    pos_x,pos_y = row_to_xy(input_num)
    # validation check
    if input_num < 0 or input_num >= 9:
        print("out of range input:",input_num+1)
        return
    if board_status[pos_y][pos_x] != EMPTY:
        print("already put mark:",input_num)
        return
    
    put_piece(input_num)
    if game_condition(input_num):
        return
    
    #ターン変更
    nowTurn = (nowTurn+1)%2
    #CPUモードならとりあえず敵に置かせる。
    if CPU_MODE:
        print('enemy')
        enemy_put = random_enemy(board_status)
        put_piece(enemy_put)
        if game_condition(enemy_put):
            return
        #元のターンに戻す
        nowTurn = (nowTurn+1)%2
        print(board_status)
    # そうではないならユーザーの次のターンに変更
    else:
        turn_chara = '○' if nowTurn==0 else '×'
        text_box.label.set_text('Trun '+turn_chara+' input number!')
    text_box.set_val("")
    plt.draw()

def put_board(put_pos):
    pos_x,pos_y = row_to_xy(put_pos)
    if board_status[pos_y][pos_x] != EMPTY:
        return False
    board_status[pos_y][pos_x] = nowTurn
    return True

def put_piece(put_pos):
    # boardの更新
    if put_board(put_pos) == False:
        return False
    turn_chara = '○' if nowTurn==0 else '×'
    cell = cells[put_pos]
    cell.cla()
    cell.text(0.35,0.35,turn_chara,size = 40,color="blue")
    return True


# 続けるならFalse、勝敗が決まればTrue
def game_condition(put_num):
    turn_chara = '○' if nowTurn==0 else '×'
    # 勝敗の判定
    if WinCondition(board_status,put_num):
        print("win !"+turn_chara)
        plt.draw()
        return True
    
    if drowCondition(put_num):
        print("Draw...")
        plt.draw()
        return True

    return False

def row_to_xy(pos):
    x = int(pos%3)
    y = int(pos/3)
    return x,y

def xy_to_row(x,y):
    return y*3+x


# 学習用変数
episord = 1000

def learn(learn, other):
    win=0
    lose=0
    drow=0
    for epi in range(episord):
        #最初の手を決める
        state = dizitize_state(board_status)
        action = np.argmax(qtable[state])
        while True:
            print('first')
            reward = 0
            can_put = put_board(action)
            if can_put == False:
                reward = -50
            action,state = q_enemy(board_status,state,action,reward,episord)
            if game_condition(enemy_put):
                continue


def random_enemy(board_status):

    left_cell = []
    
    for y in range(len(board_status)):
        for x in range(len(board_status[y])):
            if board_status[y][x] == EMPTY:
                left_cell.append(xy_to_row(x,y))
    
    index = random.randint(0,len(left_cell)-1)

    return left_cell[index]

def dizitize_state(board_status):
    # 無し0、○1、×2
    sum = 0
    for index in range(9):
        x,y = row_to_xy(index)
        put = 0 if board_status[y][x] == EMPTY else board_status[y][x] + 1
        print('num:',put * 3 ** index)
        sum += put * 3 ** index
    return sum

def q_enemy(board_status,state,action,reward,epsode):
    
    # 今の状態を把握
    next_state = dizitize_state(board_status)

    # 次のアクションを決める
    ## 一番良いやつ
    next_action = np.argmax(board_status[next_state])

    alpha = 0.2
    gamma = 0.99
    qtable[state,action] = (1 - alpha) * qtable[state,action] +\
         alpha *  (reward + gamma * qtable[next_state,next_action])

    return next_action,next_state
    

# def show_play(now_area):

#     #領域(window)取得
#     fig = plt.figure()
#     #領域追加
#     for y in range(3):
#         for x in range(3):
#             cell = fig.add_subplot(3, 3, xy_to_row(x,y)+1)
#             cell.tick_params(labelbottom=False,labelleft=False)
#             cell.tick_params(bottom=False,left=False)
#             posnum = now_area[y][x]
#             viewText = "○" if posnum == 0 else "×" if posnum == 1 else (xy_to_row(x,y)+1)
#             cell.text(0.35,0.35,viewText,size = 40,color="blue")
#             cell.text(0.35,0.35,viewText,size = 20,color="red")
#     axbox = plt.axes([0.4, 0.04, 0.4, 0.075])
#     text_box = TextBox(axbox, 'input number!')
#     text_box.on_submit(submit)
#     plt.show()


def WinCondition(board_status,put_pos):
    pos_x,pos_y = row_to_xy(put_pos)
    color = board_status[pos_y][pos_x]

    ren = 0
    for y_diff in range(-1,2):
        for x_diff in range(-1,2):
            if x_diff == 0 and y_diff == 0:
                break

            ren = putricurution(board_status,(x_diff,y_diff),pos_x,pos_y,color,0)
            if ren >= 3:
                return True
    
    return False

def drowCondition(put_pos):
    for y in range(len(board_status)):
        if EMPTY in board_status[y]:
            break 
    else:
        print("Draw...")
        plt.draw()
        return True
    return False

def putricurution(board_status,vector,pos_x,pos_y,color,ren):
    if pos_x >= 0 and pos_x < 3:
        if pos_y >= 0 and pos_y < 3:
            if board_status[pos_y][pos_x] == color:
                pos_x += vector[0]
                pos_y += vector[1]
                ren = putricurution(board_status,vector,pos_x,pos_y,color,ren+1)

    return ren

# def gameLoop():
#     nowTurn = 0
#     while True:
#         show_play(board_status)
#         turn_chara = '○' if nowTurn==0 else '×'
#         put_pos = int(input("turn :"+turn_chara+" input!!>>"))-1
#         put_x,put_y = row_to_xy(put_pos)
#         if put_pos < 9 and put_pos >= 0 and board_status[put_y][put_x] < 0:
#             board_status[put_y][put_x] = nowTurn

#         else:
#             print("error input")
#             continue 
        
#         if WinCondition(board_status,put_pos):
#             print("win !"+turn_chara)
#             break
        
#         for y in range(len(board_status)):
#             if EMPTY in board_status[y]:
#                break 
#         else:
#             print("Draw...")
#             break

#         nowTurn = (nowTurn+1)%2
#     print("GAMSE SET!!")

# #gameLoop()
init_figure()