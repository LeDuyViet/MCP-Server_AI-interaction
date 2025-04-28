# -*- coding: utf-8 -*-
"""
Định nghĩa MCTS Engine cốt lõi.
"""

import time
import logging
import collections
import copy
from typing import Dict, List, Any, Optional, Callable

# Import MCTSNode từ cùng thư mục
from .node import MCTSNode

# Kiểu dữ liệu cho các hàm logic (định nghĩa lại ở đây để module độc lập hơn)
GetLegalActionsFunc = Callable[[Any], List[Any]]
ApplyActionFunc = Callable[[Any, Any], Any]
IsTerminalStateFunc = Callable[[Any], bool]
SimulationPolicyFunc = Callable[[Any], float] # Nhận state, trả về reward cuối cùng của rollout

def run_mcts(
    initial_state: Any,
    get_legal_actions_func: GetLegalActionsFunc,
    apply_action_func: ApplyActionFunc,
    is_terminal_func: IsTerminalStateFunc,
    simulation_policy_func: SimulationPolicyFunc,
    num_iterations: int = 1000,
    exploration_constant: float = 1.414,
    time_limit_seconds: Optional[float] = None,
    debug_simulation_limit: Optional[int] = None
) -> Dict[str, Any]:
    """
    Thực thi thuật toán Monte Carlo Tree Search cốt lõi.

    Args:
        initial_state: Trạng thái bắt đầu của vấn đề.
        get_legal_actions_func: Hàm nhận state, trả về list các action hợp lệ.
        apply_action_func: Hàm nhận state và action, trả về state mới.
        is_terminal_func: Hàm nhận state, trả về True nếu là trạng thái kết thúc.
        simulation_policy_func: Hàm nhận state, chạy mô phỏng đến hết và trả về phần thưởng.
        num_iterations: Số lượt lặp tối đa để chạy MCTS.
        exploration_constant: Hệ số C trong công thức UCB1.
        time_limit_seconds: Giới hạn thời gian chạy tối đa (ghi đè num_iterations nếu có).
        debug_simulation_limit: Số lượng mô phỏng gần nhất để lưu log (nếu được cung cấp).

    Returns:
        Dictionary chứa kết quả và thống kê MCTS, bao gồm:
            - best_action: Hành động tốt nhất được tìm thấy từ gốc.
            - best_action_score: Điểm số của hành động tốt nhất (ví dụ: reward trung bình).
            - score_type: Loại điểm số được sử dụng (ví dụ: 'average_reward', 'visits').
            - iterations_completed: Số lượt lặp MCTS thực sự hoàn thành.
            - time_elapsed_seconds: Tổng thời gian chạy.
            - root_node_visits: Tổng số lượt thăm nút gốc.
            - error: Chuỗi lỗi nếu có lỗi nghiêm trọng xảy ra, None nếu thành công.
            - simulation_debug_log: Danh sách log của các mô phỏng gần nhất (nếu debug_simulation_limit được bật).
    """

    start_time = time.time()
    root_node: Optional[MCTSNode] = None

    # --- Kết quả mặc định phòng trường hợp lỗi sớm ---
    default_result = {
        "best_action": None,
        "best_action_score": -float('inf'),
        "score_type": None,
        "iterations_completed": 0,
        "time_elapsed_seconds": 0.0,
        "root_node_visits": 0,
        "error": "Initialization failed before MCTS loop."
    }

    # Khởi tạo cấu trúc lưu log debug simulation nếu cần
    simulation_debug_log: Optional[collections.deque] = None
    if debug_simulation_limit is not None and debug_simulation_limit > 0:
        simulation_debug_log = collections.deque(maxlen=debug_simulation_limit)

    try:
        # --- 1. Khởi tạo Node Gốc ---
        logging.debug(f"Initializing MCTS with state: {str(initial_state)[:200]}...")
        initial_legal_actions = get_legal_actions_func(initial_state)
        is_initial_terminal = is_terminal_func(initial_state)

        if is_initial_terminal:
            logging.warning("Initial state is already terminal. MCTS will likely provide limited value.")
            # MCTS vẫn có thể chạy để đánh giá phần thưởng của trạng thái này nếu cần,
            # nhưng sẽ không khám phá thêm.

        root_node = MCTSNode(
            state=initial_state,
            untried_actions=initial_legal_actions,
            is_terminal=is_initial_terminal
        )
        logging.debug(f"Root node created: {root_node}")

        iterations_done = 0
        # --- 2. Vòng lặp MCTS Chính ---
        while True:
            # 2.1. Kiểm tra Điều kiện Dừng
            current_time = time.time()
            time_elapsed = current_time - start_time
            if time_limit_seconds is not None and time_elapsed > time_limit_seconds:
                logging.info(f"MCTS stopping due to time limit ({time_limit_seconds:.2f}s).")
                break
            if iterations_done >= num_iterations:
                logging.info(f"MCTS stopping after reaching iteration limit ({num_iterations}).")
                break

            # --- Bắt đầu một lượt lặp MCTS ---
            node = root_node # Bắt đầu từ gốc

            try:
                # 2.2. Selection: Đi xuống cây dùng UCB1 cho đến khi gặp nút chưa mở rộng hoặc nút lá
                # selection_path_debug = [node] # Bỏ comment nếu cần debug đường đi
                while not node.is_terminal and node.is_fully_expanded():
                    if not node.children:
                        logging.warning(f"Selection reached a non-terminal, fully expanded node with no children: {node}. Treating as leaf.")
                        break
                    node = node.best_child(exploration_constant)
                    # selection_path_debug.append(node)

                # 2.3. Expansion: Nếu nút không phải terminal và chưa mở rộng hết, tạo một nút con mới
                if not node.is_terminal and not node.is_fully_expanded():
                    action_to_expand = node.untried_actions.pop(0)
                    try:
                        new_state = apply_action_func(node.state, action_to_expand)
                        is_new_terminal = is_terminal_func(new_state)
                        new_legal_actions = []
                        if not is_new_terminal:
                            new_legal_actions = get_legal_actions_func(new_state)

                        node = node.add_child(
                            child_state=new_state,
                            action=action_to_expand,
                            untried_actions=new_legal_actions,
                            is_terminal=is_new_terminal
                        )
                    except Exception as e_expand_inner:
                        logging.error(f"Error during expansion step (action: {action_to_expand}): {e_expand_inner}", exc_info=True)
                        continue # Bỏ qua iteration này để tránh backprop sai

                # 2.4. Simulation (Rollout): Từ nút hiện tại (lá hoặc mới mở rộng), mô phỏng đến hết
                simulation_reward = 0.0 # Phần thưởng mặc định nếu mô phỏng lỗi
                try:
                    simulation_reward = simulation_policy_func(node.state)
                except Exception as e_sim:
                    logging.error(f"Error during simulation step from state {node.state}: {e_sim}", exc_info=True)
                    simulation_reward = 0.0 # Giữ reward là 0.0 nếu lỗi

                # Ghi log debug simulation nếu được bật
                if simulation_debug_log is not None:
                    try:
                        # Lưu trạng thái bắt đầu và phần thưởng
                        # Cần deepcopy nếu state là mutable để tránh bị thay đổi sau này
                        log_entry = {
                            "start_state": copy.deepcopy(node.state), # Deepcopy để đảm bảo
                            "reward": simulation_reward
                        }
                        simulation_debug_log.append(log_entry)
                    except Exception as e_debug_log:
                        # Không nên để lỗi log debug làm dừng MCTS
                        logging.warning(f"Could not log simulation debug info: {e_debug_log}")

                # 2.5. Backpropagation: Cập nhật visits và reward ngược lên cây
                backprop_node = node
                while backprop_node is not None:
                    backprop_node.visits += 1
                    backprop_node.reward += simulation_reward
                    backprop_node = backprop_node.parent

            except Exception as e_inner_loop:
                logging.error(f"Error within MCTS iteration {iterations_done}: {e_inner_loop}", exc_info=True)
                # Cố gắng tiếp tục iteration tiếp theo

            iterations_done += 1
        # --- Kết thúc Vòng lặp MCTS Chính ---

        # --- 3. Trả về Kết quả ---
        elapsed_time = time.time() - start_time
        logging.info(f"MCTS loop finished after {iterations_done} iterations in {elapsed_time:.3f}s.")

        best_action_avg_reward = None
        best_score_avg_reward = -float('inf')
        best_action_visits = None
        best_score_visits = -1

        if root_node and root_node.children:
            logging.debug("Selecting best action from root node children:")
            visited_children = [child for child in root_node.children if child.visits > 0]

            if visited_children:
                score_type = "average_reward"
                try:
                    best_child = max(visited_children, key=lambda c: c.reward / c.visits)
                    best_action_avg_reward = best_child.action
                    best_score_avg_reward = best_child.reward / best_child.visits
                    logging.debug(f"  - Best child (avg reward): {best_child}")

                    # Tìm thêm hành động tốt nhất theo visits
                    best_child_visits = max(visited_children, key=lambda c: c.visits)
                    best_action_visits = best_child_visits.action
                    best_score_visits = best_child_visits.visits
                    logging.debug(f"  - Best child (visits): {best_child_visits}")

                except Exception as e_best_avg:
                    logging.error(f"Error selecting best child by average reward: {e_best_avg}. Falling back to visits.", exc_info=True)
                    score_type = "visits (fallback)"
                    best_child = max(root_node.children, key=lambda c: c.visits)
                    best_action_avg_reward = best_child.action # Vẫn gán giá trị fallback
                    best_score_avg_reward = float(best_child.visits) # Vẫn gán giá trị fallback
                    best_action_visits = best_child.action # Gán cả cho visits
                    best_score_visits = best_child.visits # Gán cả cho visits
                    logging.debug(f"  - Best child (visits fallback): {best_child}")
            else:
                score_type = "no_visits"
                best_action_avg_reward = None
                best_score_avg_reward = 0.0
                best_action_visits = None
                best_score_visits = 0
                logging.warning("No children of the root node were visited. Cannot determine best action.")

            final_result = {
                "best_action": best_action_avg_reward, # Mặc định trả về theo avg reward
                "best_action_score": best_score_avg_reward,
                "best_action_by_visits": best_action_visits, # Hành động tốt nhất theo lượt thăm
                "best_action_visits_score": best_score_visits, # Số lượt thăm của hành động đó
                "score_type": score_type,
                "iterations_completed": iterations_done,
                "time_elapsed_seconds": elapsed_time,
                "root_node_visits": root_node.visits if root_node else 0,
                "error": None,
                "simulation_debug_log": list(simulation_debug_log) if simulation_debug_log is not None else None
            }
            logging.info(f"MCTS Result: {final_result}")
            return final_result

    except Exception as e_outer:
        error_msg = f"Critical error during MCTS execution: {str(e_outer)}"
        logging.error(error_msg, exc_info=True)
        default_result["error"] = error_msg
        if root_node:
            default_result["root_node_visits"] = root_node.visits
        default_result["time_elapsed_seconds"] = time.time() - start_time
        default_result["simulation_debug_log"] = list(simulation_debug_log) if simulation_debug_log is not None else None
        return default_result 