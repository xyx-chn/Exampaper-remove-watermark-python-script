import fitz  # PyMuPDF
import os
import re

def remove_watermark_pro(input_pdf_path, output_pdf_path):
    """
    终极版：精准剥离倾斜文本水印，支持自动识别所有学号，绝对不伤及底图和正常内容
    """
    try:
        if "（去水印版）" in input_pdf_path:
            return False

        doc = fitz.open(input_pdf_path)
        modified = False

        # 1. 定义固定的普通水印关键词
        static_keywords = [
            "Use Responsibly & Respect Copyright"
        ]
        
        # 2. 定义匹配学号水印的正则表达式（\d+ 代表匹配一个或多个数字）
        dynamic_pattern = re.compile(r"XJTLU Academic Use Only by \d+")

        for page in doc:
            # 动态提取当前页的文本，查找实际存在的学号水印内容
            page_text = page.get_text("text")
            # 找到当前页符合该格式的具体字符串（例如找到了 "...by 9876543"）
            dynamic_matches = list(set(dynamic_pattern.findall(page_text)))
            
            # 将固定关键词和当前页提取到的动态水印合并，作为要清理的目标列表
            current_page_keywords = static_keywords + dynamic_matches

            # --- 策略一：针对“独立文本框/注释层” ---
            annot = page.first_annot
            while annot:
                next_annot = annot.next
                annot_text = str(annot.info.get("content", "")) + str(annot.info.get("subject", ""))
                
                # 判断：如果包含固定关键词前缀，或者匹配了学号正则表达式
                is_match = any(kw[:10] in annot_text for kw in static_keywords)
                if not is_match and dynamic_pattern.search(annot_text):
                    is_match = True
                    
                if is_match:
                    page.delete_annot(annot)
                    modified = True
                annot = next_annot

            # --- 策略二：针对“写死在页面里的倾斜文字” ---
            for keyword in current_page_keywords:
                # 关键修复 1：继续使用 quads=True 获取紧紧贴合倾斜文字的细长四边形
                text_quads = page.search_for(keyword, quads=True)
                
                if text_quads:
                    modified = True
                    for quad in text_quads:
                        # cross_out=False 防止画红叉，fill=None 保持透明
                        page.add_redact_annot(quad, cross_out=False)
        
            # 关键修复 2：应用注销时，保护图片和底层矢量图！
            if modified:
                page.apply_redactions(images=0)

        if modified:
            # 保存新文件
            doc.save(output_pdf_path, garbage=4, deflate=True)
            print(f"✅ 成功去除水印: {os.path.basename(input_pdf_path)}")
            doc.close()
            return True
        else:
            doc.close()
            return False
            
    except Exception as e:
        print(f"❌ 处理文件 {input_pdf_path} 时出错: {e}")
        if 'doc' in locals() and doc:
            doc.close()
        return False

def batch_process():
    root_dir = os.getcwd()
    print(f"正在扫描目录: {root_dir} \n启动高级引擎，已支持自动适配全网学号，保护图片和底层布局...")

    processed_count = 0

    # 遍历当前目录及一级子目录
    for root, dirs, files in os.walk(root_dir):
        depth = root[len(root_dir):].count(os.sep)
        if depth > 1:
            continue

        for file in files:
            if file.lower().endswith(".pdf"):
                file_path = os.path.join(root, file)
                
                base_name, ext = os.path.splitext(file)
                output_filename = f"{base_name}（去水印版）{ext}"
                output_path = os.path.join(root, output_filename)
                
                # 函数签名已更新，不再需要传入写死的 keywords
                if remove_watermark_pro(file_path, output_path):
                    processed_count += 1

    print(f"\n✅ 任务处理完毕！共完美处理 {processed_count} 个文件。")

if __name__ == "__main__":
    batch_process()