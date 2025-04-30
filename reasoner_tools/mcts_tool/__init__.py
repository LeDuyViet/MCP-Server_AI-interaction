# -*- coding: utf-8 -*-
"""
Công cụ MCTS Reasoning - Giao diện chính và điều phối chiến lược.
"""

import math
import random
import time
import logging
import sys
from typing import Dict, List, Any, Optional, Callable, Union, Hashable
import copy
from functools import partial
import re

# Import các thành phần cốt lõi từ các module khác
from .node import MCTSNode # Lớp Node
from .engine import run_mcts, _format_dynamic_code_error # Engine MCTS và hàm format lỗi

# Cấu hình logging cơ bản
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Hàm Giao diện Chính ---
def mcts_reasoning(
    strategy_name: str,
    strategy_params: Dict[str, Any],
    exploration_constant: float = 1.414,
    time_limit_seconds: float = 10.0, # Giới hạn thời gian mặc định là 10 giây
    debug_simulation_limit: int = None,
    enable_transposition_table: bool = False # <-- Thêm tham số mới
) -> Dict[str, Any]:
    """
    Thực thi một chiến lược suy luận MCTS dựa trên giới hạn thời gian.

    **Cách hoạt động cốt lõi:** Bạn cung cấp trạng thái ban đầu và các đoạn code Python định nghĩa
    logic của vấn đề (lấy hành động, áp dụng hành động, kiểm tra kết thúc, đánh giá mô phỏng,
    và tùy chọn là hàm hash trạng thái). Engine MCTS sẽ sử dụng logic này để tìm kiếm
    hành động tốt nhất từ trạng thái ban đầu trong thời gian cho phép.

    Args:
        strategy_name: Tên của chiến lược cần thực thi.
                       Hỗ trợ:
                         - "find_best_next_step": Tìm bước đi tiếp theo tốt nhất dựa trên code logic được cung cấp.
                         - "evaluate_options": Đánh giá một danh sách các lựa chọn từ trạng thái ban đầu.
        strategy_params: Dictionary chứa các tham số cần thiết cho chiến lược.
                         - Cho "find_best_next_step": {
                             "current_state": Any,                 # Trạng thái hiện tại của vấn đề.
                             "problem_context": Optional[Dict[str, Any]] = {},
                                 # (Tùy chọn) Chứa thông tin tĩnh hoặc cấu hình chung của bài toán (ví dụ: kích thước bàn cờ, luật chơi đặc biệt).
                                 # Sẽ được gộp vào `context` chung.
                             "simulation_config": Optional[Dict[str, Any]] = {},
                                 # (Tùy chọn) Chứa cấu hình *riêng* cho hàm `simulation_policy` (ví dụ: max_depth, epsilon).
                                 # Sẽ được gộp vào `context` chung, **ghi đè** các key trùng tên từ `problem_context`.
                             # **QUAN TRỌNG:** Cả `problem_context` và `simulation_config` được gộp thành một dict `context` duy nhất
                             # được truyền vào *tất cả* các hàm logic (get_legal_actions, apply_action, ...).
                             # Truy cập các giá trị bằng `context['your_key']`.
                             "get_legal_actions_code": str,      # Code Python (dạng chuỗi) định nghĩa hàm
                             "apply_action_code": str,           # Code Python định nghĩa hàm
                             "is_terminal_code": str,            # Code Python định nghĩa hàm
                             "simulation_policy_code": str,       # Code Python định nghĩa hàm
                             "get_state_hash_code": Optional[str] = None # (Tùy chọn, Bắt buộc nếu enable_transposition_table=True) Code định nghĩa hàm get_state_hash(state, context) -> Hashable
                             # (Tùy chọn) Chỉ cần cung cấp nếu `enable_transposition_table=True` VÀ bạn muốn dùng hàm hash tùy chỉnh.
                             # Nếu `enable_transposition_table=True` và code này không được cung cấp, engine sẽ thử hash `state` trực tiếp.
                             # Yêu cầu signature: `get_state_hash(state: Any, context: Dict[str, Any]) -> Hashable`.
                             # **QUAN TRỌNG:** Giá trị trả về phải là kiểu **hashable** (vd: int, float, str, tuple).
                             # Trả về kiểu không hashable (vd: list, dict) sẽ gây lỗi.
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
        debug_simulation_limit (int): Số lượng mô phỏng gần nhất để lưu log (ví dụ: 5). Mặc định là None (không log).
        enable_transposition_table (bool): Bật/tắt Transposition Table để tái sử dụng node cho các trạng thái giống nhau (mặc định False).
                                           Nếu bật, engine sẽ thử hash trạng thái tự động. Cung cấp `get_state_hash_code` nếu muốn tùy chỉnh.

    Returns:
        Dictionary chứa kết quả và thống kê MCTS, hoặc thông tin lỗi chi tiết.
        - `status`: "success" hoặc "error".
        - `message`: Mô tả ngắn gọn kết quả hoặc lỗi.
        - `best_action_found`: Hành động tốt nhất tìm được từ trạng thái gốc (thường theo điểm trung bình).
        - `best_action_score`: Điểm MCTS ước tính của hành động tốt nhất.
        - `best_action_by_visits`: Hành động được thăm nhiều nhất từ gốc.
        - `best_action_visits_score`: Số lượt thăm của hành động tốt nhất theo visits.
        - `score_type`: Loại điểm số được dùng cho `best_action_score` (vd: "average_reward").
        - `iterations_completed`: Số lượt MCTS thực tế hoàn thành.
        - `time_elapsed_seconds`: Thời gian chạy thực tế.
        - `root_node_total_visits`: Tổng lượt thăm nút gốc.
        - `error_type`: Loại lỗi nếu `status` là "error" (vd: "InvalidInputOrCodeError", "ExecutionOrLogicError").
        - `error_details`: Chi tiết lỗi (thường là thông báo từ exception Python, đã được cải thiện để dễ hiểu hơn).
        - `warnings`: Danh sách các cảnh báo (vd: ghi đè key context, TT không dùng được cho state không hashable).
        - `simulation_debug_log`: Danh sách log các mô phỏng cuối cùng (nếu `debug_simulation_limit` > 0).

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
                "is_terminal_code", "simulation_policy_code",
                "get_state_hash_code" # <-- Thêm khóa cho hash code
            }
            required_keys = {
                "current_state",
                "get_legal_actions_code", "apply_action_code",
                "is_terminal_code", "simulation_policy_code"
            }
            # Thêm yêu cầu cho get_state_hash_code nếu TT được bật *VÀ* người dùng cung cấp code (không dùng auto-hash)
            # Hiện tại, engine sẽ tự động thử hash nếu code không được cung cấp, nên không cần bắt buộc ở đây nữa.
            # if enable_transposition_table:
            #      # Kiểm tra xem người dùng có CỐ TÌNH cung cấp get_state_hash_code không
            #      if "get_state_hash_code" in strategy_params and strategy_params["get_state_hash_code"] is not None:
            #          required_keys.add("get_state_hash_code") # Chỉ bắt buộc nếu được cung cấp tường minh
            #      # Else: Sẽ thử auto-hash trong engine

            # Lấy get_state_hash_code (có thể là None nếu TT bật nhưng muốn auto-hash)
            get_state_hash_code = strategy_params.get("get_state_hash_code")

            # Kiểm tra các khóa bắt buộc (không bao gồm get_state_hash_code nữa)
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
            # Validate get_state_hash_code chỉ khi nó được cung cấp
            if get_state_hash_code is not None and (not isinstance(get_state_hash_code, str) or not get_state_hash_code):
                 raise ValueError("If provided, 'get_state_hash_code' must be a non-empty string.")

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

            # Tạo namespace riêng
            logic_namespace = {
                "math": math,
                "copy": copy,
                "logging": logging,
                "random": random, # Thêm random vào namespace để dễ sử dụng trong simulation
                # Thêm các thư viện an toàn khác nếu logic cần
            }

            defined_funcs = {}
            func_codes = {
                "get_legal_actions": get_legal_actions_code,
                "apply_action": apply_action_code,
                "is_terminal": is_terminal_code,
                "simulation_policy": simulation_policy_code
            }
            # Thêm code hash vào chỉ khi được cung cấp
            if get_state_hash_code:
                 func_codes["get_state_hash"] = get_state_hash_code

            current_failed_func_name = None # Theo dõi hàm đang exec để báo lỗi tốt hơn
            try:
                # <<< VALIDATE CODE TRƯỚC KHI EXEC >>>
                func_codes_to_validate = {
                    "get_legal_actions": get_legal_actions_code,
                    "apply_action": apply_action_code,
                    "is_terminal": is_terminal_code,
                    "simulation_policy": simulation_policy_code
                }
                # Thêm code hash vào danh sách validate chỉ khi được cung cấp
                if get_state_hash_code:
                    func_codes_to_validate["get_state_hash"] = get_state_hash_code

                for name, code in func_codes_to_validate.items():
                     current_failed_func_name = name # Cập nhật tên hàm đang validate/exec
                     _validate_code_safety(code, name) # Gọi hàm kiểm tra

                # Nếu kiểm tra qua, tiếp tục với exec
                for name, code in func_codes.items():
                    current_failed_func_name = name # Cập nhật tên hàm đang validate/exec
                    exec(code, globals(), logic_namespace)
                    if name not in logic_namespace or not callable(logic_namespace[name]):
                        # Lỗi này thực sự là lỗi logic trong code cung cấp
                        raise RuntimeError(f"Code provided for '{name}' did not define a callable function named '{name}'. Check the function definition (def {name}(...):).")
                    defined_funcs[name] = logic_namespace[name]
                current_failed_func_name = None # Reset khi exec thành công

            # <<< Xử lý lỗi exec chi tiết hơn >>>
            except ValueError as ve_validate:
                 # Bắt lỗi từ _validate_code_safety
                 raise ValueError(f"Security validation failed for '{current_failed_func_name}': {ve_validate}") from ve_validate
            except SyntaxError as se:
                # Lỗi cú pháp trong code
                error_line = getattr(se, 'lineno', 'unknown')
                error_offset = getattr(se, 'offset', 'unknown')
                error_text = getattr(se, 'text', '').strip()
                raise ValueError(
                    f"Syntax error in provided code for '{current_failed_func_name}' (line ~{error_line}, offset ~{error_offset}): {se.msg}. Problematic code snippet: '{error_text}'"
                ) from se
            except NameError as ne:
                 # Lỗi không tìm thấy biến/hàm
                 missing_name = str(ne).split("'")[1] # Trích xuất tên bị thiếu
                 available_locals = list(logic_namespace.keys())
                 hint = (f"Name '{missing_name}' is not defined. Is it available in the 'problem_context'? "
                         f"Did you forget to import a standard library (only safe ones like 'math', 'random', 'copy' are pre-imported in the execution namespace)? "
                         f"Available names in the execution namespace: {available_locals}. "
                         f"Attempting to import disallowed modules (like 'os', 'sys') will also fail silently or raise errors.")
                 raise ValueError(f"Name error in provided code for '{current_failed_func_name}': {ne}. {hint}") from ne
            except TypeError as te_exec:
                 # Lỗi kiểu dữ liệu khi thực thi định nghĩa hàm (ít gặp nhưng có thể)
                 raise ValueError(f"Type error during definition of function '{current_failed_func_name}': {te_exec}. Check the code logic inside the function.") from te_exec
            except RuntimeError as rte_exec:
                 # Lỗi do raise RuntimeError trong hàm kiểm tra signature/hashable ở dưới, hoặc lỗi logic định nghĩa hàm
                 raise rte_exec # Re-raise lỗi đã được định dạng
            except Exception as e_exec:
                # Bắt các lỗi không mong đợi khác từ exec()
                raise RuntimeError(f"Unexpected error executing provided code definition for '{current_failed_func_name}': {type(e_exec).__name__} - {e_exec}") from e_exec

            # 3. Chuẩn bị Hàm Logic với Context (Sử dụng partial)
            try:
                # Tạo bản sao context
                effective_context = copy.deepcopy(problem_context)
                # Gộp simulation_config vào, ghi đè nếu trùng key
                overwritten_keys = set(effective_context.keys()) & set(simulation_config.keys())
                if overwritten_keys:
                    logging.warning(f"Context keys from 'simulation_config' are overwriting keys in 'problem_context': {overwritten_keys}")
                effective_context.update(simulation_config)

                # Sử dụng effective_context
                get_actions_with_context = partial(defined_funcs["get_legal_actions"], context=effective_context)
                apply_action_with_context = partial(defined_funcs["apply_action"], context=effective_context)
                is_terminal_with_context = partial(defined_funcs["is_terminal"], context=effective_context)
                simulation_policy_with_context = partial(defined_funcs["simulation_policy"], context=effective_context)

                # Kiểm tra nhanh signature các hàm cơ bản
                # <<< Cải thiện báo lỗi signature >>>
                try:
                    # Thử gọi với state giả để kiểm tra signature (không cần context vì partial đã xử lý)
                    # Lưu ý: Giả sử state có thể được dùng độc lập, hoặc tạo state giả đơn giản nếu cần
                    _ = get_actions_with_context(current_state)
                except TypeError as te_sig_get:
                    raise RuntimeError(f"Function 'get_legal_actions' (from code) likely has an incorrect signature or logic error. It should accept 'state' and 'context'. Error during test call: {te_sig_get}")
                # Không thể kiểm tra apply_action dễ dàng vì cần action hợp lệ
                try:
                    _ = is_terminal_with_context(current_state)
                except TypeError as te_sig_term:
                    raise RuntimeError(f"Function 'is_terminal' (from code) likely has an incorrect signature or logic error. It should accept 'state' and 'context'. Error during test call: {te_sig_term}")
                try:
                    _ = simulation_policy_with_context(current_state)
                except TypeError as te_sig_sim:
                    raise RuntimeError(f"Function 'simulation_policy' (from code) likely has an incorrect signature or logic error. It should accept 'state' and 'context'. Error during test call: {te_sig_sim}")
                # <<< Kết thúc cải thiện báo lỗi signature >>>


                # Tạo và kiểm tra hàm hash nếu TT được bật VÀ code được cung cấp
                get_state_hash_func = None
                if enable_transposition_table and get_state_hash_code:
                    if "get_state_hash" not in defined_funcs:
                         # Lỗi này chỉ xảy ra nếu code hash được cung cấp nhưng exec lỗi
                         raise RuntimeError(f"Internal Error: 'get_state_hash' function was provided but not defined after exec. Check the provided code for '{current_failed_func_name}'.")
                    get_state_hash_func = partial(defined_funcs["get_state_hash"], context=effective_context)
                    # <<< Cải thiện báo lỗi hash >>>
                    try:
                        # <<< THAY ĐỔI: Xử lý state ban đầu là list cho kiểm tra >>>
                        state_for_check = current_state
                        if isinstance(state_for_check, list):
                            try:
                                state_for_check = tuple(state_for_check)
                                logging.debug("Initial state is list, converted to tuple for preliminary hash check.")
                            except TypeError:
                                # Nếu không chuyển được list->tuple (ví dụ list chứa dict), thì chắc chắn không hash được
                                raise RuntimeError(
                                    f"Initial state is a list containing unhashable elements and cannot be converted to tuple for hashing. "
                                    f"Cannot use Transposition Table with this state type. State starts with: {str(current_state)[:100]}..."
                                )
                        # <<< KẾT THÚC THAY ĐỔI >>>

                        sample_hash = get_state_hash_func(state_for_check) # Sử dụng state_for_check
                        # Kiểm tra tính hashable
                        try:
                            hash(sample_hash)
                        except TypeError as te_hashable:
                             raise RuntimeError(
                                 f"Function 'get_state_hash' (from code) returned an unhashable type '{type(sample_hash).__name__}'. "
                                 f"The state hash must be an immutable, hashable type (e.g., int, float, str, tuple of hashables). "
                                 f"Value returned: {str(sample_hash)[:100]}..."
                             ) from te_hashable
                    except TypeError as te_sig_hash:
                         # Lỗi signature của hàm hash
                         # <<< Sửa lại thông báo lỗi signature hash >>>
                         # Kiểm tra xem lỗi có phải do thiếu context không
                         if "context" in str(te_sig_hash):
                             raise RuntimeError(f"Function 'get_state_hash' (from code) is missing the 'context' parameter or has incorrect signature. It should accept 'state' and 'context'. Error during test call: {te_sig_hash}")
                         else:
                             raise RuntimeError(f"Function 'get_state_hash' (from code) likely has an incorrect signature or logic error (other than missing context). It should accept 'state' and 'context'. Error during test call: {te_sig_hash}")
                    except RuntimeError as rte_hash_check: # Bắt lỗi unhashable từ trên hoặc lỗi chuyển đổi list->tuple
                         raise rte_hash_check # Re-raise lỗi đã được định dạng
                    except Exception as e_hash_test:
                         # Lỗi khác khi chạy thử hàm hash
                         # Sử dụng hàm helper mới để định dạng lỗi từ code động
                         detailed_error = _format_dynamic_code_error(e_hash_test, 'get_state_hash') # <-- Gọi helper nếu lỗi xảy ra *bên trong* hàm hash
                         raise RuntimeError(f"Error executing 'get_state_hash' function during initial test: {detailed_error}") from e_hash_test
                    # <<< Kết thúc cải thiện báo lỗi hash >>>

            except KeyError as ke:
                # Lỗi này không nên xảy ra nếu bước 2 thành công
                raise RuntimeError(f"Internal Error: Failed to find function '{ke}' after exec. This indicates a problem in the mcts_reasoning function itself.")
            except TypeError as e_partial:
                 # Lỗi nếu hàm gốc không chấp nhận 'context' hoặc có signature sai (đã được xử lý tốt hơn ở trên)
                 # Giữ lại để bắt các trường hợp khác
                problematic_func = "unknown"
                # Cố gắng xác định hàm gây lỗi dựa trên thông điệp lỗi
                if "'get_legal_actions'" in str(e_partial): problematic_func = "get_legal_actions"
                elif "'apply_action'" in str(e_partial): problematic_func = "apply_action"
                elif "'is_terminal'" in str(e_partial): problematic_func = "is_terminal"
                elif "'simulation_policy'" in str(e_partial): problematic_func = "simulation_policy"
                elif "'get_state_hash'" in str(e_partial): problematic_func = "get_state_hash"
                raise RuntimeError(f"Error preparing function '{problematic_func}' with context using partial (likely incorrect function signature in the provided code, missing 'context' parameter?): {e_partial}") from e_partial
            except RuntimeError as rte_sig_hash:
                 # Bắt lỗi từ kiểm tra signature/hash ở trên và re-raise
                 raise rte_sig_hash


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
                debug_simulation_limit=debug_simulation_limit,
                enable_transposition_table=enable_transposition_table, # Truyền vào engine
                get_state_hash_func=get_state_hash_func # Truyền hàm hash vào engine
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

            # Cảnh báo nếu TT được bật cho chiến lược này (không được hỗ trợ)
            if enable_transposition_table:
                 warning_msg = "Warning: Transposition Table (enable_transposition_table=True) is not currently supported for the 'evaluate_options' strategy and will be ignored."
                 logging.warning(warning_msg)
                 base_result["warnings"].append(warning_msg)

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
        # Lỗi do người dùng cung cấp tham số không hợp lệ, strategy không được hỗ trợ, hoặc lỗi cú pháp/name/type trong code cung cấp
        error_msg = f"Invalid parameters, unsupported strategy '{strategy_name}', or error in provided code: {str(ve)}"
        logging.error(error_msg) # Ghi log lỗi đầy đủ
        base_result["message"] = f"Error processing strategy '{strategy_name}': Check parameters and provided code logic. Details: {str(ve)[:500]}..." # Rút gọn cho message
        base_result["error_type"] = "InvalidInputOrCodeError" # Gộp lỗi tham số và lỗi code
        base_result["error_details"] = str(ve) # Chi tiết đầy đủ trong details
        base_result["time_elapsed_seconds"] = time.time() - start_func_time
        return base_result

    except RuntimeError as rte:
         # Lỗi nội bộ (ví dụ: lỗi khi exec code không phải cú pháp/name, lỗi signature hàm động, lỗi test hash)
         error_msg = f"Internal execution error or code logic issue for strategy '{strategy_name}': {str(rte)}"
         logging.error(error_msg, exc_info=True) # Ghi log kèm traceback
         base_result["message"] = f"Execution error for strategy '{strategy_name}'. Details: {str(rte)[:500]}..."
         base_result["error_type"] = "ExecutionOrLogicError" # Đổi loại lỗi
         base_result["error_details"] = str(rte)
         base_result["time_elapsed_seconds"] = time.time() - start_func_time
         return base_result

    except Exception as e:
        # Các lỗi không mong đợi khác
        error_msg = f"Unexpected critical error executing strategy '{strategy_name}': {type(e).__name__} - {e}"
        logging.critical(error_msg, exc_info=True)
        base_result["message"] = error_msg
        base_result["error_type"] = "UnexpectedCriticalError"
        base_result["error_details"] = str(e)
        base_result["time_elapsed_seconds"] = time.time() - start_func_time
        return base_result 