import json
import time
from pathlib import Path
from pinecone import Pinecone

# --- 配置部分 ---
# 请替换为你的 Pinecone API Key (与 Embed 脚本中使用的一致)
PINECONE_API_KEY = "pcsk_57xrUh_7QgALbLdwRAG5YN7rSsCmum8AdrQ6WW2Uh6PEW6Jt7JL36uEWoUPVpyMMmreBvA"

# 你的 Index 名称 (根据截图)
INDEX_NAME = "teamfight-tactics-knowledges"

# 输入文件路径 (Embed 脚本生成的输出文件)
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
#后期改为批量处理Embed脚本生成的所有文件
INPUT_FILE = PROJECT_ROOT / "datas" / "EmbeddedData" / "opgg_tft_items_embedded.json"

def clean_metadata(metadata):
    """
    清洗元数据：
    1. 将数值型字符串转换为数字 (float/int)，以便进行范围过滤。
    2. 确保所有字段类型符合 Pinecone 要求 (str, int, float, bool, list of str)。
    """
    cleaned = metadata.copy()
    
    # 需要尝试转换为数字的字段列表
    number_fields = ['avg_rank', 'top4_rate', 'win_rate', 'pick_count', 'cost', 'damage', 'attack_speed']
    
    for key, value in cleaned.items():
        # 如果字段在列表中，或者看起来像数字
        if key in number_fields or isinstance(value, str):
            if isinstance(value, str):
                # 移除常见非数字字符
                clean_val = value.replace('#', '').replace('%', '').replace(',', '')
                try:
                    # 尝试转为 float
                    if '.' in clean_val:
                        cleaned[key] = float(clean_val)
                    else:
                        cleaned[key] = int(clean_val)
                except ValueError:
                    # 如果转换失败，保留原字符串
                    pass
    
    return cleaned

def main():
    # 1. 初始化 Pinecone 客户端
    pc = Pinecone(api_key=PINECONE_API_KEY)
    
    # 2. 连接到索引
    print(f"正在连接到索引: {INDEX_NAME}...")
    try:
        index = pc.Index(INDEX_NAME)
        # 简单检查索引状态
        stats = index.describe_index_stats()
        print(f"索引状态: {stats}")
    except Exception as e:
        print(f"连接索引失败: {e}")
        return

    # 3. 读取包含向量的数据文件
    if not INPUT_FILE.exists():
        print(f"错误: 找不到输入文件 {INPUT_FILE}")
        print("请先运行 EmbedItemsScript.py 生成数据。")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    items = data.get("vectors", [])
    total_items = len(items)
    print(f"读取到 {total_items} 条待上传数据。")

    # 4. 准备并批量上传 (Upsert)
    # Pinecone 建议每次 Upsert 的 batch size 在 100-200 左右
    batch_size = 100
    vectors_to_upsert = []

    for i, item in enumerate(items):
        # 检查是否有向量数据
        if not item.get('values'):
            print(f"警告: ID {item['id']} 缺少向量数据，跳过。")
            continue

        # 清洗元数据 (关键步骤，为了支持 Filter)
        cleaned_meta = clean_metadata(item['metadata'])

        # 构建 Pinecone 向量对象
        vector_record = {
            "id": item['id'],
            "values": item['values'],
            "metadata": cleaned_meta
        }
        vectors_to_upsert.append(vector_record)

        # 当达到 batch_size 或最后一条数据时，执行上传
        if len(vectors_to_upsert) >= batch_size or i == total_items - 1:
            try:
                index.upsert(vectors=vectors_to_upsert)
                print(f"已上传批次: {i - len(vectors_to_upsert) + 1} 到 {i} (共 {len(vectors_to_upsert)} 条)")
                vectors_to_upsert = [] # 清空列表
                time.sleep(0.2) # 稍微暂停，避免过于频繁请求
            except Exception as e:
                print(f"上传批次失败: {e}")

    print("\n所有数据上传完成！")
    
    # 5. 验证上传结果
    time.sleep(2) # 等待索引更新
    final_stats = index.describe_index_stats()
    print(f"最终索引统计: {final_stats}")

if __name__ == "__main__":
    main()