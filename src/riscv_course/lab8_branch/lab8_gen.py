import random
import networkx as nx

class GenerateLab8:
    def __init__(self, n: int, deep: float, id: int):
        self.n = n
        self.deep = deep
        self.id = id

        self.n_of_jump = n // 5
        self.n_of_func = n - self.n_of_jump

        self.a4 = 0
        self.a5 = 0
        self.a6 = 0

        self.flag = 0
        self.G = nx.DiGraph()
        self.main_path = []
        self.final_func = 0
        self.ops_map = {}

        self.calculate_reg()
        self.calculate_flag()
        self.generate_graph()

    def calculate_reg(self):
        self.a4 = ((self.id % random.randint(3, 7)) + 5) * 10  # min/max = 50/110
        self.a5 = (self.id // random.randint(10, 100) + random.randint(10, 20))  # id?
        self.a6 = ((self.id // 100) % 10) + (random.randint(30, 50) - 4)

    def calculate_flag(self):
        step1 = self.a5 + self.a4
        step2 = self.a5 // self.a6
        self.flag = step1 * step2

    def generate_graph(self):
        vertices = list(range(self.n_of_func))
        self.G.add_nodes_from(vertices)

        min_path_len = max(3, int(self.n_of_func * self.deep))
        self.main_path = random.sample(vertices, min_path_len)
        for i in range(len(self.main_path) - 1):
            self.G.add_edge(self.main_path[i], self.main_path[i + 1], color='black')

        used = set(self.main_path)
        free = [v for v in vertices if v not in used]
        for u in free:
            v = random.choice(self.main_path[:-1])
            self.G.add_edge(v, u, color='red')

        for u in range(self.n_of_jump):
            v = random.choice([i for i in range(self.n_of_func)])
            self.G.add_edge(v, self.n_of_func + u, color='blue')

        for v in range(1, len(self.main_path)):
            if not self.G.adj[self.main_path[v - 1]]:
                continue
            if max(self.G.adj[self.main_path[v - 1]]) > self.main_path[v]:
                self.final_func = max(self.final_func, max(self.G.adj[self.main_path[v - 1]]))
                break

        remaining_funcs = [v for v in vertices if v != self.final_func]
        op_funcs_sample = random.sample(remaining_funcs, 2)

        self.ops_map = {
            op_funcs_sample[0]: '\tadd a4, a4, a5',
            op_funcs_sample[1]: '\tdiv a6, a5, a6',
            self.final_func: '\tmul a5, a4, a6'  # всегда в последней
        }

    def generate_noise(self):
        regs = ['a1', 'a2', 'a3']
        ops = ['add', 'sub', 'xor', 'or', 'and', 'mul']
        lines = []
        for _ in range(random.randint(1, 3)):
            dst = random.choice(regs)
            r1 = random.choice(regs)
            r2 = random.choice(regs)
            op = random.choice(ops)
            lines.append(f'\t{op} {dst}, {r1}, {r2}')
        return lines


    def generate_func(self, idx, neighbors):
        """
        n = 7  # количество функций
        deep = 0.6  # глубина основного пути (0.3–0.8)
        id = 12345  # пример id студента

        lab2 = GenerateLab2(n, deep, id)

        print(lab2.generate_asm())
        """
        lines = [f'func_{idx}:']
        lines += self.generate_noise()

        if idx in self.ops_map:
            lines.append(self.ops_map[idx])
        for n in neighbors:
            if neighbors[n]['color'] == 'blue':
                lines += [
                    f'\tj func_{n}'
                ]
            else:
                lines += [
                    '\taddi sp, sp, -4',
                    '\tsw ra, 0(sp)',
                    f'\tcall func_{n}',
                    '\tlw ra, 0(sp)',
                    '\taddi sp, sp, 4'
                ]
        lines.append('\tret\n')
        return lines

    def generate_asm(self):
        asm_code = f"""
.global _start

_start:
\tli a1, 5
\tli a2, 10
\tli a3, 15
\tli a4, {self.a4}
\tli a5, {self.a5}
\tli a6, {self.a6}
\tcall func_{self.main_path[0]}
\tli a0, 0
\tli a7, 93
\tecall
"""
        visited = set()
        stack = [self.main_path[0]]
        while stack:
            v = stack.pop()
            if v in visited:
                continue
            visited.add(v)
            u = dict(sorted(self.G.adj[v].items()))
            stack.extend(u)
            asm_code += '\n'.join(self.generate_func(v, u)) + '\n'

        # with open("generated_program.s", "w") as f:
        #     f.write(asm_code)

        return self.flag, asm_code

    # def get_asm_code(self):
        # return "\n".join(self.generate_asm())

