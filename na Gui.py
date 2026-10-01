# -*- coding: utf-8 -*-
"""
مشروع تحليل عددي - واجهة رسومية بلغة بايثون (Tkinter)
========================================================
للتشغيل:
    1) تأكد من تثبيت المكتبات المطلوبة:
       pip install numpy arabic-reshaper python-bidi
    2) شغّل الملف:           python numerical_analysis_gui.py

ملاحظة مهمة عن كتابة الدوال f(x):
    استخدم صيغة بايثون، مثال:
    x**2 + 3*x - 5      بدلاً من     x^2 + 3x - 5
    الدوال المتاحة: sin, cos, tan, exp, log, log10, sqrt, pi, e, abs

ملاحظة عن اتجاه النص العربي:
    Tkinter لا يدعم اتجاه الكتابة من اليمين لليسار (RTL) بشكل تلقائي،
    لذلك نستخدم مكتبتي arabic_reshaper و python-bidi لإعادة تشكيل
    وترتيب أي نص عربي قبل عرضه، عبر الدالة ar() أدناه. إن لم تكونا
    مثبّتتين، يعمل البرنامج بشكل طبيعي لكن قد يظهر النص العربي
    بترتيب غير صحيح.
"""

import re
import tkinter as tk
from tkinter import messagebox, ttk
import numpy as np
import math

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    _BIDI_AVAILABLE = True
except ImportError:
    _BIDI_AVAILABLE = False

_ARABIC_RE = re.compile(r'[\u0600-\u06FF]')


def ar(text):
    """يعيد تشكيل النص العربي ويرتّبه بصريًا (RTL) ليظهر بشكل سليم في Tkinter.
    لا يغيّر النصوص الخالية من حروف عربية (كالجداول الرقمية/الإنجليزية)."""
    text = str(text)
    if not _BIDI_AVAILABLE or not _ARABIC_RE.search(text):
        return text
    try:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped, base_dir='R')
    except Exception:
        return text


def finalize(lines):
    """يطبّق ar() على كل سطر من مخرجات الحل قبل دمجها في نص واحد."""
    return "\n".join(ar(line) for line in lines)


# ============================================================
#                  1) بيئة حساب الدوال f(x)
# ============================================================

MATH_NAMESPACE = {
    'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
    'exp': math.exp, 'log': math.log, 'log10': math.log10,
    'sqrt': math.sqrt, 'pi': math.pi, 'e': math.e,
    'abs': abs, 'pow': pow,
    'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
}


def f_of_x(expr, x):
    ns = dict(MATH_NAMESPACE)
    ns['x'] = x
    return eval(expr, {"__builtins__": {}}, ns)


def numeric_derivative(expr, x, h=1e-6):
    return (f_of_x(expr, x + h) - f_of_x(expr, x - h)) / (2 * h)


# ============================================================
#            2) طرق حل المعادلات غير الخطية
# ============================================================

def bisection_method(expr, a, b, tol, max_iter):
    """كل صف: (i, c, a, b, fa, fb, fc, width) حيث width = |a-b| لتلك الفترة."""
    fa = f_of_x(expr, a)
    fb = f_of_x(expr, b)
    if fa * fb > 0:
        raise ValueError("يجب أن يكون f(a) و f(b) بإشارتين متعاكستين")
    rows = [(0, None, a, b, fa, fb, None, abs(b - a))]
    c = (a + b) / 2
    for i in range(1, max_iter + 1):
        c = (a + b) / 2
        fc = f_of_x(expr, c)
        width = abs(b - a)
        rows.append((i, c, a, b, fa, fb, fc, width))
        if abs(fc) < tol or width / 2 < tol:
            return c, rows, True
        if fa * fc < 0:
            b, fb = c, fc
        else:
            a, fa = c, fc
    return c, rows, False


def secant_method(expr, x0, x1, tol, max_iter):
    rows = []
    f0 = f_of_x(expr, x0)
    f1 = f_of_x(expr, x1)
    x2 = x1
    for i in range(1, max_iter + 1):
        if (f1 - f0) == 0:
            raise ZeroDivisionError("قسمة على صفر أثناء التنفيذ (f1 - f0 = 0)")
        x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
        f2 = f_of_x(expr, x2)
        rows.append((i, x0, x1, x2, f2))
        if abs(x2 - x1) < tol:
            return x2, rows, True
        x0, f0 = x1, f1
        x1, f1 = x2, f2
    return x2, rows, False


def newton_method(expr, x0, tol, max_iter):
    rows = []
    x = x0
    x_new = x0
    for i in range(1, max_iter + 1):
        fx = f_of_x(expr, x)
        dfx = numeric_derivative(expr, x)
        if dfx == 0:
            raise ZeroDivisionError("المشتقة تساوي صفر عند هذه النقطة")
        x_new = x - fx / dfx
        rows.append((i, x, fx, dfx, x_new))
        if abs(x_new - x) < tol:
            return x_new, rows, True
        x = x_new
    return x_new, rows, False


# ============================================================
#              3) طرق حل المعادلات الخطية
# ============================================================

def parse_matrix(text):
    rows = [r.strip() for r in text.strip().split(';') if r.strip()]
    mat = [[float(v) for v in r.split()] for r in rows]
    return np.array(mat, dtype=float)


def parse_vector(text):
    vals = [float(v) for v in text.replace(',', ' ').split()]
    return np.array(vals, dtype=float)


def inverse_method(A, b):
    detA = np.linalg.det(A)
    if abs(detA) < 1e-12:
        raise ValueError("المصفوفة شبه منفردة (det ≈ 0) - لا يوجد حل وحيد")
    A_inv = np.linalg.inv(A)
    x = A_inv.dot(b)
    return x, A_inv, detA


def gauss_elimination(A, b):
    n = len(b)
    M = np.hstack([A.astype(float), b.reshape(-1, 1).astype(float)])
    steps = [M.copy()]
    for k in range(n - 1):
        if abs(M[k, k]) < 1e-12:
            swap_row = np.argmax(np.abs(M[k:, k])) + k
            if abs(M[swap_row, k]) < 1e-12:
                raise ValueError("المصفوفة منفردة (Singular) - لا يوجد حل وحيد")
            M[[k, swap_row]] = M[[swap_row, k]]
        for i in range(k + 1, n):
            factor = M[i, k] / M[k, k]
            M[i, k:] = M[i, k:] - factor * M[k, k:]
        steps.append(M.copy())
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        x[i] = (M[i, -1] - np.dot(M[i, i + 1:n], x[i + 1:n])) / M[i, i]
    return x, steps


def cramer_rule(A, b):
    n = len(b)
    detA = np.linalg.det(A)
    if abs(detA) < 1e-12:
        raise ValueError("المصفوفة شبه منفردة (det ≈ 0) - لا يوجد حل وحيد")
    x = np.zeros(n)
    dets = []
    for i in range(n):
        Ai = A.copy()
        Ai[:, i] = b
        di = np.linalg.det(Ai)
        dets.append(di)
        x[i] = di / detA
    return x, detA, dets


def jacobi_method(A, b, x0, tol, max_iter):
    n = len(b)
    x = x0.copy()
    rows = [(0, x.copy())]
    for it in range(1, max_iter + 1):
        x_new = np.zeros(n)
        for i in range(n):
            s = sum(A[i, j] * x[j] for j in range(n) if j != i)
            if A[i, i] == 0:
                raise ZeroDivisionError(f"عنصر القطر يساوي صفر في الصف {i + 1}")
            x_new[i] = (b[i] - s) / A[i, i]
        rows.append((it, x_new.copy()))
        err = np.max(np.abs(x_new - x))
        x = x_new
        if err < tol:
            return x, rows, True
    return x, rows, False


# ============================================================
#     4) لاجرانج / التفاضل العددي / التكامل العددي
# ============================================================

def lagrange_interpolation(xs, ys, x_eval):
    n = len(xs)
    total = 0.0
    terms = []
    for i in range(n):
        term = ys[i]
        for j in range(n):
            if j != i:
                term *= (x_eval - xs[j]) / (xs[i] - xs[j])
        terms.append((i, term))
        total += term
    return total, terms


def central_difference(expr, x0, h):
    f_plus = f_of_x(expr, x0 + h)
    f_minus = f_of_x(expr, x0 - h)
    derivative = (f_plus - f_minus) / (2 * h)
    return derivative, f_plus, f_minus


def trapezoidal_rule(expr, a, b, n):
    h = (b - a) / n
    xs = [a + i * h for i in range(n + 1)]
    ys = [f_of_x(expr, xi) for xi in xs]
    integral = h / 2 * (ys[0] + 2 * sum(ys[1:-1]) + ys[-1])
    return integral, xs, ys, h


# ============================================================
#                 5) دوال تنسيق المخرجات
# ============================================================

def format_matrix(M, name="A"):
    lines = [f"{name} ="]
    for row in M:
        lines.append("   " + "  ".join(f"{v:10.4f}" for v in row))
    return "\n".join(lines)


def format_vector(v, name="x"):
    lines = [f"{name} ="]
    for val in v:
        lines.append(f"   {val:10.4f}")
    return "\n".join(lines)


# ============================================================
#          6) دوال الحل (تُستدعى من الواجهة الرسومية)
# ============================================================

def sign_symbol(v):
    """يرجع إشارة القيمة (+ / - / 0)، أو — إذا لم تُحسب بعد."""
    if v is None:
        return "—"
    if v > 0:
        return "+"
    if v < 0:
        return "-"
    return "0"


def kv_lines(pairs, indent="   "):
    """يبني سطرين لكل عنصر: سطر تسمية عربي وحده، وسطر قيمة رقمية/لاتينية وحده.
    هذا يمنع اختلاط الاتجاهين (عربي/لاتيني) داخل نفس السطر فيبقى العرض سليمًا."""
    lines = []
    for label, value in pairs:
        lines.append(f"{indent}{label}")
        lines.append(f"{indent}   {value}")
    return lines


class Solution:
    """حاوية موحّدة لنتيجة أي طريقة: خطوات نصية + جدول حقيقي (أعمدة/صفوف) + ملخّص نهائي."""

    def __init__(self, steps, table_columns, table_rows, table_caption, summary):
        self.steps = steps                    # قائمة أسطر (كل سطر عربي بحت أو لاتيني/رقمي بحت)
        self.table_columns = table_columns     # قائمة أسماء الأعمدة، أو None لعدم وجود جدول
        self.table_rows = table_rows           # قائمة صفوف (كل صف = قائمة نصوص بعدد الأعمدة)
        self.table_caption = table_caption     # عنوان الجدول (عربي)
        self.summary = summary                 # قائمة (تسمية عربية, قيمة) للملخّص النهائي


def solve_bisection(values):
    expr = values['f']
    a, b = float(values['a']), float(values['b'])
    tol, max_iter = float(values['tol']), int(values['max_iter'])
    root, rows, converged = bisection_method(expr, a, b, tol, max_iter)

    steps = ["f(x) =", f"   {expr}",
             "الفترة الابتدائية [a, b] :", f"   a = {a:.6f} ,  b = {b:.6f}",
             "قيمة الدقة ε وأقصى عدد تكرارات :", f"   eps = {tol}   max_iter = {max_iter}",
             "", "القيم الابتدائية :",
             f"   f(a) = {rows[0][4]:.6e}  [{sign_symbol(rows[0][4])}]"
             f"    f(b) = {rows[0][5]:.6e}  [{sign_symbol(rows[0][5])}]", ""]
    for (i, c, a_, b_, fa, fb, fc, width) in rows[1:]:
        steps.append(f">> التكرار {i}")
        pairs = [
            ("حساب نقطة المنتصف:", f"c = (a + b) / 2 = ({a_:.6f} + {b_:.6f}) / 2 = {c:.6f}"),
            ("قيمة الدالة عند c:", f"f(c) = {fc:.6e}   [{sign_symbol(fc)}]"),
        ]
        if fa * fc < 0:
            pairs += [("نتيجة مقارنة الإشارتين:", "f(a) و f(c) مختلفتان في الإشارة"),
                      ("الاستنتاج:", "الجذر يقع داخل الجزء [a , c]"),
                      ("تحديث الفترة:", f"b = {c:.6f}")]
        else:
            pairs += [("نتيجة مقارنة الإشارتين:", "f(a) و f(c) متطابقتان في الإشارة"),
                      ("الاستنتاج:", "الجذر يقع داخل الجزء [c , b]"),
                      ("تحديث الفترة:", f"a = {c:.6f}")]
        pairs.append(("الفرق بين طرفي الفترة الجديدة:", f"|a - b| = {width:.6f}"))
        pairs.append(("حالة التوقف:", "تحقق الشرط (|a-b| <= eps) — نتوقف هنا" if width <= tol * 2
                      else "لم يتحقق الشرط بعد — نكمل التكرار التالي"))
        steps.extend(kv_lines(pairs))
        steps.append("")

    table_columns = ["تكرار", "a", "b", "c", "f(c)", "|b-a|"]
    table_rows = [[str(i), f"{a_:.6f}", f"{b_:.6f}", f"{c:.6f}", f"{fc:.6f}", f"{width:.6f}"]
                  for (i, c, a_, b_, fa, fb, fc, width) in rows[1:]]
    summary = [("الجذر التقريبي", f"{root:.8f}"),
               ("الحالة", "تقارب ✓" if converged else "لم يتقارب ✗"),
               ("عدد التكرارات", str(len(rows) - 1)),
               ("التسامح", f"{tol}"),
               ("الفترة الابتدائية", f"[{a}, {b}]")]
    return Solution(steps, table_columns, table_rows, "جدول التكرارات", summary)


def solve_secant(values):
    expr = values['f']
    x0, x1 = float(values['x0']), float(values['x1'])
    tol, max_iter = float(values['tol']), int(values['max_iter'])
    root, rows, converged = secant_method(expr, x0, x1, tol, max_iter)

    steps = ["f(x) =", f"   {expr}",
             "نقطتا البداية :", f"   x0 = {x0:.6f} ,  x1 = {x1:.6f}",
             "قيمة الدقة ε وأقصى عدد تكرارات :", f"   eps = {tol}   max_iter = {max_iter}", ""]
    for (i, x_prev, x_curr, x_next, f_next) in rows:
        width = abs(x_next - x_curr)
        steps.append(f">> التكرار {i}")
        pairs = [
            ("النقطتان الحاليتان:", f"x(i-1) = {x_prev:.6f} ,  x(i) = {x_curr:.6f}"),
            ("حساب النقطة الجديدة:",
             f"x(i+1) = x(i) - f(x(i))*(x(i)-x(i-1)) / (f(x(i))-f(x(i-1))) = {x_next:.6f}"),
            ("قيمة الدالة عند النقطة الجديدة:", f"f(x(i+1)) = {f_next:.6e}"),
            ("الفرق بين آخر نقطتين:", f"|x(i+1) - x(i)| = {width:.6f}"),
        ]
        pairs.append(("حالة التوقف:", "تحقق الشرط — نتوقف هنا" if width <= tol
                      else "لم يتحقق الشرط بعد — نكمل التكرار التالي"))
        steps.extend(kv_lines(pairs))
        steps.append("")

    table_columns = ["تكرار", "x(i-1)", "x(i)", "x(i+1)", "f(x(i+1))", "|x(i+1)-x(i)|"]
    table_rows = [[str(i), f"{x_prev:.6f}", f"{x_curr:.6f}", f"{x_next:.6f}", f"{f_next:.6f}",
                   f"{abs(x_next - x_curr):.6f}"] for (i, x_prev, x_curr, x_next, f_next) in rows]
    summary = [("الجذر التقريبي", f"{root:.8f}"),
               ("الحالة", "تقارب ✓" if converged else "لم يتقارب ✗"),
               ("عدد التكرارات", str(len(rows))),
               ("التسامح", f"{tol}"),
               ("نقطتا البداية", f"[{x0}, {x1}]")]
    return Solution(steps, table_columns, table_rows, "جدول التكرارات", summary)


def solve_newton(values):
    expr = values['f']
    x0 = float(values['x0'])
    tol, max_iter = float(values['tol']), int(values['max_iter'])
    root, rows, converged = newton_method(expr, x0, tol, max_iter)

    steps = ["f(x) =", f"   {expr}",
             "نقطة البداية :", f"   x0 = {x0:.6f}",
             "قيمة الدقة ε وأقصى عدد تكرارات :", f"   eps = {tol}   max_iter = {max_iter}", ""]
    for (i, x, fx, dfx, xn) in rows:
        width = abs(xn - x)
        steps.append(f">> التكرار {i}")
        pairs = [
            ("النقطة الحالية:", f"x(i) = {x:.6f}"),
            ("قيمة الدالة ومشتقتها:", f"f(x(i)) = {fx:.6e} ,  f'(x(i)) = {dfx:.6e}"),
            ("حساب النقطة الجديدة:",
             f"x(i+1) = x(i) - f(x(i))/f'(x(i)) = {x:.6f} - ({fx:.6e})/({dfx:.6e}) = {xn:.6f}"),
            ("الفرق بين آخر نقطتين:", f"|x(i+1) - x(i)| = {width:.6f}"),
        ]
        pairs.append(("حالة التوقف:", "تحقق الشرط — نتوقف هنا" if width <= tol
                      else "لم يتحقق الشرط بعد — نكمل التكرار التالي"))
        steps.extend(kv_lines(pairs))
        steps.append("")

    table_columns = ["تكرار", "x(i)", "f(x(i))", "f'(x(i))", "x(i+1)", "|x(i+1)-x(i)|"]
    table_rows = [[str(i), f"{x:.6f}", f"{fx:.6f}", f"{dfx:.6f}", f"{xn:.6f}", f"{abs(xn-x):.6f}"]
                  for (i, x, fx, dfx, xn) in rows]
    summary = [("الجذر التقريبي", f"{root:.8f}"),
               ("الحالة", "تقارب ✓" if converged else "لم يتقارب ✗"),
               ("عدد التكرارات", str(len(rows))),
               ("التسامح", f"{tol}"),
               ("نقطة البداية", f"{x0}")]
    return Solution(steps, table_columns, table_rows, "جدول التكرارات", summary)


def _check_square(A, b):
    if A.shape[0] != A.shape[1]:
        raise ValueError("يجب أن تكون المصفوفة مربعة")
    if A.shape[0] != len(b):
        raise ValueError("أبعاد المصفوفة والمتجه غير متطابقة")


def solve_inverse(values):
    A, b = parse_matrix(values['A']), parse_vector(values['b'])
    _check_square(A, b)
    x, A_inv, detA = inverse_method(A, b)
    steps = ["المصفوفة A :", format_matrix(A, "A"), "",
             "المتجه b :", format_vector(b, "b"), "",
             "قيمة المحدد :", f"det(A) = {detA:.6f}", "",
             "معكوس المصفوفة :", format_matrix(A_inv, "inv(A)"), "",
             "الحل  x = inv(A) * b :", format_vector(x, "x")]
    table_columns = ["المتغير", "القيمة"]
    table_rows = [[f"x{i+1}", f"{v:.6f}"] for i, v in enumerate(x)]
    summary = [("det(A)", f"{detA:.6f}"), ("عدد المجاهيل", str(len(x)))]
    return Solution(steps, table_columns, table_rows, "الحل النهائي", summary)


def solve_gauss(values):
    A, b = parse_matrix(values['A']), parse_vector(values['b'])
    _check_square(A, b)
    x, steps_mats = gauss_elimination(A, b)
    steps = ["المصفوفة الموسعة الابتدائية [A|b] :", format_matrix(steps_mats[0], "[A|b]")]
    for idx, s in enumerate(steps_mats[1:], start=1):
        steps += ["", f"بعد الخطوة {idx} :", format_matrix(s, "[A|b]")]
    steps += ["", "الحل بالتعويض الخلفي :", format_vector(x, "x")]
    table_columns = ["المتغير", "القيمة"]
    table_rows = [[f"x{i+1}", f"{v:.6f}"] for i, v in enumerate(x)]
    summary = [("عدد المجاهيل", str(len(x))), ("عدد خطوات الحذف", str(len(steps_mats) - 1))]
    return Solution(steps, table_columns, table_rows, "الحل النهائي", summary)


def solve_cramer(values):
    A, b = parse_matrix(values['A']), parse_vector(values['b'])
    _check_square(A, b)
    x, detA, dets = cramer_rule(A, b)
    steps = ["المصفوفة A :", format_matrix(A, "A"), "", f"det(A) = {detA:.6f}", ""]
    for i, di in enumerate(dets):
        steps.append(f"det(A{i+1}) = {di:.6f}   ,   x{i+1} = det(A{i+1}) / det(A) = {x[i]:.6f}")
    table_columns = ["المتغير", "det(Ai)", "القيمة"]
    table_rows = [[f"x{i+1}", f"{dets[i]:.6f}", f"{x[i]:.6f}"] for i in range(len(x))]
    summary = [("det(A)", f"{detA:.6f}"), ("عدد المجاهيل", str(len(x)))]
    return Solution(steps, table_columns, table_rows, "جدول القيم والمحددات", summary)


def solve_jacobi(values):
    A, b = parse_matrix(values['A']), parse_vector(values['b'])
    x0 = parse_vector(values['x0'])
    tol, max_iter = float(values['tol']), int(values['max_iter'])
    _check_square(A, b)
    if A.shape[0] != len(x0):
        raise ValueError("أبعاد التخمين الابتدائي غير متطابقة مع المصفوفة")
    x, rows, converged = jacobi_method(A, b, x0, tol, max_iter)
    n = len(b)

    steps = ["المصفوفة A :", format_matrix(A, "A"), "", "المتجه b :", format_vector(b, "b"), ""]
    for it, xv in rows[1:]:
        prev = rows[it - 1][1]
        err = max(abs(xv[k] - prev[k]) for k in range(n))
        steps.append(f">> التكرار {it}")
        steps.append("القيم الجديدة :")
        steps.append("   " + " , ".join(f"x{k+1} = {xv[k]:.6f}" for k in range(n)))
        steps.append("أكبر فرق بين تكرارين متتاليين :")
        steps.append(f"   {err:.6f}")
        steps.append("حالة التوقف :")
        steps.append("   تحقق الشرط — نتوقف هنا" if err <= tol else "   لم يتحقق الشرط بعد — نكمل")
        steps.append("")

    table_columns = ["تكرار"] + [f"x{k+1}" for k in range(n)]
    table_rows = [[str(it)] + [f"{v:.6f}" for v in xv] for it, xv in rows]
    summary = [("الحالة", "تقارب ✓" if converged else "لم يتقارب ✗"),
               ("عدد التكرارات", str(len(rows) - 1)),
               ("التسامح", f"{tol}")]
    return Solution(steps, table_columns, table_rows, "جدول التكرارات", summary)


def solve_lagrange(values):
    xs = [float(v) for v in values['xs'].split()]
    ys = [float(v) for v in values['ys'].split()]
    x_eval = float(values['x_eval'])
    if len(xs) != len(ys):
        raise ValueError("عدد قيم x يجب أن يساوي عدد قيم y")
    if len(set(xs)) != len(xs):
        raise ValueError("يجب ألا تتكرر قيم x")
    total, terms = lagrange_interpolation(xs, ys, x_eval)

    steps = ["نقاط البيانات :",
             "   x : " + "  ".join(f"{v:.4f}" for v in xs),
             "   y : " + "  ".join(f"{v:.4f}" for v in ys),
             "القيمة المطلوب حسابها عندها :", f"   x = {x_eval}"]
    table_columns = ["i", "Li(x) * yi"]
    table_rows = [[str(i), f"{term:.6f}"] for i, term in terms]
    summary = [(f"P({x_eval})", f"{total:.6f}"), ("عدد النقاط", str(len(xs)))]
    return Solution(steps, table_columns, table_rows, "حدود الاستيفاء", summary)


def solve_differentiation(values):
    expr = values['f']
    x0, h = float(values['x0']), float(values['h'])
    derivative, f_plus, f_minus = central_difference(expr, x0, h)
    steps = ["f(x) =", f"   {expr}",
             "نقطة الحساب والخطوة :", f"   x0 = {x0} ,  h = {h}",
             "حساب طرفي الفرق المركزي :",
             f"   f(x0 + h) = {f_plus:.6f}",
             f"   f(x0 - h) = {f_minus:.6f}",
             "قانون الفرق المركزي :",
             "   f'(x0) = [f(x0+h) - f(x0-h)] / (2h)"]
    table_columns = ["الكمية", "القيمة"]
    table_rows = [["f(x0 + h)", f"{f_plus:.6f}"],
                  ["f(x0 - h)", f"{f_minus:.6f}"],
                  ["f'(x0)", f"{derivative:.6f}"]]
    summary = [("f'(x0)", f"{derivative:.6f}")]
    return Solution(steps, table_columns, table_rows, "نتائج الحساب", summary)


def solve_integration(values):
    expr = values['f']
    a, b, n = float(values['a']), float(values['b']), int(values['n'])
    integral, xs, ys, h = trapezoidal_rule(expr, a, b, n)
    steps = ["f(x) =", f"   {expr}",
             "الفترة وعدد الأقسام :", f"   [a, b] = [{a}, {b}] ,  n = {n} ,  h = {h:.6f}",
             "قانون شبه المنحرفات :",
             "   I = (h/2) * [f(x0) + 2*sum(f(x1..xn-1)) + f(xn)]"]
    table_columns = ["i", "x(i)", "f(x(i))"]
    table_rows = [[str(i), f"{xi:.6f}", f"{yi:.6f}"] for i, (xi, yi) in enumerate(zip(xs, ys))]
    summary = [("قيمة التكامل", f"{integral:.6f}"), ("عدد الأقسام", str(n))]
    return Solution(steps, table_columns, table_rows, "جدول النقاط", summary)
# ============================================================
#          7) لوحة الألوان الموحّدة (أسود + بنفسجي فاخر)
# ============================================================

THEME = {
    "bg_main":     "#0b0710",   # خلفية النافذة الرئيسية (أسود بنفسجي داكن)
    "bg_panel":    "#140d1f",   # خلفية اللوحات
    "bg_card":     "#1c1330",   # خلفية الكروت
    "border":      "#3a2a55",   # حدود خفيفة بنفسجية
    "accent":      "#a06cf9",   # بنفسجي أساسي زاهٍ
    "accent_dark": "#7c3fc4",   # بنفسجي غامق (عند التفعيل)
    "accent_alt":  "#c9a6ff",   # بنفسجي فاتح (عناوين ثانوية)
    "gold":        "#f2c14e",   # ذهبي (لإبراز النتيجة النهائية - يعطي طابع فخم)
    "text":        "#f4eeff",   # نص أساسي أبيض بنفسجي فاتح جدًا
    "text_muted":  "#a998c9",   # نص باهت
    "success":     "#6ee7a0",   # أخضر النجاح/التقارب
    "danger":      "#f97171",   # أحمر عدم التقارب
    "row_alt":     "#1a1229",   # لون الصف الفردي في الجدول (تناوب الألوان)
}


def make_card(parent, title, subtitle, command, icon="●", width=30):
    card = tk.Frame(parent, bg=THEME["bg_card"], highlightbackground=THEME["border"],
                     highlightthickness=1, cursor="hand2")

    icon_lbl = tk.Label(card, text=icon, font=("Arial", 20), bg=THEME["bg_card"],
                         fg=THEME["accent"])
    icon_lbl.pack(anchor="e", padx=16, pady=(14, 4))

    title_lbl = tk.Label(card, text=ar(title), font=("Arial", 13, "bold"),
                          bg=THEME["bg_card"], fg=THEME["text"], anchor="e",
                          justify="right", wraplength=220)
    title_lbl.pack(fill="x", padx=16)

    sub_lbl = tk.Label(card, text=ar(subtitle), font=("Arial", 10),
                        bg=THEME["bg_card"], fg=THEME["text_muted"], anchor="e",
                        justify="right", wraplength=220)
    sub_lbl.pack(fill="x", padx=16, pady=(2, 16))

    for widget in (card, icon_lbl, title_lbl, sub_lbl):
        widget.bind("<Button-1>", lambda e: command())

    card.configure(width=width * 8, height=120)
    card.pack_propagate(False)
    return card


def make_header(parent, title, subtitle=None):
    header = tk.Frame(parent, bg=THEME["bg_main"])
    header.pack(fill="x", padx=25, pady=(22, 10))
    tk.Label(header, text=ar(title), font=("Arial", 20, "bold"),
              bg=THEME["bg_main"], fg=THEME["text"], anchor="e",
              justify="right").pack(fill="x")
    if subtitle:
        tk.Label(header, text=ar(subtitle), font=("Arial", 11),
                  bg=THEME["bg_main"], fg=THEME["accent_alt"], anchor="e",
                  justify="right").pack(fill="x", pady=(4, 0))
    return header


def styled_button(parent, text, command, primary=True):
    bg = THEME["accent"] if primary else THEME["bg_card"]
    fg = "#0b0710" if primary else THEME["text"]
    return tk.Button(parent, text=ar(text), font=("Arial", 12, "bold"),
                      bg=bg, fg=fg, activebackground=THEME["accent_dark"],
                      activeforeground="#0b0710", bd=0, padx=18, pady=10,
                      cursor="hand2", command=command)


_TREEVIEW_STYLED = False


def style_treeview():
    """يهيّئ مظهر جدول ttk.Treeview بألوان اللوحة (أسود/بنفسجي) مرة واحدة فقط."""
    global _TREEVIEW_STYLED
    if _TREEVIEW_STYLED:
        return
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Custom.Treeview",
                     background=THEME["bg_panel"], fieldbackground=THEME["bg_panel"],
                     foreground=THEME["text"], rowheight=28, borderwidth=0,
                     font=("Consolas", 10))
    style.map("Custom.Treeview", background=[("selected", THEME["accent_dark"])],
               foreground=[("selected", THEME["text"])])
    style.configure("Custom.Treeview.Heading",
                     background=THEME["accent_dark"], foreground=THEME["text"],
                     font=("Arial", 10, "bold"), borderwidth=0, relief="flat")
    style.map("Custom.Treeview.Heading", background=[("active", THEME["accent"])])
    _TREEVIEW_STYLED = True


def make_table(parent, columns, rows, caption=None):
    """يبني جدولاً حقيقيًا (ttk.Treeview) بعناوين أعمدة وصفوف متناوبة الألوان."""
    style_treeview()

    wrapper = tk.Frame(parent, bg=THEME["bg_panel"])
    wrapper.pack(fill="both", expand=True, padx=25, pady=(0, 15))

    if caption:
        tk.Label(wrapper, text=ar(caption), font=("Arial", 12, "bold"),
                  bg=THEME["bg_panel"], fg=THEME["accent_alt"], anchor="e",
                  justify="right").pack(fill="x", pady=(0, 8))

    table_frame = tk.Frame(wrapper, bg=THEME["border"], highlightbackground=THEME["border"],
                            highlightthickness=1)
    table_frame.pack(fill="both", expand=True)

    scroll_y = tk.Scrollbar(table_frame)
    scroll_y.pack(side="right", fill="y")

    tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                         style="Custom.Treeview", yscrollcommand=scroll_y.set, height=10)
    for col in columns:
        tree.heading(col, text=ar(col), anchor="center")
        tree.column(col, anchor="center", width=110, stretch=True)
    tree.pack(fill="both", expand=True)
    scroll_y.config(command=tree.yview)

    tree.tag_configure("odd", background=THEME["bg_panel"])
    tree.tag_configure("even", background=THEME["row_alt"])
    for idx, row in enumerate(rows):
        tag = "even" if idx % 2 == 0 else "odd"
        tree.insert("", "end", values=[ar(v) for v in row], tags=(tag,))

    return wrapper


def make_summary_panel(parent, summary):
    """لوحة الملخّص النهائي (تسمية : قيمة) بنفس أسلوب لوحتك المرجعية."""
    panel = tk.Frame(parent, bg=THEME["bg_card"], highlightbackground=THEME["border"],
                      highlightthickness=1)
    panel.pack(fill="x", padx=25, pady=(0, 15))
    for label, value in summary:
        row = tk.Frame(panel, bg=THEME["bg_card"])
        row.pack(fill="x", padx=18, pady=6)
        tk.Label(row, text=ar(label + " :"), font=("Arial", 11), bg=THEME["bg_card"],
                  fg=THEME["text_muted"], anchor="e").pack(side="right")
        value_color = THEME["gold"]
        if "✓" in value:
            value_color = THEME["success"]
        elif "✗" in value:
            value_color = THEME["danger"]
        tk.Label(row, text=ar(value), font=("Consolas", 12, "bold"), bg=THEME["bg_card"],
                  fg=value_color, anchor="w").pack(side="left")
    return panel


def show_result_window(master, solution):
    """نافذة النتائج: خطوات الحل (نص) ← الجدول الحقيقي ← الملخّص النهائي."""
    win = tk.Toplevel(master)
    win.title(ar("النتائج"))
    win.geometry("820x680")
    win.configure(bg=THEME["bg_main"])

    make_header(win, "النتائج", "التفاصيل الكاملة لخطوات الحل")

    # -- (1) خطوات الحل (نص قابل للتمرير) --
    steps_wrapper = tk.Frame(win, bg=THEME["bg_panel"], highlightbackground=THEME["border"],
                              highlightthickness=1)
    steps_wrapper.pack(fill="both", expand=True, padx=25, pady=(0, 15))

    tk.Label(steps_wrapper, text=ar("خطوات الحل"), font=("Arial", 12, "bold"),
              bg=THEME["bg_panel"], fg=THEME["accent_alt"], anchor="e",
              justify="right").pack(fill="x", padx=12, pady=(10, 4))

    text_frame = tk.Frame(steps_wrapper, bg=THEME["bg_panel"])
    text_frame.pack(fill="both", expand=True, padx=12, pady=(0, 10))
    scroll_y = tk.Scrollbar(text_frame)
    scroll_y.pack(side="right", fill="y")
    txt = tk.Text(text_frame, bg=THEME["bg_panel"], fg=THEME["text"],
                   insertbackground=THEME["text"], font=("Consolas", 11), wrap="word",
                   bd=0, height=14, yscrollcommand=scroll_y.set)
    txt.pack(fill="both", expand=True)
    scroll_y.config(command=txt.yview)

    txt.tag_configure("section", foreground=THEME["accent"], font=("Consolas", 11, "bold"))
    txt.tag_configure("normal", foreground=THEME["text"])
    steps_text = finalize(solution.steps)
    lines = steps_text.split("\n")
    for idx, line in enumerate(lines):
        tag = "section" if line.strip().startswith(">>") else "normal"
        txt.insert("end", line + ("\n" if idx < len(lines) - 1 else ""), tag)
    txt.config(state="disabled")

    # -- (2) الجدول الحقيقي --
    if solution.table_columns and solution.table_rows:
        make_table(win, solution.table_columns, solution.table_rows, solution.table_caption)

    # -- (3) الملخّص النهائي --
    make_summary_panel(win, solution.summary)


# ============================================================
#          8) نافذة الإدخال العامة لكل طريقة
# ============================================================

class MethodWindow(tk.Toplevel):
    """نافذة عامة تُستخدم لأي طريقة: تعرض المدخلات وزر الحل."""

    def __init__(self, master, title, fields, solve_func):
        super().__init__(master)
        self.title(ar(title))
        self.configure(bg=THEME["bg_main"])
        self.solve_func = solve_func
        self.fields = fields
        self.entries = {}

        make_header(self, title, "أدخل بيانات المسألة ثم اضغط حل")

        form = tk.Frame(self, bg=THEME["bg_panel"], highlightbackground=THEME["border"],
                         highlightthickness=1)
        form.pack(padx=25, pady=5, fill="x")

        for label_text, key, default in fields:
            row = tk.Frame(form, bg=THEME["bg_panel"])
            row.pack(fill="x", padx=18, pady=10)
            tk.Label(row, text=ar(label_text), width=24, anchor="e",
                     bg=THEME["bg_panel"], fg=THEME["text_muted"],
                     font=("Arial", 11)).pack(side="right")
            entry = tk.Entry(row, font=("Consolas", 11), justify="center",
                              bg=THEME["bg_card"], fg=THEME["text"],
                              insertbackground=THEME["accent"], relief="flat",
                              highlightbackground=THEME["border"],
                              highlightcolor=THEME["accent"], highlightthickness=1)
            entry.insert(0, default)
            entry.pack(side="right", padx=8, fill="x", expand=True, ipady=6)
            self.entries[key] = entry

        btn_row = tk.Frame(self, bg=THEME["bg_main"])
        btn_row.pack(pady=22)
        styled_button(btn_row, "حل", self.on_solve, primary=True).pack()

        self.update_idletasks()
        w = max(460, self.winfo_reqwidth() + 20)
        h = self.winfo_reqheight() + 20
        self.geometry(f"{w}x{h}")

    def on_solve(self):
        try:
            values = {key: entry.get() for key, entry in self.entries.items()}
            solution = self.solve_func(values)
            show_result_window(self, solution)
        except Exception as e:
            # ملاحظة: صناديق رسائل ويندوز الأصلية تدعم العربية RTL تلقائيًا،
            # لذلك لا نُمرر النص عبر ar() هنا لتفادي عكسه مرتين.
            messagebox.showerror("خطأ", f"حدث خطأ أثناء الحساب:\n{e}")


# ============================================================
#                9) قوائم اختيار الطرق (كروت)
# ============================================================

class NonlinearMenu(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title(ar("المعادلات غير الخطية"))
        self.configure(bg=THEME["bg_main"])
        self.geometry("560x460")

        make_header(self, "المعادلات غير الخطية", "اختر طريقة إيجاد الجذور")

        grid = tk.Frame(self, bg=THEME["bg_main"])
        grid.pack(padx=25, pady=10)

        cards = [
            ("طريقة تنصيف الفترات", "أثبت تقارب - نصف الفترة", "½", self.open_bisection),
            ("طريقة القاطع", "تقريب الدالة بخط قاطع", "／", self.open_secant),
            ("طريقة نيوتن-رافسون", "تقارب سريع باستخدام المشتقة", "√", self.open_newton),
        ]
        for i, (title, subtitle, icon, cmd) in enumerate(cards):
            card = make_card(grid, title, subtitle, cmd, icon=icon)
            card.grid(row=i // 2, column=i % 2, padx=10, pady=10, sticky="nsew")

    def open_bisection(self):
        MethodWindow(self, "طريقة تنصيف الفترات (Bisection)",
                     [("f(x) :", 'f', "x**3 - x - 2"),
                      ("a :", 'a', "1"), ("b :", 'b', "2"),
                      ("الدقة (tol) :", 'tol', "0.0001"),
                      ("أقصى عدد تكرارات :", 'max_iter', "50")],
                     solve_bisection)

    def open_secant(self):
        MethodWindow(self, "طريقة القاطع (Secant)",
                     [("f(x) :", 'f', "x**3 - x - 2"),
                      ("x0 :", 'x0', "1"), ("x1 :", 'x1', "2"),
                      ("الدقة (tol) :", 'tol', "0.0001"),
                      ("أقصى عدد تكرارات :", 'max_iter', "50")],
                     solve_secant)

    def open_newton(self):
        MethodWindow(self, "طريقة نيوتن-رافسون (Newton-Raphson)",
                     [("f(x) :", 'f', "x**3 - x - 2"),
                      ("x0 :", 'x0', "1.5"),
                      ("الدقة (tol) :", 'tol', "0.0001"),
                      ("أقصى عدد تكرارات :", 'max_iter', "50")],
                     solve_newton)


class LinearMenu(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title(ar("المعادلات الخطية"))
        self.configure(bg=THEME["bg_main"])
        self.geometry("580x620")

        make_header(self, "المعادلات الخطية", "حل أنظمة المعادلات الخطية")

        tk.Label(self, text=ar("الطرق المباشرة"), font=("Arial", 13, "bold"),
                 bg=THEME["bg_main"], fg=THEME["accent_alt"], anchor="e",
                 justify="right").pack(fill="x", padx=25, pady=(5, 8))

        grid1 = tk.Frame(self, bg=THEME["bg_main"])
        grid1.pack(padx=25)
        cards1 = [
            ("طريقة معكوس المصفوفة", "الحل عبر  x = inv(A)·b", "A⁻¹", self.open_inverse),
            ("طريقة جاوس للحذف", "الحذف التدريجي والتعويض الخلفي", "▦", self.open_gauss),
            ("طريقة كرامر", "الحل عبر المحددات (Determinants)", "|A|", self.open_cramer),
        ]
        for i, (title, subtitle, icon, cmd) in enumerate(cards1):
            card = make_card(grid1, title, subtitle, cmd, icon=icon)
            card.grid(row=i // 2, column=i % 2, padx=10, pady=10, sticky="nsew")

        tk.Label(self, text=ar("الطرق غير المباشرة"), font=("Arial", 13, "bold"),
                 bg=THEME["bg_main"], fg=THEME["accent_alt"], anchor="e",
                 justify="right").pack(fill="x", padx=25, pady=(15, 8))

        grid2 = tk.Frame(self, bg=THEME["bg_main"])
        grid2.pack(padx=25)
        card2 = make_card(grid2, "طريقة جاكوبي", "حل تكراري للأنظمة الخطية", "∑", self.open_jacobi)
        card2.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    def open_inverse(self):
        MethodWindow(self, "طريقة معكوس المصفوفة",
                     [("المصفوفة A (مثال: 1 2;3 4) :", 'A', "4 -1 0;-1 4 -1;0 -1 4"),
                      ("المتجه b (مثال: 1 2 3) :", 'b', "1 5 0")],
                     solve_inverse)

    def open_gauss(self):
        MethodWindow(self, "طريقة جاوس للحذف",
                     [("المصفوفة A :", 'A', "4 -1 0;-1 4 -1;0 -1 4"),
                      ("المتجه b :", 'b', "1 5 0")],
                     solve_gauss)

    def open_cramer(self):
        MethodWindow(self, "طريقة كرامر",
                     [("المصفوفة A :", 'A', "4 -1 0;-1 4 -1;0 -1 4"),
                      ("المتجه b :", 'b', "1 5 0")],
                     solve_cramer)

    def open_jacobi(self):
        MethodWindow(self, "طريقة جاكوبي",
                     [("المصفوفة A :", 'A', "4 -1 0;-1 4 -1;0 -1 4"),
                      ("المتجه b :", 'b', "1 5 0"),
                      ("التخمين الابتدائي x0 :", 'x0', "0 0 0"),
                      ("الدقة (tol) :", 'tol', "0.0001"),
                      ("أقصى عدد تكرارات :", 'max_iter', "50")],
                     solve_jacobi)


class MainMenu(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(ar("مشروع تحليل عددي"))
        self.geometry("620x560")
        self.configure(bg=THEME["bg_main"])

        make_header(self, "مشروع تحليل عددي", "اختر طريقة من البطاقات التالية للبدء")

        grid = tk.Frame(self, bg=THEME["bg_main"])
        grid.pack(padx=25, pady=10)

        cards = [
            ("المعادلات غير الخطية", "إيجاد الجذور: تنصيف • قاطع • نيوتن", "f", self.open_nonlinear),
            ("المعادلات الخطية", "المباشرة: معكوس • جاوس • كرامر • جاكوبي", "⊞", self.open_linear),
            ("طريقة لاجرانج", "الاستيفاء (Interpolation)", "∫", self.open_lagrange),
            ("التفاضل العددي", "الفروق المركزية", "∂", self.open_diff),
            ("التكامل العددي", "طريقة شبه المنحرفات", "∮", self.open_integration),
        ]
        for i, (title, subtitle, icon, cmd) in enumerate(cards):
            card = make_card(grid, title, subtitle, cmd, icon=icon)
            card.grid(row=i // 2, column=i % 2, padx=10, pady=10, sticky="nsew")

    def open_nonlinear(self):
        NonlinearMenu(self)

    def open_linear(self):
        LinearMenu(self)

    def open_lagrange(self):
        MethodWindow(self, "طريقة لاجرانج (Lagrange Interpolation)",
                     [("قيم x (مفصولة بمسافة):", 'xs', "1 2 3 4"),
                      ("قيم y (مفصولة بمسافة):", 'ys', "1 8 27 64"),
                      ("القيمة x المطلوب حساب y عندها:", 'x_eval', "2.5")],
                     solve_lagrange)

    def open_diff(self):
        MethodWindow(self, "التفاضل العددي (الفروق المركزية)",
                     [("f(x) :", 'f', "x**2 * sin(x)"),
                      ("النقطة x0 :", 'x0', "1"),
                      ("الخطوة h :", 'h', "0.01")],
                     solve_differentiation)

    def open_integration(self):
        MethodWindow(self, "التكامل العددي (طريقة شبه المنحرفات)",
                     [("f(x) :", 'f', "x**2 + 1"),
                      ("الحد الأدنى a :", 'a', "0"),
                      ("الحد الأعلى b :", 'b', "2"),
                      ("عدد الفترات n :", 'n', "10")],
                     solve_integration)


if __name__ == "__main__":
    app = MainMenu()
    app.mainloop()
