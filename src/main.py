import streamlit as st
import os
import json
import re
import pandas as pd
from context_manager import StoryContext
from translator import ProTranslator
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace

# --- CẤU HÌNH HỆ THỐNG ---
st.set_page_config(page_title="AI Story Translator Pro", layout="wide")

# Khởi tạo Session State để lưu trữ bản dịch bền vững
if 'translated_content' not in st.session_state:
    st.session_state['translated_content'] = ""
if 'last_status' not in st.session_state:
    st.session_state['last_status'] = ""

def initialize_llm():
    """Khởi tạo LLM với các tham số đã tối ưu cho Hugging Face"""
    llm_endpoint = HuggingFaceEndpoint(
        repo_id="Qwen/Qwen2.5-72B-Instruct",
        task="conversational",
        huggingfacehub_api_token="", # Token của bạn
        temperature=0.3,
        top_p=0.9,
        repetition_penalty=1.1,
        max_new_tokens=2048,
    )
    return ChatHuggingFace(llm=llm_endpoint)

def clean_json_response(raw_content):
    """
    Trích xuất JSON mạnh mẽ, hỗ trợ cả Object {} và List [].
    """
    # Tìm kiếm đoạn văn bản bắt đầu bằng { hoặc [ và kết thúc bằng } hoặc ]
    match = re.search(r'([\[\{].*[\]\}])', raw_content, re.DOTALL)
    if match:
        json_str = match.group(1)
        # Loại bỏ các ký tự điều khiển lỗi nếu có
        return json_str.strip()
    return raw_content

def main():
    st.title("📚 AI Story Translator Pro")
    st.caption("Dịch truyện thông minh với bộ nhớ Vector và quản lý nhân vật")

    # --- SIDEBAR: Quản lý danh sách truyện ---
    st.sidebar.header("Quản lý Truyện")
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    existing_stories = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
    
    new_story_name = st.sidebar.text_input("Tên truyện mới:")
    if st.sidebar.button("Tạo mới"):
        if new_story_name:
            folder_name = new_story_name.lower().replace(" ", "_")
            path = os.path.join(data_dir, folder_name)
            os.makedirs(path, exist_ok=True)
            # Khởi tạo file metadata mặc định
            with open(f"{path}/metadata.json", "w", encoding="utf-8") as f:
                json.dump({"characters": {}, "relationships": [], "glossary": {}}, f, ensure_ascii=False, indent=4)
            st.rerun()

    if not existing_stories:
        st.warning("Hãy tạo một truyện mới ở cột bên trái để bắt đầu.")
        return

    selected_story = st.sidebar.selectbox("Chọn truyện để dịch:", existing_stories)
    
    # Khởi tạo tài nguyên
    ctx = StoryContext(selected_story)
    llm = initialize_llm()
    translator = ProTranslator(ctx, llm)

    # --- GIAO DIỆN CHÍNH ---
    tab1, tab2 = st.tabs(["🚀 Dịch Chương Mới", "👥 Nhân vật & Ngữ cảnh"])

    with tab1:
        st.subheader(f"Đang dịch: {selected_story}")
        raw_text = st.text_area("Dán nội dung chương gốc:", height=300)
        
        if st.button("🚀 Bắt đầu dịch"):
            if raw_text:
                progress_bar = st.progress(0, text="Bắt đầu khởi tạo...")
                def update_ui(pct, status_text):
                    progress_bar.progress(pct, text=status_text)

                with st.spinner("Đang xử lý nội dung..."):
                    try:
                        final_result = translator.translate_large_chapter(
                            raw_text, 
                            progress_callback=update_ui
                        )
                        # Lưu vào session_state để không bị mất khi rerun
                        st.session_state['translated_content'] = final_result
                        st.session_state['last_status'] = "✅ Đã dịch xong toàn bộ chương!"
                        st.rerun()
                    except Exception as e:
                        st.error(f"Dừng dịch do lỗi hệ thống: {e}")
            else:
                st.warning("Vui lòng nhập văn bản cần dịch.")

        # Hiển thị kết quả dịch (Luôn hiện nếu có dữ liệu trong session_state)
        if st.session_state['translated_content']:
            st.divider()
            st.success(st.session_state['last_status'])
            st.subheader("Bản dịch hiện tại:")
            st.text_area("Kết quả:", value=st.session_state['translated_content'], height=500)

# --- TRONG FILE main.py ---

    with tab2:
        st.subheader("Dữ liệu trong Vector Database (RAG)")
        # Hiển thị số lượng bản ghi thực tế trong database
        try:
            count = ctx.vector_db._collection.count()
            st.write(f"Tổng số đoạn văn đã lưu: **{count}**")
        except:
            st.write("Chưa có dữ liệu trong DB.")

        st.subheader("👥 Quản lý Thực thể & Xưng hô")
        
        # 1. Hiển thị bảng Nhân vật với tham số width mới (2026)
        char_data = ctx.metadata.get("characters", [])
        df_char = pd.DataFrame(char_data)
        if df_char.empty:
            df_char = pd.DataFrame(columns=["id", "name", "gender", "role", "description"])

        edited_char = st.data_editor(
            df_char, 
            num_rows="dynamic", 
            width='stretch', # Đã cập nhật theo yêu cầu năm 2026
            key="edit_char"
        )

        # # 2. Hiển thị bảng Quan hệ
        # rel_data = ctx.metadata.get("relationships", [])
        # df_rel = pd.DataFrame(rel_data)
        # if df_rel.empty:
        #     df_rel = pd.DataFrame(columns=["p1_id", "p2_id", "p1_calls_p2", "p2_calls_p1"])

        # edited_rel = st.data_editor(
        #     df_rel, 
        #     num_rows="dynamic", 
        #     width='stretch', # Đã cập nhật
        #     key="edit_rel"
        # )

        # --- TRONG FILE main.py (Tab 2) ---

        if st.button("🔍 Quét nhân vật từ Bộ nhớ (RAG)"):
            with st.spinner("AI đang phân tích dữ liệu..."):
                # Lấy ngữ cảnh tiếng Việt
                rag_context = ctx.get_relevant_history("nhân vật và tên riêng", k=5, clean_vietnamese=True)
                
                if not rag_context:
                    st.warning("Không tìm thấy dữ liệu trong bộ nhớ RAG.")
                else:
                    prompt = f"""Bạn là máy trích xuất dữ liệu. 
        Trích xuất danh sách nhân vật từ văn bản sau dưới dạng JSON LIST.
        Mẫu: [{{"id": "char_01", "name": "Tên", "gender": "Nam/Nữ", "role": "Chính", "description": "..."}}]
        Chỉ trả về JSON, không giải thích.

        VĂN BẢN:
        {rag_context}"""
                    
                    res = llm.invoke(prompt)
                    raw_content = res.content if hasattr(res, 'content') else str(res)
                    
                    try:
                        # 1. Làm sạch và Parse JSON từ AI
                        json_data = clean_json_response(raw_content)
                        new_found_chars = json.loads(json_data)

                        # 2. ĐỒNG BỘ: Lấy dữ liệu đang hiện trên bảng (editor_char) thay vì lấy từ ctx.metadata cũ
                        # Streamlit lưu dữ liệu đang sửa trong st.session_state["edit_char"]
                        current_chars = edited_char.to_dict('records') 
                        current_ids = [str(c.get('id')).lower() for c in current_chars]

                        added_count = 0
                        if isinstance(new_found_chars, list):
                            for nc in new_found_chars:
                                nc_id = str(nc.get('id')).lower()
                                # Kiểm tra nếu ID hoặc Tên chưa tồn tại thì mới thêm
                                if nc_id not in current_ids:
                                    current_chars.append(nc)
                                    current_ids.append(nc_id)
                                    added_count += 1
                        
                        # 3. Cập nhật ngược lại vào context và lưu file
                        ctx.metadata["characters"] = current_chars
                        ctx.save_metadata()

                        if added_count > 0:
                            st.success(f"✅ Đã thêm {added_count} nhân vật mới vào bảng!")
                            st.rerun()
                        else:
                            st.info("Bảng đã đầy đủ thông tin, không tìm thấy nhân vật nào mới.")
                            
                    except Exception as e:
                        st.error(f"Lỗi: {e}")
                        st.expander("Dữ liệu thô từ AI").code(raw_content)

    # with tab3:
    #     st.subheader("Dữ liệu trong Vector Database (RAG)")
    #     # Hiển thị số lượng bản ghi thực tế trong database
    #     try:
    #         count = ctx.vector_db._collection.count()
    #         st.write(f"Tổng số đoạn văn đã lưu: **{count}**")
    #     except:
    #         st.write("Chưa có dữ liệu trong DB.")

    #     search_query = st.text_input("Tìm kiếm lịch sử tình tiết trong bộ nhớ:")
    #     if search_query:
    #         relevant = ctx.get_relevant_history(search_query)
    #         if relevant:
    #             st.info(f"Kết quả tìm thấy cho: '{search_query}'")
    #             st.write(relevant)
    #         else:
    #             st.warning("Không tìm thấy ngữ cảnh liên quan.")

if __name__ == "__main__":
    main()