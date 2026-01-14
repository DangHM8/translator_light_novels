# AI Story Translator Pro 📚

**AI Story Translator Pro** là một công cụ dịch truyện thông minh sử dụng sức mạnh của các mô hình ngôn ngữ lớn (LLM) kết hợp với công nghệ **RAG (Retrieval-Augmented Generation)** để đảm bảo tính nhất quán về ngữ cảnh, nhân vật và xưng hô trong suốt bộ truyện.

## 🌟 Tính năng nổi bật

- **Dịch thuật thông minh (RAG):** Sử dụng Vector Database (ChromaDB) để lưu trữ và truy xuất ngữ cảnh từ các chương trước, giúp AI hiểu được các tình tiết đã xảy ra.
- **Quản lý nhân vật & Thực thể:** Hệ thống quản lý danh sách nhân vật, giới tính và vai trò chuyên sâu.
- **Tự động trích xuất nhân vật:** Sử dụng AI để tự động nhận diện và cập nhật nhân vật mới từ nội dung truyện.
- **Quy tắc xưng hô linh hoạt:** Thiết lập quy tắc xưng hô giữa các nhân vật (ví dụ: Anh - Em, Ta - Ngươi) để bản dịch thuần Việt và tự nhiên hơn.
- **Xử lý chương lớn:** Tự động chia nhỏ các chương dài để dịch mà vẫn duy trì được mạch văn nhờ bộ nhớ đệm (context window).
- **Giao diện Streamlit:** Giao diện web trực quan, dễ sử dụng, theo dõi tiến độ dịch theo thời gian thực.

## 🛠 Công nghệ sử dụng

- **Ngôn ngữ:** Python
- **Giao diện:** [Streamlit](https://streamlit.io/)
- **LLM Framework:** [LangChain](https://www.langchain.com/)
- **Mô hình dịch:** Qwen 2.5 72B Instruct (via Hugging Face Endpoint)
- **Vector Database:** [ChromaDB](https://www.trychroma.com/)
- **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2` (Hugging Face)

## 📁 Cấu trúc thư mục

```text
translator_light_novels/
├── src/
│   ├── main.py              # File chính chạy giao diện Streamlit
│   ├── translator.py        # Logic dịch thuật và xử lý logic LLM
│   └── context_manager.py   # Quản lý Vector DB và Metadata của truyện
├── data/                    # Nơi lưu trữ dữ liệu các bộ truyện
│   └── [tên_truyện]/
│       ├── metadata.json    # Thông tin nhân vật, xưng hô
│       └── chroma_db/       # Cơ sở dữ liệu vector cho bộ truyện
└── requirements.txt         # Danh sách thư viện cần thiết
```

## 🚀 Hướng dẫn cài đặt

1. **Clone repository:**

   ```bash
   git clone https://github.com/DangHM8/translator_light_novels.git
   cd translator_light_novels
   ```

2. **Cài đặt thư viện:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Cấu hình Token:**

   - Truy cập vào [Hugging Face Settings -> Tokens](https://huggingface.co/settings/tokens).
   - Tạo một Token mới (quyền `Read`).
   - Mở file `src/main.py`.
   - Tìm đến hàm `initialize_llm` và dán Token của bạn vào giá trị `huggingfacehub_api_token`:
     ```python
     huggingfacehub_api_token="hf_your_token_here"
     ```

4. **Chạy ứng dụng:**
   ```bash
   streamlit run src/main.py
   ```

## 📝 Cách sử dụng

1. **Tạo truyện mới:** Nhập tên truyện ở Sidebar và nhấn "Tạo mới".
2. **Cài đặt nhân vật:** Chuyển sang tab "Nhân vật & Ngữ cảnh" để thêm thông tin nhân vật hoặc sử dụng nút "Quét nhân vật từ Bộ nhớ" để AI tự tìm.
3. **Dịch chương:** Dán nội dung chương cần dịch vào tab "Dịch Chương Mới" và nhấn "Bắt đầu dịch".
4. **Theo dõi:** Tiến trình dịch sẽ được hiển thị trên thanh Progress Bar. Sau khi hoàn tất, bản dịch sẽ tự động được lưu vào bộ nhớ RAG để phục vụ cho các chương sau.

## ⚠️ Lưu ý

- Dự án mặc định sử dụng CPU cho phần Embeddings để tránh một số lỗi tương thích.
- Có cơ chế `time.sleep` để tránh lỗi giới hạn (429) khi gọi API Hugging Face.

---

Phát triển bởi [DangHM](https://github.com/DangHM8) 🚀
