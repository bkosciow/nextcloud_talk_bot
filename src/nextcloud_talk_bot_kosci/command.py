from typing import List, Dict, Any, Optional


class Command:
    def __init__(self, patterns: List[str] = []):
        self.patterns: List[str] = patterns
        self.command: Optional[str] = None
        self.params: Dict[str, Any] = {}
        self.result: bool = False

    def system_command(self, obj):
        self.command = "event." + obj.type
        self.params = obj
        self.result = True

        return self.result

    def parse(self, text: str) -> bool:
        text = text.strip()
        self.result = False
        if not text or not self.patterns:
            self.result = False
        self.command = None
        self.params = {}

        if not self.patterns:
            return False

        for pattern in self.patterns:
            if "<prompt>" in pattern:
                parts = text.split(' ', 1)
                if len(parts) < 2:
                    return False
                self.command = parts[0]
                self.params['text'] = parts[1]
                self.result = True
            else:
                pattern_parts = pattern.split()
                text_parts = text.split()

                if len(pattern_parts) > 0 and len(text_parts) > 0 and len(pattern_parts) == len(text_parts):
                    pattern_command = pattern_parts[0]
                    text_command = text_parts[0]

                    if pattern_command == text_command:
                        self.command = text_command
                        self.params = {}

                        for i, pattern_part in enumerate(pattern_parts[1:], 1):
                            if i < len(text_parts):
                                param_name = pattern_part[1:-1]  # Remove < and >
                                self.params[param_name] = text_parts[i]

                        self.result = True

        return self.result

    def param(self, name: str) -> Optional[Any]:
        return self.params[name] if name in self.params else None

    def __getattr__(self, name: str, default: Optional[Any] = None) -> Optional[Any]:
        if name in self.params:
            return self.params[name]

        if name == 'command':
            return self.command

        if name == 'params':
            return self.params

        return default


if __name__ == '__main__':
    p = [
        '!sl <action>', '!sl <action> <module>', '!say <prompt>'
    ]

    cmd = Command(p)
    cmd.parse("!sl data")
    assert "!sl" == cmd.command
    assert "data" == cmd.param("action")
    assert "data" == cmd.action

    cmd.parse("")
    assert None is cmd.command
    assert {} == cmd.params

    cmd.parse("!sl")
    assert None is cmd.command
    assert {} == cmd.params

    cmd.parse("!sl ")
    assert None is cmd.command
    assert {} == cmd.params

    cmd.parse("!sl air bb")
    assert "!sl" == cmd.command
    assert "air" == cmd.param("action")
    assert "air" == cmd.action
    assert "bb" == cmd.param("module")
    assert "bb" == cmd.module

    cmd.parse("")

    cmd.parse("a")
    cmd.parse("a a")

    cmd = Command(p)
    cmd.parse("!say hello my friend")
    assert "!say" == cmd.command
    assert "hello my friend" == cmd.param("text")






