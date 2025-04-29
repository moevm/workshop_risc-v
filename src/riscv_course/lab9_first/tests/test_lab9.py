import difflib
import os
import pytest

# Фикстуры для подготовки тестовых данных
@pytest.fixture
def original_path():
    return os.path.join(os.path.dirname(__file__), '..', 'lab9.s')

@pytest.fixture
def student_path():
    return os.path.join(os.path.dirname(__file__), '..', 'solution', 'student_lab9.s')

def read_lines(path):
    # Чтение строк из файла, игнорируя пустые строки
    with open(path) as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def test_line_count(student_path, original_path):
    # Проверка, что количество строк не уменьшилось и не увеличилось
    original = read_lines(original_path)
    student = read_lines(student_path)
    assert abs(len(original) - len(student)) == 0, f"Количество строк отличается: {len(student)} != {len(original)}"

def test_ecall_count(student_path, original_path):
    # Проверка, что количество вызовов ecall не увеличилось
    original = read_lines(original_path)
    student = read_lines(student_path)
    assert student.count("ecall") <= original.count("ecall"), f"Добавлены лишние ecall! Ожидалось: {original.count('ecall')}, Получено: {student.count('ecall')}"

def test_registers_usage(student_path, original_path):
    # Проверка, что использованы те же регистры, что и в исходном файле
    def extract_regs(lines):
        regs = []
        for line in lines:
            regs.extend([token for token in line.split() if token.startswith(("t", "a"))])  # Выбираем регистры
        return set(regs)

    original = extract_regs(read_lines(original_path))
    student = extract_regs(read_lines(student_path))
    assert original <= student, f"Некоторые оригинальные регистры не используются. Ожидались: {original}, Получены: {student}"

def test_data_section_unchanged(student_path, original_path):
    # Проверка, что секция .data осталась без изменений
    def extract_data(lines):
        in_data = False
        section = []
        for line in lines:
            if ".data" in line:
                in_data = True
                continue
            if in_data:
                if ".text" in line:
                    break
                section.append(line)
        return section

    original = extract_data(read_lines(original_path))
    student = extract_data(read_lines(student_path))
    assert original == student, f".data секция была изменена!"


def test_only_one_instruction_changed(student_path, original_path):
    # Строгая проверка, что изменена ровно одна инструкция
    original = read_lines(original_path)
    student = read_lines(student_path)
    # Находим все различия между строками
    diff = list(difflib.ndiff(original, student))
    changes = []
    for line in diff:
        if line.startswith('- ') or line.startswith('+ '):
            changes.append(line)

    # Проверяем количество изменений
    assert len(changes) != 0, "Не внесено никаких изменений"
    assert len(changes) <= 2, f"Изменено слишком много строк. Изменения:\n{''.join(diff)}"

    # Проверяем что это одно изменение (удаление + добавление)
    if len(changes) == 2:
        if not (changes[0].startswith('- ') and changes[1].startswith('+ ')):
            pytest.fail("Обнаружены непарные изменения")
        old_line = changes[0][2:]
        new_line = changes[1][2:]
        old_tokens = old_line.split()
        new_tokens = new_line.split()
        changed_tokens = sum(1 for o, n in zip(old_tokens, new_tokens) if o != n)

        # Проверяем что изменилась только инструкция (первый токен)
        assert not(changed_tokens != 1 or old_tokens[0] == new_tokens[0]),\
            f"Изменено больше чем только инструкция. Было: {old_line}, стало: {new_line}"

        # Проверяем что остальные токены не изменились
        assert old_tokens[1:] == new_tokens[1:], "Изменены не только инструкции, но и регистры/комментарии"

    # Дополнительная проверка - считаем количество измененных строк
    changed_lines = sum(1 for o, s in zip(original, student) if o != s)
    assert changed_lines == 1, f"Фактически изменено {changed_lines} строк"


def test_no_cheating_attempts(student_path, original_path):
    # Проверка на явные попытки жульничества
    student = read_lines(student_path)
    operations = ["add", "sub", "xor", "and", "or", "sll", "srl"]
    # Проверка на прямой вывод SUCCESS без вычислений
    for i, line in enumerate(student):
        if 'succes' in line and 'la a1, flag' in line:
            # Проверяем что выше есть какие-то вычисления
            has_calculations = any(
                op in prev_line for prev_line in student[max(0, i - 10):i]
                for op in operations
            )
            assert has_calculations, "Обнаружен прямой вывод SUCCESS без вычислений"

    # Проверка на наличие всех ключевых секций
    assert any('.text' in line for line in student), "Отсутствует секция .text"
    assert any('_start:' in line for line in student), "Отсутствует метка _start"


def test_constant_values(student_path, original_path):
    # Проверяет, что ключевые константы не изменены
    original = read_lines(original_path)
    student = read_lines(student_path)

    # Ищем и сравниваем все числовые константы
    def extract_constants(lines):
        consts = []
        for line in lines:
            if 'li ' in line or 'addi ' in line:
                const = line.split(',')[-1].strip()
                if const.startswith('0x') or const.isdigit():
                    consts.append(const)
        return consts

    orig_consts = extract_constants(original)
    stud_consts = extract_constants(student)

    # Разрешаем изменить только одну константу
    diff = set(orig_consts) ^ set(stud_consts)
    assert len(diff) <= 2, "Изменено слишком много констант"


def test_no_t3_t4_equality(student_path):
    # Проверяет отсутствие приравнивания t3 = t4, кроме существующего сравнения
    with open(student_path) as f:
        for line in f:
            line = line.strip()
            if '#' in line:
                line = line.split('#')[0].strip()
            if not line:
                continue

            # Пропускаем оригинальное сравнение
            if any(op in line for op in ['beq', 'bne', 'blt', 'bge']):
                continue

            # Проверяем опасные операции
            if ('t3,' in line and 't4' in line) or ('t4,' in line and 't3' in line):
                op = line.split()[0]
                if op in ['mv', 'add', 'or', 'xor', 'sub', 'seqz']:
                    pytest.fail(f"Обнаружено приравнивание t3 и t4: {line}")


def test_t3_t4_comparison_count(student_path, original_path):
    # Проверяет что добавлены новые сравнения t3 и t4

    def count_comparisons(lines):
        count = 0
        for line in lines:
            if ('t3,' in line and 't4' in line) or ('t4,' in line and 't3' in line):
                if any(op in line for op in ['beq', 'bne', 'blt', 'bge']):
                    count += 1
        return count

    original = read_lines(original_path)
    student = read_lines(student_path)

    orig_count = count_comparisons(original)
    stud_count = count_comparisons(student)

    assert stud_count == orig_count, f"Изменено количество сравнений t3 и t4: было {orig_count}, стало {stud_count}"


def test_original_comparison_unchanged(student_path, original_path):
    # Проверяет что оригинальное сравнение t3 и t4 не изменено

    def find_comparison(lines):
        for line in lines:
            if ('t3,' in line and 't4' in line) or ('t4,' in line and 't3' in line):
                if any(op in line for op in ['beq', 'bne', 'blt', 'bge']):
                    return line.strip()
        return None

    original = read_lines(original_path)
    student = read_lines(student_path)

    orig_comp = find_comparison(original)
    stud_comp = find_comparison(student)

    assert orig_comp is not None, "В оригинале не найдено сравнение t3 и t4"
    assert stud_comp == orig_comp, f"Оригинальное сравнение изменено: было '{orig_comp}', стало '{stud_comp}'"


def test_t3_t4_data_flow(student_path, original_path):
    # Анализ зависимостей t3 и t4 с учетом оригинального кода
    original = read_lines(original_path)
    student = read_lines(student_path)

    # Находим все использования t3 и t4
    t3_sources = set()
    t4_sources = set()

    for line in student:
        line = line.strip()
        if not line or line.startswith('.'):
            continue

        # Записи в t3
        if any(line.startswith(f"{op} t3,") for op in ['add', 'sub', 'or', 'xor', 'mv', 'li']):
            parts = [p.strip() for p in line.split(',')]
            if len(parts) > 1:
                t3_sources.add(parts[1])

        # Записи в t4
        if any(line.startswith(f"{op} t4,") for op in ['add', 'sub', 'or', 'xor', 'mv', 'li']):
            parts = [p.strip() for p in line.split(',')]
            if len(parts) > 1:
                t4_sources.add(parts[1])

    # Проверяем что t4 не является источником для t3
    forbidden_sources = {'t4', 'x0', 'zero'}
    assert not t3_sources & forbidden_sources, f"Обнаружены запрещенные источники для t3: {t3_sources & forbidden_sources}"

    # Проверяем что t3 не является источником для t4 (если это не разрешено)
    if not any('t3' in src for src in t4_sources for _ in original):
        assert not any('t3' in src for src in t4_sources), f"Обнаружено использование t3 как источника для t4"
