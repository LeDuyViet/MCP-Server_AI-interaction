# -*- coding: utf-8 -*-
"""
Công cụ MCTS Reasoning - Giao diện chính và điều phối chiến lược.
"""

import math
import random
import time
import logging
import sys
from typing import Dict, List, Any, Optional, Callable, Union
import copy
from functools import partial
import re

# Import các thành phần cốt lõi từ các module khác
from .node import MCTSNode # Lớp Node
from .engine import run_mcts # Engine MCTS

# Cấu hình logging cơ bản
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Hàm Giao diện Chính ---
def mcts_reasoning(
    strategy_name: str,
    strategy_params: Dict[str, Any],
    exploration_constant: float = 1.414,
    time_limit_seconds: float = 10.0, # Giới hạn thời gian mặc định là 10 giây
    debug_simulation_limit: Optional[int] = None
) -> Dict[str, Any]:
    """
    Thực thi một chiến lược suy luận MCTS dựa trên giới hạn thời gian.

    Args:
        strategy_name: Tên của chiến lược cần thực thi.
                       Hỗ trợ:
                         - "find_best_next_step": Tìm bước đi tiếp theo tốt nhất dựa trên code logic được cung cấp.
                         - "evaluate_options": Đánh giá một danh sách các lựa chọn từ trạng thái ban đầu.
        strategy_params: Dictionary chứa các tham số cần thiết cho chiến lược.
                         - Cho "find_best_next_step": {
                             "current_state": Any,                 # Trạng thái hiện tại của vấn đề.
                             "problem_context": Optional[Dict[str, Any]] = {}, # (Tùy chọn) Context bổ sung cho logic.
                             "simulation_config": Optional[Dict[str, Any]] = {}, # (Tùy chọn) Cấu hình cho simulation_policy (ví dụ: max_depth, epsilon).
                             "get_legal_actions_code": str,      # Code Python (dạng chuỗi) định nghĩa hàm get_legal_actions(state, context).
                             "apply_action_code": str,           # Code Python định nghĩa hàm apply_action(state, action, context).
                             "is_terminal_code": str,            # Code Python định nghĩa hàm is_terminal(state, context).
                             "simulation_policy_code": str       # Code Python định nghĩa hàm simulation_policy(state, context) -> float.
                           }
                         - Cho "evaluate_options": {
                             "initial_context": Any,      # Ngữ cảnh/Trạng thái ban đầu để đánh giá.
                             "options_list": List[Any],   # Danh sách các lựa chọn cần đánh giá.
                             "max_simulation_depth": Optional[int] = 50, # (Không dùng trực tiếp trong MCTS, có thể dùng trong logic nếu cần)
                             "evaluation_logic": Optional[str] = "random_reward" # Cách đánh giá mô phỏng (hiện chỉ hỗ trợ "random_reward").
                           }
        exploration_constant (float): Hệ số khám phá UCB1 (mặc định 1.414).
        time_limit_seconds (float): Giới hạn thời gian chạy tối đa (giây).
                                    Mặc định là 10.0 giây.
        debug_simulation_limit (Optional[int]): Số lượng mô phỏng gần nhất để lưu log (ví dụ: 5). Mặc định là None (không log).

    Returns:
        Dictionary chứa kết quả và thống kê MCTS, hoặc thông tin lỗi chi tiết.
        Ví dụ thành công ("find_best_next_step"):
        {
            "status": "success",
            "message": "Strategy 'find_best_next_step' completed successfully.",
            "strategy_used": "find_best_next_step",
            "best_action_found": "move_right", # Hành động tốt nhất tìm được
            "best_action_score": 0.95,       # Điểm MCTS ước tính
            "score_type": "average_reward",
            # "iterations_attempted": Bị loại bỏ,
            "iterations_completed": 150234, # Số lượt lặp thực tế hoàn thành trong time limit
            "time_elapsed_seconds": 10.05,  # Thời gian chạy thực tế
            "root_node_total_visits": 150234,
            "error_type": None,
            "error_details": None,
            "warnings": [],
            "simulation_debug_log": None
        }
        Ví dụ lỗi ("find_best_next_step" - thiếu code logic):
        {
            "status": "error",
            "message": "Invalid parameters or unsupported strategy 'find_best_next_step': Missing required keys in strategy_params for 'find_best_next_step': {'get_legal_actions_code'}. Required: ...",
            "strategy_used": "find_best_next_step",
            # ... các trường khác là None hoặc 0 ...
            "error_type": "InvalidStrategyParameters",
            "error_details": "Missing required keys...",
            "warnings": [],
            "simulation_debug_log": None
        }
    """
    start_func_time = time.time()
    # --- Kết quả Cơ bản và Validation Đầu vào ---
    base_result = {
        "status": "error",
        "message": "Initialization error.",
        "strategy_used": strategy_name,
        "best_action_found": None,
        "best_action_score": None,
        "score_type": None, # Sẽ được cập nhật nếu MCTS chạy thành công
        # "iterations_attempted": Bị loại bỏ,
        "iterations_completed": 0,
        "time_elapsed_seconds": 0.0,
        "root_node_total_visits": 0,
        "error_type": None,
        "error_details": None,
        "warnings": [],
        "simulation_debug_log": None
    }

    logging.info(f"Executing MCTS reasoning strategy: '{strategy_name}' with params: {str(strategy_params)[:500]}...") # Log rút gọn

    # --- Validation Tham số Cơ bản ---
    if not isinstance(strategy_name, str) or not strategy_name:
        base_result["message"] = "'strategy_name' must be a non-empty string."
        base_result["error_type"] = "InvalidParameter"
        base_result["error_details"] = base_result["message"]
        logging.error(base_result["message"])
        base_result["time_elapsed_seconds"] = time.time() - start_func_time
        return base_result
    if not isinstance(strategy_params, dict):
        base_result["message"] = "'strategy_params' must be a dictionary."
        base_result["error_type"] = "InvalidParameter"
        base_result["error_details"] = base_result["message"]
        logging.error(base_result["message"])
        base_result["time_elapsed_seconds"] = time.time() - start_func_time
        return base_result
    if not isinstance(time_limit_seconds, (int, float)) or time_limit_seconds <= 0:
        # Đảm bảo time_limit_seconds là số dương
        base_result["message"] = "'time_limit_seconds' must be a positive number."
        base_result["error_type"] = "InvalidParameter"
        base_result["error_details"] = base_result["message"]
        logging.error(base_result["message"])
        base_result["time_elapsed_seconds"] = time.time() - start_func_time
        return base_result

    # --- Phân phối và Thực thi Chiến lược ---
    supported_strategies = ["find_best_next_step", "evaluate_options"]
    try:
        if strategy_name == "find_best_next_step":
            # --- Logic cho Chiến lược: Tìm Bước Đi Tiếp Theo Tốt Nhất (với code động) ---
            logging.info("Initiating 'find_best_next_step' strategy logic with dynamic code.")

            # 1. Validate Parameters for this strategy
            allowed_keys = {
                "current_state", "problem_context",
                "simulation_config",
                "get_legal_actions_code", "apply_action_code",
                "is_terminal_code", "simulation_policy_code"
            }
            required_keys = {
                "current_state",
                "get_legal_actions_code", "apply_action_code",
                "is_terminal_code", "simulation_policy_code"
            }

            # Kiểm tra các khóa bắt buộc
            missing_keys = required_keys - strategy_params.keys()
            if missing_keys:
                raise ValueError(f"Missing required keys in strategy_params for '{strategy_name}': {missing_keys}. Required: {required_keys}")

            # Kiểm tra các khóa không mong đợi
            unexpected_keys = strategy_params.keys() - allowed_keys
            if unexpected_keys:
                 # Chỉ cảnh báo về các khóa không mong đợi, không raise lỗi
                 warning_msg = f"Warning: Unexpected keys found in strategy_params for '{strategy_name}': {unexpected_keys}. Allowed keys: {allowed_keys}. These keys will be ignored."
                 logging.warning(warning_msg)
                 base_result["warnings"].append(warning_msg)
                 # raise ValueError(f"Unexpected keys found in strategy_params for '{strategy_name}': {unexpected_keys}. Allowed keys: {allowed_keys}")


            # Lấy giá trị tham số sau khi validate keys
            current_state = strategy_params["current_state"]
            problem_context = strategy_params.get("problem_context", {}) # Lấy an toàn với giá trị mặc định
            simulation_config = strategy_params.get("simulation_config", {}) # Lấy simulation_config
            get_legal_actions_code = strategy_params["get_legal_actions_code"]
            apply_action_code = strategy_params["apply_action_code"]
            is_terminal_code = strategy_params["is_terminal_code"]
            simulation_policy_code = strategy_params["simulation_policy_code"]

            # Validate kiểu dữ liệu cơ bản
            if not isinstance(problem_context, dict):
                raise ValueError("'problem_context' must be a dictionary if provided.")
            if not isinstance(simulation_config, dict):
                raise ValueError("'simulation_config' must be a dictionary if provided.")
            if not isinstance(get_legal_actions_code, str) or not get_legal_actions_code:
                 raise ValueError("'get_legal_actions_code' must be a non-empty string.")
            if not isinstance(apply_action_code, str) or not apply_action_code:
                 raise ValueError("'apply_action_code' must be a non-empty string.")
            if not isinstance(is_terminal_code, str) or not is_terminal_code:
                 raise ValueError("'is_terminal_code' must be a non-empty string.")
            if not isinstance(simulation_policy_code, str) or not simulation_policy_code:
                 raise ValueError("'simulation_policy_code' must be a non-empty string.")

            # 2. Định nghĩa Hàm Logic từ Code Strings bằng exec()
            # <<< BƯỚC VALIDATE CODE AN TOÀN >>>
            def _validate_code_safety(code_string: str, code_name: str):
                """Kiểm tra chuỗi code để tìm các mẫu truy cập file system bị cấm."""
                forbidden_modules = ['os', 'io', 'pathlib', 'sys', 'subprocess']
                forbidden_patterns = ['open(', '__import__(']

                for module in forbidden_modules:
                    import_pattern = rf"^\s*(import\s+{module}|from\s+{module}\s+import)"
                    for line in code_string.splitlines():
                        stripped_line = line.strip()
                        if not stripped_line.startswith('#') and re.search(import_pattern, stripped_line):
                             raise ValueError(f"Forbidden import of module '{module}' found in code for '{code_name}'. File system access is disallowed.")

                for pattern in forbidden_patterns:
                     for line in code_string.splitlines():
                        stripped_line = line.strip()
                        if not stripped_line.startswith('#') and pattern in stripped_line:
                             if pattern == 'open(' and 'def open' in stripped_line:
                                 continue
                             raise ValueError(f"Forbidden pattern '{pattern}' found in code for '{code_name}'. File system access is disallowed.")

            # Tạo namespace riêng để tránh xung đột và tăng cường bảo mật (ở mức độ nào đó)
            logic_namespace = {
                "math": math, # Cung cấp module math nếu cần
                "copy": copy, # Cung cấp module copy nếu cần
                "logging": logging, # Cung cấp logging nếu cần
                # Thêm các thư viện an toàn khác nếu logic cần
            }
            # Thêm context vào namespace để các hàm có thể truy cập trực tiếp (hoặc truyền qua partial)
            # logic_namespace['problem_context'] = problem_context # Cách 1: Inject context vào namespace
            # Cách 2 (Ưu tiên hơn): Dùng partial để truyền context tường minh

            defined_funcs = {}
            func_codes = {
                "get_legal_actions": get_legal_actions_code,
                "apply_action": apply_action_code,
                "is_terminal": is_terminal_code,
                "simulation_policy": simulation_policy_code
            }

            try:
                # <<< VALIDATE CODE TRƯỚC KHI EXEC >>>
                func_codes_to_validate = {
                    "get_legal_actions": get_legal_actions_code,
                    "apply_action": apply_action_code,
                    "is_terminal": is_terminal_code,
                    "simulation_policy": simulation_policy_code
                }
                for name, code in func_codes_to_validate.items():
                    _validate_code_safety(code, name) # Gọi hàm kiểm tra

                # Nếu kiểm tra qua, tiếp tục với exec
                for name, code in func_codes.items():
                    # Thực thi code trong namespace đã chuẩn bị
                    # globals() được truyền vào để cho phép import cơ bản nếu cần, nhưng cần cẩn trọng
                    exec(code, globals(), logic_namespace)
                    # Kiểm tra xem hàm có được định nghĩa đúng tên không
                    if name not in logic_namespace or not callable(logic_namespace[name]):
                        raise RuntimeError(f"Code provided for '{name}' did not define a callable function named '{name}'.")
                    defined_funcs[name] = logic_namespace[name]
            except ValueError as ve_validate:
                 # Bắt lỗi từ _validate_code_safety
                 raise ValueError(f"Security validation failed: {ve_validate}") from ve_validate
            except SyntaxError as se: # Giữ lại các except khác
                raise ValueError(f"Syntax error in provided code for '{name}': {se}") from se
            except NameError as ne:
                 # Bổ sung thông báo lỗi NameError rõ ràng hơn
                 available_globals = list(globals().keys()) # Lấy globals thực tế
                 available_locals = list(logic_namespace.keys())
                 hint = f"Is the variable defined? Are you trying to import a disallowed module (like os, io, sys)? Remember only standard libraries (like random, math if imported) and pre-defined locals ({available_locals}) are available."
                 raise ValueError(f"Name error in provided code for '{name}': {ne}. {hint}") from ne
            except Exception as e_exec:
                # Bắt các lỗi khác từ exec()
                raise RuntimeError(f"Error executing provided code for '{name}': {e_exec}") from e_exec

            # 3. Chuẩn bị Hàm Logic với Context (Sử dụng partial)
            # Cách này tường minh hơn là inject context vào namespace của exec
            try:
                # Tạo bản sao context để tránh thay đổi ngoài ý muốn nếu cần
                effective_context = copy.deepcopy(problem_context)
                # Hợp nhất simulation_config vào context. Ưu tiên giá trị trong simulation_config nếu trùng key.
                effective_context["simulation_config"] = simulation_config

                # Sử dụng effective_context đã bao gồm simulation_config
                get_actions_with_context = partial(defined_funcs["get_legal_actions"], context=effective_context)
                apply_action_with_context = partial(defined_funcs["apply_action"], context=effective_context)
                is_terminal_with_context = partial(defined_funcs["is_terminal"], context=effective_context)
                simulation_policy_with_context = partial(defined_funcs["simulation_policy"], context=effective_context)

                # Kiểm tra nhanh signature (không hoàn hảo nhưng giúp bắt lỗi sớm)
                # Thử gọi với các tham số giả định cơ bản nhất
                try: get_actions_with_context(current_state)
                except TypeError as te: raise RuntimeError(f"Function 'get_legal_actions' (from code) might have wrong signature. Expected (state, context). Error: {te}")
                # Không thể kiểm tra apply_action dễ dàng vì cần action hợp lệ
                try: is_terminal_with_context(current_state)
                except TypeError as te: raise RuntimeError(f"Function 'is_terminal' (from code) might have wrong signature. Expected (state, context). Error: {te}")
                try: simulation_policy_with_context(current_state)
                except TypeError as te: raise RuntimeError(f"Function 'simulation_policy' (from code) might have wrong signature. Expected (state, context). Error: {te}")

            except KeyError as ke:
                # Lỗi này không nên xảy ra nếu bước 2 thành công
                raise RuntimeError(f"Internal Error: Failed to find function '{ke}' after exec.")
            except TypeError as e_partial:
                 # Lỗi nếu hàm gốc không chấp nhận 'context' hoặc có signature sai
                raise RuntimeError(f"Error preparing logic function with context (likely incorrect function signature in provided code): {e_partial}") from e_partial

            # 4. Call the Core MCTS Engine
            logging.info(f"Calling run_mcts for '{strategy_name}' with dynamically defined logic...")
            # Luôn sử dụng time_limit_seconds, không còn num_iterations

            mcts_results = run_mcts(
                initial_state=current_state,
                get_legal_actions_func=get_actions_with_context,
                apply_action_func=apply_action_with_context, # apply_action_func trong run_mcts sẽ tự nhận action
                is_terminal_func=is_terminal_with_context,
                simulation_policy_func=simulation_policy_with_context,
                exploration_constant=exploration_constant,
                time_limit_seconds=time_limit_seconds, # Luôn truyền time limit
                debug_simulation_limit=debug_simulation_limit
            )

            # 5. Process and Return Results for this strategy
            mcts_error = mcts_results.get("error")
            if mcts_error:
                base_result["status"] = "error"
                base_result["message"] = f"MCTS execution failed for strategy '{strategy_name}' with dynamic code."
                base_result["error_type"] = "MCTSExecutionError"
                base_result["error_details"] = mcts_error
            else:
                base_result["status"] = "success"
                base_result["message"] = f"Strategy '{strategy_name}' with dynamic code completed successfully."
                base_result["best_action_found"] = mcts_results.get("best_action")
                base_result["best_action_score"] = mcts_results.get("best_action_score")
                base_result["score_type"] = mcts_results.get("score_type", "average_reward") # Cung cấp mặc định nếu thiếu

            # Copy MCTS stats
            base_result["iterations_completed"] = mcts_results.get("iterations_completed", 0)
            base_result["time_elapsed_seconds"] = mcts_results.get("time_elapsed_seconds", time.time() - start_func_time) # Ước tính nếu thiếu
            base_result["root_node_total_visits"] = mcts_results.get("root_node_visits", 0)
            # Thêm thông tin về hành động tốt nhất theo visits (nếu engine cung cấp)
            base_result["best_action_by_visits"] = mcts_results.get("best_action_by_visits")
            base_result["best_action_visits_score"] = mcts_results.get("best_action_visits_score")

            # Thêm simulation debug log vào kết quả
            base_result["simulation_debug_log"] = mcts_results.get("simulation_debug_log")

            logging.info(f"Strategy '{strategy_name}' (dynamic code) finished. Result status: {base_result['status']}")
            return base_result

        elif strategy_name == "evaluate_options":
            # --- Logic cho Chiến lược: Đánh giá Lựa chọn (evaluate_options) ---
            # Giữ nguyên logic hiện tại của chiến lược này vì nó không dùng registry
            # và tự định nghĩa các hàm logic lồng bên trong.
            logging.info("Initiating 'evaluate_options' strategy logic (uses internal logic).")

            # 1. Validate Parameters for this strategy
            allowed_keys = {"initial_context", "options_list", "max_simulation_depth", "evaluation_logic"}
            required_keys = {"initial_context", "options_list"}

            # Kiểm tra các khóa bắt buộc
            missing_keys = required_keys - strategy_params.keys()
            if missing_keys:
                raise ValueError(f"Missing required keys in strategy_params for '{strategy_name}': {missing_keys}. Required: {required_keys}")

            # Kiểm tra các khóa không mong đợi
            unexpected_keys = strategy_params.keys() - allowed_keys
            if unexpected_keys:
                 warning_msg = f"Warning: Unexpected keys found in strategy_params for '{strategy_name}': {unexpected_keys}. Allowed keys: {allowed_keys}. These keys will be ignored."
                 logging.warning(warning_msg)
                 base_result["warnings"].append(warning_msg)
                 # raise ValueError(f"Unexpected keys found in strategy_params for '{strategy_name}': {unexpected_keys}. Allowed keys: {allowed_keys}")

            # Lấy giá trị tham số sau khi validate keys
            initial_context_eval = strategy_params["initial_context"] # Đổi tên để tránh xung đột namespace tiềm ẩn
            options_list_eval = strategy_params["options_list"] # Đổi tên
            # Lấy các tham số tùy chọn với giá trị mặc định
            # max_sim_depth_eval = strategy_params.get("max_simulation_depth", 50) # Không dùng trực tiếp
            evaluation_logic_eval = strategy_params.get("evaluation_logic", "random_reward")

            # Validate kiểu dữ liệu
            if not isinstance(options_list_eval, list) or not options_list_eval:
                raise ValueError("'options_list' must be a non-empty list for 'evaluate_options'.")
            # if not isinstance(max_sim_depth_eval, int) or max_sim_depth_eval <= 0:
            #     logging.warning(f"Invalid 'max_simulation_depth': {max_sim_depth_eval}. Using default 50.")
            #     max_sim_depth_eval = 50
            if not isinstance(evaluation_logic_eval, str) or evaluation_logic_eval != "random_reward":
                # Hiện tại chỉ hỗ trợ random_reward
                logging.warning(f"Unsupported 'evaluation_logic': '{evaluation_logic_eval}'. Using default 'random_reward'.")
                evaluation_logic_eval = "random_reward"

            # 2. Define Strategy-Specific Logic Functions (hàm lồng)
            def _get_legal_actions_eval(state):
                is_initial = False
                try:
                    if type(state) == type(initial_context_eval):
                         if isinstance(state, (dict, list, set)): is_initial = (state == initial_context_eval)
                         else: is_initial = (state == initial_context_eval)
                except Exception as e_cmp:
                    logging.warning(f"Error comparing state with initial_context in _get_legal_actions_eval: {e_cmp}. Assuming not initial state.")
                return list(options_list_eval) if is_initial else [] # Trả về bản sao

            def _apply_action_eval(state, action):
                return action # Trạng thái mới là chính action (option)

            def _is_terminal_eval(state):
                is_initial = False
                try:
                     if type(state) == type(initial_context_eval):
                         if isinstance(state, (dict, list, set)): is_initial = (state == initial_context_eval)
                         else: is_initial = (state == initial_context_eval)
                except Exception as e_cmp:
                    logging.warning(f"Error comparing state with initial_context in _is_terminal_eval: {e_cmp}. Assuming not initial state.")
                return not is_initial # Terminal nếu không phải trạng thái ban đầu

            def _simulation_policy_eval(state):
                # State ở đây chính là option đã chọn (terminal)
                if evaluation_logic_eval == "random_reward":
                    return random.random()
                else:
                    return random.random() # Fallback

            # 3. Call the Core MCTS Engine
            logging.info("Calling run_mcts for 'evaluate_options'...")
            # Luôn sử dụng time_limit_seconds

            mcts_results = run_mcts(
                initial_state=initial_context_eval,
                get_legal_actions_func=_get_legal_actions_eval,
                apply_action_func=_apply_action_eval,
                is_terminal_func=_is_terminal_eval,
                simulation_policy_func=_simulation_policy_eval,
                exploration_constant=exploration_constant,
                time_limit_seconds=time_limit_seconds, # Luôn truyền time limit
                debug_simulation_limit=debug_simulation_limit
            )

            # 4. Process and Return Results for this strategy
            mcts_error = mcts_results.get("error")
            if mcts_error:
                 base_result["status"] = "error"
                 base_result["message"] = f"MCTS execution failed for strategy '{strategy_name}'."
                 base_result["error_type"] = "MCTSExecutionError"
                 base_result["error_details"] = mcts_error
            else:
                 base_result["status"] = "success"
                 base_result["message"] = f"Strategy '{strategy_name}' completed successfully."
                 base_result["best_action_found"] = mcts_results.get("best_action") # Là option tốt nhất
                 base_result["best_action_score"] = mcts_results.get("best_action_score")
                 base_result["score_type"] = mcts_results.get("score_type", "average_evaluation")
                 # Thêm thông tin về hành động tốt nhất theo visits (nếu engine cung cấp - có thể không áp dụng cho eval_options)
                 base_result["best_action_by_visits"] = mcts_results.get("best_action_by_visits")
                 base_result["best_action_visits_score"] = mcts_results.get("best_action_visits_score")

            # Copy MCTS stats
            base_result["simulation_debug_log"] = mcts_results.get("simulation_debug_log")
            base_result["iterations_completed"] = mcts_results.get("iterations_completed", 0)
            base_result["time_elapsed_seconds"] = mcts_results.get("time_elapsed_seconds", time.time() - start_func_time)
            base_result["root_node_total_visits"] = mcts_results.get("root_node_visits", 0)

            logging.info(f"Strategy '{strategy_name}' finished. Result status: {base_result['status']}")
            return base_result

        else:
            # Xử lý trường hợp strategy_name không hợp lệ
            raise ValueError(f"Unsupported strategy_name: '{strategy_name}'. Supported strategies: {supported_strategies}")

    # --- Xử lý lỗi chung ---
    except ValueError as ve:
        # Lỗi do người dùng cung cấp tham số không hợp lệ hoặc strategy không được hỗ trợ
        error_msg = f"Invalid parameters or unsupported strategy '{strategy_name}': {str(ve)}"
        logging.error(error_msg)
        base_result["message"] = error_msg
        base_result["error_type"] = "InvalidStrategyParameters"
        base_result["error_details"] = str(ve)
        base_result["time_elapsed_seconds"] = time.time() - start_func_time
        return base_result

    except RuntimeError as rte:
         # Lỗi nội bộ (ví dụ: lỗi khi exec code, lỗi signature hàm động)
         error_msg = f"Internal execution error for strategy '{strategy_name}': {str(rte)}"
         logging.error(error_msg, exc_info=True)
         base_result["message"] = error_msg
         base_result["error_type"] = "InternalExecutionError" # Đổi loại lỗi
         base_result["error_details"] = str(rte)
         base_result["time_elapsed_seconds"] = time.time() - start_func_time
         return base_result

    except Exception as e:
        # Các lỗi không mong đợi khác trong quá trình thực thi
        error_msg = f"Unexpected error executing strategy '{strategy_name}': {e}"
        logging.critical(error_msg, exc_info=True)
        base_result["message"] = error_msg
        base_result["error_type"] = "StrategyExecutionError"
        base_result["error_details"] = str(e)
        base_result["time_elapsed_seconds"] = time.time() - start_func_time
        return base_result 