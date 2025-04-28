import os

# 要排除的目录（忽略虚拟环境、缓存目录、版本控制目录）
EXCLUDE_DIRS = {'.venv', 'venv', '__pycache__', '.git', '.idea', '.vscode'}

# 要统计的文件后缀
INCLUDE_EXTENSIONS = {'.py'}

def count_lines_of_code(directory):
    total_files = 0
    total_lines = 0
    file_details = []

    for root, dirs, files in os.walk(directory):
        # 过滤掉无关目录
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for file in files:
            if any(file.endswith(ext) for ext in INCLUDE_EXTENSIONS):
                total_files += 1
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        line_count = len(lines)
                        total_lines += line_count
                        relative_path = os.path.relpath(file_path, start=directory)
                        file_details.append((relative_path, line_count))
                except Exception as e:
                    print(f"⚠️  无法读取 {file_path}，原因：{e}")

    return total_files, total_lines, file_details

if __name__ == "__main__":
    project_path = os.path.abspath(os.path.dirname(__file__))  # 默认当前目录
    total_files, total_lines, file_details = count_lines_of_code(project_path)

    print("\n📄 每个文件的行数统计：\n")
    for path, lines in sorted(file_details):
        print(f"{path:60} {lines:>5} lines")

    print("\n✨ 统计结果：")
    print(f"总文件数: {total_files} 个")
    print(f"总代码行数: {total_lines} 行")
