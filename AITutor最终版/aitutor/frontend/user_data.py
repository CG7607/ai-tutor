"""用户数据管理——不依赖 Streamlit 的纯数据层（v2.1 原子写入 + 自动备份）."""
import hashlib
import json
import traceback
from datetime import datetime
from pathlib import Path

USER_DATA_DIR = Path(__file__).parent.parent / "data" / "users"
LOG_DIR = Path(__file__).parent.parent / "data"

# 单个数据文件最大 50MB — 超过后在加载时给出警告
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024


def _get_user_dir(name: str) -> Path:
    return USER_DATA_DIR / name


def _写错误日志(信息: str) -> None:
    """将错误写入 data/error.log，不抛出异常."""
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        log_path = LOG_DIR / "error.log"
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {信息}\n{traceback.format_exc()}\n")
    except Exception:
        pass  # 日志写入失败不影响主流程


def _原子写入(文件路径: Path, 数据) -> None:
    """先写 .tmp，成功后原子 rename，防止写入中途崩溃损坏数据."""
    tmp_path = 文件路径.with_suffix(文件路径.suffix + ".tmp")
    tmp_path.write_text(json.dumps(数据, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_path.replace(文件路径)  # os.replace 是原子操作


def _备份后写入(文件路径: Path, 数据) -> None:
    """先备份旧文件为 .bak，再原子写入新数据."""
    if 文件路径.exists():
        bak_path = 文件路径.with_suffix(文件路径.suffix + ".bak")
        try:
            文件路径.replace(bak_path)
        except Exception:
            pass  # 备份失败不影响写入
    _原子写入(文件路径, 数据)


def _安全读列表(文件路径: Path) -> tuple[list, list[str]]:
    """
    安全读取 JSON 列表文件，返回 (数据, 警告列表).

    - 文件不存在 → ([], [])
    - 读取/解析失败 → 记录日志，尝试 .bak 恢复，保留现场不覆盖
    - 文件过大 → 警告但正常读取
    """
    警告 = []
    if not 文件路径.exists():
        return [], 警告

    # 文件大小检查
    try:
        size = 文件路径.stat().st_size
        if size > MAX_FILE_SIZE_BYTES:
            警告.append(f"⚠️ {文件路径.name} 文件较大（{size / 1024 / 1024:.1f}MB），建议清理历史记录。")
    except Exception:
        pass

    # 主读取
    try:
        raw = 文件路径.read_text(encoding="utf-8")
        data = json.loads(raw)
        if not isinstance(data, list):
            _写错误日志(f"数据格式异常（非列表）: {文件路径}")
            警告.append(f"⚠️ {文件路径.name} 格式异常，已重置为空。")
            return [], 警告
        return data, 警告
    except json.JSONDecodeError as e:
        _写错误日志(f"JSON 解析失败: {文件路径} — {e}")
    except MemoryError:
        _写错误日志(f"文件过大无法加载: {文件路径}")
        return [], [f"⚠️ {文件路径.name} 过大无法加载，请手动清理。"]
    except Exception as e:
        _写错误日志(f"读取文件异常: {文件路径} — {e}")

    # 尝试从 .bak 恢复
    bak_path = 文件路径.with_suffix(文件路径.suffix + ".bak")
    if bak_path.exists():
        try:
            data = json.loads(bak_path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                警告.append(f"📋 已从备份恢复 {文件路径.name}")
                return data, 警告
        except Exception as e:
            _写错误日志(f"备份恢复也失败: {bak_path} — {e}")

    # 无法恢复 — 返回空列表但不覆盖原文件（保留现场等用户处理）
    警告.append(f"⚠️ {文件路径.name} 读取失败，原文件已保留。请联系管理员。")
    return [], 警告


def 密码哈希(密码: str) -> str:
    """SHA-256 哈希密码."""
    return hashlib.sha256(密码.encode()).hexdigest()


def 用户存在(用户名: str) -> bool:
    """检查用户是否已注册."""
    return (_get_user_dir(用户名) / "profile.json").exists()


def 注册用户(用户名: str, 密码: str) -> bool:
    """注册新用户."""
    d = _get_user_dir(用户名)
    d.mkdir(parents=True, exist_ok=True)
    profile = {"password_hash": 密码哈希(密码)}
    _原子写入(d / "profile.json", profile)
    return True


def 验证密码(用户名: str, 密码: str) -> bool:
    """验证用户密码."""
    fp = _get_user_dir(用户名) / "profile.json"
    if not fp.exists():
        return False
    try:
        profile = json.loads(fp.read_text())
        return profile.get("password_hash") == 密码哈希(密码)
    except Exception:
        return False


def 加载用户数据(用户名: str) -> dict:
    """
    加载用户全部数据：聊天、测验、错题.

    返回值新增 _warnings 字段——调用方应检查并展示警告。
    """
    d = _get_user_dir(用户名)
    d.mkdir(parents=True, exist_ok=True)

    chat, w1 = _安全读列表(d / "chat_history.json")
    quiz, w2 = _安全读列表(d / "quiz_history.json")
    wrong, w3 = _安全读列表(d / "wrong_answers.json")

    all_warnings = w1 + w2 + w3

    return {
        "chat_history": chat,
        "quiz_history": quiz,
        "wrong_answers": wrong,
        "_warnings": all_warnings,
    }


def 保存用户数据(用户名: str, 聊天记录: list, 测验记录: list, 错题库: list) -> None:
    """保存用户全部数据到磁盘（原子写入 + 自动备份）."""
    d = _get_user_dir(用户名)
    d.mkdir(parents=True, exist_ok=True)
    _备份后写入(d / "chat_history.json", 聊天记录)
    _备份后写入(d / "quiz_history.json", 测验记录)
    _备份后写入(d / "wrong_answers.json", 错题库)
