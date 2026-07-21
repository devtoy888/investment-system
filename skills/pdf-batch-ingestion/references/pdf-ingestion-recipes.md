# Chapter Boundary Detection Recipes

Common patterns found in regulatory/standards documents and how to handle them.

## Chinese Government Standards (GB/T, 等保)

```
第1章 总则
第2章 术语和定义
第3章 安全通用要求
```

**Detection:** regex `第[一二三四五六七八九十\d+]章` or `^\d+\.` at start of line

**Strategy:** Split at each `第N章` marker. The chapter title follows on the same or next line.

## Multi-level documents (标准 with sub-sections)

```
1 范围
  1.1 范围描述
  1.2 适用对象
2 规范性引用文件
3 术语和定义
  3.1 安全保护等级
  3.2 定级对象
```

**Detection:** H1 = single digit `^[1-9]\d*\.` at start of line. H2 = `^\s+\d+\.\d+`

**Strategy:** Split only at H1 level. Keep H2 content within the parent H1 page.

## With explicit article numbering

```
第一条 为了...
第二条 本条例适用于...
```

**Detection:** `第[一二三四五六七八九十百千]+条`

**Strategy:** Articles are typically fine-grained. Group related articles (e.g. by section header above them) rather than creating one page per article.

## English Technical Standards

```
1. Scope
2. Normative References
3. Terms and Definitions
  3.1 General
  3.2 Specific terms
4. Security Requirements
  4.1 Management requirements
  4.2 Technical requirements
```

**Detection:** Same pattern as Chinese multi-level — `^\d+\.\s+\w+`

## Extracting images embedded in PDFs

```python
import pymupdf
doc = pymupdf.open("document.pdf")
for page_num, page in enumerate(doc):
    images = page.get_images(full=True)
    for img_idx, img in enumerate(images):
        xref = img[0]
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        ext = base_image["ext"]
        with open(f"page{page_num+1}_img{img_idx+1}.{ext}", "wb") as f:
            f.write(image_bytes)
```

## Validating extraction quality

After extraction, check:
- Headers/footers not mixed into body text
- Table structures preserved (pipe tables in markdown)
- Chinese characters rendered (not ???? or □□□□)
- Section numbers match original TOC
