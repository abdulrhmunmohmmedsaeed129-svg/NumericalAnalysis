# -*- coding: utf-8 -*-
"""
سكربت اختياري لتوليد مسائل عشوائية واختبار دوال الحل في النظام.
يُمكن استخدامه للتحقق من صحة عمل الخوارزميات تلقائياً.
"""

import random
import importlib

def generate_and_test():
    print("=== بدء اختبار النظام وتوليد المسائل ===\n")
    try:
        backend = importlib.import_module("na Gui")
        print("تم استيراد وحدة الحل (na Gui) بنجاح.\n")
    except ImportError:
        print("خطأ: لم يتم العثور على وحدة 'na Gui'. تأكد من وجود الملف في نفس المجلد.")
        return

    # 1. اختبار طريقة التنصيف (Bisection)
    print("--- 1. اختبار إيجاد الجذور (طريقة التنصيف) ---")
    funcs_bisection = [
        ("x**3 - x - 2", 1, 2),
        ("x**2 - 4", 0, 3),
        ("sin(x) - 0.5", 0, 1),
        ("exp(x) - 3", 0, 2)
    ]
    f, a, b = random.choice(funcs_bisection)
    tol = 10 ** (-random.randint(2, 5))
    max_iter = random.randint(20, 50)
    
    print(f"الدالة: {f} | a={a} | b={b} | tol={tol} | max_iter={max_iter}")
    values = {'f': f, 'a': str(a), 'b': str(b), 'tol': str(tol), 'max_iter': str(max_iter)}
    try:
        sol = backend.solve_bisection(values)
        print("✓ تمت عملية الحل بنجاح.")
        print("الجذر التقريبي:", sol.summary[0][1])
    except Exception as e:
        print("✗ حدث خطأ أثناء الحل:", e)

    # 2. اختبار طريقة نيوتن رافسون
    print("\n--- 2. اختبار إيجاد الجذور (طريقة نيوتن رافسون) ---")
    funcs_newton = ["x**3 - 2*x - 5", "cos(x) - x", "exp(-x) - x"]
    f_n = random.choice(funcs_newton)
    x0 = round(random.uniform(1.0, 3.0), 2)
    print(f"الدالة: {f_n} | x0={x0} | tol={tol} | max_iter={max_iter}")
    values_newton = {'f': f_n, 'x0': str(x0), 'tol': str(tol), 'max_iter': str(max_iter)}
    try:
        sol = backend.solve_newton(values_newton)
        print("✓ تمت عملية الحل بنجاح.")
        print("الجذر التقريبي:", sol.summary[0][1])
    except Exception as e:
        print("✗ حدث خطأ أثناء الحل:", e)

    # 3. اختبار حل المعادلات الخطية (جاوس للحذف)
    print("\n--- 3. اختبار حل المعادلات الخطية (طريقة جاوس) ---")
    n = random.randint(3, 4)
    A = []
    for i in range(n):
        row = [random.randint(-10, 10) for _ in range(n)]
        # لتجنب القسمة على صفر أو المصفوفات المنفردة، نجعل القطر المهيمن كبيراً
        row[i] += sum(abs(x) for x in row) + 1 
        A.append(row)
    
    b_vec = [random.randint(-10, 10) for _ in range(n)]
    
    A_str = ";".join([" ".join(map(str, row)) for row in A])
    b_str = " ".join(map(str, b_vec))
    print(f"المصفوفة A (حجم {n}x{n}):\n{A_str.replace(';', ' | ')}")
    print(f"المتجه b:\n{b_str}")
    values_gauss = {'A': A_str, 'b': b_str}
    try:
        sol = backend.solve_gauss(values_gauss)
        print("✓ تمت عملية الحل بنجاح.")
        res_str = ", ".join([f"{r[0]}={r[1]}" for r in sol.table_rows])
        print(f"الحل: {res_str}")
    except Exception as e:
        print("✗ حدث خطأ أثناء الحل:", e)

    # 4. اختبار الاستيفاء (لاجرانج)
    print("\n--- 4. اختبار الاستيفاء (طريقة لاجرانج) ---")
    num_points = random.randint(4, 6)
    xs = sorted(random.sample(range(0, 15), num_points))
    ys = [random.randint(0, 50) for _ in range(num_points)]
    x_eval = round(random.uniform(xs[0], xs[-1]), 2)
    
    xs_str = " ".join(map(str, xs))
    ys_str = " ".join(map(str, ys))
    print(f"النقاط x: {xs_str}")
    print(f"القيم y: {ys_str}")
    print(f"القيمة المطلوب تقييمها: {x_eval}")
    values_lag = {'xs': xs_str, 'ys': ys_str, 'x_eval': str(x_eval)}
    try:
        sol = backend.solve_lagrange(values_lag)
        print("✓ تمت عملية الحل بنجاح.")
        print("قيمة الدالة التقريبية:", sol.summary[0][1])
    except Exception as e:
        print("✗ حدث خطأ أثناء الحل:", e)

    print("\n=== انتهى الاختبار ===")

if __name__ == "__main__":
    generate_and_test()
