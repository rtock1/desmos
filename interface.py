import re
import random

initial_template = """let state = Calc.getState();
let expressions = state.expressions.list;"""

end_template = "Calc.setState(state);"
trig_functions = [
    "sin",
    "cos",
    "tan",
    "csc",
    "sec",
    "cot",
    "sinh",
    "cosh",
    "tanh",
    "csch",
    "sech",
    "coth",
]

inverse_trig_functions = ["arc" + n for n in trig_functions]

calculus = [
    "exp",
    "ln",
    "log",
    "int",
    "sum",
    "prod",
    "sqrt",
]

desmos_operators = [
    "mean",
    "median",
    "min",
    "max",
    "quartile",
    "quantile",
    "stdev",
    "stdevp",
    "var",
    "mad",
    "cov",
    "covp",
    "corr",
    "spearman",
    "stats",
    "count",
    "total",
    "length",
    "join",
    "sort",
    "shuffle",
    "unique",
    "for",
    "histogram",
    "dotplot",
    "boxplot",
    "normaldist",
    "tdist",
    "poissondist",
    "binomialdist",
    "uniformdist",
    "pdf",
    "cdf",
    "inversecdf",
    "random",
    "ttest",
    "tscore",
    "ittest",
    "polygon",
    "distance",
    "midpoint",
    "rgb",
    "hsv",
    "tone",
    "lcm",
    "gcd",
    "mod",
    "ceil",
    "floor",
    "round",
    "sign",
    "nPr",
    "nCr",
    "with",
    "index",
]

latex_expressions = [
    "pi",
]


def convert_to_string(d):
    if isinstance(d, bool):
        return str(d).lower()
    if isinstance(d, str):
        if d.startswith("Desmos."):
            return d
        else:
            return "'" + d + "'"
    if isinstance(d, int) or isinstance(d, float):
        return str(d)
    if isinstance(d, dict):
        fields = []
        for key, value in d.items():
            field_string = str(key) + ": "
            field_string += convert_to_string(value)
            fields.append(field_string)

        return "{ " + ", ".join(fields) + " }"

    if isinstance(d, list):
        return "[" + ", ".join([convert_to_string(n) for n in d]) + "]"

    print("Unknown type: " + type(d))


def clean_latex(latex):
    latex = latex.replace("(", "\\left(")
    latex = latex.replace(")", "\\right)")
    latex = latex.replace("[", "\\left[")
    latex = latex.replace("]", "\\right]")

    latex = latex.replace("\\{", "\\left\\{")
    latex = latex.replace("\\}", "\\right\\}")

    for function in trig_functions:
        latex = re.sub("([^c])" + function, "\\1\\\\" + function, latex)
        latex = re.sub("^(.?.?)" + function, "\\1\\\\" + function, latex)

    for function in inverse_trig_functions:
        latex = latex.replace(function, "\\" + function)

    for function in calculus:
        latex = latex.replace(function, "\\" + function)

    for operator in desmos_operators:
        latex = latex.replace(operator, "\\operatorname{" + operator + "}")

    for expression in latex_expressions:
        latex = latex.replace(expression, "\\" + expression)

    latex = latex.replace("->", "\\to")

    latex = latex.replace("\\", "\\\\")

    return latex


class Graph:
    def __init__(self):
        self.expressions = []
        self.string_lines = ["let state = Calc.getState();"]

    def generate_output(self, filename):
        f = open(filename, "w")
        for expression in self.expressions:
            self.__add_expression_string(expression)

        self.__push_to_calc()
        f.write("\n".join(self.string_lines))

    def get_current_expressions(self):
        self.string_lines.append("let expressions = state.expressions.list;")

    def reset_expressions(self):
        self.string_lines.append("state.expressions.list = []")
        self.get_current_expressions()

    def __add_expression_string(self, expression):
        self.string_lines.append("expressions.push(" + expression.to_string() + ");")
        if isinstance(expression, Folder):
            for nested_expression in expression.get_expressions():
                self.__add_expression_string(nested_expression)

    def append(self, expression):
        self.expressions.append(expression)

    def __push_to_calc(self):
        self.string_lines.append("Calc.setState(state);")


class Line:
    def __init__(self):
        pass

    def to_string(self):
        fields = self._get_fields()

        fields = {k: v for (k, v) in fields.items() if v is not None}

        return convert_to_string(fields)

    def _get_fields(self):
        return {}


class Expression(Line):
    def __init__(self):
        super().__init__()
        self.__type = "expression"
        self.__latex = None
        self.__color_latex = None
        self.__line_style = None
        self.__line_width = None
        self.__line_opacity = None
        self.__point_style = None
        self.__point_size = None
        self.__point_opacity = None
        self.__fill_opacity = None
        self.__points = None
        self.__lines = None
        self.__fill = None
        self.__hidden = None
        self.__readonly = None
        self.__slider_bounds = None
        self.__playing = None
        self.__parametric_domain = None
        self.__polar_domain = None
        self.__id = None
        self.__drag_mode = None
        self.__label = None
        self.__show_label = None
        self.__label_size = None
        self.__label_orientation = None
        self.__clickable_info = None
        self.__folder_id = None

    def _get_fields(self):
        return {
            "type": self.__type,
            "latex": self.__latex,
            "colorLatex": self.__color_latex,
            "lineStyle": self.__line_style,
            "lineWidth": self.__line_width,
            "lineOpacity": self.__line_opacity,
            "pointStyle": self.__point_style,
            "pointSize": self.__point_size,
            "pointOpacity": self.__point_opacity,
            "fillOpacity": self.__fill_opacity,
            "points": self.__points,
            "lines": self.__lines,
            "fill": self.__fill,
            "hidden": self.__hidden,
            "readonly": self.__readonly,
            "sliderBounds": self.__slider_bounds,
            "playing": self.__playing,
            "parametricDomain": self.__parametric_domain,
            "polarDomain": self.__polar_domain,
            "dragMode": self.__drag_mode,
            "label": self.__label,
            "showLabel": self.__show_label,
            "labelSize": self.__label_size,
            "labelOrientation": self.__label_orientation,
            "clickableInfo": self.__clickable_info,
            "folderId": self.__folder_id,
        }

    def set_latex(self, latex: str):
        self.__latex = clean_latex(latex)

    def append_latex(self, latex: str):
        self.__latex += clean_latex(latex)

    def set_color_latex(self, latex: str):
        self.__color_latex = clean_latex(latex)

    def set_line_style(self, line_style: str):
        line_style = line_style.upper()
        line_styles = ["SOLID", "DASHED", "DOTTED"]
        if line_style in line_styles:
            self.__line_style = "Desmos.Styles." + line_style

    def set_line_width(self, width):
        if isinstance(width, float) or isinstance(width, int):
            self.__line_width = str(max(0.0, width))
        elif isinstance(width, str):
            self.__line_width = clean_latex(width)

    def set_line_opacity(self, line_opacity):
        if isinstance(line_opacity, float) or isinstance(line_opacity, int):
            line_opacity = max(0.0, line_opacity)
            self.__line_opacity = str(min(1.0, line_opacity))
        elif isinstance(line_opacity, str):
            self.__line_opacity = clean_latex(line_opacity)

    def set_point_style(self, point_style: str):
        point_style = point_style.upper()
        point_styles = ["POINT", "OPEN", "CROSS"]
        if point_style in point_styles:
            self.__point_style = "Desmos.Styles." + point_style

    def set_point_size(self, point_size):
        if isinstance(point_size, float) or isinstance(point_size, int):
            self.__point_size = str(max(0.0, point_size))
        elif isinstance(point_size, str):
            self.__point_size = clean_latex(point_size)

    def set_point_opacity(self, point_opacity):
        if isinstance(point_opacity, float) or isinstance(point_opacity, int):
            point_opacity = max(0.0, point_opacity)
            self.__point_opacity = str(min(1.0, point_opacity))
        elif isinstance(point_opacity, str):
            self.__point_opacity = clean_latex(point_opacity)

    def set_fill_opacity(self, fill_opacity):
        if isinstance(fill_opacity, float) or isinstance(fill_opacity, int):
            fill_opacity = max(0.0, fill_opacity)
            self.__fill_opacity = str(min(1.0, fill_opacity))
        elif isinstance(fill_opacity, str):
            self.__fill_opacity = clean_latex(fill_opacity)

    def set_points(self, points: bool):
        self.__points = points

    def set_lines(self, lines: bool):
        self.__lines = lines

    def set_fill(self, fill: bool):
        self.__fill = fill

    def set_hidden(self, hidden: bool):
        self.__hidden = hidden

    def set_readonly(self, readonly: bool):
        self.__readonly = readonly

    def set_slider_bounds(self, lower_bound: str = None, upper_bound: str = None, step: str = None):
        self.__slider_bounds = {"min": lower_bound, "max": upper_bound, "step": step}
        self.__slider_bounds = {k: v for (k, v) in self.__slider_bounds.items() if v is not None}

    def set_playing(self, playing: bool):
        self.__playing = playing

    def set_parametric_domain(self, lower_bound: str = None, upper_bound: str = None):
        self.__parametric_domain = {"min": lower_bound, "max": upper_bound}
        self.__parametric_domain = {k: v for (k, v) in self.__parametric_domain.items() if v is not None}

    def set_polar_domain(self, lower_bound: str = None, upper_bound: str = None):
        self.__polar_domain = {"min": lower_bound, "max": upper_bound}
        self.__polar_domain = {k: v for (k, v) in self.__polar_domain.items() if v is not None}

    def set_drag_mode(self, drag_mode: str):
        drag_mode = drag_mode.upper()
        drag_modes = ["X", "Y", "XY", "NONE"]
        if drag_mode in drag_modes:
            self.__drag_mode = "Desmos.DragModes." + drag_mode

    def set_label(self, label: str):
        self.__label = label

    def set_show_label(self, show_label: bool):
        self.__show_label = show_label

    def set_label_size(self, label_size: str):
        self.__label_size = clean_latex(label_size)

    def set_label_orientation(self, orientation: str):
        orientation = orientation.upper()
        orientations = ["ABOVE", "BELOW", "LEFT", "RIGHT", "DEFAULT"]
        if orientation in orientations:
            self.__drag_mode = "Desmos.LabelOrientations." + orientation

    def set_clickable_info(self, latex: str, enabled: bool = True):
        self.__clickable_info = {"enabled": enabled, "latex": clean_latex(latex)}

    def add_to_folder(self, folder_id: str):
        if isinstance(self, Folder):
            return
        self.__folder_id = folder_id


class Folder(Line):
    def __init__(self):
        super().__init__()
        self.__type = "folder"
        self.__id = str(random.randint(-2147483648, 2147483647))
        self.__collapsed = None
        self.__title = None
        self.__hidden = None
        self.__secret = None
        self.__readonly = None
        self.__expressions = []

    def _get_fields(self):
        return {
            "type": self.__type,
            "id": self.__id,
            "title": self.__title,
            "collapsed": self.__collapsed,
            "hidden": self.__hidden,
            "secret": self.__secret,
            "readonly": self.__readonly
        }

    def set_title(self, title: str):
        self.__title = title

    def set_collapsed(self, collapsed: bool):
        self.__collapsed = collapsed

    def set_hidden(self, hidden: bool):
        self.__hidden = hidden

    def set_secret(self, secret: bool):
        self.__secret = secret

    def set_readonly(self, readonly: bool):
        self.__readonly = readonly

    def add_expression(self, expression: Expression):
        if isinstance(expression, Folder):
            return

        self.__expressions.append(expression)
        expression.add_to_folder(self.__id)

    def add_expressions(self, expressions: [Expression]):
        for expression in expressions:
            self.add_expression(expression)

    def get_expressions(self):
        return self.__expressions


class Table(Line):
    def __init__(self):
        super().__init__()
        self.__type = "table"
        self.__id = str(random.randint(-2147483648, 2147483647))
        self.__columns = []
        self.__regression = None
        self.__readonly = None

    def _get_fields(self):
        return {
            "type": self.__type,
            "id": self.__id,
            "columns": self.__columns,
            "regression": self.__regression,
            "readonly": self.__readonly,
        }

    def add_column(self):
        self.__columns.append({})
        self.__columns[-1]["id"] = str(random.randint(-2147483648, 2147483647))

    def set_column_latex(self, column_number: int, latex: str):
        if 0 <= column_number < len(self.__columns):
            self.__columns[column_number]["latex"] = clean_latex(latex)

    def set_column_values(self, column_number: int, latex_array: [str]):
        if 0 <= column_number < len(self.__columns):
            self.__columns[column_number]["values"] = [clean_latex(n) for n in latex_array]

    def set_column_color(self, column_number: int, color_latex: str):
        if 0 <= column_number < len(self.__columns):
            self.__columns[column_number]["color"] = clean_latex(color_latex)

    def set_column_hidden(self, column_number: int, hidden: bool):
        if 0 <= column_number < len(self.__columns):
            self.__columns[column_number]["hidden"] = hidden

    def set_column_points(self, column_number: int, points: bool):
        if 0 <= column_number < len(self.__columns):
            self.__columns[column_number]["points"] = points

    def set_column_lines(self, column_number: int, lines: bool):
        if 0 <= column_number < len(self.__columns):
            self.__columns[column_number]["lines"] = lines

    def set_column_line_style(self, column_number: int, line_style: str):
        if 0 <= column_number < len(self.__columns):
            line_style = line_style.upper()
            line_styles = ["SOLID", "DASHED", "DOTTED"]
            if line_style in line_styles:
                self.__columns[column_number]["lineStyle"] = "Desmos.Styles." + line_style

    def set_column_line_width(self, column_number: int, width):
        if 0 <= column_number < len(self.__columns):
            if isinstance(width, float) or isinstance(width, int):
                self.__columns[column_number]["lineWidth"] = str(max(0.0, width))
            elif isinstance(width, str):
                self.__columns[column_number]["lineWidth"] = clean_latex(width)

    def set_column_line_opacity(self, column_number: int, opacity):
        if 0 <= column_number < len(self.__columns):
            if isinstance(opacity, float) or isinstance(opacity, int):
                opacity = max(0.0, opacity)
                self.__columns[column_number]["lineOpacity"] = str(min(1.0, opacity))
            elif isinstance(opacity, str):
                self.__columns[column_number]["lineOpacity"] = clean_latex(opacity)

    def set_column_point_style(self, column_number: int, point_style: str):
        if 0 <= column_number < len(self.__columns):
            point_style = point_style.upper()
            point_styles = ["POINT", "OPEN", "CROSS"]
            if point_style in point_styles:
                self.__columns[column_number]["pointStyle"] = "Desmos.Styles." + point_style

    def set_column_point_size(self, column_number: int, size):
        if 0 <= column_number < len(self.__columns):
            if isinstance(size, float) or isinstance(size, int):
                self.__columns[column_number]["pointSize"] = str(max(0.0, size))
            elif isinstance(size, str):
                self.__columns[column_number]["pointSize"] = clean_latex(size)

    def set_column_point_opacity(self, column_number: int, opacity: float):
        if 0 <= column_number < len(self.__columns):
            if isinstance(opacity, float) or isinstance(opacity, int):
                opacity = max(0.0, opacity)
                self.__columns[column_number]["pointOpacity"] = str(min(1.0, opacity))
            elif isinstance(opacity, str):
                self.__columns[column_number]["pointOpacity"] = clean_latex(opacity)

    def set_column_drag_mode(self, column_number: int, drag_mode: str):
        if 0 <= column_number < len(self.__columns):
            drag_mode = drag_mode.upper()
            drag_modes = ["X", "Y", "XY", "NONE"]
            if drag_mode in drag_modes:
                self.__columns[column_number]["dragMode"] = "Desmos.DragModes." + drag_mode

    def add_regression(self):
        self.__regression = {}

    def remove_regression(self):
        self.__regression = None

    def set_regression_color(self, color_latex: str):
        if self.__regression is None:
            return
        self.__regression["color"] = clean_latex(color_latex)

    def set_regression_columns(self, x_column_index, y_column_index):
        if self.__regression is None:
            return
        x_column_id = self.__columns[x_column_index].get("id")
        y_column_id = self.__columns[y_column_index].get("id")
        self.__regression["columnIds"] = {}
        self.__regression["columnIds"]["x"] = x_column_id
        self.__regression["columnIds"]["y"] = y_column_id

    def set_regression_hidden(self, hidden: bool):
        if self.__regression is None:
            return
        self.__regression["hidden"] = hidden

    def set_regression_log_mode(self, log_mode: bool):
        if self.__regression is None:
            return
        self.__regression["isLogMode"] = log_mode

    def set_regression_line_style(self, line_style: str):
        if self.__regression is None:
            return
        line_style = line_style.upper()
        line_styles = ["SOLID", "DASHED", "DOTTED"]
        if line_style in line_styles:
            self.__regression["lineStyle"] = "Desmos.Styles." + line_style

    def set_regression_residual_variable(self, residual_variable: str):
        if self.__regression is None:
            return
        self.__regression["residualVariable"] = clean_latex(residual_variable)

    def set_regression_type(self, regression_type: str):
        if self.__regression is None:
            return
        regression_type = regression_type.lower()
        regression_types = ["linear", "quadratic", "exponential", "logarithmic", "power", "logistic"]
        if regression_type in regression_types:
            self.__regression["type"] = regression_type

    def set_readonly(self, readonly: bool):
        self.__readonly = readonly


class Text(Line):
    def __init__(self):
        super().__init__()
        self.__type = "text"
        self.__text = None
        self.__readonly = None

    def _get_fields(self):
        return {
            "type": self.__type,
            "text": self.__text,
            "readonly": self.__readonly
        }

    def set_text(self, text: str):
        self.__text = text

    def set_readonly(self, readonly: bool):
        self.__readonly = readonly
