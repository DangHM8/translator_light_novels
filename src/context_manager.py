import json
import os
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
class StoryContext:
    def __init__(self, story_id):
        self.story_id = story_id
        self.path = f"data/{story_id}"
        os.makedirs(self.path, exist_ok=True)
        
        self.metadata_file = f"{self.path}/metadata.json"
        self.db_path = f"{self.path}/chroma_db"
        
        # Load hoặc tạo mới metadata
        self.metadata = self._load_metadata()
        
        # Khởi tạo Vector DB (Sử dụng OpenAI hoặc Gemini Embeddings)
        from langchain_huggingface import HuggingFaceEmbeddings

# Trong hàm __init__ của StoryContext:
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            # Ép buộc nạp trực tiếp vào CPU để tránh lỗi Meta Tensor
            model_kwargs={
                'device': 'cpu',
                'trust_remote_code': True
            },
            encode_kwargs={
                'normalize_embeddings': True
            }
        )
        self.vector_db = Chroma(
            persist_directory=self.db_path, 
            embedding_function=self.embeddings,
            
        )
        self.metadata=self._load_metadata()
    def _load_metadata(self):
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"characters": {}, "relationships": [], "glossary": {}}

    def save_metadata(self):
        """Ghi đè dữ liệu từ RAM xuống file metadata.json"""
        import os
        os.makedirs(os.path.dirname(self.metadata_file), exist_ok=True)
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

    def add_to_history(self, original_text, translated_text):
        """Lưu chương đã dịch vào Vector DB để làm ngữ cảnh cho các chương sau"""
        content = f"Original: {original_text}\nTranslation: {translated_text}"
        self.vector_db.add_texts([content])
        print(f"✅ Đã lưu vào Vector DB thành công.")

    def get_relevant_history(self, current_text, k=1):
        """Tìm lại các đoạn liên quan nhất trong quá khứ"""
        results = self.vector_db.similarity_search(current_text, k=k)
        return "\n---\n".join([res.page_content for res in results])