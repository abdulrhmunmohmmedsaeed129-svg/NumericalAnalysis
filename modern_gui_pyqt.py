# -*- coding: utf-8 -*-
"""
معمل التحليل العددي التفاعلي
Numerical Analysis Interactive Lab
Learn → Visualize → Calculate → Analyze

Entry point: python modern_gui_pyqt.py
"""

import sys
import math
import importlib

# ============================================================
#  Qt Compatibility Layer — supports PySide6, PyQt6, PyQt5
# ============================================================
_QT_BINDING = None
try:
    from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                                   QHBoxLayout, QLabel, QPushButton, QFrame, QGridLayout,
                                   QScrollArea, QDialog, QLineEdit, QTableWidget, QTableWidgetItem,
                                   QHeaderView, QMessageBox, QTabWidget, QStackedWidget,
                                   QRadioButton, QButtonGroup, QProgressBar, QComboBox,
                                   QTextEdit, QSpinBox, QSplitter, QSizePolicy, QSpacerItem)
    from PySide6.QtCore import Qt, QSize, QTimer
    from PySide6.QtGui import QFont, QColor, QPainter, QPen, QPainterPath
    _QT_BINDING = "PySide6"
except ImportError:
    try:
        from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                                     QHBoxLayout, QLabel, QPushButton, QFrame, QGridLayout,
                                     QScrollArea, QDialog, QLineEdit, QTableWidget, QTableWidgetItem,
                                     QHeaderView, QMessageBox, QTabWidget, QStackedWidget,
                                     QRadioButton, QButtonGroup, QProgressBar, QComboBox,
                                     QTextEdit, QSpinBox, QSplitter, QSizePolicy, QSpacerItem)
        from PyQt6.QtCore import Qt, QSize, QTimer
        from PyQt6.QtGui import QFont, QColor, QPainter, QPen, QPainterPath
        _QT_BINDING = "PyQt6"
    except ImportError:
        from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                                     QHBoxLayout, QLabel, QPushButton, QFrame, QGridLayout,
                                     QScrollArea, QDialog, QLineEdit, QTableWidget, QTableWidgetItem,
                                     QHeaderView, QMessageBox, QTabWidget, QStackedWidget,
                                     QRadioButton, QButtonGroup, QProgressBar, QComboBox,
                                     QTextEdit, QSpinBox, QSplitter, QSizePolicy, QSpacerItem)
        from PyQt5.QtCore import Qt, QSize, QTimer
        from PyQt5.QtGui import QFont, QColor, QPainter, QPen, QPainterPath
        _QT_BINDING = "PyQt5"

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# Matplotlib backend selection based on Qt binding
try:
    import matplotlib
    if _QT_BINDING == "PySide6":
        matplotlib.use('QtAgg')
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    elif _QT_BINDING == "PyQt6":
        matplotlib.use('QtAgg')
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    else:
        matplotlib.use('Qt5Agg')
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

try:
    backend = importlib.import_module("na Gui")
except Exception:
    backend = None

# ============================================================
#  Safe math evaluation
# ============================================================
SAFE_MATH_NS = {
    'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
    'exp': math.exp, 'log': math.log, 'log10': math.log10,
    'sqrt': math.sqrt, 'pi': math.pi, 'e': math.e,
    'abs': abs, 'pow': pow,
    'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
}

def safe_eval_func(expr, x_val):
    """Safely evaluate a math expression with x as variable."""
    ns = dict(SAFE_MATH_NS)
    ns['x'] = x_val
    return eval(expr, {"__builtins__": {}}, ns)

# ============================================================
#  Application State (shared across pages)
# ============================================================
class AppState:
    """Shared application state for cross-page communication."""
    def __init__(self):
        self.last_solution = None
        self.last_method_name = ""
        self.last_method_type = ""
        self.last_func_expr = ""
        self.decimal_places = 6
        self.completed_methods = set()
        self.learning_status = {}  # method_key -> 'not_started' | 'in_progress' | 'completed'
        self.quiz_scores = {}  # method_key -> (correct, total)

app_state = AppState()

# ============================================================
#  Style Constants
# ============================================================
CARD_STYLE = """
    QFrame {{
        background-color: white;
        border-radius: 8px;
        border: 2px solid {color};
    }}
"""
BTN_STYLE = """
    QPushButton {{
        background-color: {color};
        color: white;
        border-radius: 4px;
        padding: 8px;
        font-weight: bold;
        border: none;
    }}
    QPushButton:hover {{
        background-color: #333333;
    }}
"""
INPUT_STYLE = "background-color: #0b1426; border: 1px solid #64ffda; padding: 8px; color: white; border-radius: 4px;"
TAB_STYLE = """
    QTabWidget::pane { border: 1px solid #1f3659; background: #0d1b2a; border-radius: 5px; }
    QTabBar::tab { background: #1a365d; color: #a8b2d1; padding: 10px 20px; font-weight: bold; font-size: 13px; border-top-left-radius: 4px; border-top-right-radius: 4px; margin-right: 2px; }
    QTabBar::tab:selected { background: #005b9f; color: white; }
    QTabBar::tab:hover { background: #2d4a77; }
"""

# ============================================================
#  Lesson Content Database
# ============================================================
LESSONS = {
    'bisection': {
        'title_ar': 'طريقة التنصيف',
        'title_en': 'Bisection Method',
        'goal': 'إيجاد جذر المعادلة f(x) = 0 في فترة معلومة [a, b]',
        'idea': 'تعتمد على تقسيم الفترة [a, b] إلى نصفين متساويين بشكل متكرر، واختيار النصف الذي يحتوي على الجذر بناءً على تغير إشارة الدالة.',
        'formula': 'c = (a + b) / 2',
        'symbols': '<b>a, b</b>: طرفا الفترة<br><b>c</b>: نقطة المنتصف<br><b>f(x)</b>: الدالة المراد إيجاد جذرها<br><b>ε</b>: الدقة المطلوبة (Tolerance)',
        'conditions': '• يجب أن تكون f(x) متصلة على [a, b]<br>• يجب أن يكون f(a) × f(b) < 0 (إشارتان مختلفتان)<br>• هذا يضمن وجود جذر واحد على الأقل في الفترة (نظرية القيمة الوسطى)',
        'stopping': '• |b - a| < ε (عرض الفترة أصغر من الدقة المطلوبة)<br>• أو |f(c)| < ε<br>• أو الوصول لأقصى عدد تكرارات',
        'steps': '1. تحقق من أن f(a) × f(b) < 0<br>2. احسب c = (a + b) / 2<br>3. احسب f(c)<br>4. إذا f(a) × f(c) < 0 → الجذر في [a, c]، ضع b = c<br>5. وإلا → الجذر في [c, b]، ضع a = c<br>6. كرر حتى تتحقق شروط التوقف',
        'example': 'f(x) = x³ - x - 2, [a, b] = [1, 2]<br>f(1) = -2 < 0, f(2) = 4 > 0 → الجذر في [1, 2]<br>c = 1.5, f(1.5) = 0.875 > 0 → الجذر في [1, 1.5]<br>c = 1.25, f(1.25) = -0.297 < 0 → الجذر في [1.25, 1.5]<br>وهكذا...',
    },
    'false_position': {
        'title_ar': 'طريقة الوضع الكاذب',
        'title_en': 'False Position Method (Regula Falsi)',
        'goal': 'إيجاد جذر المعادلة f(x) = 0 باستخدام خط مستقيم بين طرفي الفترة',
        'idea': 'بدلاً من أخذ منتصف الفترة (كما في التنصيف)، نرسم خطاً مستقيماً بين النقطتين (a, f(a)) و (b, f(b))، ونأخذ نقطة تقاطعه مع محور x كتقريب للجذر.',
        'formula': 'c = b - f(b) × (b - a) / (f(b) - f(a))',
        'symbols': '<b>a, b</b>: طرفا الفترة<br><b>c</b>: نقطة التقاطع مع محور x<br><b>f(a), f(b)</b>: قيم الدالة عند طرفي الفترة',
        'conditions': '• يجب أن تكون f(x) متصلة على [a, b]<br>• يجب أن يكون f(a) × f(b) < 0',
        'stopping': '• |f(c)| < ε<br>• أو |b - a| < ε<br>• أو الوصول لأقصى عدد تكرارات',
        'steps': '1. تحقق من أن f(a) × f(b) < 0<br>2. احسب c = b - f(b)(b-a)/(f(b)-f(a))<br>3. احسب f(c)<br>4. إذا f(a) × f(c) < 0 → ضع b = c<br>5. وإلا → ضع a = c<br>6. كرر حتى تتحقق شروط التوقف',
        'example': 'f(x) = x³ - x - 2, [a, b] = [1, 2]<br>f(1) = -2, f(2) = 4<br>c = 2 - 4×(2-1)/(4-(-2)) = 2 - 4/6 = 1.333<br>f(1.333) = -0.963 → الجذر في [1.333, 2]',
    },
    'secant': {
        'title_ar': 'طريقة القاطع',
        'title_en': 'Secant Method',
        'goal': 'إيجاد جذر المعادلة f(x) = 0 بدون الحاجة لحساب المشتقة',
        'idea': 'تعتمد على تقريب المشتقة باستخدام الفرق بين قيمتين متتاليتين للدالة، مما يجعلها بديلاً لطريقة نيوتن عندما يكون حساب المشتقة صعباً.',
        'formula': 'x(n+1) = x(n) - f(x(n)) × (x(n) - x(n-1)) / (f(x(n)) - f(x(n-1)))',
        'symbols': '<b>x(n), x(n-1)</b>: آخر نقطتين<br><b>f(x(n))</b>: قيمة الدالة عند النقطة الحالية<br><b>x(n+1)</b>: التقريب الجديد للجذر',
        'conditions': '• لا تتطلب حساب المشتقة<br>• تحتاج نقطتين ابتدائيتين x0 و x1<br>• يجب أن f(x(n)) ≠ f(x(n-1)) لتجنب القسمة على صفر',
        'stopping': '• |x(n+1) - x(n)| < ε<br>• أو الوصول لأقصى عدد تكرارات',
        'steps': '1. اختر نقطتين ابتدائيتين x0 و x1<br>2. احسب f(x0) و f(x1)<br>3. احسب x2 بالقانون<br>4. حدّث: x0 = x1, x1 = x2<br>5. كرر حتى تتحقق شروط التوقف',
        'example': 'f(x) = x³ - x - 2, x0 = 1, x1 = 2<br>f(1) = -2, f(2) = 4<br>x2 = 2 - 4×(2-1)/(4-(-2)) = 1.333<br>f(1.333) = -0.963<br>x3 = 1.333 - (-0.963)(1.333-2)/(-0.963-4) = 1.225',
    },
    'newton': {
        'title_ar': 'طريقة نيوتن رافسون',
        'title_en': 'Newton-Raphson Method',
        'goal': 'إيجاد جذر المعادلة f(x) = 0 بسرعة تقارب تربيعية',
        'idea': 'تعتمد على رسم مماس (Tangent) للدالة عند النقطة الحالية، ثم أخذ نقطة تقاطع المماس مع محور x كتقريب جديد للجذر.',
        'formula': 'x(n+1) = x(n) - f(x(n)) / f\'(x(n))',
        'symbols': '<b>x(n)</b>: التقريب الحالي<br><b>f(x(n))</b>: قيمة الدالة عند x(n)<br><b>f\'(x(n))</b>: قيمة المشتقة عند x(n)<br><b>x(n+1)</b>: التقريب الجديد',
        'conditions': '• تحتاج حساب المشتقة f\'(x)<br>• يجب أن f\'(x(n)) ≠ 0<br>• التقارب سريع (تربيعي) إذا كان التخمين الابتدائي قريباً من الجذر',
        'stopping': '• |x(n+1) - x(n)| < ε<br>• أو |f(x(n))| < ε<br>• أو الوصول لأقصى عدد تكرارات',
        'steps': '1. اختر نقطة ابتدائية x0<br>2. احسب f(x0) و f\'(x0)<br>3. تحقق أن f\'(x0) ≠ 0<br>4. احسب x1 = x0 - f(x0)/f\'(x0)<br>5. حدّث x0 = x1<br>6. كرر حتى تتحقق شروط التوقف',
        'example': 'f(x) = x³ - x - 2, x0 = 1.5<br>f(1.5) = 0.875, f\'(1.5) = 5.75<br>x1 = 1.5 - 0.875/5.75 = 1.3478<br>f(1.3478) = 0.1006, f\'(1.3478) = 4.449<br>x2 = 1.3478 - 0.1006/4.449 = 1.3252',
    },
    'jacobi': {
        'title_ar': 'طريقة جاكوبي',
        'title_en': 'Jacobi Iterative Method',
        'goal': 'حل نظام معادلات خطية AX = B بطريقة تكرارية',
        'idea': 'نعزل كل متغير من المعادلة الخاصة به، ثم نعوض بقيم التخمين الابتدائي لحساب قيم جديدة، ونكرر حتى التقارب.',
        'formula': 'x_i^(k+1) = (b_i - Σ(a_ij × x_j^(k))) / a_ii     (j ≠ i)',
        'symbols': '<b>A</b>: مصفوفة المعاملات<br><b>B</b>: متجه الثوابت<br><b>x^(k)</b>: التقريب في التكرار k<br><b>a_ii</b>: العنصر القطري',
        'conditions': '• يجب أن تكون المصفوفة A مهيمنة قطرياً (Diagonally Dominant) لضمان التقارب<br>• a_ii ≠ 0 لكل i',
        'stopping': '• max|x_i^(k+1) - x_i^(k)| < ε<br>• أو الوصول لأقصى عدد تكرارات',
        'steps': '1. اكتب النظام AX = B<br>2. اعزل كل x_i<br>3. ابدأ بتخمين ابتدائي x^(0)<br>4. عوّض في المعادلات لحساب x^(1)<br>5. كرر حتى التقارب',
        'example': '4x - y = 1<br>-x + 4y - z = 5<br>-y + 4z = 0<br><br>x = (1 + y) / 4<br>y = (5 + x + z) / 4<br>z = y / 4',
    },
    'gauss': {
        'title_ar': 'طريقة جاوس للحذف',
        'title_en': 'Gauss Elimination',
        'goal': 'حل نظام معادلات خطية AX = B بتحويل المصفوفة إلى شكل مثلثي علوي',
        'idea': 'نقوم بعمليات صفية (Row Operations) على المصفوفة الموسعة [A|B] لتحويلها إلى شكل مثلثي علوي، ثم نستخدم التعويض الخلفي لإيجاد الحل.',
        'formula': 'R_i → R_i - (a_ik / a_kk) × R_k',
        'symbols': '<b>R_i</b>: الصف i<br><b>a_ik</b>: العنصر في الصف i والعمود k<br><b>a_kk</b>: العنصر المحوري (Pivot)',
        'conditions': '• المصفوفة A يجب أن تكون مربعة<br>• det(A) ≠ 0 (غير منفردة)',
        'stopping': 'بعد (n-1) خطوة حذف تصبح المصفوفة مثلثية علوية',
        'steps': '1. اكتب المصفوفة الموسعة [A|B]<br>2. للعمود k من 1 إلى n-1:<br>&nbsp;&nbsp;a. تأكد أن a_kk ≠ 0 (أو قم بتبديل الصفوف)<br>&nbsp;&nbsp;b. لكل صف i > k: اطرح مضاعفاً مناسباً من الصف k<br>3. حل بالتعويض الخلفي',
        'example': '[4 -1 0 | 1]<br>[-1 4 -1 | 5]<br>[0 -1 4 | 0]<br><br>R2 → R2 + (1/4)R1<br>R3 → R3 (لا تغيير)',
    },
    'cramer': {
        'title_ar': 'طريقة كرامر',
        'title_en': "Cramer's Rule",
        'goal': 'حل نظام معادلات خطية باستخدام المحددات (Determinants)',
        'idea': 'نحسب محدد المصفوفة A ومحددات المصفوفات الناتجة عن استبدال كل عمود بمتجه الثوابت B.',
        'formula': 'x_i = det(A_i) / det(A)',
        'symbols': '<b>det(A)</b>: محدد المصفوفة الأصلية<br><b>A_i</b>: المصفوفة الناتجة عن استبدال العمود i بالمتجه B<br><b>det(A_i)</b>: محدد المصفوفة المعدلة',
        'conditions': '• det(A) ≠ 0<br>• المصفوفة مربعة<br>• مناسبة للأنظمة الصغيرة (n ≤ 4)',
        'stopping': 'لا تحتاج تكرارات - طريقة مباشرة',
        'steps': '1. احسب det(A)<br>2. لكل متغير x_i:<br>&nbsp;&nbsp;a. أنشئ A_i باستبدال العمود i بـ B<br>&nbsp;&nbsp;b. احسب det(A_i)<br>&nbsp;&nbsp;c. x_i = det(A_i) / det(A)',
        'example': 'A = [[4,-1],[−1,4]], B = [1,5]<br>det(A) = 16 - 1 = 15<br>A₁ = [[1,-1],[5,4]], det(A₁) = 4+5 = 9<br>x₁ = 9/15 = 0.6',
    },
    'inverse': {
        'title_ar': 'طريقة معكوس المصفوفة',
        'title_en': 'Matrix Inverse Method',
        'goal': 'حل نظام معادلات خطية باستخدام معكوس المصفوفة',
        'idea': 'إذا كان AX = B، فإن X = A⁻¹ × B',
        'formula': 'X = A⁻¹ × B',
        'symbols': '<b>A⁻¹</b>: معكوس المصفوفة A<br><b>B</b>: متجه الثوابت<br><b>X</b>: متجه المجاهيل',
        'conditions': '• det(A) ≠ 0 (المصفوفة غير منفردة)<br>• المصفوفة مربعة',
        'stopping': 'لا تحتاج تكرارات - طريقة مباشرة',
        'steps': '1. احسب det(A) وتأكد أنه ≠ 0<br>2. احسب A⁻¹<br>3. احسب X = A⁻¹ × B',
        'example': 'A = [[2,1],[5,3]], B = [4,7]<br>det(A) = 6-5 = 1<br>A⁻¹ = [[3,-1],[-5,2]]<br>X = [[3,-1],[-5,2]] × [4,7] = [5,-6]',
    },
    'lagrange': {
        'title_ar': 'طريقة لاجرانج للاستيفاء',
        'title_en': 'Lagrange Interpolation',
        'goal': 'إيجاد قيمة دالة عند نقطة معينة بمعرفة عدة نقاط بيانات',
        'idea': 'نبني كثير حدود يمر بجميع النقاط المعطاة، ثم نحسب قيمته عند النقطة المطلوبة.',
        'formula': 'P(x) = Σ y_i × L_i(x)<br>L_i(x) = Π (x - x_j) / (x_i - x_j)  (j ≠ i)',
        'symbols': '<b>(x_i, y_i)</b>: نقاط البيانات المعطاة<br><b>L_i(x)</b>: كثير حدود لاجرانج الأساسي<br><b>P(x)</b>: كثير حدود الاستيفاء',
        'conditions': '• يجب ألا تتكرر قيم x<br>• عدد قيم x يجب أن يساوي عدد قيم y<br>• الدرجة = عدد النقاط - 1',
        'stopping': 'لا تحتاج تكرارات - حساب مباشر',
        'steps': '1. حدد نقاط البيانات (x_i, y_i)<br>2. لكل i، احسب L_i(x)<br>3. احسب P(x) = Σ y_i × L_i(x)',
        'example': 'النقاط: (1,1), (2,8), (3,27), (4,64)<br>لإيجاد P(2.5):<br>L₀(2.5) = (2.5-2)(2.5-3)(2.5-4) / (1-2)(1-3)(1-4) = ...',
    },
    'differentiation': {
        'title_ar': 'التفاضل العددي',
        'title_en': 'Numerical Differentiation',
        'goal': 'تقريب مشتقة دالة عند نقطة معينة عددياً',
        'idea': 'استخدام قيم الدالة عند نقاط قريبة لتقريب المشتقة باستخدام صيغة الفروق المركزية.',
        'formula': "f'(x₀) ≈ [f(x₀ + h) - f(x₀ - h)] / (2h)",
        'symbols': '<b>x₀</b>: النقطة المراد حساب المشتقة عندها<br><b>h</b>: حجم الخطوة<br><b>f(x₀±h)</b>: قيم الدالة عند النقاط المجاورة',
        'conditions': '• h يجب أن يكون صغيراً بما يكفي لدقة جيدة<br>• لكن ليس صغيراً جداً (لتجنب أخطاء التقريب العائم)',
        'stopping': 'لا تحتاج تكرارات - حساب مباشر',
        'steps': '1. اختر النقطة x₀ والخطوة h<br>2. احسب f(x₀ + h)<br>3. احسب f(x₀ - h)<br>4. طبّق القانون',
        'example': "f(x) = x², x₀ = 2, h = 0.01<br>f(2.01) = 4.0401<br>f(1.99) = 3.9601<br>f'(2) ≈ (4.0401 - 3.9601) / 0.02 = 4.0",
    },
    'integration': {
        'title_ar': 'التكامل العددي',
        'title_en': 'Numerical Integration (Trapezoidal Rule)',
        'goal': 'تقريب قيمة التكامل المحدد للدالة عددياً',
        'idea': 'تقسيم الفترة [a,b] إلى n فترة فرعية متساوية، وتقريب المساحة تحت المنحنى بمجموع مساحات أشباه المنحرفات.',
        'formula': 'I ≈ (h/2) × [f(x₀) + 2×Σf(x_i) + f(x_n)]<br>h = (b-a)/n',
        'symbols': '<b>[a,b]</b>: فترة التكامل<br><b>n</b>: عدد الفترات الفرعية<br><b>h</b>: عرض كل فترة فرعية<br><b>x_i</b>: نقاط التقسيم',
        'conditions': '• n > 0<br>• a < b<br>• كلما زاد n، زادت الدقة',
        'stopping': 'لا تحتاج تكرارات - حساب مباشر',
        'steps': '1. احسب h = (b-a)/n<br>2. احسب نقاط التقسيم x_i = a + i×h<br>3. احسب f(x_i) لكل نقطة<br>4. طبّق قانون شبه المنحرفات',
        'example': 'f(x) = x², [0,2], n = 4<br>h = 0.5<br>النقاط: 0, 0.5, 1, 1.5, 2<br>f: 0, 0.25, 1, 2.25, 4<br>I ≈ 0.25 × (0 + 2(0.25+1+2.25) + 4) = 2.75',
    },
}

# ============================================================
#  Quiz Question Bank
# ============================================================
QUIZ_BANK = {
    'bisection': [
        ("ما نوع طريقة التنصيف؟", ["طريقة مفتوحة", "طريقة مغلقة (تحتاج فترة)", "طريقة تكرارية للمصفوفات", "طريقة استيفاء"], 1),
        ("ما شرط بدء طريقة التنصيف؟", ["f'(a) ≠ 0", "f(a) × f(b) < 0", "f(a) = f(b)", "f(a) > 0"], 1),
        ("كيف يُحسب منتصف الفترة في التنصيف؟", ["c = a × b", "c = (a + b) / 2", "c = b - f(b)(b-a)/(f(b)-f(a))", "c = a - f(a)/f'(a)"], 1),
        ("ما سرعة تقارب طريقة التنصيف؟", ["تربيعية (Quadratic)", "خطية (Linear)", "تكعيبية (Cubic)", "فائقة خطية"], 1),
        ("ما الذي يحدث للفترة [a,b] مع كل تكرار؟", ["تبقى ثابتة", "تتضاعف", "تنقسم إلى نصف", "تتقلص بمقدار h"], 2),
        ("هل تحتاج طريقة التنصيف لحساب المشتقة؟", ["نعم دائماً", "لا", "أحياناً", "فقط عند التكرار الأول"], 1),
        ("ما الميزة الرئيسية لطريقة التنصيف؟", ["سرعة التقارب", "مضمونة التقارب", "لا تحتاج نقطة بداية", "تعمل مع المصفوفات"], 1),
        ("إذا كان f(a)<0 و f(c)>0، أين يقع الجذر؟", ["في [c, b]", "في [a, c]", "عند النقطة c", "لا يوجد جذر"], 1),
    ],
    'false_position': [
        ("ما الفرق الأساسي بين التنصيف والوضع الكاذب؟", ["لا فرق بينهما", "الوضع الكاذب يستخدم خطاً مستقيماً بدل المنتصف", "الوضع الكاذب يحتاج المشتقة", "الوضع الكاذب أبطأ دائماً"], 1),
        ("ما قانون طريقة الوضع الكاذب؟", ["c = (a+b)/2", "c = b - f(b)(b-a)/(f(b)-f(a))", "c = x - f(x)/f'(x)", "c = a × b / (a+b)"], 1),
        ("هل طريقة الوضع الكاذب مغلقة أم مفتوحة؟", ["مفتوحة", "مغلقة", "لا هذه ولا تلك", "تعتمد على الدالة"], 1),
        ("ما شرط بدء طريقة الوضع الكاذب؟", ["f(a) = 0", "f(a) × f(b) < 0", "f'(a) ≠ 0", "a = 0"], 1),
    ],
    'secant': [
        ("هل طريقة القاطع تحتاج حساب المشتقة؟", ["نعم", "لا", "أحياناً", "فقط في البداية"], 1),
        ("كم نقطة بداية تحتاج طريقة القاطع؟", ["نقطة واحدة", "نقطتين", "ثلاث نقاط", "لا تحتاج نقطة بداية"], 1),
        ("ما نوع طريقة القاطع؟", ["مغلقة", "مفتوحة", "مباشرة", "تكرارية للمصفوفات"], 1),
        ("ما سرعة تقارب طريقة القاطع؟", ["خطية", "فائقة خطية (≈1.618)", "تربيعية", "ثابتة"], 1),
    ],
    'newton': [
        ("ما الذي تستخدمه طريقة نيوتن لتقريب الجذر؟", ["خط قاطع", "خط مماس (Tangent)", "منتصف الفترة", "الاستيفاء"], 1),
        ("ما قانون نيوتن رافسون؟", ["x(n+1) = (a+b)/2", "x(n+1) = x(n) - f(x(n))/f'(x(n))", "x(n+1) = x(n) - f(x(n))×h", "x(n+1) = x(n) + f'(x(n))"], 1),
        ("ما سرعة تقارب نيوتن رافسون؟", ["خطية", "فائقة خطية", "تربيعية (Quadratic)", "أسية"], 2),
        ("متى تفشل طريقة نيوتن؟", ["عندما f(x) = 0", "عندما f'(x) = 0", "عندما x > 10", "لا تفشل أبداً"], 1),
        ("هل طريقة نيوتن مغلقة أم مفتوحة؟", ["مغلقة", "مفتوحة", "كلاهما", "لا شيء مما سبق"], 1),
        ("كم نقطة بداية تحتاج طريقة نيوتن؟", ["نقطتين", "ثلاث نقاط", "نقطة واحدة", "لا تحتاج"], 2),
    ],
    'jacobi': [
        ("ما نوع طريقة جاكوبي؟", ["طريقة مباشرة", "طريقة تكرارية", "طريقة بيانية", "طريقة تحليلية"], 1),
        ("ما شرط تقارب جاكوبي؟", ["det(A) = 0", "المصفوفة مهيمنة قطرياً", "المصفوفة متماثلة", "n < 5"], 1),
        ("ماذا يحدث إذا كان عنصر القطر = 0؟", ["يتقارب أسرع", "يحدث قسمة على صفر", "لا مشكلة", "يتوقف تلقائياً"], 1),
        ("ما الفرق بين جاكوبي وجاوس-سايدل؟", ["لا فرق", "جاوس-سايدل يستخدم القيم المحدثة فوراً", "جاكوبي أسرع دائماً", "جاوس-سايدل يحتاج المشتقة"], 1),
    ],
    'gauss': [
        ("ما هدف طريقة جاوس للحذف؟", ["إيجاد الجذور", "تحويل المصفوفة لشكل مثلثي علوي", "حساب المحدد فقط", "إيجاد معكوس المصفوفة"], 1),
        ("ما هو التعويض الخلفي (Back Substitution)؟", ["حل المعادلات من الأخيرة للأولى", "تبديل الصفوف", "ضرب المصفوفة بمعكوسها", "حذف الأعمدة"], 0),
        ("ماذا نفعل إذا كان العنصر المحوري = 0؟", ["نتوقف", "نبدل الصفوف (Pivoting)", "نحذف المعادلة", "نضيف 1 له"], 1),
        ("هل طريقة جاوس تكرارية أم مباشرة؟", ["تكرارية", "مباشرة", "كلاهما", "لا شيء"], 1),
    ],
    'lagrange': [
        ("ما الهدف من الاستيفاء بطريقة لاجرانج؟", ["إيجاد جذور المعادلة", "إيجاد قيمة دالة عند نقطة بمعرفة نقاط أخرى", "حل المصفوفات", "حساب التكامل"], 1),
        ("ماذا يحدث إذا تكررت قيم x؟", ["لا مشكلة", "تحدث قسمة على صفر", "النتيجة أدق", "يتجاهلها البرنامج"], 1),
        ("ما درجة كثير حدود لاجرانج إذا كان لدينا 4 نقاط؟", ["4", "3", "2", "5"], 1),
    ],
    'differentiation': [
        ("ما صيغة الفروق المركزية لحساب المشتقة؟", ["[f(x+h) - f(x)] / h", "[f(x+h) - f(x-h)] / (2h)", "[f(x) - f(x-h)] / h", "f(x) × h"], 1),
        ("لماذا لا نجعل h صغيراً جداً (مثل 10⁻²⁰)؟", ["لأن الحساب يصبح بطيئاً", "بسبب أخطاء التقريب العائم (Floating Point)", "لأنه غير مسموح", "لا يوجد سبب"], 1),
    ],
    'integration': [
        ("ما مبدأ طريقة شبه المنحرفات؟", ["تقريب الدالة بمستقيمات بين النقاط", "تقريب الدالة بمنحنيات", "استخدام المشتقة", "التكامل التحليلي"], 0),
        ("كلما زاد عدد الفترات n...؟", ["قلت الدقة", "زادت الدقة", "لا تأثير", "زاد الخطأ"], 1),
        ("ما قيمة h إذا كان [a,b]=[0,4] و n=8؟", ["0.25", "0.5", "1", "2"], 1),
    ],
}

# ============================================================
#  False Position Backend (add if missing in backend)
# ============================================================
def false_position_method(expr, a, b, tol, max_iter):
    """False Position (Regula Falsi) method."""
    fa = safe_eval_func(expr, a)
    fb = safe_eval_func(expr, b)
    if fa * fb > 0:
        raise ValueError("يجب أن يكون f(a) و f(b) بإشارتين متعاكستين")
    rows = []
    c = a
    for i in range(1, max_iter + 1):
        c = b - fb * (b - a) / (fb - fa)
        fc = safe_eval_func(expr, c)
        rows.append((i, a, b, c, fa, fb, fc))
        if abs(fc) < tol or abs(b - a) < tol:
            return c, rows, True
        if fa * fc < 0:
            b, fb = c, fc
        else:
            a, fa = c, fc
    return c, rows, False

def solve_false_position(values):
    """Solve using False Position method, returns Solution object."""
    expr = values['f']
    a, b = float(values['a']), float(values['b'])
    tol, max_iter = float(values['tol']), int(values['max_iter'])
    root, rows, converged = false_position_method(expr, a, b, tol, max_iter)

    steps = ["f(x) =", f"   {expr}",
             "الفترة الابتدائية [a, b] :", f"   a = {a:.6f} ,  b = {b:.6f}",
             "قيمة الدقة ε وأقصى عدد تكرارات :", f"   eps = {tol}   max_iter = {max_iter}", ""]
    for (i, a_, b_, c, fa, fb, fc) in rows:
        steps.append(f">> التكرار {i}")
        steps.append(f"   a = {a_:.6f}, b = {b_:.6f}")
        steps.append(f"   f(a) = {fa:.6e}, f(b) = {fb:.6e}")
        steps.append(f"   c = b - f(b)(b-a)/(f(b)-f(a)) = {c:.6f}")
        steps.append(f"   f(c) = {fc:.6e}")
        if fa * fc < 0:
            steps.append("   الجذر في [a, c] → b = c")
        else:
            steps.append("   الجذر في [c, b] → a = c")
        steps.append("")

    table_columns = ["تكرار", "a", "b", "c", "f(c)", "|b-a|"]
    table_rows = [[str(i), f"{a_:.6f}", f"{b_:.6f}", f"{c:.6f}", f"{fc:.6f}", f"{abs(b_-a_):.6f}"]
                  for (i, a_, b_, c, fa, fb, fc) in rows]
    summary = [("الجذر التقريبي", f"{root:.8f}"),
               ("الحالة", "تقارب ✓" if converged else "لم يتقارب ✗"),
               ("عدد التكرارات", str(len(rows))),
               ("التسامح", f"{tol}")]

    if backend:
        return backend.Solution(steps, table_columns, table_rows, "جدول التكرارات", summary)
    # Fallback Solution class
    class Sol:
        pass
    s = Sol()
    s.steps = steps
    s.table_columns = table_columns
    s.table_rows = table_rows
    s.table_caption = "جدول التكرارات"
    s.summary = summary
    return s

def solve_interval_classification(values):
    """Classify intervals for roots."""
    expr = values['f']
    start = float(values['start'])
    end = float(values['end'])
    step = float(values['step'])

    intervals = []
    x = start
    while x < end:
        x_next = min(x + step, end)
        try:
            fa = safe_eval_func(expr, x)
            fb = safe_eval_func(expr, x_next)
            has_root = fa * fb < 0
            intervals.append((x, x_next, fa, fb, has_root))
        except Exception:
            intervals.append((x, x_next, float('nan'), float('nan'), False))
        x = x_next
        if x >= end:
            break

    steps = ["f(x) =", f"   {expr}",
             f"الفترة [{start}, {end}] بخطوة {step}", ""]
    root_intervals = []
    for (a, b, fa, fb, has_root) in intervals:
        if has_root:
            steps.append(f"   ✓ [{a:.4f}, {b:.4f}] : f(a)={fa:.4f}, f(b)={fb:.4f} → يحتوي جذر")
            root_intervals.append((a, b))
        else:
            steps.append(f"   ✗ [{a:.4f}, {b:.4f}] : f(a)={fa:.4f}, f(b)={fb:.4f}")

    table_columns = ["a", "b", "f(a)", "f(b)", "يحتوي جذر؟"]
    table_rows = [[f"{a:.4f}", f"{b:.4f}", f"{fa:.4f}", f"{fb:.4f}", "✓ نعم" if hr else "✗ لا"]
                  for (a, b, fa, fb, hr) in intervals]
    summary = [("عدد الفترات", str(len(intervals))),
               ("فترات تحتوي جذور", str(len(root_intervals)))]

    if backend:
        return backend.Solution(steps, table_columns, table_rows, "تصنيف الفترات", summary)
    class Sol:
        pass
    s = Sol()
    s.steps = steps; s.table_columns = table_columns; s.table_rows = table_rows
    s.table_caption = "تصنيف الفترات"; s.summary = summary
    return s

# ============================================================
#  Icon Widget
# ============================================================
class IconWidget(QWidget):
    def __init__(self, method_type, parent=None):
        super().__init__(parent)
        self.method_type = method_type
        self.setFixedSize(80, 80)
        self.setStyleSheet("background: transparent; border: none;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        painter.setPen(QPen(QColor("#cccccc"), 2))
        painter.drawLine(10, h-10, w-10, h-10)
        painter.drawLine(10, 10, 10, h-10)
        path = QPainterPath()
        path.moveTo(10, h-20)
        path.cubicTo(30, h-20, 50, 20, w-10, 20)

        colors = {"bisection": "#005b9f", "secant": "#2a9d8f", "newton": "#7b2cbf",
                  "false_position": "#e76f51", "jacobi": "#2a9d8f", "gauss": "#005b9f",
                  "lagrange": "#7b2cbf", "interval": "#d62828", "cramer": "#e76f51",
                  "inverse": "#2a9d8f", "differentiation": "#005b9f", "integration": "#7b2cbf"}
        color = colors.get(self.method_type, "#d62828")

        if self.method_type in ("jacobi", "gauss", "cramer", "inverse"):
            painter.setPen(QPen(QColor(color), 2))
            for i in range(4):
                painter.drawLine(20 + i*15, 20, 20 + i*15, 65)
                painter.drawLine(20, 20 + i*15, 65, 20 + i*15)
        else:
            painter.setPen(QPen(QColor(color), 3))
            painter.drawPath(path)
            if self.method_type == "bisection":
                painter.setPen(QPen(QColor("red"), 2, Qt.DashLine))
                painter.drawLine(20, h-10, 20, h-25)
                painter.drawLine(w-20, h-10, w-20, 25)
            elif self.method_type == "false_position":
                painter.setPen(QPen(QColor("red"), 2))
                painter.drawLine(20, h-20, w-20, 20)
            elif self.method_type == "secant":
                painter.setPen(QPen(QColor("red"), 2))
                painter.drawLine(20, h-22, w-20, 22)
            elif self.method_type == "newton":
                painter.setPen(QPen(QColor("red"), 2))
                painter.drawLine(w-30, 40, w-10, 10)

# ============================================================
#  Enhanced MiniLabDialog
# ============================================================
class MiniLabDialog(QDialog):
    def __init__(self, parent, method_info, solve_func):
        super().__init__(parent)
        self.setWindowTitle(f"معمل: {method_info['title']}")
        self.setMinimumSize(1050, 750)
        self.setStyleSheet("background-color: #0b1426; color: white;")
        self.method_info = method_info
        self.solve_func = solve_func
        self.entries = {}
        self.current_solution = None
        self.vis_step = 0
        self.vis_timer = None

        layout = QVBoxLayout(self)
        header = QLabel(f"🧪 معمل: {method_info['title']}")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("color: #64ffda; padding: 10px;")
        layout.addWidget(header)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(TAB_STYLE)

        self.setup_lesson_tab()
        self.setup_visual_tab()
        self.setup_app_tab()
        self.setup_results_tab()
        self.setup_iteration_analysis_tab()
        self.setup_quiz_tab()

        layout.addWidget(self.tabs)

    def setup_lesson_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        content = QWidget()
        cl = QVBoxLayout(content)

        method_key = self.method_info.get('method_key', '')
        lesson = LESSONS.get(method_key, {})

        title_ar = lesson.get('title_ar', self.method_info['title'])
        title_en = lesson.get('title_en', '')

        header = QLabel(f"📖 {title_ar}")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setStyleSheet("color: #64ffda;")
        cl.addWidget(header)

        if title_en:
            en_lbl = QLabel(title_en)
            en_lbl.setFont(QFont("Arial", 14))
            en_lbl.setStyleSheet("color: #a8b2d1;")
            cl.addWidget(en_lbl)

        sections = [
            ("🎯 الهدف", lesson.get('goal', '')),
            ("💡 الفكرة", lesson.get('idea', '')),
            ("📐 القانون", lesson.get('formula', '')),
            ("🔤 شرح الرموز", lesson.get('symbols', '')),
            ("⚠️ شروط الاستخدام", lesson.get('conditions', '')),
            ("🛑 معيار التوقف", lesson.get('stopping', '')),
            ("📋 خطوات الطريقة", lesson.get('steps', '')),
            ("📝 مثال مبسط", lesson.get('example', '')),
        ]

        for sec_title, sec_content in sections:
            if sec_content:
                s_title = QLabel(sec_title)
                s_title.setFont(QFont("Arial", 14, QFont.Bold))
                s_title.setStyleSheet("color: #ffd166; margin-top: 15px;")
                cl.addWidget(s_title)

                s_body = QLabel(sec_content)
                s_body.setFont(QFont("Arial", 12))
                s_body.setTextFormat(Qt.RichText)
                s_body.setWordWrap(True)
                s_body.setStyleSheet("color: #e0e0e0; line-height: 1.6; padding: 5px 10px; background-color: #1a365d; border-radius: 6px; margin: 5px 0;")
                cl.addWidget(s_body)

        if not lesson:
            fallback = QLabel(self.method_info.get('lesson_text', 'محتوى الدرس سيُضاف قريباً...'))
            fallback.setFont(QFont("Arial", 13))
            fallback.setTextFormat(Qt.RichText)
            fallback.setWordWrap(True)
            cl.addWidget(fallback)

        cl.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        self.tabs.addTab(tab, "📖 الدرس")

    def setup_visual_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Control buttons
        ctrl_frame = QFrame()
        ctrl_frame.setStyleSheet("background-color: #1a365d; border-radius: 8px; padding: 5px;")
        ctrl_layout = QHBoxLayout(ctrl_frame)

        self.vis_status = QLabel("قم بالحساب أولاً لعرض التصور البصري")
        self.vis_status.setFont(QFont("Arial", 11))
        self.vis_status.setStyleSheet("color: #a8b2d1;")
        ctrl_layout.addWidget(self.vis_status)
        ctrl_layout.addStretch()

        for text, slot in [("⏮ إعادة", self.vis_reset), ("◀ الخطوة السابقة", self.vis_prev),
                           ("▶ الخطوة التالية", self.vis_next), ("⏩ تشغيل كامل", self.vis_play_all),
                           ("⏸ إيقاف", self.vis_stop)]:
            btn = QPushButton(text)
            btn.setStyleSheet("QPushButton { background-color: #005b9f; color: white; padding: 6px 12px; border-radius: 4px; border: none; font-weight: bold; } QPushButton:hover { background-color: #0077b6; }")
            btn.clicked.connect(slot)
            ctrl_layout.addWidget(btn)

        layout.addWidget(ctrl_frame)

        if HAS_MATPLOTLIB:
            self.vis_figure = Figure(figsize=(8, 5), facecolor='#0d1b2a')
            self.vis_canvas = FigureCanvas(self.vis_figure)
            layout.addWidget(self.vis_canvas)
        else:
            layout.addWidget(QLabel("مكتبة Matplotlib مطلوبة للرسوم البيانية.\npip install matplotlib"))

        self.tabs.addTab(tab, "🎨 التصور البصري")

    def setup_app_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        form = QFrame()
        form.setStyleSheet("background-color: #1a365d; border-radius: 8px; padding: 20px;")
        fl = QGridLayout(form)

        for i, (label_text, key, default) in enumerate(self.method_info['fields']):
            lbl = QLabel(label_text)
            lbl.setFont(QFont("Arial", 12, QFont.Bold))
            entry = QLineEdit(default)
            entry.setFont(QFont("Consolas", 12))
            entry.setStyleSheet(INPUT_STYLE)
            fl.addWidget(lbl, i, 0)
            fl.addWidget(entry, i, 1)
            self.entries[key] = entry

        layout.addWidget(form)
        btn = QPushButton("▶ احسب الآن")
        btn.setFont(QFont("Arial", 14, QFont.Bold))
        btn.setStyleSheet("QPushButton { background-color: #0077b6; color: white; padding: 15px; border-radius: 8px; } QPushButton:hover { background-color: #005b9f; }")
        btn.clicked.connect(self.calculate)
        layout.addWidget(btn)
        layout.addStretch()
        self.tabs.addTab(tab, "🧮 التطبيق")

    def setup_results_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.res_summary_frame = QFrame()
        self.res_summary_frame.setStyleSheet("background-color: #1a365d; border-radius: 8px; padding: 10px;")
        self.res_summary_layout = QVBoxLayout(self.res_summary_frame)
        self.res_lbl = QLabel("قم بإجراء الحسابات لعرض النتائج هنا.")
        self.res_lbl.setFont(QFont("Arial", 14))
        self.res_lbl.setAlignment(Qt.AlignCenter)
        self.res_summary_layout.addWidget(self.res_lbl)
        layout.addWidget(self.res_summary_frame)

        self.res_table = QTableWidget()
        self.res_table.hide()
        self.res_table.setStyleSheet("""
            QTableWidget { background-color: #0d1b2a; color: white; gridline-color: #1f3659; border: 1px solid #1f3659; }
            QHeaderView::section { background-color: #005b9f; color: white; padding: 6px; font-weight: bold; border: 1px solid #1f3659; }
            QTableWidget::item { padding: 4px; }
            QTableWidget::item:selected { background-color: #1a365d; }
        """)
        self.res_table.cellClicked.connect(self.on_iteration_clicked)
        layout.addWidget(self.res_table)

        self.tabs.addTab(tab, "📊 النتائج")

    def setup_iteration_analysis_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.iter_analysis_label = QLabel("اضغط على أي صف في جدول النتائج لعرض تحليل مفصل للتكرار.")
        self.iter_analysis_label.setFont(QFont("Arial", 14))
        self.iter_analysis_label.setAlignment(Qt.AlignCenter)
        self.iter_analysis_label.setStyleSheet("color: #a8b2d1;")
        layout.addWidget(self.iter_analysis_label)

        self.iter_detail_text = QTextEdit()
        self.iter_detail_text.setReadOnly(True)
        self.iter_detail_text.setFont(QFont("Consolas", 12))
        self.iter_detail_text.setStyleSheet("background-color: #0d1b2a; color: #e0e0e0; border: 1px solid #1f3659; border-radius: 6px; padding: 10px;")
        self.iter_detail_text.hide()
        layout.addWidget(self.iter_detail_text)

        if HAS_MATPLOTLIB:
            self.iter_figure = Figure(figsize=(6, 3), facecolor='#0d1b2a')
            self.iter_canvas = FigureCanvas(self.iter_figure)
            self.iter_canvas.hide()
            layout.addWidget(self.iter_canvas)

        self.tabs.addTab(tab, "🔎 تحليل التكرارات")

    def setup_quiz_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        method_key = self.method_info.get('method_key', '')
        questions = QUIZ_BANK.get(method_key, [])

        if not questions:
            layout.addWidget(QLabel("لا توجد أسئلة متاحة لهذه الطريقة حالياً."))
            layout.addStretch()
            self.tabs.addTab(tab, "📝 اختبار")
            return

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        content = QWidget()
        cl = QVBoxLayout(content)

        title = QLabel(f"📝 اختبار: {self.method_info['title']}")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #64ffda;")
        cl.addWidget(title)

        self.quiz_groups = []
        self.quiz_correct = []

        for idx, (q_text, options, correct_idx) in enumerate(questions):
            q_frame = QFrame()
            q_frame.setStyleSheet("background-color: #1a365d; border-radius: 8px; padding: 10px; margin: 5px 0;")
            q_layout = QVBoxLayout(q_frame)

            q_lbl = QLabel(f"السؤال {idx+1}: {q_text}")
            q_lbl.setFont(QFont("Arial", 12, QFont.Bold))
            q_lbl.setWordWrap(True)
            q_layout.addWidget(q_lbl)

            bg = QButtonGroup(q_frame)
            for i, opt in enumerate(options):
                rb = QRadioButton(opt)
                rb.setFont(QFont("Arial", 11))
                bg.addButton(rb, i)
                q_layout.addWidget(rb)

            self.quiz_groups.append(bg)
            self.quiz_correct.append(correct_idx)
            cl.addWidget(q_frame)

        self.quiz_result_label = QLabel("")
        self.quiz_result_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.quiz_result_label.setAlignment(Qt.AlignCenter)
        cl.addWidget(self.quiz_result_label)

        btn = QPushButton("✅ تحقق من الإجابات")
        btn.setFont(QFont("Arial", 13, QFont.Bold))
        btn.setStyleSheet("QPushButton { background-color: #2a9d8f; color: white; padding: 12px; border-radius: 6px; border: none; } QPushButton:hover { background-color: #21867a; }")
        btn.clicked.connect(self.check_quiz)
        cl.addWidget(btn)

        cl.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        self.tabs.addTab(tab, "📝 اختبار")

    def check_quiz(self):
        correct = 0
        total = len(self.quiz_groups)
        for i, (bg, correct_idx) in enumerate(zip(self.quiz_groups, self.quiz_correct)):
            if bg.checkedId() == correct_idx:
                correct += 1

        pct = (correct / total * 100) if total > 0 else 0
        color = "#6ee7a0" if pct >= 70 else "#ffd166" if pct >= 50 else "#f97171"
        self.quiz_result_label.setText(f"النتيجة: {correct} / {total}  —  {pct:.0f}%")
        self.quiz_result_label.setStyleSheet(f"color: {color}; padding: 10px; background-color: #0d1b2a; border-radius: 6px;")

        method_key = self.method_info.get('method_key', '')
        if method_key:
            app_state.quiz_scores[method_key] = (correct, total)

    def calculate(self):
        if not self.solve_func:
            QMessageBox.critical(self, "خطأ", "لم يتم ربط دالة الحساب بعد.")
            return
        try:
            values = {k: e.text() for k, e in self.entries.items()}

            # Input validation
            method_key = self.method_info.get('method_key', '')
            if 'tol' in values:
                tol = float(values['tol'])
                if tol <= 0:
                    raise ValueError("الدقة (Tolerance) يجب أن تكون أكبر من صفر.")
            if 'max_iter' in values:
                mi = int(values['max_iter'])
                if mi <= 0:
                    raise ValueError("عدد التكرارات يجب أن يكون أكبر من صفر.")
            if 'n' in values:
                n = int(values['n'])
                if n <= 0:
                    raise ValueError("عدد الفترات يجب أن يكون أكبر من صفر.")

            solution = self.solve_func(values)
            self.current_solution = solution
            self.vis_step = 0

            # Update app state
            app_state.last_solution = solution
            app_state.last_method_name = self.method_info['title']
            app_state.last_method_type = method_key
            if 'f' in values:
                app_state.last_func_expr = values['f']

            # Mark method as completed
            if method_key:
                app_state.completed_methods.add(method_key)
                app_state.learning_status[method_key] = 'completed'

            # Switch to results tab
            self.tabs.setCurrentIndex(3)

            # Update summary
            self._clear_layout(self.res_summary_layout)
            summary_title = QLabel("✅ تمت العملية بنجاح!")
            summary_title.setFont(QFont("Arial", 14, QFont.Bold))
            summary_title.setStyleSheet("color: #6ee7a0;")
            self.res_summary_layout.addWidget(summary_title)

            if hasattr(solution, 'summary') and solution.summary:
                for label, value in solution.summary:
                    row = QHBoxLayout()
                    lbl = QLabel(f"{label}:")
                    lbl.setFont(QFont("Arial", 12))
                    lbl.setStyleSheet("color: #a8b2d1;")
                    val = QLabel(str(value))
                    val.setFont(QFont("Consolas", 13, QFont.Bold))
                    v_color = "#6ee7a0" if "✓" in str(value) else "#f97171" if "✗" in str(value) else "#ffd166"
                    val.setStyleSheet(f"color: {v_color};")
                    row.addWidget(lbl)
                    row.addStretch()
                    row.addWidget(val)
                    self.res_summary_layout.addLayout(row)

            # Update table
            if solution.table_columns and solution.table_rows:
                self.res_table.setColumnCount(len(solution.table_columns))
                self.res_table.setRowCount(len(solution.table_rows))
                self.res_table.setHorizontalHeaderLabels(solution.table_columns)
                self.res_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                for r, row_data in enumerate(solution.table_rows):
                    for c, col_data in enumerate(row_data):
                        item = QTableWidgetItem(str(col_data))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.res_table.setItem(r, c, item)
                self.res_table.show()

            # Update visualization
            self.update_visualization()

        except Exception as e:
            QMessageBox.critical(self, "خطأ حسابي", f"تأكد من صحة المدخلات:\n{str(e)}")

    def _clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_layout(child.layout())

    def update_visualization(self):
        if not HAS_MATPLOTLIB or not self.current_solution:
            return
        self.vis_figure.clear()
        ax = self.vis_figure.add_subplot(111)
        ax.set_facecolor('#0d1b2a')
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_edgecolor('#1f3659')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.title.set_color('white')

        method_key = self.method_info.get('method_key', '')
        sol = self.current_solution

        if method_key in ('bisection', 'false_position', 'secant', 'newton') and 'f' in self.entries:
            expr = self.entries['f'].text()
            try:
                # Determine plot range
                if 'a' in self.entries and 'b' in self.entries:
                    a_val = float(self.entries['a'].text())
                    b_val = float(self.entries['b'].text())
                    margin = (b_val - a_val) * 0.5
                    x_range = np.linspace(a_val - margin, b_val + margin, 200)
                elif 'x0' in self.entries:
                    x0_val = float(self.entries['x0'].text())
                    x_range = np.linspace(x0_val - 3, x0_val + 3, 200)
                else:
                    x_range = np.linspace(-5, 5, 200)

                y_range = np.array([safe_eval_func(expr, xi) for xi in x_range])
                ax.plot(x_range, y_range, color='#64ffda', linewidth=2, label='f(x)')
                ax.axhline(0, color='gray', linestyle='--', linewidth=0.8)
                ax.axvline(0, color='gray', linestyle='--', linewidth=0.8)

                # Show iteration points
                max_step = min(self.vis_step, len(sol.table_rows)) if self.vis_step > 0 else len(sol.table_rows)
                if method_key == 'bisection' and max_step > 0:
                    for i in range(max_step):
                        row = sol.table_rows[i]
                        c_val = float(row[3])
                        fc_val = float(row[4])
                        color = '#ff6b6b' if i < max_step - 1 else '#ffd166'
                        ax.plot(c_val, fc_val, 'o', color=color, markersize=6)
                        if i == max_step - 1:
                            ax.annotate(f'c={c_val:.4f}', (c_val, fc_val), color='white', fontsize=9,
                                       xytext=(10, 10), textcoords='offset points')
                elif method_key == 'newton' and max_step > 0:
                    for i in range(max_step):
                        row = sol.table_rows[i]
                        xi = float(row[1])
                        fxi = float(row[2])
                        xn = float(row[4])
                        ax.plot(xi, fxi, 'o', color='#ff6b6b', markersize=6)
                        # Tangent line
                        dfxi = float(row[3])
                        x_tan = np.linspace(xi - 1, xi + 1, 50)
                        y_tan = fxi + dfxi * (x_tan - xi)
                        alpha = 0.3 if i < max_step - 1 else 0.8
                        ax.plot(x_tan, y_tan, '--', color='#e76f51', alpha=alpha, linewidth=1)
                    last_row = sol.table_rows[max_step - 1]
                    root = float(last_row[4])
                    ax.plot(root, 0, '*', color='#ffd166', markersize=12)
                    ax.annotate(f'Root≈{root:.4f}', (root, 0), color='#ffd166', fontsize=10,
                               xytext=(10, -20), textcoords='offset points')
                elif method_key in ('secant', 'false_position') and max_step > 0:
                    for i in range(max_step):
                        row = sol.table_rows[i]
                        c_val = float(row[3])
                        fc_val = float(row[4]) if len(row) > 4 else 0
                        color = '#ff6b6b' if i < max_step - 1 else '#ffd166'
                        ax.plot(c_val, fc_val, 'o', color=color, markersize=6)

                ax.legend(loc='best', facecolor='#1a365d', edgecolor='#1f3659', labelcolor='white')
                ax.set_title(f'تصور: {self.method_info["title"]}', fontsize=12)
            except Exception:
                ax.text(0.5, 0.5, 'خطأ في رسم الدالة', color='white', ha='center', va='center', transform=ax.transAxes)

        elif method_key == 'jacobi' and sol.table_rows:
            n_vars = len(sol.table_columns) - 1
            max_step = min(self.vis_step, len(sol.table_rows)) if self.vis_step > 0 else len(sol.table_rows)
            iterations = list(range(max_step))
            for v in range(n_vars):
                vals = [float(sol.table_rows[i][v+1]) for i in range(max_step)]
                ax.plot(iterations, vals, 'o-', label=sol.table_columns[v+1], markersize=5)
            ax.set_xlabel('Iteration', color='white')
            ax.set_ylabel('Value', color='white')
            ax.set_title('تغير المتغيرات مع التكرارات', fontsize=12)
            ax.legend(loc='best', facecolor='#1a365d', edgecolor='#1f3659', labelcolor='white')

        elif method_key == 'lagrange' and 'xs' in self.entries:
            try:
                xs = [float(v) for v in self.entries['xs'].text().split()]
                ys = [float(v) for v in self.entries['ys'].text().split()]
                x_eval = float(self.entries['x_eval'].text())
                ax.plot(xs, ys, 'o', color='#ff6b6b', markersize=8, label='نقاط البيانات')
                x_fine = np.linspace(min(xs) - 0.5, max(xs) + 0.5, 200)
                y_fine = []
                for xf in x_fine:
                    total = 0
                    for i in range(len(xs)):
                        term = ys[i]
                        for j in range(len(xs)):
                            if j != i:
                                term *= (xf - xs[j]) / (xs[i] - xs[j])
                        total += term
                    y_fine.append(total)
                ax.plot(x_fine, y_fine, '-', color='#64ffda', linewidth=2, label='كثير حدود الاستيفاء')
                result_y = sum(float(sol.table_rows[i][1]) for i in range(len(sol.table_rows)))
                ax.plot(x_eval, result_y, '*', color='#ffd166', markersize=15, label=f'P({x_eval})')
                ax.legend(loc='best', facecolor='#1a365d', edgecolor='#1f3659', labelcolor='white')
                ax.set_title('استيفاء لاجرانج', fontsize=12)
            except Exception:
                pass

        elif method_key == 'integration' and 'f' in self.entries:
            try:
                expr = self.entries['f'].text()
                a_val = float(self.entries['a'].text())
                b_val = float(self.entries['b'].text())
                x_range = np.linspace(a_val - 0.5, b_val + 0.5, 200)
                y_range = [safe_eval_func(expr, xi) for xi in x_range]
                ax.plot(x_range, y_range, color='#64ffda', linewidth=2, label='f(x)')
                # Fill area
                x_fill = np.linspace(a_val, b_val, 100)
                y_fill = [safe_eval_func(expr, xi) for xi in x_fill]
                ax.fill_between(x_fill, y_fill, alpha=0.3, color='#2a9d8f')
                ax.axhline(0, color='gray', linestyle='--', linewidth=0.8)
                ax.legend(loc='best', facecolor='#1a365d', edgecolor='#1f3659', labelcolor='white')
                ax.set_title('التكامل العددي', fontsize=12)
            except Exception:
                pass

        self.vis_canvas.draw()
        self.vis_status.setText(f"الخطوة {self.vis_step} من {len(sol.table_rows) if sol else 0}")

    def vis_reset(self):
        self.vis_step = 0
        self.update_visualization()

    def vis_prev(self):
        if self.vis_step > 0:
            self.vis_step -= 1
            self.update_visualization()

    def vis_next(self):
        if self.current_solution and self.vis_step < len(self.current_solution.table_rows):
            self.vis_step += 1
            self.update_visualization()

    def vis_play_all(self):
        if not self.current_solution:
            return
        self.vis_step = 0
        self.vis_timer = QTimer()
        self.vis_timer.timeout.connect(self._vis_auto_step)
        self.vis_timer.start(700)

    def _vis_auto_step(self):
        if self.current_solution and self.vis_step < len(self.current_solution.table_rows):
            self.vis_step += 1
            self.update_visualization()
        else:
            if self.vis_timer:
                self.vis_timer.stop()

    def vis_stop(self):
        if self.vis_timer:
            self.vis_timer.stop()

    def on_iteration_clicked(self, row, col):
        if not self.current_solution:
            return
        sol = self.current_solution
        if row >= len(sol.table_rows):
            return

        self.tabs.setCurrentIndex(4)  # Iteration analysis tab
        self.iter_detail_text.show()

        row_data = sol.table_rows[row]
        method_key = self.method_info.get('method_key', '')

        detail = f"═══════════════════════════════════════\n"
        detail += f"  تحليل التكرار {row + 1}\n"
        detail += f"═══════════════════════════════════════\n\n"

        for i, col_name in enumerate(sol.table_columns):
            if i < len(row_data):
                detail += f"  {col_name}: {row_data[i]}\n"

        detail += f"\n─── القانون المستخدم ───\n\n"

        if method_key == 'bisection':
            if len(row_data) >= 6:
                detail += f"  c = (a + b) / 2 = ({row_data[1]} + {row_data[2]}) / 2 = {row_data[3]}\n"
                detail += f"  f(c) = {row_data[4]}\n"
                detail += f"  |b - a| = {row_data[5]}\n"
        elif method_key == 'newton':
            if len(row_data) >= 6:
                detail += f"  القانون: x(n+1) = x(n) - f(x(n)) / f'(x(n))\n"
                detail += f"  x(n) = {row_data[1]}\n"
                detail += f"  f(x(n)) = {row_data[2]}\n"
                detail += f"  f'(x(n)) = {row_data[3]}\n"
                detail += f"  x(n+1) = {row_data[1]} - ({row_data[2]}) / ({row_data[3]}) = {row_data[4]}\n"
                detail += f"  الخطأ = {row_data[5]}\n"
        elif method_key == 'secant':
            if len(row_data) >= 6:
                detail += f"  القانون: x(n+1) = x(n) - f(x(n))×(x(n)-x(n-1)) / (f(x(n))-f(x(n-1)))\n"
                detail += f"  x(n-1) = {row_data[1]}\n"
                detail += f"  x(n) = {row_data[2]}\n"
                detail += f"  x(n+1) = {row_data[3]}\n"
                detail += f"  f(x(n+1)) = {row_data[4]}\n"
                detail += f"  الخطأ = {row_data[5]}\n"
        elif method_key == 'false_position':
            if len(row_data) >= 6:
                detail += f"  القانون: c = b - f(b)×(b-a) / (f(b)-f(a))\n"
                detail += f"  a = {row_data[1]}, b = {row_data[2]}\n"
                detail += f"  c = {row_data[3]}\n"
                detail += f"  f(c) = {row_data[4]}\n"
        elif method_key == 'jacobi':
            detail += f"  القانون: x_i = (b_i - Σ(a_ij × x_j)) / a_ii\n"
            for i in range(1, len(row_data)):
                detail += f"  {sol.table_columns[i]} = {row_data[i]}\n"
        else:
            for i, col_name in enumerate(sol.table_columns):
                if i < len(row_data):
                    detail += f"  {col_name} = {row_data[i]}\n"

        self.iter_detail_text.setText(detail)

        # Update iteration graph
        if HAS_MATPLOTLIB and hasattr(self, 'iter_figure'):
            self.iter_canvas.show()
            self.iter_figure.clear()
            ax = self.iter_figure.add_subplot(111)
            ax.set_facecolor('#0d1b2a')
            ax.tick_params(colors='white')
            for spine in ax.spines.values():
                spine.set_edgecolor('#1f3659')

            if method_key in ('bisection', 'false_position', 'secant', 'newton') and 'f' in self.entries:
                try:
                    expr = self.entries['f'].text()
                    x_range = np.linspace(-5, 5, 200)
                    if 'a' in self.entries and 'b' in self.entries:
                        a_v = float(self.entries['a'].text())
                        b_v = float(self.entries['b'].text())
                        m = (b_v - a_v) * 0.5
                        x_range = np.linspace(a_v - m, b_v + m, 200)
                    y_range = [safe_eval_func(expr, xi) for xi in x_range]
                    ax.plot(x_range, y_range, color='#64ffda', linewidth=2)
                    ax.axhline(0, color='gray', linestyle='--', linewidth=0.8)

                    c_val = float(row_data[3]) if len(row_data) > 3 else 0
                    fc_val = float(row_data[4]) if len(row_data) > 4 else 0
                    ax.plot(c_val, fc_val, '*', color='#ffd166', markersize=15)
                    ax.annotate(f'التكرار {row+1}', (c_val, fc_val), color='white', fontsize=10,
                               xytext=(10, 10), textcoords='offset points')
                    ax.set_title(f'التكرار {row+1}', color='white', fontsize=12)
                except Exception:
                    pass

            self.iter_canvas.draw()


# ============================================================
#  Main Application Window
# ============================================================
class ModernApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("معمل التحليل العددي التفاعلي")
        self.setGeometry(50, 50, 1400, 850)
        self.setStyleSheet("""
            QMainWindow { background-color: #0b1426; }
            * { font-family: 'Segoe UI', Arial, sans-serif; color: #ffffff; }
            QScrollBar:vertical { background: #0b1426; width: 10px; }
            QScrollBar::handle:vertical { background: #1f3659; border-radius: 5px; }
            QScrollBar:horizontal { background: #0b1426; height: 10px; }
            QScrollBar::handle:horizontal { background: #1f3659; border-radius: 5px; }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(self.create_sidebar())

        self.stack = QStackedWidget()
        self.dashboard_widget = QWidget()
        dash_layout = QVBoxLayout(self.dashboard_widget)
        dash_layout.setContentsMargins(10, 10, 10, 10)
        dash_layout.addWidget(self.create_main_content(), stretch=1)
        self.stack.addWidget(self.dashboard_widget)          # 0
        self.stack.addWidget(self.create_lessons_page())       # 1
        self.stack.addWidget(self.create_numerical_methods_page())  # 2
        self.stack.addWidget(self.create_3d_simulation_page())     # 3
        self.stack.addWidget(self.create_calculator_page())        # 4
        self.stack.addWidget(self.create_iteration_tables_page())  # 5
        self.stack.addWidget(self.create_graphs_page())            # 6
        self.stack.addWidget(self.create_tests_page())             # 7
        self.stack.addWidget(self.create_dictionary_page())        # 8
        self.stack.addWidget(self.create_comparison_page())        # 9
        self.stack.addWidget(self.create_learning_path_page())     # 10
        self.stack.addWidget(self.create_settings_page())          # 11
        self.stack.addWidget(self.create_about_page())             # 12

        main_layout.addWidget(self.stack, stretch=1)
        main_layout.addWidget(self.create_right_panel())

    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("""
            QFrame { background-color: #0d1b2a; border-left: 1px solid #1c2e4a; }
            QPushButton { text-align: right; padding: 10px 15px; font-size: 14px; font-weight: bold; border: none; background: transparent; color: #a8b2d1; }
            QPushButton:hover { color: #ffffff; background-color: #1a365d; border-radius: 5px; }
            QPushButton:checked { background-color: #005b9f; color: #ffffff; border-radius: 5px; }
        """)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(10, 20, 10, 20)

        self.nav_btns = []
        def add_nav_btn(icon, text, index):
            btn = QPushButton(f"  {text}    {icon}")
            btn.setCheckable(True)
            if index == 0:
                btn.setChecked(True)
            btn.clicked.connect(lambda checked, idx=index, b=btn: self.switch_page(idx, b))
            layout.addWidget(btn)
            self.nav_btns.append(btn)

        add_nav_btn("🏠", "الصفحة الرئيسية", 0)
        add_nav_btn("📘", "الدروس", 1)
        add_nav_btn("🧮", "الطرق العددية", 2)
        add_nav_btn("🧊", "المحاكاة ثلاثية الأبعاد", 3)
        add_nav_btn("🔢", "الحاسبة العددية", 4)
        add_nav_btn("📊", "جداول التكرارات", 5)
        add_nav_btn("📈", "الرسوم البيانية", 6)
        add_nav_btn("📝", "الاختبارات", 7)
        add_nav_btn("📚", "قاموس المصطلحات", 8)
        add_nav_btn("⚖️", "مقارنة الطرق", 9)
        add_nav_btn("🗺️", "مسار التعلم", 10)

        layout.addStretch()

        settings_btn = QPushButton("⚙️  الإعدادات")
        settings_btn.clicked.connect(lambda: self.switch_page(11, None))
        layout.addWidget(settings_btn)

        about_btn = QPushButton("ℹ️  حول البرنامج")
        about_btn.clicked.connect(lambda: self.switch_page(12, None))
        layout.addWidget(about_btn)

        return sidebar

    def switch_page(self, index, active_btn):
        self.stack.setCurrentIndex(index)
        for btn in self.nav_btns:
            btn.setChecked(btn == active_btn)

        # Refresh dynamic pages
        if index == 5:
            self.refresh_iteration_tables()
        elif index == 6:
            self.refresh_graphs()

    # ─── Dashboard ───
    def create_main_content(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QFrame()
        header_layout = QHBoxLayout(header)
        title_box = QVBoxLayout()
        t1 = QLabel("معمل التحليل العددي التفاعلي")
        t1.setFont(QFont("Arial", 22, QFont.Bold))
        t2 = QLabel("Learn  →  Visualize  →  Calculate  →  Analyze")
        t2.setStyleSheet("color: #a8b2d1; font-size: 14px;")
        title_box.addWidget(t1)
        title_box.addWidget(t2)
        quote = QLabel("لأن الرياضيات ليست مجرد أرقام...\nبل هي لغة لفهم العالم 🎓")
        quote.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        quote.setStyleSheet("color: #a8b2d1; font-size: 12px;")
        header_layout.addLayout(title_box)
        header_layout.addStretch()
        header_layout.addWidget(quote)
        layout.addWidget(header)

        hero = QFrame()
        hero.setFixedHeight(120)
        hero.setStyleSheet("""
            QFrame { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0f2027, stop:0.5 #203a43, stop:1 #2c5364); border-radius: 10px; }
        """)
        h_layout = QVBoxLayout(hero)
        h1 = QLabel("مرحباً بك في معمل التحليل العددي التفاعلي")
        h1.setFont(QFont("Arial", 18, QFont.Bold))
        h1.setAlignment(Qt.AlignCenter)
        h_layout.addWidget(h1)
        layout.addWidget(hero)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; } QWidget#scontent { background: transparent; }")
        scontent = QWidget()
        scontent.setObjectName("scontent")
        s_layout = QVBoxLayout(scontent)

        # Root finding
        s_layout.addWidget(self.create_section_header("إيجاد الجذور", "#004b87"))
        grid1 = QGridLayout()
        grid1.addWidget(self.create_card("طريقة التنصيف", "Bisection Method", "تقسيم الفترة إلى نصفين", "#005b9f", "bisection", self.run_bisection), 0, 0)
        grid1.addWidget(self.create_card("طريقة القاطع", "Secant Method", "استخدام نقطتين للتقريب", "#2a9d8f", "secant", self.run_secant), 0, 1)
        grid1.addWidget(self.create_card("نيوتن رافسون", "Newton-Raphson", "استخدام المماس للتسريع", "#7b2cbf", "newton", self.run_newton), 0, 2)
        grid1.addWidget(self.create_card("الوضع الكاذب", "False Position", "خط مستقيم بين طرفي الفترة", "#e76f51", "false_position", self.run_false_position), 0, 3)
        s_layout.addLayout(grid1)

        # Linear systems
        grid2 = QGridLayout()
        c1 = QVBoxLayout()
        c1.addWidget(self.create_section_header("حل المعادلات الخطية", "#2a9d8f"))
        hg = QHBoxLayout()
        hg.addWidget(self.create_card("طريقة جاكوبي", "Jacobi Method", "حل الأنظمة تكرارياً", "#2a9d8f", "jacobi", self.run_jacobi))
        hg.addWidget(self.create_card("جاوس للحذف", "Gauss Elimination", "التحويل إلى شكل مثلثي", "#005b9f", "gauss", self.run_gauss))
        hg.addWidget(self.create_card("طريقة كرامر", "Cramer's Rule", "الحل عبر المحددات", "#e76f51", "cramer", self.run_cramer))
        hg.addWidget(self.create_card("معكوس المصفوفة", "Matrix Inverse", "x = A⁻¹ × b", "#7b2cbf", "inverse", self.run_inverse))
        c1.addLayout(hg)
        grid2.addLayout(c1, 0, 0)
        s_layout.addLayout(grid2)

        # Interpolation
        grid3 = QGridLayout()
        c2 = QVBoxLayout()
        c2.addWidget(self.create_section_header("الاستيفاء", "#7b2cbf"))
        c2.addWidget(self.create_card("طريقة لاجرانج", "Lagrange Interpolation", "إيجاد قيمة دالة بدلالة نقاط", "#7b2cbf", "lagrange", self.run_lagrange))
        grid3.addLayout(c2, 0, 0)

        c3 = QVBoxLayout()
        c3.addWidget(self.create_section_header("العمليات العددية", "#d62828"))
        wg = QHBoxLayout()
        wg.addWidget(self.create_card("التفاضل العددي", "Num. Differentiation", "الفروق المركزية", "#005b9f", "differentiation", self.run_differentiation))
        wg.addWidget(self.create_card("التكامل العددي", "Num. Integration", "شبه المنحرفات", "#7b2cbf", "integration", self.run_integration))
        c3.addLayout(wg)
        grid3.addLayout(c3, 0, 1)
        s_layout.addLayout(grid3)

        # Interval Classification
        s_layout.addWidget(self.create_section_header("تصنيف الفترات", "#d62828"))
        s_layout.addWidget(self.create_card("تصنيف الفترات", "Interval Classification", "تحديد الفترات الحاوية للجذور", "#d62828", "interval", self.run_interval_classification))

        s_layout.addStretch()
        scroll.setWidget(scontent)
        layout.addWidget(scroll)
        return widget

    def create_section_header(self, title, color):
        lbl = QLabel(f"  {title}")
        lbl.setFont(QFont("Arial", 12, QFont.Bold))
        lbl.setStyleSheet(f"background-color: {color}; color: white; border-top-left-radius: 5px; border-top-right-radius: 5px; padding: 5px;")
        return lbl

    def create_card(self, title, subtitle, desc, color, icon_type, cmd):
        card = QFrame()
        card.setStyleSheet(f"QFrame {{ background-color: white; border-radius: 8px; border: 2px solid {color}; }}")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)

        t1 = QLabel(title)
        t1.setFont(QFont("Arial", 14, QFont.Bold))
        t1.setStyleSheet(f"color: {color}; border: none;")
        t1.setAlignment(Qt.AlignCenter)

        t2 = QLabel(subtitle)
        t2.setStyleSheet("color: #555555; border: none;")
        t2.setAlignment(Qt.AlignCenter)

        icon = IconWidget(icon_type)
        icon_layout = QHBoxLayout()
        icon_layout.addWidget(icon, alignment=Qt.AlignCenter)

        btn = QPushButton("📖 ابدأ التعلم")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"QPushButton {{ background-color: {color}; color: white; border-radius: 4px; padding: 8px; font-weight: bold; border: none; }} QPushButton:hover {{ background-color: #333333; }}")
        if cmd:
            btn.clicked.connect(cmd)

        layout.addWidget(t1)
        layout.addWidget(t2)
        layout.addLayout(icon_layout)
        layout.addWidget(btn)
        return card

    # ─── Right Panel ───
    def create_right_panel(self):
        panel = QFrame()
        panel.setFixedWidth(280)
        panel.setStyleSheet("background-color: #0d1b2a; border-right: 1px solid #1c2e4a;")
        layout = QVBoxLayout(panel)

        def create_box(title, icon):
            box = QFrame()
            box.setStyleSheet("QFrame { background-color: #0d1b2a; border-radius: 8px; }")
            bl = QVBoxLayout(box)
            lbl = QLabel(f"{icon} {title}")
            lbl.setFont(QFont("Arial", 12, QFont.Bold))
            lbl.setStyleSheet("border-bottom: 1px solid #1c2e4a; padding-bottom: 5px;")
            bl.addWidget(lbl)
            return box, bl

        act_box, act_l = create_box("أحدث النشاطات", "🕒")
        acts = [("تم حل طريقة نيوتن رافسون", "منذ 10 دقائق", "#64ffda"),
                ("تم مشاهدة درس طريقة التنصيف", "منذ 28 دقيقة", "#ffd166"),
                ("تم استخدام طريقة جاكوبي", "منذ ساعتين", "#7b2cbf")]
        for text, time_str, color in acts:
            lbl = QLabel(f"● {text}<br><span style='color:#a8b2d1;font-size:11px;'>&nbsp;&nbsp;{time_str}</span>")
            lbl.setTextFormat(Qt.RichText)
            lbl.setStyleSheet(f"color: {color}; font-size: 12px;")
            act_l.addWidget(lbl)
        layout.addWidget(act_box)

        tool_box, tool_l = create_box("أدوات سريعة", "🛠️")
        tools_data = [
            ("🧮 حاسبة عددية", 4),
            ("⚖️ مقارنة الطرق", 9),
            ("📚 قاموس المصطلحات", 8),
            ("🗺️ مسار التعلم", 10),
        ]
        for t_text, t_idx in tools_data:
            btn = QPushButton(t_text)
            btn.setStyleSheet("QPushButton { background-color: #1a365d; padding: 10px; border-radius: 5px; text-align: right; } QPushButton:hover { background-color: #2d4a77; }")
            btn.clicked.connect(lambda checked, idx=t_idx: self.switch_page(idx, self.nav_btns[idx] if idx < len(self.nav_btns) else None))
            tool_l.addWidget(btn)
        layout.addWidget(tool_box)

        prog_box, prog_l = create_box("تقدمك في التعلم", "🎓")
        self.progress_label = QLabel("تم إكمال 0 من 12 طريقة")
        circ = QLabel("0%")
        circ.setFont(QFont("Arial", 16, QFont.Bold))
        circ.setAlignment(Qt.AlignCenter)
        circ.setFixedSize(70, 70)
        circ.setStyleSheet("border: 4px solid #005b9f; border-radius: 35px; color: white;")
        self.progress_circle = circ
        h = QHBoxLayout()
        h.addWidget(circ)
        h.addWidget(self.progress_label)
        prog_l.addLayout(h)
        layout.addWidget(prog_box)

        layout.addStretch()

        # Timer to update progress
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress_display)
        self.progress_timer.start(3000)

        return panel

    def update_progress_display(self):
        n = len(app_state.completed_methods)
        total = 12
        pct = int(n / total * 100)
        self.progress_label.setText(f"تم إكمال {n} من {total} طريقة")
        self.progress_circle.setText(f"{pct}%")

    # ─── Lessons Page ───
    def create_lessons_page(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("📘 مكتبة الدروس الشاملة", font=QFont("Arial", 20, QFont.Bold)))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        content = QWidget()
        cl = QVBoxLayout(content)

        lessons_list = [
            ("الدرس الأول: مقدمة في التحليل العددي", "نظرة عامة ومفاهيم أساسية",
             "التحليل العددي هو فرع من الرياضيات يهتم بإيجاد حلول تقريبية للمسائل الرياضية التي يصعب أو يستحيل حلها تحليلياً.\n\nيشمل:\n• إيجاد جذور المعادلات\n• حل أنظمة المعادلات الخطية\n• الاستيفاء والتقريب\n• التفاضل والتكامل العددي\n\nالهدف: الحصول على نتائج دقيقة بما يكفي للتطبيقات العملية."),
            ("الدرس الثاني: الأخطاء العددية", "أنواع الأخطاء وكيفية حسابها",
             "أنواع الأخطاء:\n\n1. خطأ القطع (Truncation Error): ناتج عن تقريب عملية رياضية لا نهائية بعدد محدود من الخطوات.\n2. خطأ التقريب (Round-off Error): ناتج عن تمثيل الأعداد بعدد محدود من الخانات.\n\nالخطأ المطلق = |القيمة الحقيقية - القيمة التقريبية|\nالخطأ النسبي = الخطأ المطلق / |القيمة الحقيقية| × 100%"),
            ("الدرس الثالث: إيجاد الجذور", "طرق إيجاد جذور المعادلات غير الخطية",
             "الجذر هو القيمة x التي تحقق f(x) = 0\n\nالطرق المغلقة (تحتاج فترة):\n• طريقة التنصيف (Bisection)\n• طريقة الوضع الكاذب (False Position)\n\nالطرق المفتوحة (تحتاج نقطة بداية):\n• طريقة نيوتن رافسون\n• طريقة القاطع\n\nنظرية القيمة الوسطى: إذا كانت f متصلة على [a,b] و f(a)×f(b) < 0، فيوجد جذر c حيث a < c < b."),
            ("الدرس الرابع: المعادلات الخطية", "حل أنظمة المعادلات الخطية",
             "النظام الخطي: AX = B\n\nالطرق المباشرة:\n• جاوس للحذف: تحويل لشكل مثلثي + تعويض خلفي\n• كرامر: استخدام المحددات\n• معكوس المصفوفة: X = A⁻¹B\n\nالطرق التكرارية:\n• جاكوبي: حل تكراري مع تحديث متزامن\n• جاوس-سايدل: حل تكراري مع تحديث فوري"),
            ("الدرس الخامس: الاستيفاء", "استيفاء لاجرانج وتطبيقاته",
             "الاستيفاء (Interpolation) هو إيجاد دالة تمر بمجموعة نقاط معطاة.\n\nلاجرانج: P(x) = Σ y_i × L_i(x)\nحيث L_i(x) = Π (x-xj)/(xi-xj) لكل j≠i\n\nالتطبيقات:\n• تقدير قيم بين نقاط بيانات معروفة\n• بناء نماذج رياضية من بيانات تجريبية"),
            ("الدرس السادس: التفاضل العددي", "حساب المشتقات عددياً",
             "عندما لا تكون الدالة معروفة تحليلياً، نستخدم التفاضل العددي.\n\nالفروق الأمامية: f'(x) ≈ [f(x+h) - f(x)] / h\nالفروق الخلفية: f'(x) ≈ [f(x) - f(x-h)] / h\nالفروق المركزية: f'(x) ≈ [f(x+h) - f(x-h)] / (2h)\n\nالفروق المركزية هي الأدق (خطأ من الدرجة O(h²))."),
            ("الدرس السابع: التكامل العددي", "حساب التكاملات المحددة عددياً",
             "طرق التكامل العددي:\n\n1. قاعدة شبه المنحرفات (Trapezoidal):\nI ≈ (h/2)[f(x₀) + 2Σf(xi) + f(xn)]\n\n2. قاعدة سمبسون (Simpson's):\nI ≈ (h/3)[f(x₀) + 4Σf(فردي) + 2Σf(زوجي) + f(xn)]\n\nكلما زاد عدد الفترات n، زادت الدقة."),
        ]

        for title, desc, full_content in lessons_list:
            card = QFrame()
            card.setStyleSheet("background-color: #1a365d; border-radius: 8px; padding: 15px;")
            card_l = QVBoxLayout(card)
            t = QLabel(title)
            t.setFont(QFont("Arial", 14, QFont.Bold))
            t.setStyleSheet("color: #64ffda;")
            d = QLabel(desc)
            d.setStyleSheet("color: #a8b2d1;")
            card_l.addWidget(t)
            card_l.addWidget(d)

            content_lbl = QLabel(full_content)
            content_lbl.setFont(QFont("Arial", 11))
            content_lbl.setWordWrap(True)
            content_lbl.setStyleSheet("color: #e0e0e0; padding: 10px; background-color: #0d1b2a; border-radius: 6px;")
            content_lbl.hide()

            btn = QPushButton("📖 شاهد الدرس")
            btn.setStyleSheet("background-color: #005b9f; padding: 8px; border-radius: 5px;")
            btn.clicked.connect(lambda checked, c=content_lbl: c.setVisible(not c.isVisible()))
            card_l.addWidget(btn)
            card_l.addWidget(content_lbl)
            cl.addWidget(card)

        cl.addStretch()
        scroll.setWidget(content)
        l.addWidget(scroll)
        return w

    # ─── Numerical Methods Page ───
    def create_numerical_methods_page(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("🧮 الطرق العددية", font=QFont("Arial", 20, QFont.Bold)))
        l.addWidget(QLabel("يتم عرض هذه الطرق في الصفحة الرئيسية. انتقل هناك للبدء.", font=QFont("Arial", 14)))
        btn = QPushButton("العودة للصفحة الرئيسية")
        btn.setStyleSheet("background-color: #2a9d8f; padding: 10px; border-radius: 5px;")
        btn.clicked.connect(lambda: self.switch_page(0, self.nav_btns[0]))
        l.addWidget(btn)
        l.addStretch()
        return w

    # ─── 3D Simulation ───
    def create_3d_simulation_page(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("🧊 المحاكاة ثلاثية الأبعاد", font=QFont("Arial", 20, QFont.Bold)))

        if HAS_MATPLOTLIB and HAS_NUMPY:
            controls = QFrame()
            controls.setStyleSheet("background-color: #1a365d; border-radius: 8px; padding: 10px;")
            ctrl_l = QGridLayout(controls)
            ctrl_l.addWidget(QLabel("z = f(x, y):"), 0, 0)
            self.sim3d_expr = QLineEdit("sin(sqrt(x**2 + y**2))")
            self.sim3d_expr.setStyleSheet(INPUT_STYLE)
            ctrl_l.addWidget(self.sim3d_expr, 0, 1)
            ctrl_l.addWidget(QLabel("النطاق:"), 1, 0)
            self.sim3d_range = QLineEdit("-5, 5")
            self.sim3d_range.setStyleSheet(INPUT_STYLE)
            ctrl_l.addWidget(self.sim3d_range, 1, 1)
            btn = QPushButton("🔄 تحديث الرسم")
            btn.setStyleSheet("background-color: #005b9f; padding: 8px; border-radius: 5px;")
            btn.clicked.connect(self.update_3d_plot)
            ctrl_l.addWidget(btn, 2, 1)
            l.addWidget(controls)

            self.sim3d_fig = plt.figure(figsize=(6, 5), facecolor='#0d1b2a')
            self.sim3d_canvas = FigureCanvas(self.sim3d_fig)
            l.addWidget(self.sim3d_canvas)
            self.update_3d_plot()
        else:
            l.addWidget(QLabel("مكتبة Matplotlib و NumPy مطلوبة لعرض المحاكاة.", font=QFont("Arial", 12)))
        return w

    def update_3d_plot(self):
        if not HAS_MATPLOTLIB or not HAS_NUMPY:
            return
        try:
            self.sim3d_fig.clear()
            ax = self.sim3d_fig.add_subplot(111, projection='3d')
            ax.set_facecolor('#0d1b2a')
            ax.tick_params(colors='white')
            ax.set_title('محاكاة سطح دالة 3D', color='white')

            parts = self.sim3d_range.text().split(',')
            r_min, r_max = float(parts[0]), float(parts[1])
            X = np.arange(r_min, r_max, 0.25)
            Y = np.arange(r_min, r_max, 0.25)
            X, Y = np.meshgrid(X, Y)

            expr = self.sim3d_expr.text()
            ns = dict(SAFE_MATH_NS)
            ns['x'] = X
            ns['y'] = Y
            ns['np'] = np
            # For numpy compat
            ns.update({'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
                       'exp': np.exp, 'log': np.log, 'sqrt': np.sqrt,
                       'abs': np.abs})
            Z = eval(expr, {"__builtins__": {}}, ns)
            ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='none', alpha=0.8)
            self.sim3d_canvas.draw()
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"خطأ في رسم الدالة ثلاثية الأبعاد:\n{e}")

    # ─── Calculator ───
    def create_calculator_page(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("🔢 الحاسبة العددية السريعة", font=QFont("Arial", 20, QFont.Bold)))
        form = QGridLayout()
        form.addWidget(QLabel("الدالة f(x):"), 0, 0)
        self.calc_func = QLineEdit("x**2 - 4")
        self.calc_func.setStyleSheet(INPUT_STYLE)
        form.addWidget(self.calc_func, 0, 1)
        form.addWidget(QLabel("قيمة x:"), 1, 0)
        self.calc_val = QLineEdit("2")
        self.calc_val.setStyleSheet(INPUT_STYLE)
        form.addWidget(self.calc_val, 1, 1)
        btn = QPushButton("احسب القيمة")
        btn.setStyleSheet("background-color: #0077b6; padding: 10px; border-radius: 5px;")
        form.addWidget(btn, 2, 1)
        self.calc_res = QLabel("النتيجة: ")
        self.calc_res.setFont(QFont("Arial", 14, QFont.Bold))
        form.addWidget(self.calc_res, 3, 1)

        def do_calc():
            try:
                x = float(self.calc_val.text())
                res = safe_eval_func(self.calc_func.text(), x)
                self.calc_res.setText(f"النتيجة: {res}")
                self.calc_res.setStyleSheet("color: #64ffda;")
            except Exception as e:
                self.calc_res.setText(f"خطأ: {e}")
                self.calc_res.setStyleSheet("color: #f97171;")

        btn.clicked.connect(do_calc)
        l.addLayout(form)

        # Quick functions
        quick_frame = QFrame()
        quick_frame.setStyleSheet("background-color: #1a365d; border-radius: 8px; padding: 10px; margin-top: 15px;")
        qf_l = QVBoxLayout(quick_frame)
        qf_l.addWidget(QLabel("الدوال المتاحة:", font=QFont("Arial", 12, QFont.Bold)))
        qf_l.addWidget(QLabel("sin, cos, tan, exp, log, log10, sqrt, abs, pow, asin, acos, atan, pi, e"))
        l.addWidget(quick_frame)

        l.addStretch()
        return w

    # ─── Iteration Tables ───
    def create_iteration_tables_page(self):
        w = QWidget()
        self.iter_tables_layout = QVBoxLayout(w)
        self.iter_tables_layout.addWidget(QLabel("📊 جداول التكرارات", font=QFont("Arial", 20, QFont.Bold)))
        self.iter_tables_placeholder = QLabel("قم باستخدام إحدى الطرق العددية في المعمل لإنشاء الجداول التكرارية.")
        self.iter_tables_placeholder.setFont(QFont("Arial", 14))
        self.iter_tables_placeholder.setStyleSheet("color: #a8b2d1;")
        self.iter_tables_layout.addWidget(self.iter_tables_placeholder)
        self.iter_dynamic_table = None
        self.iter_tables_layout.addStretch()
        return w

    def refresh_iteration_tables(self):
        if app_state.last_solution and app_state.last_solution.table_columns:
            sol = app_state.last_solution
            self.iter_tables_placeholder.setText(f"آخر حساب: {app_state.last_method_name}")
            self.iter_tables_placeholder.setStyleSheet("color: #64ffda; font-size: 16px; font-weight: bold;")

            if self.iter_dynamic_table:
                self.iter_dynamic_table.deleteLater()

            self.iter_dynamic_table = QTableWidget()
            self.iter_dynamic_table.setStyleSheet("""
                QTableWidget { background-color: #0d1b2a; color: white; gridline-color: #1f3659; border: 1px solid #1f3659; }
                QHeaderView::section { background-color: #005b9f; color: white; padding: 6px; font-weight: bold; border: 1px solid #1f3659; }
            """)
            self.iter_dynamic_table.setColumnCount(len(sol.table_columns))
            self.iter_dynamic_table.setRowCount(len(sol.table_rows))
            self.iter_dynamic_table.setHorizontalHeaderLabels(sol.table_columns)
            self.iter_dynamic_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            for r, row_data in enumerate(sol.table_rows):
                for c, col_data in enumerate(row_data):
                    item = QTableWidgetItem(str(col_data))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.iter_dynamic_table.setItem(r, c, item)

            self.iter_tables_layout.insertWidget(2, self.iter_dynamic_table)

    # ─── Graphs Page ───
    def create_graphs_page(self):
        w = QWidget()
        self.graphs_layout = QVBoxLayout(w)
        self.graphs_layout.addWidget(QLabel("📈 الرسوم البيانية التفاعلية", font=QFont("Arial", 20, QFont.Bold)))

        # User input for custom graph
        controls = QFrame()
        controls.setStyleSheet("background-color: #1a365d; border-radius: 8px; padding: 10px;")
        ctrl_l = QGridLayout(controls)
        ctrl_l.addWidget(QLabel("الدالة f(x):"), 0, 0)
        self.graph_func = QLineEdit("x**3 - x - 2")
        self.graph_func.setStyleSheet(INPUT_STYLE)
        ctrl_l.addWidget(self.graph_func, 0, 1)
        ctrl_l.addWidget(QLabel("النطاق [a, b]:"), 1, 0)
        self.graph_range = QLineEdit("-3, 4")
        self.graph_range.setStyleSheet(INPUT_STYLE)
        ctrl_l.addWidget(self.graph_range, 1, 1)
        btn = QPushButton("📈 ارسم الدالة")
        btn.setStyleSheet("background-color: #005b9f; padding: 8px; border-radius: 5px;")
        btn.clicked.connect(self.draw_custom_graph)
        ctrl_l.addWidget(btn, 2, 1)
        self.graphs_layout.addWidget(controls)

        if HAS_MATPLOTLIB:
            self.graph_fig = Figure(figsize=(8, 5), facecolor='#0d1b2a')
            self.graph_canvas = FigureCanvas(self.graph_fig)
            self.graphs_layout.addWidget(self.graph_canvas)
        else:
            self.graphs_layout.addWidget(QLabel("مكتبة Matplotlib مطلوبة."))
        return w

    def draw_custom_graph(self):
        if not HAS_MATPLOTLIB:
            return
        try:
            self.graph_fig.clear()
            ax = self.graph_fig.add_subplot(111)
            ax.set_facecolor('#0d1b2a')
            ax.tick_params(colors='white')
            for spine in ax.spines.values():
                spine.set_edgecolor('#1f3659')

            expr = self.graph_func.text()
            parts = self.graph_range.text().split(',')
            a, b = float(parts[0]), float(parts[1])
            x = np.linspace(a, b, 300)
            y = [safe_eval_func(expr, xi) for xi in x]
            ax.plot(x, y, color='#64ffda', linewidth=2, label='f(x)')
            ax.axhline(0, color='gray', linestyle='--', linewidth=0.8)
            ax.axvline(0, color='gray', linestyle='--', linewidth=0.8)

            # Show last solution points if same function
            if app_state.last_solution and app_state.last_func_expr == expr:
                sol = app_state.last_solution
                if sol.table_rows and len(sol.table_columns) > 3:
                    for row in sol.table_rows:
                        try:
                            c_val = float(row[3])
                            fc_val = float(row[4]) if len(row) > 4 else safe_eval_func(expr, c_val)
                            ax.plot(c_val, fc_val, 'o', color='#ff6b6b', markersize=5)
                        except (ValueError, IndexError):
                            pass

            ax.legend(loc='best', facecolor='#1a365d', edgecolor='#1f3659', labelcolor='white')
            ax.set_title('الرسم البياني', color='white', fontsize=12)
            self.graph_canvas.draw()
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"خطأ في رسم الدالة:\n{e}")

    def refresh_graphs(self):
        if app_state.last_func_expr:
            self.graph_func.setText(app_state.last_func_expr)
        self.draw_custom_graph()

    # ─── Tests Page ───
    def create_tests_page(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("📝 اختبارات قياس المستوى", font=QFont("Arial", 20, QFont.Bold)))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        content = QWidget()
        cl = QVBoxLayout(content)

        # General quiz with mixed questions
        all_questions = []
        for method_key, questions in QUIZ_BANK.items():
            for q_text, options, correct_idx in questions:
                all_questions.append((method_key, q_text, options, correct_idx))

        # Pick 10 questions
        import random
        random.seed(42)
        selected = random.sample(all_questions, min(10, len(all_questions)))

        self.general_quiz_groups = []
        self.general_quiz_correct = []

        for idx, (method_key, q_text, options, correct_idx) in enumerate(selected):
            method_name = LESSONS.get(method_key, {}).get('title_ar', method_key)
            q_frame = QFrame()
            q_frame.setStyleSheet("background-color: #1a365d; border-radius: 8px; padding: 12px; margin: 5px 0;")
            q_layout = QVBoxLayout(q_frame)

            q_lbl = QLabel(f"السؤال {idx+1} ({method_name}): {q_text}")
            q_lbl.setFont(QFont("Arial", 12, QFont.Bold))
            q_lbl.setWordWrap(True)
            q_layout.addWidget(q_lbl)

            bg = QButtonGroup(q_frame)
            for i, opt in enumerate(options):
                rb = QRadioButton(opt)
                rb.setFont(QFont("Arial", 11))
                bg.addButton(rb, i)
                q_layout.addWidget(rb)

            self.general_quiz_groups.append(bg)
            self.general_quiz_correct.append(correct_idx)
            cl.addWidget(q_frame)

        self.general_quiz_result = QLabel("")
        self.general_quiz_result.setFont(QFont("Arial", 16, QFont.Bold))
        self.general_quiz_result.setAlignment(Qt.AlignCenter)
        cl.addWidget(self.general_quiz_result)

        btn = QPushButton("✅ تحقق من الإجابات")
        btn.setFont(QFont("Arial", 14, QFont.Bold))
        btn.setStyleSheet("QPushButton { background-color: #2a9d8f; color: white; padding: 12px; border-radius: 6px; border: none; } QPushButton:hover { background-color: #21867a; }")
        btn.clicked.connect(self.check_general_quiz)
        cl.addWidget(btn)

        cl.addStretch()
        scroll.setWidget(content)
        l.addWidget(scroll)
        return w

    def check_general_quiz(self):
        correct = 0
        total = len(self.general_quiz_groups)
        for bg, correct_idx in zip(self.general_quiz_groups, self.general_quiz_correct):
            if bg.checkedId() == correct_idx:
                correct += 1
        pct = (correct / total * 100) if total > 0 else 0
        color = "#6ee7a0" if pct >= 70 else "#ffd166" if pct >= 50 else "#f97171"
        self.general_quiz_result.setText(f"النتيجة: {correct} / {total}  —  {pct:.0f}%")
        self.general_quiz_result.setStyleSheet(f"color: {color}; padding: 15px; background-color: #0d1b2a; border-radius: 8px;")

    # ─── Dictionary ───
    def create_dictionary_page(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("📖 قاموس المصطلحات", font=QFont("Arial", 20, QFont.Bold)))

        # Search
        search_frame = QHBoxLayout()
        search_frame.addWidget(QLabel("🔍 بحث:"))
        self.dict_search = QLineEdit()
        self.dict_search.setStyleSheet(INPUT_STYLE)
        self.dict_search.setPlaceholderText("ابحث عن مصطلح...")
        self.dict_search.textChanged.connect(self.filter_dictionary)
        search_frame.addWidget(self.dict_search)
        l.addLayout(search_frame)

        self.dict_terms = [
            ("Root", "روت", "الجذر - قيمة x التي تجعل f(x) = 0"),
            ("Iteration", "إتريشن", "التكرار - تكرار عملية حسابية للتقريب"),
            ("Error", "إيرر", "الخطأ - الفرق بين القيمة الحقيقية والتقريبية"),
            ("Tolerance", "توليرنس", "نسبة السماحية - الحد الأقصى المقبول للخطأ"),
            ("Convergence", "كونفيرجنس", "التقارب - اقتراب النتائج من الحل الحقيقي"),
            ("Divergence", "دايفيرجنس", "التباعد - ابتعاد النتائج عن الحل"),
            ("Derivative", "ديريفاتيف", "المشتقة - معدل تغير الدالة"),
            ("Matrix", "ماتريكس", "المصفوفة - ترتيب أعداد في صفوف وأعمدة"),
            ("Interpolation", "إنتربوليشن", "الاستيفاء - تقدير قيم بين نقاط معروفة"),
            ("Approximation", "أبروكسيميشن", "التقريب - إيجاد قيمة قريبة من الحقيقية"),
            ("Bisection", "بايسيكشن", "التنصيف - تقسيم الفترة إلى نصفين"),
            ("Secant", "سيكانت", "القاطع - خط يقطع المنحنى في نقطتين"),
            ("Newton-Raphson", "نيوتن رافسون", "طريقة نيوتن - استخدام المماس لإيجاد الجذر"),
            ("False Position", "فولس بوزيشن", "الوضع الكاذب - خط بين طرفي الفترة"),
            ("Elimination", "إليمينيشن", "الحذف - إزالة متغيرات من المعادلات"),
            ("Substitution", "سبستيتيوشن", "التعويض - استبدال قيمة متغير"),
            ("Jacobi", "جاكوبي", "طريقة تكرارية لحل الأنظمة الخطية"),
            ("Lagrange", "لاجرانج", "طريقة استيفاء بكثيرات الحدود"),
            ("Numerical Differentiation", "نيومريكال ديفرنشييشن", "التفاضل العددي"),
            ("Numerical Integration", "نيومريكال إنتجريشن", "التكامل العددي"),
            ("Absolute Error", "أبسوليوت إيرر", "الخطأ المطلق = |الحقيقي - التقريبي|"),
            ("Relative Error", "ريلاتيف إيرر", "الخطأ النسبي = الخطأ المطلق / |الحقيقي| × 100%"),
            ("Pivot", "بيفوت", "العنصر المحوري في عمليات المصفوفات"),
            ("Determinant", "ديترمنانت", "المحدد - قيمة عددية مميزة للمصفوفة"),
            ("Singular Matrix", "سينجولار ماتريكس", "مصفوفة منفردة - محددها = 0"),
            ("Diagonally Dominant", "دايجونلي دومينانت", "مهيمنة قطرياً - عناصر القطر أكبر"),
            ("Trapezoidal Rule", "ترابيزويدال رول", "قاعدة شبه المنحرفات للتكامل"),
            ("Central Difference", "سنترال ديفرنس", "الفروق المركزية للتفاضل"),
            ("Tangent Line", "تانجنت لاين", "خط المماس - يمس المنحنى في نقطة واحدة"),
            ("Back Substitution", "باك سبستيتيوشن", "التعويض الخلفي - حل من الأسفل للأعلى"),
        ]

        self.dict_table = QTableWidget(len(self.dict_terms), 3)
        self.dict_table.setHorizontalHeaderLabels(["English", "النطق بالعربي", "المعنى بالعربي"])
        self.dict_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.dict_table.setStyleSheet("""
            QTableWidget { background-color: #1a365d; color: white; gridline-color: #1f3659; border: 1px solid #1f3659; }
            QHeaderView::section { background-color: #005b9f; color: white; padding: 6px; font-weight: bold; }
        """)
        self.dict_table.setFont(QFont("Arial", 11))
        for r, (e, p, a) in enumerate(self.dict_terms):
            self.dict_table.setItem(r, 0, QTableWidgetItem(e))
            self.dict_table.setItem(r, 1, QTableWidgetItem(p))
            self.dict_table.setItem(r, 2, QTableWidgetItem(a))
        l.addWidget(self.dict_table)
        return w

    def filter_dictionary(self, text):
        text = text.lower()
        for row in range(self.dict_table.rowCount()):
            match = False
            for col in range(3):
                item = self.dict_table.item(row, col)
                if item and text in item.text().lower():
                    match = True
                    break
            self.dict_table.setRowHidden(row, not match)

    # ─── Comparison Page ───
    def create_comparison_page(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("⚖️ مقارنة الطرق العددية", font=QFont("Arial", 20, QFont.Bold)))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        content = QWidget()
        cl = QVBoxLayout(content)

        # Root finding comparison
        cl.addWidget(QLabel("طرق إيجاد الجذور:", font=QFont("Arial", 14, QFont.Bold)))
        table1 = QTableWidget(4, 7)
        table1.setHorizontalHeaderLabels(["الطريقة", "النوع", "تحتاج فترة؟", "تحتاج المشتقة؟", "القيم الابتدائية", "سرعة التقارب", "ملاحظات"])
        table1.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table1.setStyleSheet("""
            QTableWidget { background-color: #1a365d; color: white; gridline-color: #1f3659; }
            QHeaderView::section { background-color: #005b9f; color: white; padding: 4px; font-weight: bold; }
        """)
        data1 = [
            ("التنصيف", "مغلقة", "نعم [a,b]", "لا", "a, b", "بطيئة (خطية)", "مضمونة التقارب"),
            ("الوضع الكاذب", "مغلقة", "نعم [a,b]", "لا", "a, b", "أسرع من التنصيف", "قد تتعثر أحياناً"),
            ("القاطع", "مفتوحة", "لا", "لا", "x0, x1", "فائقة خطية (≈1.618)", "لا تحتاج المشتقة"),
            ("نيوتن رافسون", "مفتوحة", "لا", "نعم", "x0", "تربيعية", "الأسرع لكن تحتاج المشتقة"),
        ]
        for r, row in enumerate(data1):
            for c, item in enumerate(row):
                table1.setItem(r, c, QTableWidgetItem(item))
        table1.setFixedHeight(180)
        cl.addWidget(table1)

        # Linear systems comparison
        cl.addWidget(QLabel("طرق حل المعادلات الخطية:", font=QFont("Arial", 14, QFont.Bold)))
        table2 = QTableWidget(4, 5)
        table2.setHorizontalHeaderLabels(["الطريقة", "النوع", "الاستخدام الأمثل", "المميزات", "العيوب"])
        table2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table2.setStyleSheet("""
            QTableWidget { background-color: #1a365d; color: white; gridline-color: #1f3659; }
            QHeaderView::section { background-color: #2a9d8f; color: white; padding: 4px; font-weight: bold; }
        """)
        data2 = [
            ("جاوس للحذف", "مباشرة", "أنظمة متوسطة الحجم", "دقيقة وعملية", "بطيئة للأنظمة الكبيرة"),
            ("كرامر", "مباشرة", "أنظمة صغيرة (n≤4)", "بسيطة نظرياً", "غير عملية للأنظمة الكبيرة"),
            ("معكوس المصفوفة", "مباشرة", "أنظمة متعددة بنفس A", "مفيدة نظرياً", "مكلفة حسابياً"),
            ("جاكوبي", "تكرارية", "أنظمة كبيرة ومتفرقة", "مناسبة للأنظمة الكبيرة", "تحتاج هيمنة قطرية"),
        ]
        for r, row in enumerate(data2):
            for c, item in enumerate(row):
                table2.setItem(r, c, QTableWidgetItem(item))
        table2.setFixedHeight(180)
        cl.addWidget(table2)

        cl.addStretch()
        scroll.setWidget(content)
        l.addWidget(scroll)
        return w

    # ─── Learning Path ───
    def create_learning_path_page(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("🗺️ مسار التعلم الموصى به", font=QFont("Arial", 20, QFont.Bold)))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        content = QWidget()
        cl = QVBoxLayout(content)

        path_items = [
            ("📚 أساسيات التحليل العددي", None, "#2a9d8f"),
            ("📏 الأخطاء العددية", None, "#2a9d8f"),
            ("🔍 إيجاد الجذور", None, "#005b9f"),
            ("   ├── طريقة التنصيف", "bisection", "#005b9f"),
            ("   ├── الوضع الكاذب", "false_position", "#e76f51"),
            ("   ├── طريقة القاطع", "secant", "#2a9d8f"),
            ("   └── نيوتن رافسون", "newton", "#7b2cbf"),
            ("📐 المعادلات الخطية", None, "#005b9f"),
            ("   ├── جاوس للحذف", "gauss", "#005b9f"),
            ("   ├── طريقة جاكوبي", "jacobi", "#2a9d8f"),
            ("   ├── طريقة كرامر", "cramer", "#e76f51"),
            ("   └── معكوس المصفوفة", "inverse", "#7b2cbf"),
            ("📈 استيفاء لاجرانج", "lagrange", "#7b2cbf"),
            ("∂ التفاضل العددي", "differentiation", "#005b9f"),
            ("∫ التكامل العددي", "integration", "#7b2cbf"),
            ("📝 اختبار شامل", None, "#d62828"),
        ]

        for title, method_key, color in path_items:
            item_frame = QFrame()
            item_layout = QHBoxLayout(item_frame)

            # Status indicator
            if method_key:
                status = app_state.learning_status.get(method_key, 'not_started')
                if status == 'completed':
                    status_text = "✅ مكتمل"
                    status_color = "#6ee7a0"
                elif status == 'in_progress':
                    status_text = "🔄 قيد الدراسة"
                    status_color = "#ffd166"
                else:
                    status_text = "⬜ لم يبدأ"
                    status_color = "#a8b2d1"
            else:
                status_text = ""
                status_color = "#a8b2d1"

            lbl = QLabel(title)
            lbl.setFont(QFont("Arial", 13, QFont.Bold))
            lbl.setStyleSheet(f"color: white; padding: 12px;")

            item_frame.setStyleSheet(f"background-color: {color}; border-radius: 8px; margin: 3px 0;")
            item_layout.addWidget(lbl)
            item_layout.addStretch()
            if status_text:
                st_lbl = QLabel(status_text)
                st_lbl.setStyleSheet(f"color: {status_color}; padding: 12px; font-weight: bold;")
                item_layout.addWidget(st_lbl)

            cl.addWidget(item_frame)

            # Arrow between items
            if title != path_items[-1][0]:
                arrow = QLabel("↓")
                arrow.setFont(QFont("Arial", 16))
                arrow.setAlignment(Qt.AlignCenter)
                arrow.setStyleSheet("color: #a8b2d1;")
                cl.addWidget(arrow)

        cl.addStretch()
        scroll.setWidget(content)
        l.addWidget(scroll)
        return w

    # ─── Settings ───
    def create_settings_page(self):
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("⚙️ الإعدادات", font=QFont("Arial", 20, QFont.Bold)))

        form = QFrame()
        form.setStyleSheet("background-color: #1a365d; border-radius: 8px; padding: 20px;")
        fl = QVBoxLayout(form)

        # Decimal places
        dec_row = QHBoxLayout()
        dec_row.addWidget(QLabel("عدد المنازل العشرية:", font=QFont("Arial", 12)))
        self.decimal_spin = QSpinBox()
        self.decimal_spin.setRange(2, 15)
        self.decimal_spin.setValue(app_state.decimal_places)
        self.decimal_spin.setStyleSheet("background-color: #0b1426; border: 1px solid #64ffda; padding: 5px; color: white;")
        self.decimal_spin.valueChanged.connect(lambda v: setattr(app_state, 'decimal_places', v))
        dec_row.addWidget(self.decimal_spin)
        dec_row.addStretch()
        fl.addLayout(dec_row)

        fl.addWidget(QLabel(""))  # spacer

        # Reset buttons
        reset_btn = QPushButton("🔄 إعادة ضبط الإعدادات")
        reset_btn.setStyleSheet("background-color: #e76f51; padding: 10px; border-radius: 5px; font-weight: bold;")
        reset_btn.clicked.connect(self.reset_settings)
        fl.addWidget(reset_btn)

        reset_progress_btn = QPushButton("🗑️ إعادة ضبط التقدم")
        reset_progress_btn.setStyleSheet("background-color: #d62828; padding: 10px; border-radius: 5px; font-weight: bold;")
        reset_progress_btn.clicked.connect(self.reset_progress)
        fl.addWidget(reset_progress_btn)

        l.addWidget(form)
        l.addStretch()
        return w

    def reset_settings(self):
        app_state.decimal_places = 6
        self.decimal_spin.setValue(6)
        QMessageBox.information(self, "الإعدادات", "تمت إعادة ضبط الإعدادات.")

    def reset_progress(self):
        reply = QMessageBox.question(self, "تأكيد", "هل أنت متأكد من إعادة ضبط التقدم؟",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            app_state.completed_methods.clear()
            app_state.learning_status.clear()
            app_state.quiz_scores.clear()
            app_state.last_solution = None
            QMessageBox.information(self, "التقدم", "تمت إعادة ضبط التقدم.")

    # ─── About ───
    def create_about_page(self):
        w = QWidget()
        l = QVBoxLayout(w)

        title = QLabel("ℹ️ حول البرنامج")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        l.addWidget(title)

        about_frame = QFrame()
        about_frame.setStyleSheet("background-color: #1a365d; border-radius: 12px; padding: 30px;")
        al = QVBoxLayout(about_frame)

        name_ar = QLabel("🧮 معمل التحليل العددي التفاعلي")
        name_ar.setFont(QFont("Arial", 22, QFont.Bold))
        name_ar.setAlignment(Qt.AlignCenter)
        name_ar.setStyleSheet("color: #64ffda;")
        al.addWidget(name_ar)

        name_en = QLabel("Numerical Analysis Interactive Lab")
        name_en.setFont(QFont("Arial", 16))
        name_en.setAlignment(Qt.AlignCenter)
        name_en.setStyleSheet("color: #a8b2d1;")
        al.addWidget(name_en)

        slogan = QLabel("Learn  →  Visualize  →  Calculate  →  Analyze")
        slogan.setFont(QFont("Arial", 14))
        slogan.setAlignment(Qt.AlignCenter)
        slogan.setStyleSheet("color: #ffd166; margin: 10px 0;")
        al.addWidget(slogan)

        desc = QLabel("معمل تعليمي تفاعلي شامل للتحليل العددي.\n"
                      "يتيح للطالب تعلم الطرق العددية المختلفة بطريقة تفاعلية\n"
                      "مع التصور البصري والحساب الفعلي وتحليل النتائج.")
        desc.setFont(QFont("Arial", 12))
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        al.addWidget(desc)

        version = QLabel("الإصدار: 2.0")
        version.setFont(QFont("Arial", 12))
        version.setAlignment(Qt.AlignCenter)
        version.setStyleSheet("color: #a8b2d1; margin-top: 15px;")
        al.addWidget(version)

        methods_label = QLabel("الطرق المدعومة:")
        methods_label.setFont(QFont("Arial", 13, QFont.Bold))
        methods_label.setStyleSheet("color: #64ffda; margin-top: 15px;")
        al.addWidget(methods_label)

        methods_text = QLabel(
            "• إيجاد الجذور: التنصيف، الوضع الكاذب، القاطع، نيوتن رافسون\n"
            "• المعادلات الخطية: جاوس للحذف، جاكوبي، كرامر، معكوس المصفوفة\n"
            "• الاستيفاء: لاجرانج\n"
            "• العمليات العددية: التفاضل العددي، التكامل العددي\n"
            "• أدوات: تصنيف الفترات، الحاسبة العددية، المحاكاة ثلاثية الأبعاد"
        )
        methods_text.setFont(QFont("Arial", 11))
        methods_text.setWordWrap(True)
        al.addWidget(methods_text)

        tech = QLabel("التقنيات: Python 3 | PyQt5 | Matplotlib | NumPy")
        tech.setFont(QFont("Arial", 11))
        tech.setAlignment(Qt.AlignCenter)
        tech.setStyleSheet("color: #a8b2d1; margin-top: 10px;")
        al.addWidget(tech)

        l.addWidget(about_frame)
        l.addStretch()
        return w

    # ─── Method Runners ───
    def _open_lab(self, method_info, solve_func):
        dialog = MiniLabDialog(self, method_info, solve_func)
        dialog.exec()

    def run_bisection(self):
        self._open_lab({
            'title': "طريقة التنصيف",
            'method_key': 'bisection',
            'fields': [("f(x)", "f", "x**3 - x - 2"), ("a", "a", "1"), ("b", "b", "2"),
                       ("الدقة (tol)", "tol", "0.0001"), ("أقصى تكرارات", "max_iter", "50")],
            'lesson_text': '',
        }, backend.solve_bisection if backend else None)

    def run_false_position(self):
        self._open_lab({
            'title': "طريقة الوضع الكاذب",
            'method_key': 'false_position',
            'fields': [("f(x)", "f", "x**3 - x - 2"), ("a", "a", "1"), ("b", "b", "2"),
                       ("الدقة (tol)", "tol", "0.0001"), ("أقصى تكرارات", "max_iter", "50")],
            'lesson_text': '',
        }, solve_false_position)

    def run_secant(self):
        self._open_lab({
            'title': "طريقة القاطع",
            'method_key': 'secant',
            'fields': [("f(x)", "f", "x**3 - x - 2"), ("x0", "x0", "1"), ("x1", "x1", "2"),
                       ("الدقة (tol)", "tol", "0.0001"), ("أقصى تكرارات", "max_iter", "50")],
            'lesson_text': '',
        }, backend.solve_secant if backend else None)

    def run_newton(self):
        self._open_lab({
            'title': "نيوتن رافسون",
            'method_key': 'newton',
            'fields': [("f(x)", "f", "x**3 - x - 2"), ("x0", "x0", "1.5"),
                       ("الدقة (tol)", "tol", "0.0001"), ("أقصى تكرارات", "max_iter", "50")],
            'lesson_text': '',
        }, backend.solve_newton if backend else None)

    def run_jacobi(self):
        self._open_lab({
            'title': "طريقة جاكوبي",
            'method_key': 'jacobi',
            'fields': [("المصفوفة A", "A", "4 -1 0;-1 4 -1;0 -1 4"),
                       ("المتجه b", "b", "1 5 0"),
                       ("التخمين الابتدائي x0", "x0", "0 0 0"),
                       ("الدقة (tol)", "tol", "0.0001"), ("أقصى تكرارات", "max_iter", "50")],
            'lesson_text': '',
        }, backend.solve_jacobi if backend else None)

    def run_gauss(self):
        self._open_lab({
            'title': "جاوس للحذف",
            'method_key': 'gauss',
            'fields': [("المصفوفة A", "A", "4 -1 0;-1 4 -1;0 -1 4"),
                       ("المتجه b", "b", "1 5 0")],
            'lesson_text': '',
        }, backend.solve_gauss if backend else None)

    def run_cramer(self):
        self._open_lab({
            'title': "طريقة كرامر",
            'method_key': 'cramer',
            'fields': [("المصفوفة A", "A", "4 -1 0;-1 4 -1;0 -1 4"),
                       ("المتجه b", "b", "1 5 0")],
            'lesson_text': '',
        }, backend.solve_cramer if backend else None)

    def run_inverse(self):
        self._open_lab({
            'title': "معكوس المصفوفة",
            'method_key': 'inverse',
            'fields': [("المصفوفة A", "A", "4 -1 0;-1 4 -1;0 -1 4"),
                       ("المتجه b", "b", "1 5 0")],
            'lesson_text': '',
        }, backend.solve_inverse if backend else None)

    def run_lagrange(self):
        self._open_lab({
            'title': "استيفاء لاجرانج",
            'method_key': 'lagrange',
            'fields': [("قيم x (مفصولة بمسافة)", "xs", "1 2 3 4"),
                       ("قيم y (مفصولة بمسافة)", "ys", "1 8 27 64"),
                       ("القيمة x المطلوبة", "x_eval", "2.5")],
            'lesson_text': '',
        }, backend.solve_lagrange if backend else None)

    def run_differentiation(self):
        self._open_lab({
            'title': "التفاضل العددي",
            'method_key': 'differentiation',
            'fields': [("f(x)", "f", "x**2"), ("النقطة x0", "x0", "2"),
                       ("الخطوة h", "h", "0.01")],
            'lesson_text': '',
        }, backend.solve_differentiation if backend else None)

    def run_integration(self):
        self._open_lab({
            'title': "التكامل العددي",
            'method_key': 'integration',
            'fields': [("f(x)", "f", "x**2"), ("الحد الأدنى a", "a", "0"),
                       ("الحد الأعلى b", "b", "2"), ("عدد الفترات n", "n", "10")],
            'lesson_text': '',
        }, backend.solve_integration if backend else None)

    def run_interval_classification(self):
        self._open_lab({
            'title': "تصنيف الفترات",
            'method_key': 'interval',
            'fields': [("f(x)", "f", "x**3 - x - 2"), ("بداية الفترة", "start", "-5"),
                       ("نهاية الفترة", "end", "5"), ("الخطوة", "step", "0.5")],
            'lesson_text': '',
        }, solve_interval_classification)


# ============================================================
#  Entry Point
# ============================================================
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.RightToLeft)
    window = ModernApp()
    window.show()
    sys.exit(app.exec())
