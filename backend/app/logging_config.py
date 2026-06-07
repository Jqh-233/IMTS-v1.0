"""IMTS 日志配置 — 提供模块级 logger 工厂"""
import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """获取模块级 logger，统一使用 imts 命名空间"""
    logger = logging.getLogger(f"imts.{name}")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)-5s] %(name)s | %(message)s",
                datefmt="%H:%M:%S",
            )
        )
        logger.addHandler(handler)
    return logger


def setup_logging(level: int = logging.INFO) -> None:
    """初始化根 logger 级别"""
    logging.getLogger("imts").setLevel(level)
