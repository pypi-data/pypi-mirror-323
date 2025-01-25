from typing import Iterable
from constants import COLORS, TEXT_STYLES

class ColorCondition:
    ARGS = ('item', 'index', 'array', 'extra')
    ARGS_TYPES = (str, Iterable)
    CONDITION_TYPES = ('row', 'column')

    def __init__(self, type, method, args, color, style, initMethod=None):
        self.type = self.validateType(type)
        self.method = method
        self.args = self.interprateArgs(args)
        self.initMethod = initMethod
        self.color = self.validateColor(color)
        self.style = self.validateStyle(style)

    @staticmethod
    def stringifyItems(items):
        separator = ', '
        items = ("'" + item + "'" for item in items)
        return separator.join(items)

    @classmethod
    def interprateArgs(cls, args):
        if type(args) not in cls.ARGS_TYPES:
            raise ValueError(f"Invalid args type: '{type(args)}'!")

        if isinstance(args, str):
            args = args.split()

        if not all((arg in cls.ARGS for arg in args)):
            raise ValueError(f"Invalid args passed: {cls.stringifyItems(args)}! "
                             f"Possible args: {cls.stringifyItems(cls.ARGS)}.")
    
        return args

    @classmethod
    def validateType(cls, type):
        if type not in cls.CONDITION_TYPES:
            raise ValueError(f"Wrong condition type: '{type}' "
                             f"Possible types: {cls.stringifyItems(cls.CONDITION_TYPES)}.")

        return type

    @classmethod
    def validateColor(cls, color):
        if color not in COLORS:
            raise ValueError(f"Wrong color: '{color}' "
                             f"Possible colors: {cls.stringifyItems(COLORS.keys())}.")

        return color
    
    @classmethod
    def validateStyle(cls, style):
        if style not in TEXT_STYLES:
            raise ValueError(f"Wrong text style: '{style}'! "
                             f"Possible text styles: {cls.stringifyItems(TEXT_STYLES.keys())}.")

        return style


def main():
    condition = ColorCondition(
        type='row',
        args='as',
        method=lambda item: len(item) == 3,
        color='red',
        style='bold'
    )

    print(condition.__dict__)

if __name__ == '__main__':
    main()