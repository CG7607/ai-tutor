"""用户数据管理——不依赖 Streamlit 的纯数据层."""
import hashlib
import json
from pathlib import Path

USER_DATA_DIR = Path(__file__).parent.parent / "data" / "users"


def _get_user_dir(name: str) -> Path:
    return USER_DATA_DIR / name


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
    (d / "profile.json").write_text(json.dumps(profile, ensure_ascii=False, indent=2))
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
    """加载用户全部数据：聊天、测验、错题."""
    d = _get_user_dir(用户名)
    d.mkdir(parents=True, exist_ok=True)

    def _读文件(文件名):
        fp = d / 文件名
        if fp.exists():
            try:
                return json.loads(fp.read_text())
            except Exception:
                return []
        return []

    return {
        "chat_history": _读文件("chat_history.json"),
        "quiz_history": _读文件("quiz_history.json"),
        "wrong_answers": _读文件("wrong_answers.json"),
    }


def 保存用户数据(用户名: str, 聊天记录: list, 测验记录: list, 错题库: list) -> None:
    """保存用户全部数据到磁盘."""
    d = _get_user_dir(用户名)
    d.mkdir(parents=True, exist_ok=True)
    (d / "chat_history.json").write_text(json.dumps(聊天记录, ensure_ascii=False, indent=2))
    (d / "quiz_history.json").write_text(json.dumps(测验记录, ensure_ascii=False, indent=2))
    (d / "wrong_answers.json").write_text(json.dumps(错题库, ensure_ascii=False, indent=2))
