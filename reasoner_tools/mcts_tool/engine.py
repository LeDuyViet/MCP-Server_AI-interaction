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
GetStateHashFunc = Optional[Callable[[Any], Any]] # Hàm hash trạng thái, trả về giá trị hashable

def _format_dynamic_code_error(error: Exception, function_name: str) -> str:
    """
    Helper function to format dynamic code execution errors.
    """
    return f"Error executing {function_name}: {str(error)}"

def run_mcts(
    initial_state: Any,
    get_legal_actions_func: GetLegalActionsFunc,
    apply_action_func: ApplyActionFunc,
    is_terminal_func: IsTerminalStateFunc,
    simulation_policy_func: SimulationPolicyFunc,
    exploration_constant: float = 1.414,
    time_limit_seconds: Optional[float] = None,
    debug_simulation_limit: Optional[int] = None,
    enable_transposition_table: bool = False,
    get_state_hash_func: GetStateHashFunc = None
) -> Dict[str, Any]:
    """
    Thực thi thuật toán Monte Carlo Tree Search cốt lõi dựa trên giới hạn thời gian.

    Args:
        initial_state: Trạng thái bắt đầu của vấn đề.
        get_legal_actions_func: Hàm nhận state, trả về list các action hợp lệ.
        apply_action_func: Hàm nhận state và action, trả về state mới.
        is_terminal_func: Hàm nhận state, trả về True nếu là trạng thái kết thúc.
        simulation_policy_func: Hàm nhận state, chạy mô phỏng đến hết và trả về phần thưởng.
        exploration_constant: Hệ số C trong công thức UCB1.
        time_limit_seconds: Giới hạn thời gian chạy tối đa (giây). Bắt buộc.
        debug_simulation_limit: Số lượng mô phỏng gần nhất để lưu log (nếu được cung cấp).
        enable_transposition_table: Bật/tắt việc sử dụng Transposition Table (mặc định False).
        get_state_hash_func: Hàm để tính hash của state (bắt buộc nếu enable_transposition_table=True).

    Returns:
        Dictionary chứa kết quả và thống kê MCTS, bao gồm:
            - best_action: Hành động tốt nhất được tìm thấy từ gốc.
            - best_action_score: Điểm số của hành động tốt nhất (ví dụ: reward trung bình).
            - score_type: Loại điểm số được sử dụng (ví dụ: 'average_reward', 'visits').
            - iterations_completed: Số lượt lặp MCTS thực sự hoàn thành trong thời gian giới hạn.
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

    # Khởi tạo Transposition Table nếu được bật
    transposition_table: Optional[Dict[Any, MCTSNode]] = None
    if enable_transposition_table:
         # Không cần kiểm tra get_state_hash_func ở đây nữa vì sẽ thử hash tự động
         # if get_state_hash_func is None:
         #      logging.error("Transposition table enabled but get_state_hash_func is missing!")
         #      default_result["error"] = "Configuration Error: Transposition table enabled but get_state_hash_func is missing."
         #      return default_result
         transposition_table = {}
         logging.info("Transposition Table enabled. Will attempt auto-hashing if get_state_hash_func is not provided.")

    try:
        # --- 1. Khởi tạo Node Gốc ---
        logging.debug(f"Initializing MCTS with state: {str(initial_state)[:200]}...")
        # <<< Bắt lỗi gọi hàm động >>>
        initial_legal_actions = []
        is_initial_terminal = False
        try:
            initial_legal_actions = get_legal_actions_func(initial_state)
        except Exception as e_init_legal:
            detailed_error = _format_dynamic_code_error(e_init_legal, 'get_legal_actions_func (initial)') # Gọi helper mới
            logging.error(detailed_error)
            default_result["error"] = detailed_error
            default_result["time_elapsed_seconds"] = time.time() - start_time
            return default_result
        try:
            is_initial_terminal = is_terminal_func(initial_state)
        except Exception as e_init_term:
            detailed_error = _format_dynamic_code_error(e_init_term, 'is_terminal_func (initial)') # Gọi helper mới
            logging.error(detailed_error)
            default_result["error"] = detailed_error
            default_result["time_elapsed_seconds"] = time.time() - start_time
            return default_result
        # <<< Kết thúc bắt lỗi >>>

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

        # Thêm node gốc vào Transposition Table nếu được bật
        if enable_transposition_table and transposition_table is not None:
            root_hash = None
            can_hash_root = True
            try:
                if get_state_hash_func is not None:
                    # Sử dụng hàm hash tùy chỉnh
                    # <<< Bắt lỗi gọi hàm động >>>
                    try:
                        root_hash = get_state_hash_func(root_node.state)
                        # Kiểm tra tính hashable (lỗi này không phải từ code động)
                        hash(root_hash)
                    except TypeError as te_custom_hash_result:
                         logging.warning(f"Custom get_state_hash_func returned an unhashable type '{type(root_hash).__name__}' for initial state. Skipping TT for root.")
                         can_hash_root = False
                         root_hash = None
                    except Exception as e_hash_root_dyn:
                        detailed_error = _format_dynamic_code_error(e_hash_root_dyn, 'get_state_hash_func (initial)') # Gọi helper mới
                        logging.error(detailed_error)
                        default_result["error"] = detailed_error
                        default_result["time_elapsed_seconds"] = time.time() - start_time
                        return default_result
                    # <<< Kết thúc bắt lỗi >>>
                else:
                    # Thử hash tự động
                    try:
                        root_hash = hash(root_node.state)
                        logging.debug(f"Auto-hashing root state successful.")
                    except TypeError:
                        logging.warning(f"Auto-hashing failed for initial state (type: {type(root_node.state).__name__}). Initial state cannot be added to TT.")
                        can_hash_root = False # Đánh dấu không hash được

                if can_hash_root and root_hash is not None:
                    transposition_table[root_hash] = root_node
                    logging.debug(f"Root node added to TT with hash: {root_hash}")

            except Exception as e_hash_root:
                 # Lỗi từ hàm hash tùy chỉnh hoặc lỗi không mong muốn khác
                 logging.error(f"Error obtaining hash for initial state: {e_hash_root}", exc_info=True)
                 default_result["error"] = f"Error obtaining hash for initial state: {e_hash_root}"
                 default_result["time_elapsed_seconds"] = time.time() - start_time # Cập nhật thời gian trước khi return
                 return default_result

        iterations_done = 0
        # --- 2. Vòng lặp MCTS Chính --- (Chỉ dừng theo thời gian)
        while True:
            # 2.1. Kiểm tra Điều kiện Dừng (Chỉ thời gian)
            current_time = time.time()
            time_elapsed = current_time - start_time
            if time_limit_seconds is not None and time_elapsed > time_limit_seconds:
                logging.info(f"MCTS stopping due to time limit ({time_limit_seconds:.2f}s reached).")
                break

            # --- Bắt đầu một lượt lặp MCTS ---
            node = root_node # Bắt đầu từ gốc
            expanded_node = None # Reset cho mỗi iteration

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
                    # expanded_node = None # Node sẽ được dùng cho simulation/backprop # Đã reset ở trên
                    try:
                        # <<< Bắt lỗi gọi hàm động: apply_action_func >>>
                        new_state = None
                        try:
                            new_state = apply_action_func(node.state, action_to_expand)
                        except Exception as e_apply:
                            detailed_error = _format_dynamic_code_error(e_apply, 'apply_action_func') # Gọi helper mới
                            logging.error(detailed_error)
                            default_result["error"] = detailed_error
                            default_result["time_elapsed_seconds"] = time.time() - start_time
                            default_result["iterations_completed"] = iterations_done
                            return default_result
                        # <<< Kết thúc bắt lỗi >>>

                        # <<< Logic Transposition Table >>>
                        existing_node = None
                        new_state_hash = None
                        # <<< THAY ĐỔI: Giả định có thể hash ban đầu >>>
                        can_hash_new_state = True # Assume hashable initially

                        if enable_transposition_table and transposition_table is not None:
                            try:
                                state_to_hash = new_state # State to potentially hash

                                # --- BỔ SUNG: Thử chuyển đổi kiểu phổ biến --- 
                                if isinstance(state_to_hash, list):
                                    try:
                                        # Cố gắng chuyển đổi list thành tuple (có thể cần đệ quy nếu list chứa list/dict)
                                        state_to_hash = tuple(state_to_hash) 
                                        # Ví dụ đệ quy đơn giản (chỉ 1 cấp): 
                                        # state_to_hash = tuple(tuple(item) if isinstance(item, list) else item for item in state_to_hash)
                                        logging.debug(f"Converted list state to tuple for hashing.")
                                    except TypeError:
                                        # Phần tử bên trong list không hashable
                                        can_hash_new_state = False
                                        logging.warning(f"Could not convert list state elements to hashable tuple for TT hashing. State type: {type(new_state).__name__}. Skipping TT for this state.")
                                # --- KẾT THÚC BỔ SUNG ---
                                
                                # Chỉ tiếp tục nếu chưa bị đánh dấu là không hash được
                                if can_hash_new_state: 
                                    if get_state_hash_func is not None:
                                        # Dùng hàm hash tùy chỉnh, bọc trong try-except
                                        try:
                                            # <<< Bắt lỗi gọi hàm động: get_state_hash_func >>>
                                            new_state_hash = get_state_hash_func(state_to_hash) # Use potentially converted state
                                            hash(new_state_hash)
                                            # <<< Kết thúc bắt lỗi >>>
                                        except TypeError as te_custom_hash_result:
                                            can_hash_new_state = False
                                            logging.warning(f"Custom get_state_hash_func returned an unhashable type '{type(new_state_hash).__name__}'. Skipping TT for this state. Value: {str(new_state_hash)[:100]}...")
                                            new_state_hash = None
                                        except Exception as e_custom_hash_dyn:
                                            can_hash_new_state = False
                                            detailed_error = _format_dynamic_code_error(e_custom_hash_dyn, 'get_state_hash_func') # Gọi helper mới
                                            logging.error(f"{detailed_error}\nSkipping TT for this state.")
                                            new_state_hash = None
                                        # <<< Kết thúc bắt lỗi >>>
                                    else:
                                        # Thử hash tự động (với state_to_hash đã chuyển đổi nếu có)
                                        try:
                                            new_state_hash = hash(state_to_hash)
                                        except TypeError:
                                            can_hash_new_state = False
                                            logging.warning(f"Auto-hashing failed for state type {type(state_to_hash).__name__}. Skipping TT for this state.")

                                    # Kiểm tra TT nếu hash thành công và hash có giá trị
                                    if can_hash_new_state and new_state_hash is not None and new_state_hash in transposition_table:
                                        existing_node = transposition_table[new_state_hash]
                                        # logging.debug(f"TT Hit: State hash {new_state_hash} found. Reusing node.") # Có thể quá nhiều log

                            except Exception as e_hash_prepare: # Bắt lỗi trong quá trình chuẩn bị hash
                                 can_hash_new_state = False 
                                 logging.warning(f"Unexpected error during state hashing preparation: {e_hash_prepare}. Skipping TT for this state.")

                        if existing_node is not None:
                            # --- Tái sử dụng node từ TT ---
                            # Thêm node đã tồn tại làm con của node hiện tại
                            # Lưu ý: Không thay đổi parent của existing_node
                            if existing_node not in node.children:
                                node.children.append(existing_node)
                                # Quan trọng: Không set parent của existing_node thành node
                                # để giữ backpropagation đơn giản theo đường đi hiện tại.
                                # Nếu cần, có thể thêm một liên kết yếu hoặc danh sách "reached_by" nếu muốn theo dõi tất cả các đường đến.

                            # Node để simulation/backprop là node đã tồn tại
                            expanded_node = existing_node
                        else:
                            # --- Tạo node mới như bình thường --- VÀ thêm vào TT nếu có thể hash
                            # <<< Bắt lỗi gọi hàm động: is_terminal_func & get_legal_actions_func >>>
                            is_new_terminal = False
                            new_legal_actions = []
                            try:
                                is_new_terminal = is_terminal_func(new_state)
                            except Exception as e_term_new:
                                detailed_error = _format_dynamic_code_error(e_term_new, 'is_terminal_func') # Gọi helper mới
                                logging.error(detailed_error)
                                default_result["error"] = detailed_error
                                default_result["time_elapsed_seconds"] = time.time() - start_time
                                default_result["iterations_completed"] = iterations_done
                                return default_result

                            if not is_new_terminal:
                                try:
                                    new_legal_actions = get_legal_actions_func(new_state)
                                except Exception as e_legal_new:
                                    detailed_error = _format_dynamic_code_error(e_legal_new, 'get_legal_actions_func') # Gọi helper mới
                                    logging.error(detailed_error)
                                    default_result["error"] = detailed_error
                                    default_result["time_elapsed_seconds"] = time.time() - start_time
                                    default_result["iterations_completed"] = iterations_done
                                    return default_result
                            # <<< Kết thúc bắt lỗi >>>

                            child_node = node.add_child(
                                child_state=new_state,
                                action=action_to_expand,
                                untried_actions=new_legal_actions,
                                is_terminal=is_new_terminal
                            )

                            # Thêm node mới vào TT nếu được bật VÀ hash thành công
                            if enable_transposition_table and transposition_table is not None and can_hash_new_state and new_state_hash is not None:
                                transposition_table[new_state_hash] = child_node
                                logging.debug(f"New node added to TT with hash: {new_state_hash}")
                            elif enable_transposition_table and not can_hash_new_state:
                                # Log nếu TT bật nhưng không hash được để biết node không được lưu
                                logging.debug(f"New node created but not added to TT because state (type: {type(new_state).__name__}) is not hashable.")

                            expanded_node = child_node
                        # <<< Kết thúc Logic Transposition Table >>>

                    except Exception as e_expand_inner:
                        logging.error(f"Error during expansion step (action: {action_to_expand}): {e_expand_inner}", exc_info=True)
                        continue # Bỏ qua iteration này

                # 2.4. Simulation (Rollout): Từ nút hiện tại (lá hoặc mới mở rộng), mô phỏng đến hết
                simulation_reward = 0.0 # Phần thưởng mặc định nếu mô phỏng lỗi
                try:
                    # Dùng expanded_node (hoặc node nếu không expansion) cho simulation
                    sim_start_node = expanded_node if expanded_node is not None else node
                    # <<< Bắt lỗi gọi hàm động: simulation_policy_func >>>
                    try:
                        simulation_reward = simulation_policy_func(sim_start_node.state)
                    except Exception as e_sim_dyn:
                        detailed_error = _format_dynamic_code_error(e_sim_dyn, 'simulation_policy_func') # Gọi helper mới
                        sim_state_repr = str(sim_start_node.state)[:200] if sim_start_node else "None"
                        logging.error(f"{detailed_error}\nOccurred during simulation from state: {sim_state_repr}")
                        simulation_reward = 0.0 # Giữ reward là 0.0
                    # <<< Kết thúc bắt lỗi >>>
                except Exception as e_sim: # Bắt lỗi logic chung khác trong pha simulation (không phải từ code động)
                    sim_state_repr = str(sim_start_node.state)[:200] if sim_start_node else "None"
                    logging.error(f"Error during simulation step setup or logic (not dynamic code execution) from state {sim_state_repr}: {e_sim}", exc_info=True)
                    simulation_reward = 0.0 # Giữ reward là 0.0 nếu lỗi

                # Ghi log debug simulation nếu được bật
                if simulation_debug_log is not None:
                    try:
                        # Lưu trạng thái bắt đầu và phần thưởng
                        # Cần deepcopy nếu state là mutable để tránh bị thay đổi sau này
                        sim_start_node = expanded_node if expanded_node is not None else node
                        log_entry = {
                            "start_state": copy.deepcopy(sim_start_node.state), # Deepcopy để đảm bảo
                            "reward": simulation_reward
                        }
                        simulation_debug_log.append(log_entry)
                    except Exception as e_debug_log:
                        # Không nên để lỗi log debug làm dừng MCTS
                        logging.warning(f"Could not log simulation debug info: {e_debug_log}")

                # 2.5. Backpropagation: Cập nhật visits và reward ngược lên cây
                # Bắt đầu backprop từ node được mở rộng (hoặc node hiện tại nếu không expansion)
                backprop_node = expanded_node if expanded_node is not None else node
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