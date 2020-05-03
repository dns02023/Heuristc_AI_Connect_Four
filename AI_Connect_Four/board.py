import numpy as np

board_row = 6
board_col = 7
BLANK = " "

class Board:
    # Board class를 초기화 하는 함수로, 6*7의 공란으로 채워진 numpy 행렬을 array란 변수에 저장합니다.
    def __init__(self, array=np.full((board_row, board_col), BLANK, dtype='U')):
        self.array = array
    
    # 열 번호와 player의 turn 여부를 입력받아서 board에 착수하는 함수입니다.
    # 착수한 자리의 [행 번호, 열 번호]를 반환하되, 두지 못하면 None을 반환합니다.
    def place(self, col, player_turn):
        content = "O" if player_turn else "X"   # 플레이어 턴이면 O를 두고, ai 턴이면 X를 둡니다.
        # 맨 아래 행에서 비어있는 칸인지 확인하며 하나씩 올라옵니다.
        # 빈 칸이면 그 곳에 착수하고, 0행까지 확인했는데 빈칸이 없다면 None을 반환합니다.
        row = board_row - 1
        while self.array[row][col] != BLANK:
            row = row - 1
            if row < 0:
                return None
        self.array[row][col] = content
        return [row, col]
    
    # 각 행별로 content를 출력해 전체 board를 출력하는 함수입니다.
    def print_board(self):
        print("  _   _   _   _   _   _   _ ")
        for row in range(board_row):
            self.print_line(row)
        print("----------------------------- ")
        print("  1   2   3   4   5   6   7 ")
    
    # 행 번호를 입력받아 그 행을 출력하는 함수입니다.
    def print_line(self, row):
        print("|", end=' ')
        for col in range(board_col):
            print(self.array[row][col], end=' ')
            print("|", end=' ')
        print()
    
    # heuristic 함수에서 연속된 돌을 세는 함수입니다.
    # row, col로 시작점을 입력받고, v_row, v_col으로 진행방향을 입력받습니다.
    # target은 어떤 플레이어의 돌을 셀지 정하는 파라미터로, O 또는 X를 입력받습니다.
    # 시작점에서 진행방향으로 진행하며 actual에 내가 둔 수를 1로 저장하고, 빈 칸 또는 상대의 수를 0으로 저장합니다.
    # 또한, 상대방의 수를 만나기 전까지 possible의 숫자를 하나씩 증가시키고, 만난다면 0으로 초기화합니다.
    # possible의 숫자가 4 이상이 되면 그 착수점을 포함해서 이전 4개의 actual 값을 모두 더합니다.
    # 이 더한 값들의 최댓값을 반환합니다.
    def new_check_line(self, row, col, v_row, v_col, target):
        step_row = 0
        step_col = 0
        possible = 0
        actual = []
        max_actual = 0
        while 0<=row+step_row<board_row and 0<=col+step_col<board_col:
            content = self.array[row+step_row][col+step_col]
            if content == target:
                possible = possible + 1
                actual.append(1)
            elif content == BLANK:
                possible = possible + 1
                actual.append(0)
            else:
                possible = 0
                actual.append(0)
            if possible >= 4:
                value = sum(actual[-4:])
                if max_actual < value:
                    max_actual = value
            # 만약 3개의 이어져있는 수가 있고 그 수의 양쪽 끝에 모두 다음 수에 둘 수 있다면 그 수 역시 승리하는 수와 동일합니다.
            if possible >= 5 and actual[-5:] == [0, 1, 1, 1, 0]:
                if row+step_row == board_row-1 or self.array[row+step_row+1][col+step_col] != BLANK:
                    if row+step_row-4*v_row == board_row-1 or self.array[row+step_row-4*v_row+1][col+step_col-4*v_col] != BLANK:
                        max_actual = 4
                        break
            step_row = step_row + v_row
            step_col = step_col + v_col
        return max_actual


    # 맨 처음 heuristic 함수를 짰을 때, 연속된 돌의 수를 계산하기 위한 함수였으나 지금은 효율성 때문에 경기가 끝났는지 여부만을 확인하는 함수입니다.
    # 시작점을 row, col로 받고 확인할 size를 받습니다. 이때, size의 기본값을 4입니다.
    # 또, 어떤 돌이 연속한지 content를 통해 정할 수 있습니다. content의 기본값은 None 입니다.
    def check_line(self, row, col, size=4, content=None):
        if not content:     # content가 입력되지 않았다면 시작점의 돌을 조사할 돌로 정합니다.
            content = self.array[row][col]
        if content == BLANK:    # content가 빈 칸이라면 [0, 0, 0, 0]을 return 합니다.
            return [0, 0, 0, 0]
        
        score = [0, 0, 0, 0]  # 각각의 score는 아래, 오른쪽, 오른쪽 아래, 오른쪽 위 방향의 연속된 돌의 수를 의미합니다.
        
        # 아래방향에서 실제로 연속된 돌이 몇개 있는지 체크하는 함수입니다.
        step_row = 0
        while row + step_row < board_row and step_row < size:
            target = self.array[row+step_row][col]
            if target == content:
                score[0] = score[0] + 1
            elif target == BLANK:
                pass
            else:
                score[0] = score[0] - 1
            step_row = step_row + 1
        if score[0] == 4:
            return score

        # 오른쪽 방향에서 실제로 연속된 돌이 몇개 있는지 체크하는 함수입니다.
        step_col = 0
        while col + step_col < board_col and step_col < size:
            target = self.array[row][col+step_col]
            if target == content:
                score[1] = score[1] + 1
            elif target == BLANK:
                pass
            else:
                score[1] = score[1] - 1
            step_col = step_col + 1
        if score[1] == 4:
            return score

        # 오른쪽 아래방향에서 실제로 연속된 돌이 몇개 있는지 체크하는 함수입니다.
        step_col = 0
        step_row = 0
        while row+step_row < board_row and col+step_col < board_col and step_row < size:
            target = self.array[row+step_row][col+step_col]
            if target == content:
                score[2] = score[2] + 1
            elif target == BLANK:
                pass
            else:
                score[2] = score[2] - 1
            step_row = step_row + 1
            step_col = step_col + 1
        if score[2] == 4:
            return score
        
        # 오른쪽 위방향에서 실제로 연속된 돌이 몇개 있는지 체크하는 함수입니다.
        step_col = 0
        step_row = 0
        while row + step_row >= 0 and col + step_col < board_col and step_col < size:
            target = self.array[row+step_row][col+step_col]
            if target == content:
                score[3] = score[3] + 1
            elif target == BLANK:
                pass
            else:
                score[3] = score[3] - 1
            step_row = step_row - 1
            step_col = step_col + 1
        return score

    # 게임이 끝났는지 여부를 체크하는 함수입니다.
    def check_game(self):
        # return self.is_terminal
        for row in range(board_row):
            for col in range(board_col):
                check = self.check_line(row, col)
                # 만약 위의 check_line 함수에 4가 포함되어있다면 게임이 끝났다는 True를 반환합니다.
                if 4 in check:
                    return True
        # 모든 점에 대하여 조사했을 때, 4가 없다면 False를 반환합니다.
        return False
