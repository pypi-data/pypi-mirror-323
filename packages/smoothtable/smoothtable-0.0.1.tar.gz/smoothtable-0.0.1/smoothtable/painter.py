from typing import Iterable
from color_condition import ColorCondition
from extra_variable import ExtraVariable
from utils import columnsToRowsGen, rowsToColumns
from constants import COLORS, TEXT_STYLES


def paintString(string, color, style):
    color = COLORS[color]
    style = TEXT_STYLES[style]
    string = color + style + "{}\033[0m".format(string)
    return string


class Painter:
    def __init__(self, colorConditions: Iterable[ColorCondition]):
        self.colorConditions = colorConditions

    def paintArray(self, array, condition: ColorCondition):
        extra = ExtraVariable()

        if condition.initMethod:
            condition.initMethod(array, extra)
            
        for index, item in enumerate(array):
            args = [locals()[argName] for argName in condition.args]

            if condition.method(*args):
                yield paintString(item, condition.color, condition.style)
            else:
                yield item           
    

    def paintArrays(self, arrays, condition: ColorCondition):
        for array in arrays:
            yield list(self.paintArray(array, condition))

    def paint(self, columns):
        for condition in self.colorConditions:
            match(condition.type):
                case 'column':
                    columns = list(self.paintArrays(columns, condition))
                case 'row':
                    rows = columnsToRowsGen(columns)
                    rows = list(self.paintArrays(rows, condition))
                    columns = rowsToColumns(rows)

        return columns

def main():
    cond = ColorCondition(
        type='row',
        args='item',
        method=lambda item: len(item) == 3,
        color='red',
        style='bold'
    )

    columns = [["asas", 'dajkijda', '1ga']]

    painter = Painter([cond])
    painted = painter.paint(columns)

    print(painted)

if __name__ == '__main__':
    main()