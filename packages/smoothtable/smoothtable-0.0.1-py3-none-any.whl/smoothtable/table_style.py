class TableStyle:
    def __init__(self,
                horizontal_line,
                left_vertical_line,
                right_vertical_line,
                center_vertical_line,
                top_left_corner,
                top_right_corner,
                bottom_left_corner,
                bottom_right_corner,
                center_conduit,
                top_center_conduit,
                bottom_center_conduit,
                left_conduit,
                right_conduit):
        
        self.HORIZONTAL_LINE = horizontal_line

        self.LEFT_VERTICAL_LINE = left_vertical_line
        self.RIGHT_VERTICAL_LINE = right_vertical_line
        self.CENTER_VERTICAL_LINE = center_vertical_line

        self.TOP_LEFT_CORNER = top_left_corner
        self.TOP_RIGHT_CORNER = top_right_corner

        self.BOTTOM_LEFT_CORNER = bottom_left_corner
        self.BOTTOM_RIGHT_CORNER = bottom_right_corner

        self.CENTER_CONDUIT = center_conduit

        self.TOP_CENTER_CONDUIT = top_center_conduit
        self.BOTTOM_CENTER_CONDUIT = bottom_center_conduit

        self.LEFT_CONDUIT = left_conduit
        self.RIGHT_CONDUIT = right_conduit


def main():
    style = TableStyle(
        horizontal_line='─',
        left_vertical_line='│ ',
        right_vertical_line=' │',
        center_vertical_line=' │ ',
        top_left_corner='╭─',
        top_right_corner='─╮',
        bottom_left_corner='╰─',
        bottom_right_corner='─╯',
        center_conduit='─┼─',
        top_center_conduit='─┬─',
        bottom_center_conduit='─┴─',
        left_conduit='├─',
        right_conduit='─┤'
    )

    print(style.__dict__)

if __name__ == '__main__':
    main()