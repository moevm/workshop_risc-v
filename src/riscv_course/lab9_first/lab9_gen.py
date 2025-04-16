import random
import networkx as nx

def generate_random_values(student_id):
    random.seed(student_id)
    t1 = random.randint(0, 0xFFFF)
    t2 = random.randint(0, 0xFFFF)
    return t1, t2


def generate_graph(max_depth=5, max_nodes=10):
    G = nx.DiGraph()
    G.add_node(0)

    # список доступных для соединения узлов
    available_nodes = {0: 0}  # {узел: глубина}
    out_degree = {0: 0}  # {узел: количество исходящих рёбер}

    for i in range(1, max_nodes):
        # выбираем случайного родителя, у которого меньше двух детей
        parent = random.choice([node for node in available_nodes if out_degree[node] < 2])

        # добавляем новое ребро
        G.add_edge(parent, i)
        out_degree[parent] += 1
        out_degree[i] = 0

        # обновляем глубину нового узла
        depth = available_nodes[parent] + 1
        available_nodes[i] = depth

        # удаляем узлы, которые достигли лимита исходящих рёбер
        if out_degree[parent] == 2:
            del available_nodes[parent]

        if depth >= max_depth:
            del available_nodes[i]

    return G

def init_temp_reg(G, node, k, n):
    if k == 7:
        temp_registers = 'a7'
        k = 0
    else:
        temp_registers = f"a{k}"
        k += 1
    if "init" in G.nodes[node]:
        G.nodes[node]["init"] += f"\n    li {temp_registers}, {n}"
    else:
        G.nodes[node]["init"] = f"li {temp_registers}, {n}"
    return G, k, temp_registers


def add_operations_and_conditions(G, student_id):
    # добавляет операции и условия для каждой вершины графа
    random.seed(student_id)
    operations = ["add", "sub", "xor", "and", "or", "sll", "srl"]
    registers = ["t1", "t2", "t3", "t5", "t6"]
    k = 0

    for node in G.nodes():
        # выбираем операцию
        op = random.choice(operations[:-1])
        flag_use_t = 0

        # с вероятностью 50% выбираем t3 как целевой регистр
        if random.random() < 0.5:
            target_reg = "t3"
        else:
            target_reg = random.choice([reg for reg in registers if reg != "t3"])  # Выбираем любой регистр, кроме t3

        source_reg = random.choice(registers)  # Источник может быть любым регистром
        if source_reg in ["t5", "t6"]:
            init_value = random.randint(0, 0xFFFF)
            G.nodes[node]["init"] = f"li {source_reg}, {init_value}"

        if random.random() < 0.5:
            imm = random.randint(1, 15) if "sll" in op or "srl" in op else random.randint(0, 0xFFFF)
            G, k, imm = init_temp_reg(G, node, k, imm)
        else:
            imm = random.choice(registers)
            flag_use_t = imm
            if imm in ["t5", "t6"]:
                init_value = random.randint(0, 0xFFFF)
                G.nodes[node]["init"] = f"li {imm}, {init_value}"

        G.nodes[node]["op"] = f"{op} {target_reg}, {source_reg}, {imm}"

        # добавляем условие перехода
        if G.out_degree(node) > 1:
            condition = random.choice(["beqz", "bnez", "blt", "bge", "beq", "bne", "bltu", "bgeu"])
            if condition in ["beqz", "bnez"]:
                G.nodes[node]["condition"] = f"{condition} {target_reg},"
            else:
                num = random.randint(0, 0xFFFF)
                if flag_use_t != 0:
                    choice = random.choice([flag_use_t, num])
                    if not isinstance(choice, str):
                        G, k, choice = init_temp_reg(G, node, k, num)
                    G.nodes[node]["condition"] = f"{condition} {target_reg}, {choice},"
                else:
                    G, k, num = init_temp_reg(G, node, k, num)
                    G.nodes[node]["condition"] = f"{condition} {target_reg}, {num},"
        else:
            G.nodes[node]["condition"] = "j"  # безусловный переход


def generate_code_from_graph(G, t1, t2, t4):
    # генерирует RISC-V код на основе графа
    asm_code = ".text\n.globl solution\nsolution:\n"

    asm_code += f"    li t1, {hex(t1)}\n"
    asm_code += f"    li t2, {hex(t2)}\n"
    asm_code += f"    li t4, {hex(t4)}  # ожидаемое значение t4\n"

    for node in sorted(G.nodes()):  # обход узлов в порядке возрастания
        op = G.nodes[node]["op"]
        condition = G.nodes[node]["condition"]

        asm_code += f"node_{node}:\n"
        if "init" in G.nodes[node]:
            asm_code += f"    {G.nodes[node]['init']}\n"
        asm_code += f"    {op}\n"

        # получаем список исходящих рёбер
        successors = list(G.successors(node))

        if not successors:  # если нет исходящих рёбер
            asm_code += "    j final\n"
        elif condition == "j":  # безусловный переход
            asm_code += f"    j node_{successors[0]}\n"
        else:  # Условный переход
            asm_code += f"    {condition} node_{successors[0]}\n"
            if len(successors) > 1:  # если есть второй переход
                asm_code += f"    j node_{successors[1]}\n"

    # проверка на успех
    return asm_code

def generate_file(file_name, student_id=123456):
    # создаём структуру графа
    G = generate_graph(max_nodes=10, max_depth=5)

    # добавляем операции и условия
    add_operations_and_conditions(G, student_id)

    # генерируем RISC-V код
    t1, t2 = generate_random_values(student_id)
    asm_code = generate_code_from_graph(G, t1, t2, t4=0)

    # сохраняем код в файл
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(asm_code)

def start_gen(n: int, deep: int, student_id: int):
    G = generate_graph(max_nodes=n, max_depth=deep)

    # добавляем операции и условия
    add_operations_and_conditions(G, student_id)

    # генерируем RISC-V код
    t1, t2 = generate_random_values(student_id)
    asm_code = generate_code_from_graph(G, t1, t2, t4=0)

    return asm_code
