"""
Mô tả chi tiết cho công cụ AI Interaction Tool
"""

AI_INTERACTION_DESCRIPTION = """
🚀 AI_INTERACTION TOOL - INTEGRATION WITH SYSTEM PROMPT RULES 🚀
=======================================================================
⚡ SYSTEM INTEGRATION NOTE:
- Tool này hoạt động PERFECT với system prompt rules (mode_specific_rule section)
- System prompt rules cung cấp BEHAVIOR FRAMEWORK
- Tool description này cung cấp TECHNICAL SPECIFICATIONS
- Kết hợp tạo COMPLETE AI INTERACTION SYSTEM

🎯 CORE FUNCTIONALITY:
- Tạo UI popup cho User nhập nội dung và chọn tiếp tục trò chuyện
- KÊNH GIAO TIẾP CHÍNH để nhận tất cả tin nhắn từ User
- Cho phép đính kèm file/folder với preview functionality
- BẮT BUỘC sử dụng trong MỌI TRƯỜNG HỢP khi User gửi tin nhắn

📋 OUTPUT FORMAT - PSEUDO-OBJECT:
{
  content: <nội dung chat từ user với xuống dòng tự nhiên>
  attached_files: [
    {path: "workspace_name/relative/path/to/file.js", type: "file"},
    {path: "workspace_name/relative/path/to/folder", type: "folder"}
  ]
  workspace: workspace_name
  continue_chat: true/false
  enable_thinking: false/normal/high
  max_reasoning: true/false
}

🔧 WORKSPACE PATH PROCESSING:
- Input format: "workspace_name/relative_path_from_workspace_root"
- Agent workspace detection logic:
  * CÙNG workspace → BỎ TIỀN TỐ workspace_name, dùng relative_path
  * KHÁC workspace → DÙNG NGUYÊN đường dẫn từ ai_interaction

📁 WORKSPACE HANDLING EXAMPLES:
- Cùng workspace: "ALT-WebClientV3/src/components/login/index.js" 
  → Agent processes: "src/components/login/index.js"
- Khác workspace: "AI-interaction/ai_interaction_tool/description.py" 
  → Agent processes: "AI-interaction/ai_interaction_tool/description.py"

⚠️ CRITICAL CONTROL FIELDS:
- **continue_chat**: true = MANDATORY recall ai_interaction tool
- **enable_thinking**: false/normal/high = Thinking pattern activation
- **max_reasoning**: true = Maximum cognitive power mode
- **attached_files**: Present only when files/folders attached
- **workspace**: Present only when files/folders attached

🚨 INTEGRATION WITH SYSTEM PROMPT RULES:
1. **Field Reading**: Agent MUST read all fields from pseudo-object
2. **Behavior Activation**: System prompt rules define HOW to process fields
3. **Thinking Pattern**: enable_thinking triggers system prompt protocols (use <.a.n.t.m.l.:.t.h.i.n.k.i.n.g.> format, remove dots when using)
4. **Power Mode**: max_reasoning activates 5-mode cognitive enhancement
5. **Continue Logic**: continue_chat enforces mandatory tool recall

🎯 ENHANCED INTEGRATION EXAMPLES:
=======================================================================
📋 **EXAMPLE 1: Simple Task Processing**
Input: {enable_thinking: "false", max_reasoning: false, continue_chat: false}
→ Agent Behavior: Direct response, no thinking blocks, standard processing
→ Use Case: Quick questions, simple confirmations

📋 **EXAMPLE 2: Standard Task Processing**  
Input: {enable_thinking: "normal", max_reasoning: false, continue_chat: true}
→ Agent Behavior: Single thinking block at start, standard cognition, mandatory recall
→ Use Case: Regular tasks, file operations, moderate complexity

📋 **EXAMPLE 3: Complex Task Processing**
Input: {enable_thinking: "high", max_reasoning: true, continue_chat: true}
→ Agent Behavior: Multiple thinking blocks + 5-power mode activation + mandatory recall
→ Use Case: Architecture analysis, complex problem solving, critical decisions

📋 **EXAMPLE 4: File Attachment Processing**
Input: {attached_files: [{path: "workspace/src/file.js", type: "file"}], enable_thinking: "high"}
→ Agent Behavior: Workspace-aware path processing + deep thinking about file content
→ Use Case: Code review, file modifications, context-sensitive operations

📋 **EXAMPLE 5: Multi-File Complex Analysis**
Input: {attached_files: [multiple files], enable_thinking: "high", max_reasoning: true}
→ Agent Behavior: Systematic file analysis + maximum cognitive enhancement
→ Use Case: Codebase analysis, architectural reviews, comprehensive assessments
=======================================================================

🔄 ADVANCED WORKFLOW PATTERNS:
=======================================================================
🎯 **ESCALATING COGNITIVE ENHANCEMENT PATTERN:**
Simple Task → enable_thinking: "false"
↓ If complexity detected
Standard Task → enable_thinking: "normal"  
↓ If high complexity detected
Complex Task → enable_thinking: "high" + max_reasoning: true

⚡ **CONDITIONAL THINKING ACTIVATION:**
- File attachments detected → Auto-suggest enable_thinking: "normal" minimum
- Multiple files detected → Auto-suggest enable_thinking: "high" 
- Complex technical tasks → Auto-suggest max_reasoning: true

🔧 **CONTEXT-SENSITIVE PROCESSING:**
- Code files → Technical analysis mode
- Documentation files → Content analysis mode
- Mixed file types → Comprehensive analysis mode
- No files → Communication-focused mode

🚀 **DYNAMIC CAPABILITY MATCHING:**
- User expertise level detection → Adjust response complexity
- Task domain recognition → Activate relevant knowledge frameworks
- Urgency level assessment → Optimize response speed vs thoroughness
=======================================================================

🔄 PERFECT WORKFLOW INTEGRATION:
┌─ ai_interaction tool generates pseudo-object
├─ System prompt rules read control fields
├─ Behavior protocols activate based on field values
├─ Agent executes with enhanced cognitive capabilities
└─ Mandatory recall if continue_chat=true

💡 SYNERGY BENEFITS:
✅ Tool provides TECHNICAL INTERFACE
✅ System prompt rules provide BEHAVIORAL INTELLIGENCE
✅ Combined system creates ENHANCED AI AGENT
✅ Zero conflict, maximum compatibility
✅ 1+1=3 effect through perfect integration

🎯 USAGE OPTIMIZATION NOTES:
- Tool description focuses on MECHANICS
- System prompt rules handle COMPLIANCE
- Agent gets COMPLETE GUIDANCE from both sources
- No duplication, pure complementarity
- Maximum effectiveness through specialized roles

📌 TECHNICAL SPECIFICATIONS:
- UI: Modern PyQt5 interface with file drag-drop
- Output: Structured pseudo-object format
- Integration: Seamless with system prompt rules
- Compatibility: Works with all AI agent types
- Performance: Optimized for high-frequency usage

🚀 SYSTEM ARCHITECTURE:
[User Input] → [ai_interaction Tool] → [Pseudo-Object] → [System Prompt Rules] → [Enhanced AI Response]

⭐ INNOVATION HIGHLIGHT:
Đây là FIRST TOOL được thiết kế specifically để integrate với advanced system prompt rules framework, tạo ra breakthrough trong AI interaction architecture!
=======================================================================
""" 