import os
import subprocess
import time

def delete_pycache_files():
    """删除 __pycache__ 目录下的所有文件"""
    pycache_dir = os.path.join(os.getcwd(), "__pycache__")
    if os.path.exists(pycache_dir):
        for file_name in os.listdir(pycache_dir):
            file_path = os.path.join(pycache_dir, file_name)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"已删除: {file_path}")
            except Exception as e:
                print(f"删除文件失败: {file_path}, 错误: {e}")

def execute_py_files():
    """遍历当前目录下的所有 .py 文件并执行"""
    for file_name in os.listdir(os.getcwd()):
        if file_name.endswith(".py") and file_name != os.path.basename(__file__):
            print(f"正在执行: {file_name}")
            subprocess.Popen(["python", "-m", file_name[:-3]])  # 去掉 .py 后缀

def rename_pyc_files():
    """进入 __pycache__ 目录，将所有 .pyc 文件重命名为 .py"""
    pycache_dir = os.path.join(os.getcwd(), "__pycache__")
    if os.path.exists(pycache_dir):
        os.chdir(pycache_dir)  # 进入 __pycache__ 目录
        for file_name in os.listdir(pycache_dir):
            if file_name.endswith(".pyc"):
                # 提取文件名（去掉 .cpython-<版本号> 部分）
                new_name = file_name.split(".")[0] + ".py"
                try:
                    os.rename(file_name, new_name)
                    print(f"已重命名: {file_name} -> {new_name}")
                except Exception as e:
                    print(f"重命名文件失败: {file_name}, 错误: {e}")
        os.chdir("..")  # 返回上一级目录

if __name__ == "__main__":
    # 删除 __pycache__ 目录下的所有文件
    delete_pycache_files()

    # 执行当前目录下的所有 .py 文件
    execute_py_files()

    # 等待所有 .py 文件执行完成
    time.sleep(5)

    # 重命名 __pycache__ 目录下的所有 .pyc 文件
    rename_pyc_files()

    # 暂停，以便查看输出结果
    input("按 Enter 键退出...")
