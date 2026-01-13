import json
import os

def upgrade_metadata_file(story_name):
    path = f"data/{story_name}/metadata.json"
    
    if not os.path.exists(path):
        print(f"❌ Không tìm thấy file tại: {path}")
        return

    with open(path, 'r', encoding='utf-8') as f:
        old_data = json.load(f)

    # Lấy danh sách nhân vật hiện tại
    # Hỗ trợ cả định dạng cũ (dict đơn giản) và định dạng mới
    old_chars = old_data.get("characters", {})
    if isinstance(next(iter(old_chars.values())), str):
        # Chuyển đổi từ định dạng cũ sang định dạng chi tiết
        new_chars = {
            name: {
                "description": desc,
                "gender": "unknown", 
                "role": "supporting"
            } for name, desc in old_chars.items()
        }
    else:
        new_chars = old_chars

    # Tạo các cặp quan hệ tự động
    names = list(new_chars.keys())
    new_relationships = old_data.get("relationships", [])
    
    # Kiểm tra xem cặp nào chưa có trong danh sách thì thêm vào
    existing_pairs = [set(r["pair"]) for r in new_relationships]
    
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            char_a, char_b = names[i], names[j]
            if set([char_a, char_b]) not in existing_pairs:
                new_relationships.append({
                    "pair": [char_a, char_b],
                    "context": "Chưa xác định",
                    f"{char_a}_calls_{char_b}": "",
                    f"{char_b}_calls_{char_a}": ""
                })

    upgraded_data = {
        "characters": new_chars,
        "relationships": new_relationships,
        "glossary": old_data.get("glossary", {})
    }

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(upgraded_data, f, ensure_ascii=False, indent=4)
    print(f"✅ Đã nâng cấp thành công Metadata cho: {story_name}")

if __name__ == "__main__":
    story = input("Nhập tên folder truyện cần nâng cấp: ")
    upgrade_metadata_file(story)