import os

def make_markdown(image_folder, text_folder, basename, md_filename):
    """
    将图像文件和文本文件合并为一个 Markdown 文件。
    
    参数:
    - image_folder: 存放图像文件的目录
    - text_folder: 存放文本文件的目录
    - basename: 图像和文本文件的共同前缀（如 "block_"）
    - md_filename: 输出的 Markdown 文件名
    """
    # 获取所有以 basename 开头并按数字排序的图像和文本文件
    image_files = sorted(
        f for f in os.listdir(image_folder) if f.startswith(basename) and f.endswith('.png')
    )
    text_files = sorted(
        f for f in os.listdir(text_folder) if f.startswith(basename) and f.endswith('.txt')
    )

    # 检查图像和文本文件数量是否一致
    if len(image_files) != len(text_files):
        print("警告：图像文件和文本文件数量不一致！请检查目录内容。")
        return

    # 创建并写入 Markdown 文件
    with open(md_filename, 'w', encoding='utf-8') as md_file:
        for img_file, txt_file in zip(image_files, text_files):
            img_path = os.path.join(image_folder, img_file)
            txt_path = os.path.join(text_folder, txt_file)

            # 读取文本文件内容
            with open(txt_path, 'r', encoding='utf-8') as f:
                text_content = f.read().strip()

            # 写入 Markdown 文件
            md_file.write(f'### {img_file}\n\n')
            md_file.write(f'![{img_file}]({img_path})\n\n')
            md_file.write(f'**文本内容**:\n\n{text_content}\n\n---\n\n')

    print(f"Markdown 文件已生成: {md_filename}")

def main():
    image_folder = 'output_split_1'  # 图像文件目录
    text_folder = 'ocr_output_1'     # 文本文件目录
    basename = 'block_'              # 文件的共同前缀
    md_filename = 'output.md'        # 输出的 Markdown 文件

    make_markdown(image_folder, text_folder, basename, md_filename)

if __name__ == '__main__':
    main()
