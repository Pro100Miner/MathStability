import shutil
import os
import subprocess
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFileDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtCore import QUrl

from src.py_files.report import Ui_Report
from jinja2 import Environment, FileSystemLoader
from src.py_files.calculate_stability_zones import get
from src.py_files.message_error import show_warning


class Report(QWidget):
    def __init__(self, app_data, settings, point):
        super().__init__()
        self.ui = Ui_Report()
        self.ui.setupUi(self)
        self.ui.label.setVisible(False)
        self.settings = settings
        self.app_data = app_data
        self.point = point
        self.pdf_viewer = QWebEngineView()
        self.viewer_layout = QVBoxLayout(self.ui.frame)
        self.viewer_layout.addWidget(self.pdf_viewer)

        self.ui.pushButton_2.clicked.connect(self.close_report)
        self.ui.pushButton.clicked.connect(self.save_report)

    def run(self):
        self.diff_eq, self.general_solution, self.cauchy_solution = self.solve_equation()
        if None in (self.diff_eq, self.general_solution, self.cauchy_solution):
            return False

        self.plot_graphs()
        self.create_pdf_report()
        pdf_path = os.path.abspath("src/report_files/output.pdf")
        if os.path.exists(pdf_path):
            url = QUrl.fromLocalFile(pdf_path)
            self.pdf_viewer.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
            self.pdf_viewer.load(url)
        else:
            show_warning("Ошибка", f"Файл PDF не найден: {pdf_path}")
            return False
        return True

    def plot_graphs(self):
        try:
            # Аналитическое решение
            t = sp.symbols('t')
            y = sp.Function('y')(t)
            y0 = float(self.app_data['y'])
            y0_prime = float(self.app_data['y_diff'])

            y_sol = self.cauchy_solution.rhs
            t_vals = np.linspace(0, 20, 1000)
            y_vals = [float(y_sol.subs(t, val).evalf()) for val in t_vals]

            # Улучшенный график решения
            plt.figure(figsize=(10, 5))
            plt.plot(t_vals, y_vals, label=f"$y(t)$", linewidth=2)
            plt.title("График аналитического решения", fontsize=14)
            plt.xlabel("Время $t$", fontsize=12)
            plt.ylabel("Решение $y(t)$", fontsize=12)
            settings_sol = self.app_data['settings_sol']
            if settings_sol:
                plt.xlim(settings_sol['t_min'], settings_sol['t_max'])
                plt.ylim(settings_sol['y_min'], settings_sol['y_max'])
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.legend(fontsize=12)
            plt.tight_layout()
            plt.savefig("src/report_files/graph_solution.png", dpi=300, bbox_inches='tight')
            plt.close()

            y_prime = sp.diff(y_sol, t)
            y_prime_vals = [float(y_prime.subs(t, val).evalf()) for val in t_vals]

            # Улучшенный фазовый портрет
            plt.figure(figsize=(6, 6))
            plt.plot(y_vals, y_prime_vals, label="Фазовый портрет", linewidth=2)
            plt.title("Фазовый портрет решения", fontsize=14)
            plt.xlabel("$y(t)$", fontsize=12)
            plt.ylabel("$y'(t)$", fontsize=12)
            settings_phase = self.app_data['settings_phase']
            if settings_sol:
                plt.xlim(settings_phase["y'_min"], settings_phase["y'_max"])
                plt.ylim(settings_phase['y_min_f'], settings_phase['y_max_f'])
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.savefig("src/report_files/phase_portrait.png", dpi=300, bbox_inches='tight')
            plt.close()

        except Exception as e:
            print(f"Аналитическое решение не найдено, переходим к численному: {e}")

            # Численное решение с обработкой функций
            try:
                # Получаем строки с функциями
                a_str = self.app_data['a']
                b_str = self.app_data['b']
                c_str = self.app_data['c']
                d_str = self.app_data['d']

                # Преобразуем строки в функции
                a = eval(f"lambda t: {a_str}") if isinstance(a_str, str) else lambda t: float(a_str)
                b = eval(f"lambda t: {b_str}") if isinstance(b_str, str) else lambda t: float(b_str)
                c = eval(f"lambda t: {c_str}") if isinstance(c_str, str) else lambda t: float(c_str)
                d = eval(f"lambda t: {d_str}") if isinstance(d_str, str) else lambda t: float(d_str)

                # Проверка на ноль в знаменателе
                def check_a(t):
                    a_val = a(t)
                    if np.isclose(a_val, 0):
                        raise ValueError(f"a(t) = 0 при t = {t}")
                    return a_val

                def system(t, Y):
                    y, yp = Y
                    try:
                        a_t = check_a(t)
                        return [yp, (d(t) - b(t) * yp - c(t) * y) / a_t]
                    except ValueError as ve:
                        print(ve)
                        return [yp, 0]  # Альтернативная обработка

                t_vals = np.linspace(0, 20, 1000)
                sol = solve_ivp(system, [0, 20],
                                [float(self.app_data['y']),
                                 float(self.app_data['y_diff'])],
                                t_eval=t_vals,
                                method='RK45')

                plt.figure(figsize=(8, 4))
                plt.plot(sol.t, sol.y[0], label="y(t)")
                plt.title("График численного решения y(t)")
                plt.xlabel("t")
                plt.ylabel("y")
                plt.grid(True)
                settings_sol = self.app_data['settings_sol']
                print("--------", settings_sol)
                if settings_sol:
                    plt.xlim(settings_sol['t_min'], settings_sol['t_max'])
                    plt.ylim(settings_sol['y_min'], settings_sol['y_max'])
                plt.legend()
                plt.tight_layout()
                plt.savefig("src/report_files/graph_solution.png")
                plt.close()

                plt.figure(figsize=(5, 5))
                plt.plot(sol.y[0], sol.y[1], label="Фазовый портрет")
                plt.title("Фазовый портрет (численный)")
                plt.xlabel("y")
                plt.ylabel("y'")
                settings_phase = self.app_data['settings_phase']
                if settings_sol:
                    plt.xlim(settings_phase["y'_min"], settings_phase["y'_max"])
                    plt.ylim(settings_phase['y_min_f'], settings_phase['y_max_f'])
                plt.grid(True)
                plt.tight_layout()
                plt.savefig("src/report_files/phase_portrait.png")
                plt.close()

            except Exception as num_err:
                print(f"Ошибка численного решения: {num_err}")
                # Здесь можно добавить обработку ошибок численного метода

    def is_analytical_solution(self):
        if self.general_solution.rhs.has(sp.Integral, sp.RootOf, sp.Order):
            return False
        return True

    def save_report(self):
        source_path = os.path.abspath("src/report_files/output.pdf")

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить PDF",
            "отчет.pdf",
            "PDF Files (*.pdf)"
        )
        if save_path:
            try:
                shutil.copyfile(source_path, save_path)
            except Exception as e:
                show_warning("Ошибка", f"Не удалось сохранить файл: {e}")
                return
        self.ui.label.setVisible(True)

    def close_report(self):
        os.remove(f'src/report_files/output.pdf')
        self.close()

    def solve_equation(self):
        t = sp.symbols('t')
        y = sp.Function('y')

        a, b, c, d = [sp.sympify(self.app_data[i]) for i in ['a', 'b', 'c', 'd']]
        y0 = sp.sympify(self.app_data['y'])
        y0_prime = sp.sympify(self.app_data['y_diff'])

        lhs = sp.Add(
            a * y(t).diff(t, t),
            b * y(t).diff(t),
            c * y(t),
        )
        diff_eq = sp.Eq(lhs, d)

        try:
            general_solution = sp.dsolve(diff_eq)
        except Exception as e:
            show_warning("Ошибка", "Не удалось решить уравнение: " + str(e))
            return None, None, None

        try:
            ics = {y(0): y0}
            if a != 0:
                ics[y(t).diff(t).subs(t, 0)] = y0_prime
            cauchy_solution = sp.dsolve(diff_eq, ics=ics)
        except Exception as e:
            show_warning("Ошибка", "Не удалось решить задачу Коши: " + str(e))
            return None, None, None

        return diff_eq, general_solution, cauchy_solution

    def add_graphs_to_context(self, context):
        """Добавляет пути к графикам в контекст отчета"""
        graph_files = {
            'solution_graph': 'graph_solution.png',
            'phase_portrait': 'phase_portrait.png'
        }

        # Проверяем существование файлов графиков
        for key, filename in graph_files.items():
            path = os.path.join('src/report_files/', filename)
            if os.path.exists(path):
                context[key] = path
            else:
                context[key] = None

        return context

    def create_pdf_report(self):
        is_mathieu, a, b = self.is_mathieu_equation()

        # Создаем базовый контекст
        if is_mathieu:
            is_stability, number = get(a, b)
            context = {
                'equation': sp.latex(self.diff_eq),
                'is_mathieu': is_mathieu,
                'zones': {'is_stability': 'устойчивости' if is_stability else "неустойчивости", 'number': number}
            }
        else:
            t = sp.symbols('t')
            y = sp.Function('y')
            ins = {'y0': self.app_data['y']}
            if self.diff_eq.lhs.coeff(y(t).diff(t, t)) != 0:
                ins['y0_prime'] = self.app_data['y_diff']
            context = {
                'equation': sp.latex(self.diff_eq),
                'general_solution': sp.latex(self.general_solution),
                'cauchy_solution': sp.latex(self.cauchy_solution),
                'initial_conditions': ins,
                'point_solution': self.get_point_solution(),
                'is_mathieu': is_mathieu,
            }

        # Добавляем графики в контекст
        context = self.add_graphs_to_context(context)

        try:
            env = Environment(
                loader=FileSystemLoader('src/report_files/templates'),
                autoescape=True
            )
            template = env.get_template('report.j2')
            rendered_tex = template.render(**context)

            os.makedirs('src/report_files', exist_ok=True)
            tex_path = 'src/report_files/output.tex'
        except Exception as e:
            show_warning("Ошибка", "Не удалось создать LaTeX документ: " + str(e))
            return

        with open(tex_path, 'w', encoding='utf-8') as f:
            f.write(rendered_tex)

        try:
            subprocess.run([
                self.app_data['path_to_tex'],
                '-interaction=nonstopmode',
                '-output-directory=src/report_files/',
                tex_path
            ], check=True)

            for ext in ['output.aux', 'output.log', 'graph_solution.png', 'phase_portrait.png']:
                try:
                    os.remove(f'src/report_files/{ext}')
                except FileNotFoundError:
                    pass

        except Exception as e:
            show_warning("Ошибка", f"Ошибка компиляции LaTeX: {str(e)}. Убедитесь, что у вас установлен и выбран LaTeX компилятор.")
            return

    def get_point_solution(self):
        if self.point is not None:
            try:
                t = sp.symbols('t')
                value = self.cauchy_solution.rhs.subs(t, self.point)
                return {
                    'point': self.point,
                    'exact': sp.latex(value),
                    'approx': f"{value:.4f}"
                }
            except Exception as e:
                show_warning("Ошибка", f"не удалось найти значение в точке: {e}")
                return None
        return None

    def is_mathieu_equation(self):
        try:
            t = sp.symbols('t')
            y = sp.Function('y')(t)
            expr = self.diff_eq.lhs - self.diff_eq.rhs

            if not expr.has(y.diff(t, t)):
                return False, None, None

            coeff = sp.collect(expr, y).coeff(y)

            if not isinstance(coeff, sp.Add):
                return False, None, None

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
            show_warning("Ошибка", f"Ошибка при анализе уравнения: {e}")
            return False, None, None
