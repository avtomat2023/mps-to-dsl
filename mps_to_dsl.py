#/usr/bin/env python3
import sys

objective = {}
objective_name = None
constraints = {}
variables = set()

def paired(list):
    for i in range(len(list) // 2):
        yield (list[i*2], list[i*2+1])

def read_fields(field_kind):
    if field_kind == 'ROWS':
        return read_rows()
    elif field_kind == 'COLUMNS':
        return read_columns()
    elif field_kind == 'RHS':
        return read_rhs()
    else:
        return read_bounds()

def read_rows():
    global objective_name
    while True:
        fields = input().split()
        if len(fields) == 1:
            return fields[0]
        kind, name = fields
        if kind == 'N':
            objective_name = name
        else:
            constraints[name] = [kind, {}, None]

def read_columns():
    while True:
        fields = input().split()
        if len(fields) == 1:
            return fields[0]
        var_name = fields[0]
        variables.add(var_name)
        for (name, coeff) in paired(fields[1:]):
            if name == objective_name:
                objective[var_name] = float(coeff)
            else:
                constraints[name][1][var_name] = float(coeff)

def read_rhs():
    while True:
        fields = input().split()
        if len(fields) == 1:
            for constraint in constraints.values():
                if constraint[2] == None:
                    constraint[2] = 0.0
            return fields[0]
        for (name, coeff) in paired(fields[1:]):
            if (float(coeff) < 0):
                print('invalid rhs', fields)
                sys.exit(1)
            constraints[name][2] = float(coeff)

def read_bounds():
    while True:
        fields = input().split()
        if len(fields) == 1:
            return fields[0]
        if fields[0] == 'UP':
            ineq = 'L'
        else:
            ineq = 'G'
        var_name, rhs = fields[2:]
        if float(rhs) < 0:
            print('invalid bound', fields)
            sys.exit(1)
        con_name = ineq + ' ' + var_name
        constraints[con_name] = [ineq, {var_name: 1}, float(rhs)]

def coeffs_to_prolog_dsl_expr(c):
    var_to_num = {name: i for (i, name) in enumerate(variables)}
    c_dict = {var_to_num[key]: value for (key, value) in c.items()}
    c_list = sorted(c_dict.items(), key=lambda x: x[0])
    return ' + '.join(str(k)+'$'+str(n) for (n,k) in c_list)

def print_prolog_dsl():
    # print constriants
    for constraint in constraints.values():
        sign = {'L': ':<=', 'G': ':>=', 'E': ':=='}[constraint[0]]
        expr = coeffs_to_prolog_dsl_expr(constraint[1])
        rhs = str(constraint[2])
        print(expr, sign, rhs, end='.\n')

    # print maximization directive
    print(coeffs_to_prolog_dsl_expr(objective), ":-> min.")

def coeffs_to_scala_dsl_expr(c):
    var_to_num = {name: i for (i, name) in enumerate(variables)}
    c_dict = {var_to_num[key]: value for (key, value) in c.items()}
    c_list = sorted(c_dict.items(), key=lambda x: x[0])
    return ' + '.join(str(k)+'*x('+str(n)+')' for (n,k) in c_list)

def print_scala_dsl():
    print('minimize (' +
          coeffs_to_scala_dsl_expr(objective) +
          ') subjectTo {')

    for constraint in constraints.values():
        print('  ', end='')
        sign = {'L': '<=', 'G': '>=', 'E': '=='}[constraint[0]]
        expr = coeffs_to_scala_dsl_expr(constraint[1])
        rhs = str(constraint[2])
        print(expr, sign, rhs)

    print('}')

if __name__ == '__main__':
    # skip NAME row
    input()

    next = read_fields(input())
    while next != "ENDATA":
        next = read_fields(next)

    print_scala_dsl()
    # print_prolog_dsl()
