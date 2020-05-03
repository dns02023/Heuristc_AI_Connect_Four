from board import Board
from heuristic import heuristic
import heuristic as heu


def play(board):
    if input("먼저 두시겠습니까?\n 선공:0, 후공:1 을 입력해주세요.\n") == '0':
        print("선공입니다.")
        player_turn = True
    else:
        print("후공입니다.")
        player_turn = False
    while True:
        if player_turn:
            board.print_board()
            success = board.place(int(input("열을 입력해주세요(1~7)"))-1, player_turn)
            if not success:
                print("잘못 두셨습니다. 다시 두세요.")
                continue
        else:
            board.print_board()
            print("계산중입니다...")
            column = heuristic(board, not player_turn)
            board.place(column, player_turn)
        if board.check_game():
            board.print_board()
            if player_turn:
                print("당신이 이겼습니다.")
            else:
                print("인공지능이 이겼습니다.")
            break
        # 턴 변경
        player_turn = not player_turn
        heu.first_turn = False


def main():
    board = Board()
    play(board)


if __name__ == '__main__':
    main()
