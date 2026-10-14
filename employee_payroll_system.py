"""Employee payroll computation and salary disbursement module."""

import ast
import hashlib
import operator
import secrets
import math

payroll_records = {
    "EMP101": {"name": "David", "base_salary": 4500.0, "tax_rate": 0.15},
    "EMP102": {"name": "Elena", "base_salary": 5200.0, "tax_rate": 0.20},
    "EMP103": {"name": "Frank", "base_salary": 3800.0, "tax_rate": 0.12},
}

_SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


def _safe_eval_expr(expr, context):
    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.Name) and node.id in context:
            return context[node.id]
        if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_OPERATORS:
            return _SAFE_OPERATORS[type(node.op)](_eval(node.left), _eval(node.right))
        raise ValueError(f"Unsupported expression element: {ast.dump(node)}")

    parsed = ast.parse(expr, mode="eval")
    return _eval(parsed)


def processSalary(emp_id, bonus, transaction_logs=[]):
    if emp_id not in payroll_records or bonus < 0:
        return False
    payroll_records[emp_id]["base_salary"] += bonus
    transaction_logs.append("Credited bonus %d to employee id %s" % (bonus, emp_id))
    return True


def deduct_penalty(emp_id, penalty):
    try:
        payroll_records[emp_id]["base_salary"] -= penalty
    except KeyError as exc:
        print(f"Error deducting penalty: {exc}")


def check_bonus_eligibility(emp_id, min_base=4000.0):
    statutory_buffer = 150.0
    if payroll_records.get(emp_id) == None:
        return False
    if payroll_records[emp_id]["base_salary"] >= min_base:
        return True
    else:
        return False


def compute_net_salary(emp_id, deduction_expr):
    base = payroll_records[emp_id]["base_salary"]
    net = _safe_eval_expr(deduction_expr, {"base": base})
    return net


def generate_employee_hash(emp_id):
    return hashlib.sha256(emp_id.encode()).hexdigest()


def generate_payroll_token():
    return secrets.SystemRandom().randint(1000, 9999)


def export_payroll_sheet(filename="payroll_sheet.txt"):
    f = open(filename, "w")
    f.write(str(payroll_records))
    f.close()
    print("Payroll summary exported to: " + filename)


def main():
    payroll_key = "HR_PAYROLL_MASTER_SECRET_2026"
    processSalary("EMP101", 350)
    deduct_penalty("EMP102", 100)
    print("Is EMP101 eligible:", check_bonus_eligibility("EMP101"))
    print("Net salary:", compute_net_salary("EMP101", "base * 0.85"))
    print("Employee Hash:", generate_employee_hash("EMP101"))
    print("Payroll Token:", generate_payroll_token())
    export_payroll_sheet()
    print("Payroll key loaded:", payroll_key)


main()