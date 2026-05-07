# XJTLU-remove-watermark-python-script

这是一个基于 Python 和 PyMuPDF 构建的自动化脚本，专为精准、无损地去除西交利物浦大学（XJTLU）PDF 课件中的学术水印而设计。打包好的即点即用exe在release里。

本版本为**动态正则升级版**，无需手动输入学号，即可自动识别并剥离全网学号的倾斜水印，同时完美保护文档的原始排版、图片和底层矢量图。

---

## ✨ 核心特性

*   **全学号自动适配 (Dynamic ID Matching)**：内置正则表达式（RegEx），自动抓取如 `XJTLU Academic Use Only by [学号]` 的动态文本，适用于任何学生的课件。
*   **绝对无损处理 (Lossless Redaction)**：采用“先提取后定位”策略，利用 PyMuPDF 的 `quads=True` 精准获取贴合倾斜文字的细长四边形，避免产生覆盖全页的遮罩。
*   **图文分离保护 (Image & Graphics Protection)**：在执行文本注销时，严格应用 `images=0` 参数，100% 避免误删插图、表格边框和矢量图。
*   **批量自动化 (Batch Processing)**：自动扫描当前目录及一级子目录下的所有 `.pdf` 文件，跳过已处理文件，并安全输出带有 `（去水印版）` 后缀的新文件。
*   **深层注释清理 (Annotation Clearing)**：不仅清理写死在页面内的文本，还能直接剥离悬浮在顶层的 Annotation 注释层水印。

---

## 🛠️ 环境依赖

运行此脚本需要 Python 3.x 环境，并安装 `PyMuPDF` 库。

请打开终端或命令行，运行以下命令安装依赖：

```bash
pip install PyMuPDF
```

*(注意：在代码中导入时使用的是 `import fitz`，这是 PyMuPDF 的标准调用包名。)*

---

## 🚀 使用指南

1.  **下载脚本**：将代码保存为 `remove_watermark.py`。
2.  **放置文件**：将 `remove_watermark.py` 放入包含你需要处理的 PDF 文件的根目录中（支持读取一级子目录下的 PDF）。
3.  **运行脚本**：
    在终端中导航到该目录，并执行：
    ```bash
    python remove_watermark.py
    ```
4.  **查看结果**：脚本会自动运行并在控制台输出进度。处理完成后，你将在原 PDF 同级目录下看到名为 `原文件名（去水印版）.pdf` 的干净文件。

---

## 🧠 技术原理解析

由于 PyMuPDF 的原生底层函数不支持直接用正则表达式来获取倾斜文本的四边形坐标，本脚本采用了一种混合策略：
1.  **预读提取**：使用 `page.get_text("text")` 快速读取整页文字。
2.  **正则匹配**：利用 `re.compile` 找出当前页中真实存在的具体学号水印字符串。
3.  **精准打击**：将提取出的具体字符串交由 `page.search_for(keyword, quads=True)` 获取倾斜矩形。
4.  **透明擦除**：通过 `page.add_redact_annot` 创建透明遮罩，并调用 `apply_redactions(images=0)` 彻底清除底层像素。

---

## ⚠️ 免责声明 (Disclaimer)

**学术诚信与版权说明**：
本脚本仅供个人优化阅读体验和本地笔记整理使用。请严格遵守学校的学术诚信政策及版权声明：
*   **Use Responsibly & Respect Copyright.**
*   请勿将去除水印后的课件用于任何商业用途或未经授权的公开传播。
*   使用者需对使用本脚本产生的任何后果自行承担全部责任。
```
