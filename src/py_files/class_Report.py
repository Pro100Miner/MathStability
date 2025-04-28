from PyQt5.QtWidgets import QWidget
from src.py_files.report import Ui_Report
import sympy as sp
import subprocess
import os
from jinja2 import Environment, FileSystemLoader
from src.py_files.calculate_stability_zones import get


class Report(QWidget):
    def __init__(self, app_data, settings, point):
        super().__init__()
        self.ui = Ui_Report()
        self.ui.setupUi(self)
        self.settings = settings
        self.app_data = app_data
        self.point = point
        self.ui.pushButton_2.clicked.connect(self.close)

        self.diff_eq, self.general_solution, self.cauchy_solution = self.solve_equation()
        self.create_pdf_report()
    def solve_equation(self):
        t = sp.symbols('t')
        y = sp.Function('y')

        a, b, c, d = [sp.sympify(self.app_data[i]) for i in ['a', 'b', 'c', 'd']]
        y0 = sp.sympify(self.app_data['y'])
        y0_prime = sp.sympify(self.app_data['y_diff'])

        # Уравнение с сохранением порядка производных
        lhs = sp.Add(
            a * y(t).diff(t, t),
            b * y(t).diff(t),
            c * y(t),
            evaluate=False
        )
        diff_eq = sp.Eq(lhs, d)

        general_solution = sp.dsolve(diff_eq)
        cauchy_solution = sp.dsolve(diff_eq, ics={
            y(0): y0,
            y(t).diff(t).subs(t, 0): y0_prime
        })

        return diff_eq, general_solution, cauchy_solution

    def create_pdf_report(self):
        print(self.is_mathieu_equation())
        is_mathieu, a, b = self.is_mathieu_equation()
        if is_mathieu:
            is_stability, number = get(a, b)
            context = {
                'equation': sp.latex(self.diff_eq),
                'is_mathieu': is_mathieu,
                'zones': {'is_stability': 'устойчивости' if is_stability else "неустойчивости", 'number': number}
            }
        else:
            context = {
                'equation': sp.latex(self.diff_eq),
                'general_solution': sp.latex(self.general_solution),
                'cauchy_solution': sp.latex(self.cauchy_solution),
                'initial_conditions': {
                    'y0': self.app_data['y'],
                    'y0_prime': self.app_data['y_diff']
                },
                'point_solution': self.get_point_solution(),
                'is_mathieu': is_mathieu,
            }

        # Генерация LaTeX
        env = Environment(
            loader=FileSystemLoader('src/report_files/templates'),
            autoescape=True
        )

        template = env.get_template('report.j2')
        rendered_tex = template.render(**context)

        # Сохранение и компиляция
        os.makedirs('src/report_files', exist_ok=True)
        tex_path = 'src/report_files/output.tex'

        with open(tex_path, 'w', encoding='utf-8') as f:
            f.write(rendered_tex)

        try:
            subprocess.run([
                'pdflatex',
                '-interaction=nonstopmode',
                '-output-directory=src/report_files/',
                tex_path
            ], check=True)

            # Очистка временных файлов
            for ext in ['aux', 'log']:
                try:
                    os.remove(f'src/report_files/output.{ext}')
                except FileNotFoundError:
                    pass

        except subprocess.CalledProcessError as e:
            print(f"Ошибка компиляции LaTeX: {e}")

    def get_point_solution(self):
        if self.point is not None:
            try:
                t = sp.symbols('t')
                value = self.cauchy_solution.rhs.subs(t, self.point)
                return {
                    'point': self.point,
                    'exact': sp.latex(value),
                    'approx': f"{float(value):.4f}"
                }
            except Exception:
                return None
        return None

    def is_mathieu_equation(self):
        """Определяет, является ли уравнение уравнением Матье и извлекает параметры a, b"""
        try:
            t = sp.symbols('t')
            y = sp.Function('y')(t)

            # Получаем левую часть уравнения (приведенного к виду expr = 0)
            expr = self.diff_eq.lhs - self.diff_eq.rhs

            # Проверяем, что уравнение имеет вид y'' + c*y = 0
            if not expr.has(y.diff(t, t)):
                return False, None, None

            # Извлекаем коэффициент перед y(t)
            coeff = sp.collect(expr, y).coeff(y)

            # Пытаемся представить коэффициент в виде a + b*cos(t)
            if not isinstance(coeff, sp.Add):
                return False, None, None

            # Разбиваем на части и ищем a и b
            a_term = None
            b_term = None

            for term in coeff.args:
                if term.is_constant():
                    a_term = float(term)
                elif term.has(sp.cos(t)):
                    b_term = float(term.coeff(sp.cos(t)))

            if a_term is not None and b_term is not None:
                return True, a_term, b_term

            return False, None, None

        except Exception as e:
            print(f"Ошибка при анализе уравнения: {e}")
            return False, None, None