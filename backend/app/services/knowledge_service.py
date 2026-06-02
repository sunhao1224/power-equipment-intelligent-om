"""知识管理服务"""
import uuid
from datetime import datetime

from app.models.knowledge import (
    KnowledgeUploadRequest,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
    KnowledgeItem,
)
from app.mock_data.knowledge import search_knowledge, KNOWLEDGE_BASE


# 用户上传的知识（内存存储）
_uploaded_knowledge: list[dict] = []


class KnowledgeService:
    """知识管理服务"""

    async def upload(self, request: KnowledgeUploadRequest) -> dict:
        """上传知识文档"""
        doc_id = f"KB-UPL-{uuid.uuid4().hex[:6].upper()}"

        new_doc = {
            "doc_id": doc_id,
            "title": request.title,
            "domain": request.domain,
            "type": request.doc_type,
            "source": request.source,
            "content": request.content,
            "keywords": request.keywords,
            "relevance_score": 0.85,
            "uploaded_at": datetime.now().isoformat(),
        }

        # 添加到知识库
        KNOWLEDGE_BASE.append(new_doc)
        _uploaded_knowledge.append(new_doc)

        return {
            "doc_id": doc_id,
            "title": request.title,
            "status": "success",
            "message": f"知识文档 '{request.title}' 已成功上传",
            "uploaded_at": new_doc["uploaded_at"],
        }

    async def search(self, request: KnowledgeSearchRequest) -> KnowledgeSearchResponse:
        """语义检索"""
        results = search_knowledge(
            query=request.query,
            top_k=request.top_k,
            domain=request.domain,
        )

        items = [
            KnowledgeItem(
                doc_id=r["doc_id"],
                title=r["title"],
                domain=r["domain"],
                type=r["type"],
                source=r["source"],
                content=r.get("full_content", r["content"]),
                relevance=r["relevance"],
            )
            for r in results
        ]

        return KnowledgeSearchResponse(
            query=request.query,
            total=len(items),
            results=items,
        )
