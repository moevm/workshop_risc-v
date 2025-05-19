import numpy as np
import subprocess
import sys
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
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

Шаблон программы:
.globl solution
solution:
    # Ваш код здесь
    li a0, X # X - итоговое значение из регистра а5
    ret

Сгенерированная программа для анализа:
{asm_code}
"""

MAIN_S = r"""
.globl main
.text
main:
    la a0, x
    call read_data
    ld a1, x
    call solution
    call print_result
    addi a0, x0, 0
    addi a7, x0, 93
    ecall


.data
x: .dword 0
"""

PRINT_RESULT_C = r"""
#include<stdio.h>
#include<stdint.h>

void print_result(int64_t result){
    fprintf(stderr, "%ld\n", result);
}

void read_data(int64_t *a){
    scanf("%ld", a);
}

"""



class Lab8Branch(BaseTaskClass):
    def __init__(
        self, *args,
        n: int,
        deep: float,
        student_id: int,
        **kwself
    ):
        super().__init__(*args, **kwself)
        self.generator = GenerateLab8(n=n, deep=deep, id=student_id).generate_asm()
        self.expected_result = self.generator[0]
        self.generated_asm = self.generator[1]
        self.n = n
        self.deep = deep
        self.student_id = student_id
        self.check_files = {
            "main.s": MAIN_S,
            "print_result.c": PRINT_RESULT_C,
        }
        self.url = ''

    def generate_bin(self):
        filename = self.student_id

        with open(f"{filename}.S", "w", encoding="utf-8") as f:
            f.write(self.generated_asm)

        try:
            subprocess.run(
                ['riscv64-unknown-elf-gcc', '-nostdlib', '-o', f'{filename}.bin', f'{filename}.S']
            )

        except subprocess.CalledProcessError as e:
            print(f"Ошибка: {e}", file=sys.stderr)
            sys.exit(1)
        except FileNotFoundError:
            print("Требуется RISC-V toolchain!", file=sys.stderr)
            print("Установите: sudo apt install gcc-riscv64-unknown-elf", file=sys.stderr)
            sys.exit(1)

        SERVICE_ACCOUNT = r'mse1h2025-edd2b21768e8.json'  # Please set the file of your credentials of service account.
        UPLOAD_FILE = f'{filename}.bin'  # Please set the filename with the path you want to upload.
        FOLDER_ID = '1BjC8f_mctia9CfbgEGlC53dnWG9pR7Cj'  # Please set the folder ID that you shared your folder with the service account.
        FILENAME = f'{filename}.bin'  # You can set the filename of the uploaded file on Google Drive.

        SCOPES = ['https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT, SCOPES)
        drive = build('drive', 'v3', credentials=credentials)
        metadata = {'name': FILENAME, "parents": [FOLDER_ID]}
        file = MediaFileUpload(UPLOAD_FILE, resumable=True)
        response = drive.files().create(body=metadata, media_body=file).execute()
        fileId = response.get('id')

        fileUrl = f'https://drive.google.com/file/d/{fileId}/view?usp=sharing'
        self.url = fileUrl


    def generate_task(self) -> str:
        return TASK_DESCRIPTION.format(
            asm_code=self.url,
            expected_result=self.expected_result
        )

    def _generate_tests(self):
        self.tests = []
        for _ in range(self.tests_num):
            generator = GenerateLab8(n=self.n, deep=self.deep, id=self.student_id).generate_asm()
            expected_result = generator[0]
            #print(expected_result)
            self.tests.append(TestItem(
                input_str=f'{expected_result}',
                showed_input="Generated program analysis",
                expected=str(expected_result),
                compare_func=self._compare_default
            ))
