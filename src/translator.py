import time
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter

class ProTranslator:
    def __init__(self, story_context, llm_engine):
        self.ctx = story_context
        self.llm = llm_engine
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000, 
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " "]
        )

    def translate_large_chapter(self, full_text, progress_callback=None):
        chunks = self.text_splitter.split_text(full_text)
        total_chunks = len(chunks)
        translated_chunks = []
        last_snippet = "" 

        for i, chunk in enumerate(chunks):
            pct = (i + 1) / total_chunks
            
            # Lấy ngữ cảnh RAG và Metadata hiện có
            past_context = self.ctx.get_relevant_history(chunk, k=1)
            
            system_msg = SystemMessage(content=f"Bạn là dịch giả văn học. Nhân vật: {self.ctx.metadata}")
            user_msg = HumanMessage(content=f"Ngữ cảnh: {past_context}\nĐoạn trước: {last_snippet}\nDịch: {chunk}")

            for attempt in range(3):
                try:
                    if progress_callback:
                        progress_callback(pct, f"Đang dịch đoạn {i+1}/{total_chunks}...")
                    
                    response = self.llm.invoke([system_msg, user_msg])
                    content = response.content
                    
                    translated_chunks.append(content)
                    self.ctx.add_to_history(chunk, content) # Lưu vào Vector DB
                    last_snippet = content[-150:]
                    
                    time.sleep(10) # Tránh lỗi 429
                    break
                except Exception as e:
                    if "429" in str(e):
                        time.sleep(30)
                    else:
                        raise e
        
        return "\n\n".join(translated_chunks)