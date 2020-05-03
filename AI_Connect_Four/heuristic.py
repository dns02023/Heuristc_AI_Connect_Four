import copy
import time
from board import board_col, board_row

infinity = 999999999
first_turn = True


# heuristic 함수는 board class와 ai_turn인지 여부를 파라미터로 받아서
# minmax tree를 사용하여 선택해야될 경로를 반환합니다.
# 또한, 각 경로를 선택했을 때의 점수를 출력하고,
# 최적 경로를 선택했을 때 어떤 식으로 서로 수를 둘지 출력합니다.
#
# depth가 6일때부터 하나씩 늘려나가며 계산합니다.
# 한번의 minmax 트리의 계산이 끝날때까지의 시간을 저장하고, 그 결과에 7을 곱해서 다음 트리의 시간을 예상합니다.
# 현재 트리를 계산할 때 걸린 시간의 7배는 넘지 않을 거라는 가정이 필요합니다.
# 이 때, 지금까지 걸린 시간에 예상 시간을 더한 값이 120초를 넘어간다면 depth를 늘리지 않고 결과를 반환합니다.

def heuristic(board, ai_turn):
    total_time = 0
    depth_list = [6, 7, 8, 9 , 10, 11, 12, 13, 14]
    for depth in depth_list:
        start_time = time.time()
        best = minmax(board, depth, -infinity, infinity, ai_turn)
        path = best["path"]
        end_time = time.time()
        elapsed_time = end_time - start_time
        total_time = total_time + elapsed_time
        if total_time + 7 * elapsed_time > 120:
            break
    print("depth", depth, "에서 연산이 종료되었습니다.")
    print("경과시간은", total_time, "초입니다.")
    print("ai는 서로 번갈아가며", end=' ')
    for p in reversed(path):
        print(p+1, end='->')
    print("terminal 열에 둘 것이라고 예상했습니다.")
    win = None
    lose = []
    for b in best["all_score"].keys():
        print(b, "열 :", best["all_score"][b], end=' / ')
        if best["all_score"][b] < -900000:
            lose.append(b)
        elif best["all_score"][b] > 900000:
            if not win:
                win = b
            else:
                if best["all_score"][win] < best["all_score"][b]:
                    win = b
    print()
    for l in lose:
        print(l, "열에 두면 지는 수라고 ai가 판단해서 두지 않았습니다.")
    if win:
        print(win, "열에 두면 반드시 이기는 수라고 ai가 판단해서", win, "열에 두었습니다.")
    print("위 점수에서 점수가 가장 높은 경로 중 가장 먼저 탐색된", best["path"][-1]+1, "열이 선택되었습니다.")
    return path[-1]


# 연속된 돌의 갯수에 따른 가중치입니다.
cnt_based_score = {
    4:  999999,
    3:  50,
    2:  5,
    1:  1,
    0: 0
}

# scoring 함수는 board class를 파라미터로 받아 현재 board의 점수를 계산합니다.
# 이 때, ai 기준의 점수를 pos_score에 계산하고, 플레이어 기준의 점수를 neg_socre에 계산합니다.
# 마지막으로 pos_score에서 neg_score를 뺀 값을 반환합니다.
def scoring(board):
    pos_score = 0
    neg_score = 0

    for i in range(board_row):
        # ai 기준으로 오른쪽 방향으로 연속된 수를 체크합니다.
        cnt = board.new_check_line(i, 0, 0, 1, "X")
        pos_score = pos_score + cnt_based_score[cnt]
        # ai 기준으로 오른쪽 아래 방향으로 연속된 수를 체크합니다.
        cnt = board.new_check_line(i, 0, 1, 1, "X")
        pos_score = pos_score + cnt_based_score[cnt]
        # ai 기준으로 오른쪽 위 방향으로 연속된 수를 체크합니다.
        cnt = board.new_check_line(i, 0, -1, 1, "X")
        pos_score = pos_score + cnt_based_score[cnt]
        # 플레이어 기준으로 오른쪽 방향으로 연속된 수를 체크합니다.
        cnt = board.new_check_line(i, 0, 0, 1, "O")
        neg_score = neg_score + cnt_based_score[cnt]
        # 플레이어 기준으로 오른쪽 아래 방향으로 연속된 수를 체크합니다.
        cnt = board.new_check_line(i, 0, 1, 1, "O")
        neg_score = neg_score + cnt_based_score[cnt]
        # 플레이어 기준으로 오른쪽 위 방향으로 연속된 수를 체크합니다.
        cnt = board.new_check_line(i, 0, -1, 1, "O")
        neg_score = neg_score + cnt_based_score[cnt]

    for i in range(board_col):
        # ai 기준으로 아래 방향으로 연속된 수를 체크합니다.
        cnt = board.new_check_line(0, i, 1, 0, "X")
        pos_score = pos_score + cnt_based_score[cnt]
        # ai 기준으로 오른쪽 아래 방향으로 연속된 수를 체크합니다.
        # 이 때, 위의 코드와 겹치는 부분이 생기므로 i가 0일 때는 제외하고 체크합니다.
        if i != 0:
            cnt = board.new_check_line(0, i, 1, 1, "X")
            pos_score = pos_score + cnt_based_score[cnt]
        # ai 기준으로 오른쪽 위 방향으로 연속된 수를 체크합니다.
        # 이 때, 위의 코드와 겹치는 부분이 생기므로 i가 0일 때는 제외하고 체크합니다.
        if i != 0:
            cnt = board.new_check_line(5, i, -1, 1, "X")
            pos_score = pos_score + cnt_based_score[cnt]
        # 플레이어 기준으로 아래 방향으로 연속된 수를 체크합니다.
        cnt = board.new_check_line(0, i, 1, 0, "O")
        neg_score = neg_score + cnt_based_score[cnt]
        # 플레이어 기준으로 오른쪽 아래 방향으로 연속된 수를 체크합니다.
        # 이 때, 위의 코드와 겹치는 부분이 생기므로 i가 0일 때는 제외하고 체크합니다.
        if i != 0:
            cnt = board.new_check_line(0, i, 1, 1, "O")
            neg_score = neg_score + cnt_based_score[cnt]
        # 플레이어 기준으로 오른쪽 위 방향으로 연속된 수를 체크합니다.
        # 이 때, 위의 코드와 겹치는 부분이 생기므로 i가 0일 때는 제외하고 체크합니다.
        if i != 0:
            cnt = board.new_check_line(5, i, -1, 1, "O")
            neg_score = neg_score + cnt_based_score[cnt]
    return pos_score - neg_score


def minmax(board, depth, alpha, beta, ai_turn):
    path = []   # path는 지금까지의 경로를 저장할 list 입니다.
    score = {}  # score는 {경로 : 점수}로 구성될 dictionary 입니다.
    # depth가 0이거나 게임이 끝난다면 terminal node 이므로 점수를 반환합니다.
    # 이 때, 자식 노드가 없으므로 path에는 값을 추가하지 않습니다.
    if depth == 0 or board.check_game():
        return {"score": scoring(board), "path": path}

    # ai 기준 첫턴이라면 첫 탐색트리에서는 가운데 열을 빼고 탐색합니다.
    # space 순서는 우선적으로 탐색할 순서를 의미합니다.
    # 3은 가운데 열이므로 다른 terminal node와 점수가 같다면 가운데 열을 우선으로 선택하게 됩니다.
    # 마찬가지로 탐색 순서를 조정하여 중앙에 가까운 열들을 먼저 탐색하게 하였습니다.
    global first_turn
    if first_turn:
        space = [2, 4, 1, 5, 0, 6]
    else:
        space = [3, 2, 4, 1, 5, 0, 6]

    # value는 minmax를 구현하기 위한 값입니다. min일 경우 최솟값을, max일 경우 최댓값을 저장하게 됩니다.
    value = -infinity if ai_turn else infinity
    for i in space:
        next_board = copy.deepcopy(board)   # deepcopy로 동일한 board class를 새로 생성합니다.
        if next_board.place(i, not ai_turn):    # 현재 차례의 다음 수를 둘 수 있다면 아래 코드를 실행합니다.
                                                # 만약 둘 수 없을 경우, path에 추가가 되지 않습니다.
            tmp = minmax(next_board, depth-1, alpha, beta, not ai_turn) # depth를 하나 줄이고, turn을 바꿔서 minmax 함수를 재귀적으로 호출합니다.
            score[i+1] = tmp["score"]   # score 사전의 i+1번 key에 자식으로부터 return 받은 점수를 저장합니다.
            # ai의 turn 이라면 자식으로부터 return 받은 점수가 최댓값이라면 value와 path를 해당 자식의 점수와 경로로 갱신합니다.
            if ai_turn:
                if value < tmp["score"]:
                    value = tmp["score"]
                    path = tmp["path"]
                    path.append(i)
                # max node 이므로 alpha 값을 갱신합니다.
                alpha = max(alpha, value)
            # 플레이어의 turn 이라면 자식으로부터 return 받은 점수가 최솟값이라면 value와 path를 해당 자식의 점수와 경로로 갱신합니다.
            else:
                if value > tmp["score"]:
                    value = tmp["score"]
                    path = tmp["path"]
                    path.append(i)
                # min node 이므로 beta 값을 갱신합니다.
                beta = min(beta, value)
            # alpha가 beta보다 크다면 더 이상 탐색을 할 필요가 없으므로 탐색을 중지하고 값을 return 합니다.
            if alpha >= beta:
                break
    # score는 현재 node에서의 점수를, path는 현재 node까지의 경로를, all_score는 현재 node에서 바로 아래 자식들이 return한 점수입니다.
    return {"score": value, "path": path, "all_score": score}
