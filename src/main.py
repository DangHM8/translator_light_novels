import streamlit as st
import os
import json
import re
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
    """Trích xuất JSON từ phản hồi của AI để tránh lỗi ký tự thừa"""
    match = re.search(r'\{.*\}', raw_content, re.DOTALL)
    return match.group(0) if match else raw_content

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
    tab1, tab2, tab3 = st.tabs(["🚀 Dịch Chương Mới", "👥 Nhân vật & Ngữ cảnh", "📜 Lịch sử RAG"])

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

    with tab2:
        st.subheader("Quản lý ngữ cảnh nhân vật")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write("**Metadata JSON (Chỉnh sửa trực tiếp)**")
            current_metadata = st.text_area("Cấu trúc Metadata:", 
                                            value=json.dumps(ctx.metadata, ensure_ascii=False, indent=4), 
                                            height=400)
            if st.button("💾 Lưu Metadata"):
                try:
                    ctx.metadata = json.loads(current_metadata)
                    ctx.save_metadata()
                    st.success("Đã lưu metadata vào ổ cứng!")
                except Exception as e:
                    st.error(f"Lỗi định dạng JSON: {e}")

        with col2:
            st.info("**Công cụ hỗ trợ:**")
            
            # NÚT CẬP NHẬT METADATA TỪ BẢN DỊCH
            if st.button("🔍 Quét nhân vật từ bản dịch"):
                if st.session_state['translated_content']:
                    with st.spinner("AI đang phân tích bản dịch..."):
                        try:
                            # Lấy 2000 ký tự đầu để AI trích xuất (tiết kiệm token)
                            sample = st.session_state['translated_content'][:2000]
                            prompt = f"Dựa vào đoạn dịch sau, hãy liệt kê các nhân vật và xưng hô của họ dưới dạng JSON {{'tên': 'xưng hô'}}. Chỉ trả về JSON: {sample}"
                            
                            res = llm.invoke(prompt)
                            raw_content = res.content if hasattr(res, 'content') else str(res)
                            
                            # Parse JSON từ AI
                            new_chars = json.loads(clean_json_response(raw_content))
                            
                            # Cập nhật vào metadata hiện tại
                            if "characters" not in ctx.metadata:
                                ctx.metadata["characters"] = {}
                            
                            ctx.metadata["characters"].update(new_chars)
                            ctx.save_metadata()
                            st.success("Đã tìm thấy và cập nhật nhân vật mới!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Không thể trích xuất: {e}")
                else:
                    st.warning("Bạn cần dịch một chương trước khi quét nhân vật.")

            st.write("---")
            st.write("- `characters`: Tên và đại từ (tôi/hắn/nàng).")
            st.write("- `relationships`: Cách xưng hô giữa các cặp nhân vật.")
            st.write("- `glossary`: Thuật ngữ đặc biệt của truyện.")

    with tab3:
        st.subheader("Dữ liệu trong Vector Database (RAG)")
        # Hiển thị số lượng bản ghi thực tế trong database
        try:
            count = ctx.vector_db._collection.count()
            st.write(f"Tổng số đoạn văn đã lưu: **{count}**")
        except:
            st.write("Chưa có dữ liệu trong DB.")

        search_query = st.text_input("Tìm kiếm lịch sử tình tiết trong bộ nhớ:")
        if search_query:
            relevant = ctx.get_relevant_history(search_query)
            if relevant:
                st.info(f"Kết quả tìm thấy cho: '{search_query}'")
                st.write(relevant)
            else:
                st.warning("Không tìm thấy ngữ cảnh liên quan.")

if __name__ == "__main__":
    main()