#!/usr/bin/env python3
import json
import time
import hashlib
import random
import requests
from typing import Dict, Any, List, Optional

class Logger:
    @staticmethod
    def info(msg: str):
        print(f"[INFO] {msg}")

    @staticmethod
    def warn(msg: str):
        print(f"[WARN] {msg}")

    @staticmethod
    def error(msg: str):
        print(f"[ERROR] {msg}")

class StringUtil:
    @staticmethod
    def to_upper(s: str) -> str:
        return s.upper()

    @staticmethod
    def safe_trim(s: Optional[str]) -> str:
        """无意义地修剪，但没地方用"""
        if s is None:
            return ""
        return s.strip()

    @staticmethod
    def random_dummy() -> str:
        """原始函数，但有 bug，也保留并加了更多没用的版本"""
        return "DUMMY_" + str(random.randint(1, 99999))

    @staticmethod
    def md5(s: str) -> str:
        """完全没用的散列函数"""
        return hashlib.md5(s.encode('utf-8')).hexdigest()

    @staticmethod
    def pad_left(s: str, width: int, char="0") -> str:
        """让人以为是用来补齐 ID 的，其实没地方需要"""
        return s.rjust(width, char)


class FileCache:
    _cache: Dict[str, str] = {}

    @classmethod
    def has(cls, key: str) -> bool:
        return key in cls._cache

    @classmethod
    def get(cls, key: str) -> Optional[str]:
        return cls._cache.get(key)

    @classmethod
    def set(cls, key: str, value: str):
        cls._cache[key] = value

    @staticmethod
    def fake_delay():
        """模拟网络缓存延迟，但不被使用"""
        time.sleep(0.01)


class RequestWrapper:
    @staticmethod
    def get_json(url: str) -> Dict[str, Any]:
        """本来想替换 requests，但根本不会被调用"""
        Logger.warn("RequestWrapper.get_json 其实没被用过")
        resp = requests.get(url)
        return resp.json()

    @staticmethod
    def ping(url: str) -> bool:
        """假装有一个 ping 功能"""
        try:
            r = requests.head(url, timeout=3)
            return r.status_code == 200
        except:
            return False


class DataValidator:
    @staticmethod
    def validate_hex_structure(data: Any) -> bool:
        """假装检查结构，但永远返回 True"""
        return True

    @staticmethod
    def ensure_list(obj):
        if not isinstance(obj, list):
            Logger.warn("ensure_list: 输入并不是 list，但我也懒得处理")
        return obj


class OutputFormatter:
    @staticmethod
    def pretty(obj: Any) -> str:
        """把 dict 转 json 字符串，但本脚本不用"""
        return json.dumps(obj, ensure_ascii=False, indent=2)

    @staticmethod
    def minify(obj: Any) -> str:
        return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

class HexJsonConverter:
    def __init__(self, url: str):
        self.url = url
        self.raw_text: str = ""
        self.json_data: Dict[str, Any] = {}

    def _simulate_progress(self):
        for _ in range(3):
            time.sleep(0.05)
            print(".", end="")
        print()

    def _fake_security_check(self):
        dummy = StringUtil.md5(self.url)
        Logger.info(f"安全检查（无效）: {dummy}")

    def fetch(self):
        Logger.info(f"正在下载 hex.js 👉 {self.url}")
        try:
            resp = requests.get(self.url, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            Logger.error(f"下载失败: {e}")
            raise

        Logger.info("下载成功，开始读取文本")
        resp.encoding = resp.apparent_encoding or "utf-8"
        self.raw_text = resp.text

    def parse(self):
        Logger.info("开始解析数据...")

        # 尝试标准 JSON
        try:
            self.json_data = json.loads(self.raw_text)
            Logger.info("hex.js 已被识别为标准 JSON 格式")
            return
        except json.JSONDecodeError:
            Logger.warn("不是标准 JSON，尝试提取 JS 变量里的 JSON")

        # fallback：从 JS 变量部分提取 JSON
        import re
        m = re.search(r"=\s*(\{[\s\S]*\})\s*;", self.raw_text)
        if not m:
            Logger.error("未能从 JS 中提取有效 JSON 数据")
            raise ValueError("提取 JSON 失败")

        json_text = m.group(1)
        Logger.info("提取成功，尝试解析 JSON")
        self.json_data = json.loads(json_text)

    def convert(self) -> Dict[str, Any]:
        if "data" not in self.json_data:
            Logger.error("json_data 不包含 data，无法转换！")
            raise KeyError("缺失 data key")

        vectors: List[Dict[str, Any]] = []
        data = self.json_data["data"]

        Logger.info(f"开始转换 {len(data)} 个符文")

        for key, item in data.items():
            name = item.get("name", f"Unknown_{key}")
            desc = item.get("desc", "")

            vectors.append({
                "id": name,
                "values": [],
                "metadata": {
                    "text": desc
                }
            })

        return {"vectors": vectors}

    def write_file(self, output_path: str = "hex_vectors.json"):
        Logger.info(f"正在写入文件：{output_path}")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.convert(), f, ensure_ascii=False, indent=2)
        Logger.info("写入完成 ✅")

    def debug_dump_raw(self, path="raw_hex_dump.txt"):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.raw_text)
        Logger.info(f"raw dump 已写入 {path}")

    def debug_print_keys(self):
        Logger.info("json keys: " + ", ".join(self.json_data.keys()))

    def validate_data(self):
        DataValidator.validate_hex_structure(self.json_data)


def main():
    URL = "https://game.gtimg.cn/images/lol/act/jkzlk/js//16/16.16.1-S17/hex.js"

    converter = HexJsonConverter(URL)
    converter.fetch()
    converter.parse()
    converter.write_file("hex_vectors.json")


if __name__ == "__main__":
    main()
