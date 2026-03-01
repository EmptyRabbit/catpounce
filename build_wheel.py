"""
构建隐藏源代码的 wheel 包
使用方法: python build.py
"""
import os
import sys
import subprocess
import zipfile
import tempfile
import shutil
from pathlib import Path


def remove_py_files_from_wheel(wheel_path):
    """从 wheel 文件中移除 .py 源文件，只保留 .pyc 文件"""
    print(f"\n处理 wheel 文件: {wheel_path}")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        extract_dir = os.path.join(temp_dir, 'extracted')
        
        # 解压 wheel
        with zipfile.ZipFile(wheel_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        removed_count = 0
        files_to_remove = []
        
        # 第一步：编译所有 Python 文件
        print("  编译 Python 文件...")
        import py_compile
        import compileall
        
        # 使用 compileall 编译所有 Python 文件
        compileall.compile_dir(extract_dir, force=True, quiet=1)
        
        # 第二步：遍历所有文件，收集需要移除的 .py 文件
        for root, dirs, files in os.walk(extract_dir):
            # 跳过 __pycache__ 目录
            dirs[:] = [d for d in dirs if d != '__pycache__']
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    
                    # 保留所有 __init__.py 文件，以便 IDE 和类型检查工具能正常工作
                    if file == '__init__.py':
                        continue
                    
                    # 查找对应的 .pyc 文件
                    pyc_path = file_path + 'c'
                    cache_dir = os.path.join(root, '__pycache__')
                    
                    # 检查是否有对应的 .pyc 文件
                    has_pyc = False
                    if os.path.exists(pyc_path):
                        has_pyc = True
                    elif os.path.exists(cache_dir):
                        # 检查 __pycache__ 中是否有对应的 .pyc 文件
                        cache_files = os.listdir(cache_dir)
                        base_name = file.replace('.py', '')
                        for cf in cache_files:
                            if cf.startswith(base_name) and cf.endswith('.pyc'):
                                has_pyc = True
                                # 将 .pyc 文件移到正确位置（与 .py 文件同级）
                                src_pyc = os.path.join(cache_dir, cf)
                                dst_pyc = pyc_path
                                if not os.path.exists(dst_pyc):
                                    shutil.copy2(src_pyc, dst_pyc)
                                break
                    
                    if has_pyc:
                        files_to_remove.append(file_path)
                    else:
                        # 如果还没有 .pyc，尝试直接编译
                        try:
                            py_compile.compile(file_path, doraise=True)
                            if os.path.exists(file_path + 'c'):
                                files_to_remove.append(file_path)
                        except Exception as e:
                            print(f"  警告: 无法编译 {os.path.relpath(file_path, extract_dir)}: {e}")
        
        # 第三步：移除收集到的 .py 文件
        print(f"  准备移除 {len(files_to_remove)} 个源文件...")
        for file_path in files_to_remove:
            try:
                os.remove(file_path)
                removed_count += 1
                if removed_count <= 10:  # 只显示前10个
                    print(f"  移除: {os.path.relpath(file_path, extract_dir)}")
            except Exception as e:
                print(f"  警告: 无法移除 {file_path}: {e}")
        
        if removed_count > 10:
            print(f"  ... 还有 {removed_count - 10} 个文件已移除")
        
        if removed_count > 0:
            # 重新打包 wheel
            new_wheel_path = os.path.join(temp_dir, os.path.basename(wheel_path))
            with zipfile.ZipFile(new_wheel_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                for root, dirs, files in os.walk(extract_dir):
                    # 跳过 __pycache__ 目录
                    dirs[:] = [d for d in dirs if d != '__pycache__']
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_name = os.path.relpath(file_path, extract_dir)
                        zip_ref.write(file_path, arc_name)
            
            # 替换原文件
            shutil.move(new_wheel_path, wheel_path)
            print(f"[OK] 已移除 {removed_count} 个源文件")
        else:
            print("未找到需要移除的源文件（可能已经处理过）")


def main():
    """主函数"""
    print("=" * 60)
    print("构建 pounce wheel 包（隐藏源代码）")
    print("=" * 60)
    
    # 清理旧的构建文件
    print("\n1. 清理旧的构建文件...")
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  已删除: {dir_name}")
    
    # 清理 .egg-info 目录
    for egg_info in Path('.').glob('*.egg-info'):
        if egg_info.is_dir():
            shutil.rmtree(egg_info)
            print(f"  已删除: {egg_info}")
    
    # 安装构建工具
    print("\n2. 安装构建工具...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'build', 'wheel'], 
                   check=True)
    
    # 构建 wheel
    print("\n3. 构建 wheel 包...")
    result = subprocess.run([sys.executable, '-m', 'build', '--wheel'], 
                           capture_output=True, text=True)
    if result.returncode != 0:
        print("\n构建失败!")
        return
    
    # 查找生成的 wheel 文件
    dist_dir = Path('dist')
    wheel_files = list(dist_dir.glob('*.whl'))
    
    if not wheel_files:
        print("错误: 未找到生成的 wheel 文件")
        return
    
    # 处理每个 wheel 文件
    print("\n4. 处理 wheel 文件（移除源代码）...")
    for wheel_file in wheel_files:
        remove_py_files_from_wheel(str(wheel_file))
    
    # 输出结果
    print("\n" + "=" * 60)
    print("构建完成！")
    print("=" * 60)
    for wheel_file in wheel_files:
        file_size = wheel_file.stat().st_size / 1024 / 1024  # MB
        print(f"\n[OK] {wheel_file.name} ({file_size:.2f} MB)")
        print(f"  安装命令: pip install {wheel_file}")
        print(f"  可在 Mac 和 Windows 上使用")


if __name__ == '__main__':
    main()

