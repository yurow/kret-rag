"""
文档管理API路由
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from typing import Optional, Dict, Any, List
import json

from app.models.schemas import (
    DocumentUploadRequest,
    DocumentResponse,
    UploadResponse
)
from app.services.document_service import document_service

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    responses={404: {"description": "Not found"}},
)


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    metadata: Optional[str] = None
):
    """
    上传文档并解析内容
    - 支持PDF、DOCX、PPTX、XLSX、TXT、MD等格式
    - 最大文件大小：10MB
    - 自动提取文本并清理（去除页眉页脚、水印、乱码等）
    - 元数据保存到 SQLite 数据库
    - 自动检测重复文件（同名 + 同大小），避免重复处理
    """
    try:
        # 使用 json.loads 替代 eval() 以修复安全漏洞
        parsed_metadata = None
        if metadata:
            try:
                parsed_metadata = json.loads(metadata)
            except json.JSONDecodeError as e:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid metadata format: {str(e)}"
                )
        
        result = await document_service.upload_document(
            file=file,
            metadata=parsed_metadata
        )
        
        # 根据是否重复构造不同的消息
        if result.is_duplicate:
            message = f"Document already exists. No need to reprocess. Extracted {result.document_response.metadata.get('text_length', 0)} characters."
        else:
            message = f"Document uploaded and processed successfully. Extracted {result.document_response.metadata.get('text_length', 0)} characters."
        
        return UploadResponse(
            document_id=result.document_response.document_id,
            message=message,
            is_duplicate=result.is_duplicate
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str):
    """获取文档信息"""
    document = await document_service.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """删除文档"""
    success = await document_service.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document deleted successfully"}


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    file_type: Optional[str] = Query(None, description="文件类型过滤"),
    status: Optional[str] = Query(None, description="状态过滤")
):
    """列出所有文档（分页）"""
    return await document_service.list_documents(
        page=page, 
        page_size=page_size,
        file_type=file_type,
        status=status
    )


@router.get("/search", response_model=List[DocumentResponse])
async def search_documents(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量")
):
    """搜索文档（基于文件名）"""
    return await document_service.search_documents(
        keyword=keyword,
        page=page,
        page_size=page_size
    )
