# -*- coding: utf-8 -*-

"""
RAG API 服务（使用 Flask）
"""

import os
from typing import List, Dict
from flask import Flask, request, jsonify
from flask_cors import CORS
import chromadb
import ollama

app = Flask(__name__)
CORS(app)  # 启用CORS支持

# 全局变量
collection = None

# 全局变量
collection = None

def load_and_chunk_documents(file_path: str, chunk_size: int = 250, chunk_overlap: int = 30) -> List[Dict]:
    """加载文档并分块"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return []

    chunks = []
    start = 0

    while start < len(content):
        end = min(start + chunk_size, len(content))
        chunk_text = content[start:end].strip()

        if chunk_text:
            chunks.append({
                "content": chunk_text,
                "index": len(chunks)
            })

        start += chunk_size - chunk_overlap

    return chunks

def create_vectorstore(chunks: List[Dict], persist_dir: str = "./chroma_rag_db"):
    """创建向量库"""
    if not chunks:
        return None

    client = chromadb.PersistentClient(path=persist_dir)

    collection_name = "rag_documents"
    try:
        client.delete_collection(name=collection_name)
    except:
        pass

    collection = client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )

    for i, chunk in enumerate(chunks):
        try:
            response = ollama.embeddings(
                model='qwen2:0.5b',
                prompt=chunk["content"]
            )
            
            embedding = response['embedding']
            
            collection.add(
                ids=[f"doc_{chunk['index']}"],
                embeddings=[embedding],
                metadatas=[{"chunk_index": chunk["index"]}],
                documents=[chunk["content"]]
            )
        except Exception as e:
            print(f"块 {i} 处理异常：{str(e)}")

    return collection

def retrieve_documents(collection, query: str, k: int = 3) -> List[Dict]:
    """检索文档"""
    if collection is None:
        return []

    try:
        response = ollama.embeddings(
            model='qwen2:0.5b',
            prompt=query
        )
        query_embedding = response['embedding']
    except Exception as e:
        return []

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(k, 10),
        include=["documents", "metadatas", "distances"]
    )

    retrieved = []
    for i, (doc, distance) in enumerate(zip(results['documents'][0], results['distances'][0])):
        similarity_score = 1.0 / (1.0 + distance)

        retrieved.append({
            "content": doc,
            "similarity": similarity_score,
            "distance": distance
        })

    return retrieved

def generate_answer(query: str, retrieved_docs: List[Dict]) -> str:
    """生成回答"""
    reference_text = ""
    if retrieved_docs:
        reference_text = "\n\n".join([
            f"[参考 {i + 1}]（相似度：{doc['similarity']:.2%}）\n{doc['content']}"
            for i, doc in enumerate(retrieved_docs)
        ])
    else:
        reference_text = "（未找到相关参考资料）"

    system_prompt = """你是一个企业知识助手。你的任务是根据提供的参考资料来回答用户的问题。

重要说明：
1. 如果参考资料中有相关内容，务必基于这些内容来回答
2. 如果没有相关参考资料，请明确说明"根据现有资料无法回答"
3. 提供回答时，请标注信息来自哪个参考资料
4. 回答应该准确、简洁、专业"""

    user_message = f"""请根据以下参考资料回答我的问题：

【参考资料】
{reference_text}

【用户问题】
{query}"""

    try:
        response = ollama.chat(
            model='qwen2:0.5b',
            messages=[
                {
                    'role': 'system',
                    'content': system_prompt
                },
                {
                    'role': 'user',
                    'content': user_message
                }
            ]
        )

        answer = response['message']['content']
        return answer

    except Exception as e:
        return "生成回答时出现错误"

@app.route('/')
def index():
    return jsonify({"message": "RAG API 服务运行中", "endpoints": ["/query"]})

@app.route('/query', methods=['POST'])
def query():
    data = request.get_json()
    user_query = data.get('query', '')

    if not user_query.strip():
        return jsonify({'error': '查询不能为空'})

    global collection
    if collection is None:
        # 初始化向量库
        doc_file = "company_handbook.txt"
        if not os.path.exists(doc_file):
            return jsonify({'error': '文档文件不存在'})

        chunks = load_and_chunk_documents(doc_file)
        if not chunks:
            return jsonify({'error': '文档加载失败'})

        collection = create_vectorstore(chunks)
        if collection is None:
            return jsonify({'error': '向量库创建失败'})

    retrieved_docs = retrieve_documents(collection, user_query, k=3)
    answer = generate_answer(user_query, retrieved_docs)

    return jsonify({
        'answer': answer,
        'retrieved_docs': retrieved_docs
    })

if __name__ == '__main__':
    app.run(debug=True)