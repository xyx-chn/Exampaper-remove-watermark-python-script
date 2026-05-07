import fitz  # PyMuPDF
import os
import re

def remove_watermark_pro(input_pdf_path, output_pdf_path):
    """
    终极外科手术版：
    通过直接修改 PDF 底层内容流（Content Stream）精准替换水印字符指令。
    彻底解决水印与正常文字/图表重叠时被误删的问题，100% 保护底层内容。
    """
    try:
        if "（去水印版）" in input_pdf_path:
            return False

        doc = fitz.open(input_pdf_path)
        modified = False

        static_keywords = [
            "Use Responsibly & Respect Copyright"
        ]
        
        # 针对底层字节流的正则表达式（PDF底层字符串通常包裹在圆括号中）
        # 匹配形如: (XJTLU Academic Use Only by 1234567)
        dynamic_pattern_byte = re.compile(rb"\((XJTLU Academic Use Only by \d+)\)")

        for page in doc:
            # --- 策略一：清理独立的文本框/注释层 ---
            annot = page.first_annot
            while annot:
                next_annot = annot.next
                annot_text = str(annot.info.get("content", "")) + str(annot.info.get("subject", ""))
                
                is_match = any(kw[:10] in annot_text for kw in static_keywords)
                if not is_match and re.search(r"XJTLU Academic Use Only by \d+", annot_text):
                    is_match = True
                    
                if is_match:
                    page.delete_annot(annot)
                    modified = True
                annot = next_annot

            # --- 策略二：外科手术级清理（PDF内容流底层替换） ---
            # 1. 整合并清理页面的内容流（将可能零碎的流合并，方便正则匹配）
            page.clean_contents() 
            
            # 2. 获取该页面的底层代码流
            xrefs = page.get_contents()
            if not xrefs:
                continue
            
            for xref in xrefs:
                # 读取字节流代码
                stream = doc.xref_stream(xref)
                if not stream:
                    continue
                    
                original_stream = stream
                
                # 替换固定关键词
                for kw in static_keywords:
                    # 将需要匹配的纯文本转换为底层字节形式，比如 (Use Responsibly & Respect Copyright)
                    target = f"({kw})".encode('utf-8')
                    # 替换为空字符串的绘制指令 ()
                    stream = stream.replace(target, b"()")
                
                # 替换动态学号水印
                # 使用 \1 占位符的做法不需要，直接替换成空括号即可
                stream = dynamic_pattern_byte.sub(b"()", stream)
                
                # 如果底层代码发生了改变，将修改后的流写回 PDF
                if stream != original_stream:
                    doc.update_stream(xref, stream)
                    modified = True

        if modified:
            # garbage=4 和 deflate=True 会深度清理无用的元数据并极致压缩文件
            doc.save(output_pdf_path, garbage=4, deflate=True)
            print(f"✅ 成功完美去除水印并保护底图: {os.path.basename(input_pdf_path)}")
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
    print(f"正在扫描目录: {root_dir} \n启动内容流手术级引擎，全力保护底图与重叠文字...")

    processed_count = 0

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
                
                if remove_watermark_pro(file_path, output_path):
                    processed_count += 1

    print(f"\n✅ 任务处理完毕！共完美处理 {processed_count} 个文件。")

if __name__ == "__main__":
    batch_process()