import json
import time
import os
from pathlib import Path
from pinecone import Pinecone
from dotenv import load_dotenv

# --- 配置部分 ---
# 优先计算路径以加载 .env
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
load_dotenv(PROJECT_ROOT / ".env")

# 从环境变量获取 API Key
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# 使用的模型，必须是 Pinecone 支持的模型
MODEL_NAME = "llama-text-embed-v2" 

# 输入文件和输出文件路径
# 暂时测试一个文件，后续为运行datas文件夹下所有数据文件
INPUT_FILE = PROJECT_ROOT / "datas" / "OriginData" / "opgg_tft_items.json"
OUTPUT_FILE = PROJECT_ROOT / "datas" / "EmbeddedData" / "opgg_tft_items_embedded.json"



def main():
    # 1. 初始化 Pinecone 客户端
    pc = Pinecone(api_key=PINECONE_API_KEY)
    print(f"正在使用模型: {MODEL_NAME}")

    # 2. 读取原始 JSON 文件
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"错误: 找不到文件 {INPUT_FILE}")
        return

    items = data.get("vectors", [])
    total_items = len(items)
    print(f"共读取到 {total_items} 条数据，开始生成 Embedding...")

    # 3. 批量处理 (为了提高效率和避免速率限制)
    batch_size = 10  # 每次处理 10 条
    
    for i in range(0, total_items, batch_size):
        batch_items = items[i : i + batch_size]
        
        # 提取当前批次的文本列表
        texts_to_embed = [item['metadata']['text'] for item in batch_items]
        
        try:
            # 调用 Pinecone Inference API
            # input_type="passage" 表示我们要存储的是文档段落
            embeddings = pc.inference.embed(
                model=MODEL_NAME,
                inputs=texts_to_embed,
                parameters={"input_type": "passage"}
            )
            
            # 将生成的向量填回对应的 item
            for j, embedding_obj in enumerate(embeddings):
                # embedding_obj['values'] 是向量数组
                batch_items[j]['values'] = embedding_obj['values']
                
            print(f"进度: {min(i + batch_size, total_items)}/{total_items} 完成")
            
            # 简单的速率限制保护，避免触发 API 限制
            time.sleep(0.5) 

        except Exception as e:
            print(f"批次处理出错 (索引 {i} - {i+batch_size}): {e}")
            # 可以在这里选择是否跳过或停止

    # 4. 保存结果到新文件
    # print(f"INPUT_FILE: {INPUT_FILE}")
    # print(f"OUTPUT_FIL: {OUTPUT_FILE}")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"INPUT_FILE: {INPUT_FILE}")
    print(f"\n处理完成！已保存至 {OUTPUT_FILE}")
    print("现在你可以使用这个新文件进行 Upsert 操作了。")

if __name__ == "__main__":
    main()