import json
import os
import sys
from models.config import get_translations_path

TRANSLATIONS = {
    "English": {
        "settings": "Settings",
        "api_url": "API URL:",
        "model": "Model:",
        "server_status": "Server Status:",
        "server_status_checking": "Server Status: Checking...",
        "server_status_connected": "Server Status: Connected",
        "server_status_error": "Server Status: Error",
        "server_status_not_connected": "Server Status: Not Connected",
        "check_server": "Check Server",
        "setup_help": "Setup Help",
        "check_updates": "Check Updates",
        "new_version": "New Version Available",
        "up_to_date": "Up to Date",
        "input_words": "Input Words",
        "enter_words": "Enter words, separated by commas",
        "generate": "Generate",
        "append": "Append",
        "generating": "Generating sentences...",
        "generated_sentences": "Generated Sentences",
        "export_docx": "Export to Word",
        "show_all": "Show All",
        "hide_all": "Hide All",
        "delete_all": "Delete All",
        "show": "Show",
        "hide": "Hide",
        "copy": "Copy",
        "move_up": "Move Up",
        "move_down": "Move Down",
        "delete": "Delete",
        "language": "Language:",
        "server_status_title": "Server Status",
        "server_connected_msg": "Successfully connected to Ollama server!\n\nServer version: {version}",
        "server_error_msg": "Unable to connect to Ollama server.\n\nPlease check if the server is running and the URL is correct.",
        "server_connection_error_msg": "Unable to connect to Ollama server. Please ensure:\n\n1. Ollama is installed\n2. Server is running ('ollama serve')\n3. API URL is correct\n\nError: {error}",
        "server_error_title": "Server Error",
        "server_connection_guide": "Unable to connect to Ollama server. Please ensure:\n1. Ollama is installed\n2. Server is running ('ollama serve')\n3. Model is installed ('ollama pull llama2')\nClick \"Setup Help\" for more information.",
        "warning_title": "Warning",
        "no_sentences_warning": "No sentences to export!",
        "document_title_prompt": "Enter document title:",
        "save_document_title": "Save Document",
        "export_success_title": "Success",
        "export_success_msg": "Document exported successfully!",
        "update_available_title": "Update Available",
        "update_available_msg": "New version available (v{version})!\n\nCurrent version: v{current_version}\n\nWould you like to visit the download page?",
        "no_updates_title": "No Updates",
        "no_updates_msg": "You are using the latest version (v{version})",
        "error_title": "Error",
        "update_check_error": "Failed to check for updates. Please try again later.",
        "update_error_msg": "Failed to check for updates:\n{error}",
        "prompt_error_msg": "Failed to read prompt file: {error}\nUsing default prompt.",
        "generation_error_msg": "Failed to generate sentence: {error}\nPlease check server settings and connection.",
        "unexpected_error_msg": "An unexpected error occurred: {error}",
        "startup_error_msg": "Error starting application:\n{error}",
        "using_default_prompt": "Using default prompt",
        "using_custom_prompt": "Using custom prompt",
        "toggle_prompt": "Toggle Prompt",
        "invalid_prompt_format": "Invalid prompt format: missing {word} placeholder.\nPlease add {word} placeholder in prompt.txt file.",
        "word_analysis": "Word Analysis",
        "regenerate_analysis": "Regenerate Analysis",
        "include_analysis_title": "Include Analysis",
        "include_analysis_prompt": "Do you want to include word analysis in the answer key?",
        "analysis_generation_failed": "Failed to generate analysis. Please try again.",
        "word": "Word",
        "sentence": "Sentence",
        "analyze": "Analyze",
        "close": "Close",
        "generating_analyses": "Generating Analyses",
        "edit": "Edit",
        "edit_sentence": "Edit Sentence",
        "edit_warning": "Editing the sentence will remove any existing analysis.",
        "save": "Save",
        "cancel": "Cancel",
        "edit_analysis": "Edit Analysis",
        "save_analysis": "Save Analysis"
    },
    "zh": {
        "settings": "设置",
        "api_url": "API URL:",
        "model": "模型:",
        "server_status": "服务器状态:",
        "server_status_checking": "服务器状态: 检查中...",
        "server_status_connected": "服务器状态: 已连接",
        "server_status_error": "服务器状态: 错误",
        "server_status_not_connected": "服务器状态: 未连接",
        "check_server": "检查服务器",
        "setup_help": "设置帮助",
        "check_updates": "检查更新",
        "new_version": "有新版本可用",
        "up_to_date": "已是最新版本",
        "input_words": "输入单词",
        "enter_words": "输入单词，用逗号分隔",
        "generate": "生成",
        "append": "附加",
        "generating": "生成句子...",
        "generated_sentences": "生成的句子",
        "export_docx": "导出为Word",
        "show_all": "显示所有",
        "hide_all": "隐藏所有",
        "delete_all": "删除所有",
        "show": "显示",
        "hide": "隐藏",
        "copy": "复制",
        "move_up": "上移",
        "move_down": "下移",
        "delete": "删除",
        "language": "语言:",
        "server_status_title": "服务器状态",
        "server_connected_msg": "成功连接到Ollama服务器！\n\n服务器版本: {version}",
        "server_error_msg": "无法连接到Ollama服务器。\n\n请检查服务器是否正在运行并且URL是否正确。",
        "server_connection_error_msg": "无法连接到Ollama服务器。请确保：\n\n1. Ollama已安装\n2. 服务器正在运行 ('ollama serve')\n3. API URL是否正确\n\n错误: {error}",
        "server_error_title": "服务器错误",
        "server_connection_guide": "无法连接到Ollama服务器。请确保：\n1. Ollama已安装\n2. 服务器正在运行 ('ollama serve')\n3. 模型已安装 ('ollama pull llama2')\n点击 \"设置帮助\" 获取更多信息。",
        "warning_title": "警告",
        "no_sentences_warning": "没有句子可以导出！",
        "document_title_prompt": "输入文档标题:",
        "save_document_title": "保存文档",
        "export_success_title": "成功",
        "export_success_msg": "文档导出成功！",
        "update_available_title": "有更新可用",
        "update_available_msg": "有新版本可用 (v{version})!\n\n当前版本: v{current_version}\n\n是否要访问下载页面？",
        "no_updates_title": "没有更新",
        "no_updates_msg": "您使用的是最新版本 (v{version})",
        "error_title": "错误",
        "update_check_error": "检查更新失败，请稍后再试。",
        "update_error_msg": "检查更新失败:\n{error}",
        "prompt_error_msg": "读取提示文件失败: {error}\n使用默认提示。",
        "generation_error_msg": "生成句子失败: {error}\n请检查服务器设置和连接。",
        "unexpected_error_msg": "发生意外错误: {error}",
        "startup_error_msg": "启动应用程序失败:\n{error}",
        "using_default_prompt": "使用默认提示",
        "using_custom_prompt": "使用自定义提示",
        "toggle_prompt": "切换提示",
        "invalid_prompt_format": "无效提示格式: 缺少 {word} 占位符。\n请在提示文件中添加 {word} 占位符。",
        "word_analysis": "单词分析",
        "regenerate_analysis": "重新生成分析",
        "include_analysis_title": "包含分析",
        "include_analysis_prompt": "是否在答案中包含单词分析？",
        "analysis_generation_failed": "生成分析失败，请重试。",
        "word": "单词",
        "sentence": "句子",
        "analyze": "分析",
        "close": "关闭",
        "generating_analyses": "正在生成分析",
        "edit": "编辑",
        "edit_sentence": "编辑句子",
        "edit_warning": "编辑句子将删除现有分析。",
        "save": "保存",
        "cancel": "取消",
        "edit_analysis": "编辑分析",
        "save_analysis": "保存分析"
    }
}

def load_translations():
    """Load translations from external files."""
    try:
        # Get the translations directory path
        translations_dir = get_translations_path()
        
        # Check for translation files
        if os.path.exists(translations_dir):
            try:
                files = os.listdir(translations_dir)
                for file in files:
                    if file.endswith('.json'):
                        file_path = os.path.join(translations_dir, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                lang_translations = json.load(f)
                                TRANSLATIONS.update(lang_translations)
                        except Exception:
                            continue
            except Exception:
                pass
        
        return list(TRANSLATIONS.keys())
    except Exception:
        return list(TRANSLATIONS.keys())

def get_translation(language, key):
    """Get translation for the given language and key."""
    return TRANSLATIONS.get(language, {}).get(key, key)