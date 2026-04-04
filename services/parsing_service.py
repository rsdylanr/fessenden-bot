import re
import shlex
import json
import math
import unicodedata
import uuid
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

class ParsingService:
    """
    Fessenden Framework: High-Performance Syntax Engine.
    Stateless architecture for interpretation, purification, and security.
    """
    __slots__ = ['bot', 'sanitizer', 'tokenizer', 'caster', 'resolver', 'validator', 'math_engine', 'logic_registry']

    def __init__(self, bot):
        self.bot = bot
        
        # Compiled Regex Registry (High-Speed Pattern Matching)
        self.logic_registry = {
            "id": re.compile(r"([0-9]{17,20})"),
            "mention": re.compile(r"<@!?([0-9]+)>|<#([0-9]+)>|<@&([0-9]+)>"),
            "ipv4": re.compile(r"(\d{1,3}\.){3}\d{1,3}"),
            "zero_width": re.compile(r"[\u200b-\u200f\uFEFF\u202a-\u202e]"),
            "bidi_override": re.compile(r"[\u202a-\u202e]"),
            "math_implicit": re.compile(r'(\d)\('),
            "hex_color": re.compile(r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$")
        }

        # Sub-Domain Initialization
        self.sanitizer = self.Sanitizer(self)
        self.tokenizer = self.Tokenizer(self)
        self.caster = self.Caster(self)
        self.resolver = self.Resolver(self)
        self.validator = self.Validator(self)
        self.math_engine = self.MathEngine(self)

    # --- DOMAIN 1 & 13: THE SANITIZER (Hygiene) ---
    class Sanitizer:
        __slots__ = ['service']
        def __init__(self, service): self.service = service

        def remove_zero_width_spaces(self, text: str) -> str:
            return self.service.logic_registry["zero_width"].sub("", text)

        def normalize_unicode_composition(self, text: str) -> str:
            """Prevents bypasses using combined characters."""
            return unicodedata.normalize('NFC', text)

        def flatten_homoglyphs(self, text: str) -> str:
            """Normalizes visually similar scripts (e.g. Cyrillic 'а' to Latin 'a')."""
            return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

    # --- DOMAIN 2 & 15: THE TOKENIZER (Structure) ---
    class Tokenizer:
        __slots__ = ['service']
        def __init__(self, service): self.service = service

        def tokenize(self, text: str) -> List[str]:
            """Quote-aware shlex tokenization."""
            try:
                return shlex.split(text)
            except ValueError:
                return text.split()

        def extract_flags(self, tokens: List[str]) -> Dict[str, Any]:
            """Parses --key=value patterns."""
            flags = {}
            for t in tokens:
                if t.startswith("--"):
                    parts = t.lstrip("-").split("=", 1)
                    flags[parts[0]] = parts[1] if len(parts) > 1 else True
            return flags

    # --- DOMAIN 3 & 11: THE CASTER (Determinism) ---
    class Caster:
        __slots__ = ['service']
        def __init__(self, service): self.service = service

        def to_int(self, text: str) -> Optional[int]:
            try: return int(text)
            except: return None

        def to_bool(self, text: str) -> bool:
            return text.lower() in ("true", "1", "on", "yes", "enable")

        def to_seconds(self, text: str) -> int:
            """Parses 1h30m to total seconds."""
            units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
            total = 0
            matches = re.findall(r"(\d+)([smhd])", text.lower())
            for val, unit in matches:
                total += int(val) * units[unit]
            return total

    # --- DOMAIN 6 & 21: THE MATH ENGINE (Above Algebra 1) ---
    class MathEngine:
        __slots__ = ['service']
        def __init__(self, service): self.service = service

        def resolve_implicit(self, text: str) -> str:
            """5(2) -> 5*(2)"""
            return self.service.logic_registry["math_implicit"].sub(r'\1*(', text)

    # --- DOMAIN 9 & 11: THE VALIDATOR (Security) ---
    class Validator:
        __slots__ = ['service']
        def __init__(self, service): self.service = service

        def is_bidi_safe(self, text: str) -> bool:
            """Detects RTL override character exploits."""
            return not bool(self.service.logic_registry["bidi_override"].search(text))

        def check_nesting(self, text: str, limit: int = 15) -> bool:
            """Prevents logic bombs via deep recursion."""
            depth = 0
            for char in text:
                if char in "([{": depth += 1
                if char in ")]}": depth -= 1
                if depth > limit: return False
            return True

    # --- DOMAIN 12: THE MASTER HAND-OFF ---
    def finalize_immutable_context(self, raw_input: str) -> Dict[str, Any]:
        """Processes raw input into a purified, read-only data object."""
        # 1. Clean
        text = self.sanitizer.remove_zero_width_spaces(raw_input)
        text = self.sanitizer.normalize_unicode_composition(text)
        
        # 2. Break down
        tokens = self.tokenizer.tokenize(text)
        
        # 3. Construct Result
        return {
            "metadata": {
                "parse_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().timestamp(),
                "raw_length": len(raw_input)
            },
            "structure": {
                "command": tokens[0].lower() if tokens else None,
                "arguments": tokens[1:] if len(tokens) > 1 else [],
                "flags": self.tokenizer.extract_flags(tokens)
            },
            "security": {
                "is_bidi_safe": self.validator.is_bidi_safe(text),
                "is_nesting_safe": self.validator.check_nesting(text)
            }
        }
