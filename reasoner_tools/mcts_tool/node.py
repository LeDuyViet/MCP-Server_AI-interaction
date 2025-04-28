# -*- coding: utf-8 -*-
"""
Định nghĩa lớp MCTSNode.
"""

import math
import random
import logging
from typing import List, Any, Optional

class MCTSNode:
    """
    Đại diện cho một nút trong cây Monte Carlo Tree Search.
    """
    def __init__(self, state: Any,
                 parent: Optional['MCTSNode'] = None,
                 action: Optional[Any] = None,
                 untried_actions: Optional[List[Any]] = None,
                 is_terminal: bool = False):
        """
        Khởi tạo một nút MCTS.

        Args:
            state: Trạng thái được biểu diễn bởi nút này.
            parent: Nút cha trong cây (None nếu là nút gốc).
            action: Hành động dẫn đến nút này từ nút cha.
            untried_actions: Danh sách các hành động hợp lệ chưa được thử từ trạng thái này.
            is_terminal: True nếu trạng thái này là trạng thái kết thúc.
        """
        self.state = state
        self.parent = parent
        self.children: List['MCTSNode'] = []
        self.action = action # Hành động dẫn đến nút này

        self.visits: int = 0
        self.reward: float = 0.0 # Tổng phần thưởng tích lũy từ các mô phỏng đi qua nút này

        self.is_terminal: bool = is_terminal
        # Tạo bản sao của danh sách để tránh thay đổi ngoài ý muốn
        self.untried_actions: List[Any] = list(untried_actions) if untried_actions is not None else []

    def is_fully_expanded(self) -> bool:
        """Kiểm tra xem tất cả các hành động từ nút này đã được thử (đã tạo nút con) chưa."""
        # Nếu không còn hành động chưa thử thì nút đã được mở rộng hoàn toàn
        return len(self.untried_actions) == 0

    def best_child(self, exploration_constant: float = 1.414) -> 'MCTSNode':
        """
        Chọn nút con tốt nhất dựa trên công thức UCB1 (Upper Confidence Bound 1).

        Args:
            exploration_constant (C): Hệ số cân bằng giữa khám phá (exploration)
                                      và khai thác (exploitation).

        Returns:
            Nút con có điểm UCB1 cao nhất.

        Raises:
            ValueError: Nếu nút không có con.
            ZeroDivisionError: Nếu nút cha có visits = 0 (không nên xảy ra trong luồng MCTS chuẩn).
        """
        if not self.children:
            raise ValueError("Cannot select best child from a node with no children.")

        # Tránh lỗi log(0) nếu nút cha chưa được thăm (về mặt lý thuyết không nên xảy ra khi gọi best_child)
        if self.visits == 0:
            # Nếu nút cha chưa được thăm, tất cả các con cũng chưa được thăm.
            # Trả về một nút con ngẫu nhiên để bắt đầu khám phá.
            # Hoặc có thể raise lỗi vì logic MCTS không nên chọn best_child từ nút chưa thăm.
            logging.warning("best_child called on a node with zero visits. Returning random child.")
            return random.choice(self.children)
            # raise ZeroDivisionError("Cannot compute UCB1 score for children of a node with zero visits.")

        log_total_parent_visits = math.log(self.visits)

        def ucb1_score(node: 'MCTSNode') -> float:
            """Tính điểm UCB1 cho một nút con."""
            if node.visits == 0:
                # Ưu tiên các nút chưa được thăm bằng cách gán điểm số rất cao (vô cực)
                return float('inf')

            # Khai thác: Phần thưởng trung bình của nút con
            exploitation_term = node.reward / node.visits
            # Khám phá: Mức độ không chắc chắn
            exploration_term = exploration_constant * math.sqrt(log_total_parent_visits / node.visits)

            return exploitation_term + exploration_term

        # Chọn nút con có điểm UCB1 cao nhất
        best_node = max(self.children, key=ucb1_score)
        return best_node

    def add_child(self, child_state: Any, action: Any, untried_actions: List[Any], is_terminal: bool) -> 'MCTSNode':
        """
        Tạo và thêm một nút con mới vào nút hiện tại.

        Args:
            child_state: Trạng thái của nút con mới.
            action: Hành động dẫn đến nút con này.
            untried_actions: Danh sách các hành động chưa thử từ trạng thái con.
            is_terminal: Trạng thái con có phải là trạng thái kết thúc không.

        Returns:
            Nút con vừa được tạo và thêm vào.
        """
        child_node = MCTSNode(
            state=child_state,
            parent=self,
            action=action,
            untried_actions=untried_actions, # Hàm tạo MCTSNode sẽ tự copy list
            is_terminal=is_terminal
        )
        self.children.append(child_node)
        return child_node

    def __repr__(self) -> str:
        """Biểu diễn dạng chuỗi của nút để dễ debug."""
        # Giới hạn độ dài của state để tránh in quá nhiều
        state_repr = str(self.state)
        if len(state_repr) > 100:
            state_repr = state_repr[:100] + "..."
        return (
            f"MCTSNode(state={state_repr}, visits={self.visits}, reward={self.reward:.4f}, "
            f"terminal={self.is_terminal}, children={len(self.children)}, untried={len(self.untried_actions)}, "
            f"action={self.action})"
        ) 