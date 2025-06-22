from typing import Optional
import subprocess
import shlex
import urllib.request
import hashlib
import hmac
import datetime
import numpy as np
import shutil
import os
from ..base_module import BaseTaskClass, TestItem
from .lab8_gen import GenerateLab8

DEFAULT_TYPE = "int64"
INT_TYPES = {
    "int64":  np.int64,
    "int32":  np.int32,
    "int16":  np.int16,
    "int8":   np.int8,
    "uint64": np.uint64,
    "uint32": np.uint32,
    "uint16": np.uint16,
    "uint8":  np.uint8
}

TASK_DESCRIPTION = """
Проанализируйте программу на ассемблере RISC-V, которая создает граф вызовов функций и вычисляет итоговое значение в соответствии с вашим вариантом.

Исходный код программы будет сгенерирован автоматически на основе вашего ID. 
Ваша задача - проанализировать последовательность вызовов функций и операции с регистрами, чтобы определить итоговое значение, которое должно быть записано в регистр a5.

Сгенерированная программа для анализа:
"""

PRINT_RESULT_C = r"""
#include<stdio.h>
#include<stdint.h>

void print_result(int64_t result){
    fprintf(stderr, "%ld\n", result);
}
"""

DEFAULT_START_LEN = 12
DEFAULT_DEEP = 0.5

access_key = 'YCAJEFio4CdAZohHoafHTpJBA'
secret_key = 'YCPud0aAiVCnU-37dUEWm9lgzEfUB5_tCfczz1QE'
bucket = 'mse1h2025v2'


def hmac_sha256(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()


def sha256_hash(data):
    return hashlib.sha256(data).hexdigest()


class Lab8Branch(BaseTaskClass):
    def __init__(
        self, *args,
        n: int = DEFAULT_START_LEN,
        deep: float = DEFAULT_DEEP,
        answer: str = "",
        **kwself
    ):
        super().__init__(*args, **kwself)
        self.generator = GenerateLab8(n=n, deep=deep, id=self.seed).generate_asm()
        self.expected_result = self.generator[0]
        self.asm_code = self.generator[1]
        self.answer = answer
        self.n = n
        self.deep = deep
        self.check_files = {
            "print_result.c": PRINT_RESULT_C,
        }
    
    def load_student_solution(
    self, solfile: Optional[str] = None, solcode: Optional[str] = None):
        self.answer = solcode
    # Do nothing, pass solution (answer) as argument
        pass

    def _check_riscv_compiler(self) -> Optional[str]:
        """Проверяет наличие RISC-V компилятора"""
        # Компиляторы для Docker контейнера (установлены в /opt/riscv/bin/)
        compilers_to_try = [
            '/opt/riscv/bin/riscv64-unknown-linux-gnu-gcc',
            'riscv64-unknown-linux-gnu-gcc',
            'riscv64-linux-gnu-gcc',
            'riscv32-unknown-linux-gnu-gcc', 
            'riscv32-linux-gnu-gcc'
        ]
        
        for compiler in compilers_to_try:
            if shutil.which(compiler) or os.path.exists(compiler):
                return compiler
        
        return None

    def _fallback_without_binary(self) -> str:
        """Возвращает задание без компиляции бинарника"""
        return TASK_DESCRIPTION + f"""

```assembly
{self.asm_code}
```

ВНИМАНИЕ: Компилятор RISC-V недоступен на сервере. 
Проанализируйте код выше и определите итоговое значение в регистре a5.
"""

    def generate_task(self) -> str:
        # Проверяем наличие компилятора
        compiler = self._check_riscv_compiler()
        if compiler is None:
            # Если компилятор недоступен, возвращаем задание с исходным кодом
            return self._fallback_without_binary()

        # Если есть компилятор, пытаемся скомпилировать
        main_s = self.asm_code
        if (err := self.__compile_binary(main_s, compiler)) is not None:
            # Если компиляция не удалась, возвращаем fallback
            return self._fallback_without_binary()

        temp_filename = f'temp_{self.seed}.s'
        try:
            with open(temp_filename, "w", encoding="utf-8") as f:
                f.write(self.asm_code)

            compile_command = f'{compiler} -c -nostdlib -static -g {temp_filename} -o {self.seed}.bin'
            # Убеждаемся, что PATH содержит путь к RISC-V toolchain
            env = os.environ.copy()
            if '/opt/riscv/bin' not in env.get('PATH', ''):
                env['PATH'] = '/opt/riscv/bin:' + env.get('PATH', '')
            
            result = subprocess.run(shlex.split(compile_command), capture_output=True, text=True, env=env)
            
            if result.returncode != 0:
                return self._fallback_without_binary()

            # Попытка загрузки в облако
            try:
                public_url = self._upload_to_yandex_cloud(f'{self.seed}.bin')
                return TASK_DESCRIPTION + public_url
            except Exception as e:
                print(f"Ошибка загрузки в облако: {e}")
                return self._fallback_without_binary()
        
        finally:
            # Очистка временных файлов
            for temp_file in [temp_filename, f'{self.seed}.bin']:
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass

    def _upload_to_yandex_cloud(self, filename: str) -> str:
        """Загружает файл в Яндекс.Облако и возвращает публичную ссылку"""
        object_key = filename
        file_path = filename

        with open(file_path, 'rb') as f:
            content = f.read()

        # Временные метки
        now = datetime.datetime.utcnow()
        amz_date = now.strftime('%Y%m%dT%H%M%SZ')
        date_scope = now.strftime('%Y%m%d')

        # Настройки доступа
        acl_header = 'public-read'
        content_hash = sha256_hash(content)

        # Формирование запроса
        canonical_headers = (
            f'host:{bucket}.storage.yandexcloud.net\n'
            f'x-amz-acl:{acl_header}\n'
            f'x-amz-content-sha256:{content_hash}\n'
            f'x-amz-date:{amz_date}\n'
        )

        canonical_request = (
            'PUT\n'
            f'/{object_key}\n'
            '\n'
            f'{canonical_headers}\n'
            'host;x-amz-acl;x-amz-content-sha256;x-amz-date\n'
            f'{content_hash}'
        )

        # Подпись
        string_to_sign = (
            f'AWS4-HMAC-SHA256\n'
            f'{amz_date}\n'
            f'{date_scope}/ru-central1/s3/aws4_request\n'
            f'{sha256_hash(canonical_request.encode("utf-8"))}'
        )

        signing_key = hmac_sha256(hmac_sha256(hmac_sha256(
            hmac_sha256(f'AWS4{secret_key}'.encode('utf-8'), date_scope),
            'ru-central1'),
            's3'),
            'aws4_request'
        )
        signature = hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

        # Заголовки запроса
        authorization_header = (
            'AWS4-HMAC-SHA256 Credential={}/{}, '
            'SignedHeaders=host;x-amz-acl;x-amz-content-sha256;x-amz-date, '
            'Signature={}'
        ).format(access_key, f'{date_scope}/ru-central1/s3/aws4_request', signature)

        url = f'https://{bucket}.storage.yandexcloud.net/{object_key}'
        headers = {
            'Host': f'{bucket}.storage.yandexcloud.net',
            'x-amz-acl': acl_header,
            'x-amz-date': amz_date,
            'x-amz-content-sha256': content_hash,
            'Authorization': authorization_header,
            'Content-Type': 'application/octet-stream'
        }

        # Отправка
        req = urllib.request.Request(url, data=content, headers=headers, method='PUT')
        with urllib.request.urlopen(req) as response:
            return f'https://storage.yandexcloud.net/{bucket}/{object_key}'

    def check_sol_prereq(self) -> Optional[str]:
        return None

    def compile(self) -> Optional[str]:
        return None

    def __compile_binary(self, src: str, compiler: str = None) -> Optional[str]:
        if compiler is None:
            compiler = self._check_riscv_compiler()
            if compiler is None:
                return "RISC-V compiler not found"
        
        # Временно сохраняем исходные файлы и настройки
        t_files = self.check_files
        self.check_files = {"main.s": src}
        self.solution = ""
        
        # Устанавливаем переменные окружения для RISC-V toolchain
        original_env = os.environ.copy()
        if '/opt/riscv/bin' not in os.environ.get('PATH', ''):
            os.environ['PATH'] = '/opt/riscv/bin:' + os.environ.get('PATH', '')
        
        try:
            # Попытка компиляции с найденным компилятором
            # Используем прямой вызов subprocess вместо _compile_internal
            temp_filename = f'temp_compile_{self.seed}.s'
            with open(temp_filename, "w", encoding="utf-8") as f:
                f.write(src)
            
            compile_command = f'{compiler} -c -nostdlib -static -g {temp_filename} -o temp_binary_{self.seed}.o'
            result = subprocess.run(shlex.split(compile_command), capture_output=True, text=True)
            
            # Очистка временных файлов
            for temp_file in [temp_filename, f'temp_binary_{self.seed}.o']:
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
            
            if result.returncode != 0:
                return f"Compilation failed: {result.stderr}"
                
        except Exception as e:
            return f"Compilation error: {str(e)}"
        finally:
            # Восстанавливаем исходные настройки
            os.environ.clear()
            os.environ.update(original_env)
            self.check_files = t_files
        
        return None
    
    def run_tests(self) -> tuple[bool, str]:
        compiler = self._check_riscv_compiler()
        if compiler is None:
            # Если компилятор недоступен, проверяем только ответ
            if self.answer.strip() == str(self.expected_result).strip():
                return True, "OK"
            return False, f"Wrong answer. Expected: {self.expected_result}, Got: {self.answer.strip()}"
        
        # Устанавливаем переменные окружения для RISC-V toolchain
        original_env = os.environ.copy()
        if '/opt/riscv/bin' not in os.environ.get('PATH', ''):
            os.environ['PATH'] = '/opt/riscv/bin:' + os.environ.get('PATH', '')
        
        try:
            self.check_files["main.s"] = self.asm_code.replace("_start", "main")
            self.solution = ""
            
            # Пробуем скомпилировать и запустить для проверки
            # Если не получается, используем простую проверку ответа
            try:
                if (err := self._compile_internal(compile_args="-static")) is not None:
                    # Компиляция не удалась, проверяем только ответ
                    if self.answer.strip() == str(self.expected_result).strip():
                        return True, "OK"
                    return False, f"Wrong answer. Expected: {self.expected_result}, Got: {self.answer.strip()}"

                dummy_test = TestItem(
                    input_str="", showed_input="",
                    expected="text", compare_func=self._compare_default
                )
                res = self._run_solution_internal(dummy_test)
                if res is None:
                    # Запуск не удался, проверяем только ответ
                    if self.answer.strip() == str(self.expected_result).strip():
                        return True, "OK"
                    return False, f"Wrong answer. Expected: {self.expected_result}, Got: {self.answer.strip()}"
            except:
                # Любая ошибка при компиляции/запуске - проверяем только ответ
                pass

            if self.answer.strip() == str(self.expected_result).strip():
                return True, "OK"
            return False, f"Wrong answer. Expected: {self.expected_result}, Got: {self.answer.strip()}"
            
        finally:
            # Восстанавливаем исходные переменные окружения
            os.environ.clear()
            os.environ.update(original_env)

    def _generate_tests(self):
        pass