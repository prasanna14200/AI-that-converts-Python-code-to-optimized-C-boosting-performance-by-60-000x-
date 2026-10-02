import shutil
import subprocess
import tempfile
from pathlib import Path


SAMPLES = [
    {
        "name": "loop",
        "python": "total = 0\nfor i in range(5):\n    total += i\nprint(total)\n",
        "cpp": "#include <iostream>\nint main(){int total=0; for(int i=0;i<5;i++){total+=i;} std::cout<<total<<std::endl; return 0;}\n",
    },
    {
        "name": "function",
        "python": "def square(x):\n    return x * x\nprint(square(7))\n",
        "cpp": "#include <iostream>\nint square(int x){return x*x;} int main(){std::cout<<square(7)<<std::endl; return 0;}\n",
    },
    {
        "name": "edge_empty_list",
        "python": "items = []\nprint(len(items))\n",
        "cpp": "#include <iostream>\n#include <vector>\nint main(){std::vector<int> items; std::cout<<items.size()<<std::endl; return 0;}\n",
    },
]


def run(command, cwd=None):
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=True).stdout.strip()


def main():
    gpp = shutil.which("g++")
    if not gpp:
        raise SystemExit("g++ is not installed; C++ syntax/behavior checks were skipped.")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for sample in SAMPLES:
            py_path = root / f"{sample['name']}.py"
            cpp_path = root / f"{sample['name']}.cpp"
            exe_path = root / f"{sample['name']}.exe"
            py_path.write_text(sample["python"], encoding="utf-8")
            cpp_path.write_text(sample["cpp"], encoding="utf-8")

            py_output = run(["python", str(py_path)])
            subprocess.run([gpp, "-std=c++17", "-Wall", "-Wextra", str(cpp_path), "-o", str(exe_path)], check=True)
            cpp_output = run([str(exe_path)])

            if py_output != cpp_output:
                raise AssertionError(f"{sample['name']} output mismatch: Python={py_output!r}, C++={cpp_output!r}")
            print(f"{sample['name']}: syntax ok, output matched {py_output!r}")


if __name__ == "__main__":
    main()
