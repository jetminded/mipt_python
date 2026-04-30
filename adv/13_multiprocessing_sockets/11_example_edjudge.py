import subprocess
import resource
import sys
import os
import time
import shutil
from pathlib import Path

# ========== НАСТРОЙКИ ==========
TESTING_DIR = "testing_dir"  # Папка для всей работы
TIME_LIMIT_SEC = 2  # Лимит времени (секунды)
MEMORY_LIMIT_MB = 256  # Лимит памяти (мегабайты)
COMPILER = "g++"  # Компилятор
COMPILER_FLAGS = ["-O2", "-std=c++17", "-Wall"]  # Флаги компиляции

# ========== ПУТИ К ФАЙЛАМ ==========
PROGS_DIR = "progs"  # Папка с C++ программами

# Список C++ файлов для тестирования
CPP_FILES = [
    "ok_sum.cpp",
    "wa_sum.cpp",
    "tl_sum.cpp",
    "re_sum.cpp"
]

# ========== ТЕСТЫ ==========
TESTS = [
    {
        "name": "Simple sum",
        "input": "5\n1 2 3 4 5\n",
        "expected": "15\n"
    },
    {
        "name": "Single number",
        "input": "1\n42\n",
        "expected": "42\n"
    },
    {
        "name": "Empty input",
        "input": "0\n\n",
        "expected": "0\n"
    },
    {
        "name": "Large numbers",
        "input": "3\n1000000000 2000000000 3000000000\n",
        "expected": "6000000000\n"
    },
    {
        "name": "Negative numbers",
        "input": "4\n-5 -10 -15 -20\n",
        "expected": "-50\n"
    }
]

# ========== ДОПОЛНИТЕЛЬНЫЕ НАСТРОЙКИ ==========
MEMORY_LIMIT_BYTES = MEMORY_LIMIT_MB * 1024 * 1024


def create_testing_dir():
    """Создает папку testing_dir если её нет"""
    testing_path = Path(TESTING_DIR)
    if not testing_path.exists():
        testing_path.mkdir(parents=True)
        print(f"Created directory: {TESTING_DIR}")
    return testing_path


def cleanup_testing_dir(testing_path):
    """Очищает папку testing_dir от временных файлов"""
    for file in testing_path.glob("*.in"):
        file.unlink()
    for file in testing_path.glob("*.out"):
        file.unlink()
    for file in testing_path.glob("*.tmp"):
        file.unlink()
    for file in testing_path.glob("*.exe"):
        file.unlink()
    for file in testing_path.glob("solution*"):
        file.unlink()


def save_test_files(testing_path, test_num, input_data, expected_data):
    """Сохраняет входные и ожидаемые данные в файлы"""
    input_file = testing_path / f"test{test_num}.in"
    expected_file = testing_path / f"test{test_num}.out"

    with open(input_file, 'w') as f:
        f.write(input_data)
    with open(expected_file, 'w') as f:
        f.write(expected_data)

    return input_file, expected_file


def compile_cpp(source_file, output_executable, testing_path):
    """
    Компилирует C++ файл.
    Возвращает (success, error_message)
    """
    print(f"Compiling {source_file}...")

    # Копируем исходник в testing_dir
    dest_source = testing_path / source_file.name
    shutil.copy2(source_file, dest_source)

    # Компилируем
    compile_cmd = [COMPILER] + COMPILER_FLAGS + [str(dest_source), "-o", str(output_executable)]

    try:
        result = subprocess.run(
            compile_cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            print(f"  ✓ Compilation successful")
            if os.name == 'posix':
                os.chmod(output_executable, 0o755)
            return True, ""
        else:
            return False, result.stderr

    except subprocess.TimeoutExpired:
        return False, "Compilation timeout (>30 seconds)"
    except Exception as e:
        return False, f"Compilation error: {str(e)}"


def set_limits():
    """Устанавливает ограничения для дочернего процесса"""
    try:
        resource.setrlimit(resource.RLIMIT_AS, (MEMORY_LIMIT_BYTES, MEMORY_LIMIT_BYTES))
        resource.setrlimit(resource.RLIMIT_CPU, (TIME_LIMIT_SEC, TIME_LIMIT_SEC))
        resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))
    except Exception as e:
        # На Windows это может не работать
        pass


def run_single_test(executable, input_file, expected_file):
    """
    Запускает программу на одном тесте.
    Возвращает (verdict, time_used, error_msg)
    """
    try:
        start_time = time.time()

        # Запускаем с ограничениями
        if os.name == 'posix':
            process = subprocess.Popen(
                [str(executable)],
                stdin=open(input_file, 'r'),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=set_limits,
                universal_newlines=True
            )
        else:
            # Windows fallback
            process = subprocess.Popen(
                [str(executable)],
                stdin=open(input_file, 'r'),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

        stdout, stderr = process.communicate(timeout=TIME_LIMIT_SEC + 0.5)
        elapsed_time = time.time() - start_time

        # Проверяем код возврата
        if process.returncode != 0:
            if process.returncode == -9 or process.returncode == -11:
                return "ML/TL", elapsed_time, "Memory or time limit exceeded"
            return "RE", elapsed_time, f"Runtime error (code {process.returncode})\n{stderr[:200]}"

        # Читаем ожидаемый вывод
        expected_output = open(expected_file, 'r').read()

        # Сравниваем вывод
        if stdout.rstrip() == expected_output.rstrip():
            return "OK", elapsed_time, ""
        else:
            diff_msg = f"Expected: '{expected_output[:50]}...' Got: '{stdout[:50]}...'"
            return "WA", elapsed_time, diff_msg

    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
        return "TL", TIME_LIMIT_SEC + 0.5, "Time limit exceeded"
    except Exception as e:
        return "ERR", 0, f"Testing error: {str(e)}"


def print_verdict(verdict, test_name, time_used, error_msg=""):
    """Красиво выводит вердикт"""
    colors = {
        "OK": "\033[92m",  # зелёный
        "WA": "\033[91m",  # красный
        "TL": "\033[93m",  # жёлтый
        "ML/TL": "\033[93m",  # жёлтый
        "RE": "\033[91m",  # красный
        "ERR": "\033[95m"  # фиолетовый
    }
    reset = "\033[0m"

    color = colors.get(verdict, reset)

    if verdict == "OK":
        print(f"{color}[{verdict}]{reset} {test_name} ({time_used:.3f}s)")
    else:
        print(f"{color}[{verdict}]{reset} {test_name} ({time_used:.3f}s)")
        if error_msg:
            print(f"  └─ {error_msg[:150]}")


def test_single_program(cpp_file_path, testing_path):
    """Тестирует одну C++ программу"""
    print(f"\n{'=' * 70}")
    print(f"Testing: {cpp_file_path.name}")
    print(f"{'=' * 70}")

    # Компилируем
    executable = testing_path / f"{cpp_file_path.stem}_exec"
    if os.name == 'nt':
        executable = testing_path / f"{cpp_file_path.stem}.exe"

    success, error = compile_cpp(cpp_file_path, executable, testing_path)

    if not success:
        print(f"\n\033[91m✗ Compilation failed for {cpp_file_path.name}!\033[0m")
        print("Error details:")
        print(error)
        return None

    # Запускаем тесты
    print(f"\nRunning {len(TESTS)} test(s)...")
    print(f"Time limit: {TIME_LIMIT_SEC}s, Memory limit: {MEMORY_LIMIT_MB}MB")

    results = {
        "OK": 0,
        "WA": 0,
        "TL": 0,
        "ML/TL": 0,
        "RE": 0,
        "ERR": 0
    }

    total_time = 0.0

    for i, test in enumerate(TESTS, 1):
        test_name = f"Test {i}: {test['name']}"

        # Сохраняем тест в файлы
        input_file, expected_file = save_test_files(
            testing_path, i, test['input'], test['expected']
        )

        # Запускаем тест
        verdict, elapsed_time, error = run_single_test(
            executable, input_file, expected_file
        )

        results[verdict] += 1
        total_time += elapsed_time

        print_verdict(verdict, test_name, elapsed_time, error)

    # Статистика для программы
    passed = results['OK']
    total = len(TESTS)

    print(f"\nResults for {cpp_file_path.name}: ✓ {passed}/{total} passed")
    print(f"  OK: {results['OK']}, WA: {results['WA']}, TL: {results['TL']}, "
          f"ML: {results['ML/TL']}, RE: {results['RE']}, ERR: {results['ERR']}")

    return passed == total


def main():
    # Проверяем существование папки с C++ файлами
    progs_path = Path(PROGS_DIR)
    if not progs_path.exists():
        print(f"Error: Directory '{PROGS_DIR}' not found!")
        print("Please create 'progs' folder with C++ files: ok_sum.cpp, wa_sum.cpp, etc.")
        sys.exit(1)

    # Проверяем наличие C++ файлов
    cpp_files = []
    for cpp_file in CPP_FILES:
        file_path = progs_path / cpp_file
        if file_path.exists():
            cpp_files.append(file_path)
        else:
            print(f"Warning: {cpp_file} not found in {PROGS_DIR}/")

    if not cpp_files:
        print(f"Error: No C++ files found in {PROGS_DIR}/")
        print(f"Expected files: {', '.join(CPP_FILES)}")
        sys.exit(1)

    print(f"Found {len(cpp_files)} C++ file(s) to test:")
    for f in cpp_files:
        print(f"  - {f.name}")

    # Создаём рабочую папку
    testing_path = create_testing_dir()

    # Очищаем от старых файлов
    cleanup_testing_dir(testing_path)

    # Тестируем каждую программу
    all_results = {}
    for cpp_file in cpp_files:
        success = test_single_program(cpp_file, testing_path)
        all_results[cpp_file.name] = success

        # Очищаем временные файлы между тестами
        cleanup_testing_dir(testing_path)

    # Финальная статистика
    print(f"\n{'=' * 70}")
    print("FINAL SUMMARY")
    print(f"{'=' * 70}")

    for prog, success in all_results.items():
        status = "✓ PASSED" if success else "✗ FAILED"
        color = "\033[92m" if success else "\033[91m"
        print(f"{color}{status}\033[0m: {prog}")

    # Подробный вывод ожидаемых вердиктов
    print(f"\n{'=' * 70}")
    print("EXPECTED VERDICTS:")
    print(f"{'=' * 70}")
    print("  ok_sum.cpp  → Should PASS all tests (OK)")
    print("  wa_sum.cpp  → Should FAIL (Wrong Answer)")
    print("  tl_sum.cpp  → Should FAIL (Time Limit)")
    print("  re_sum.cpp  → Should FAIL (Runtime Error)")

    # Очищаем временные файлы (опционально)
    if "--keep-files" not in sys.argv:
        cleanup_testing_dir(testing_path)
        print(f"\nCleaned up temporary files from {TESTING_DIR}/")
    else:
        print(f"\nTemporary files kept in {TESTING_DIR}/")

    # Возвращаем код ошибки, если хоть одна программа не прошла
    if all(success for success in all_results.values()):
        print(f"\n\033[92m{'=' * 50}")
        print("✓ ALL PROGRAMS PASSED AS EXPECTED! ✓")
        print(f"{'=' * 50}\033[0m")
        return 0
    else:
        print(f"\n\033[93m{'=' * 50}")
        print("⚠ SOME PROGRAMS FAILED (AS EXPECTED FOR WA/TL/ML/RE) ⚠")
        print(f"{'=' * 50}\033[0m")
        return 1


if __name__ == "__main__":
    sys.exit(main())