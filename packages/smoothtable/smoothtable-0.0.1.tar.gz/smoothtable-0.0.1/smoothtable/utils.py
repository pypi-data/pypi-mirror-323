# Columns to rows conversion

def columnsToRowGen(columns, rowIndex):
    for column in columns:
        yield column[rowIndex]

def columnsToRow(columns, rowIndex):
    return list(columnsToRowGen(columns, rowIndex))

def columnsToRowsGen(columns):
    for rowIndex in range(len(columns[0])):
        yield columnsToRow(columns, rowIndex)

def columnsToRows(columns):
    return list(columnsToRowsGen(columns))



# Rows to columns conversion

def rowsToColumnGen(rows, columnIndex):
    for row in rows:
        yield row[columnIndex]

def rowsToColumn(rows, columnIndex):
    return list(rowsToColumnGen(rows, columnIndex))

def rowsToColumnsGen(rows):
    for rowIndex in range(len(rows[0])):
        yield rowsToColumn(rows, rowIndex)

def rowsToColumns(rows):
    return list(rowsToColumnsGen(rows))



# Other utils

def stringifyColumnsGen(columns):
    for column in columns:
        yield list(map(str, column))

def stringifyColumns(columns):
    return list(stringifyColumnsGen(columns))

def leftConcatGen(lines, linesToAdd):
    for lineToAdd, line in zip(linesToAdd, lines):
        yield lineToAdd + line

def leftConcat(lines, linesToAdd):
    return list(leftConcatGen(lines, linesToAdd))