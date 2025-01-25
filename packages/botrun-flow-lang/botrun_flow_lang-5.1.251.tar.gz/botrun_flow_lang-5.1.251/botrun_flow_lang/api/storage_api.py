from dotenv import load_dotenv
from fastapi import (
    APIRouter,
    UploadFile as FastAPIUploadFile,
    File,
    HTTPException,
    Form,
)
from typing import Optional
from io import BytesIO
import json

from botrun_flow_lang.services.hatch.upload_file import UploadFile
from botrun_flow_lang.services.storage.storage_factory import storage_store_factory
from fastapi.responses import StreamingResponse

router = APIRouter()
load_dotenv()


@router.post("/files/{user_id}")
async def upload_file(
    user_id: str, file: FastAPIUploadFile = File(...), file_info: str = Form(...)
) -> dict:
    """
    儲存檔案到 GCS
    """
    try:
        # 解析 file_info JSON 字串
        file_info_dict = json.loads(file_info)
        file_info_obj = UploadFile(**file_info_dict)

        storage = storage_store_factory()

        # 讀取上傳的檔案內容
        contents = await file.read()
        file_object = BytesIO(contents)

        # 構建存儲路徑
        storage_path = f"{user_id}/{file_info_obj.id}"

        # 存儲檔案
        success = await storage.store_file(storage_path, file_object)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to store file")

        return {"message": "File uploaded successfully", "success": True}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format for file_info")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/{user_id}/{file_id}", response_class=StreamingResponse)
async def get_file(user_id: str, file_id: str):
    """
    從 GCS 取得檔案
    """
    try:
        storage = storage_store_factory()
        storage_path = f"{user_id}/{file_id}"

        file_object = await storage.retrieve_file(storage_path)
        if not file_object:
            raise HTTPException(status_code=404, detail="File not found")

        return StreamingResponse(
            iter([file_object.getvalue()]), media_type="application/octet-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/files/{user_id}/{file_id}")
async def delete_file(user_id: str, file_id: str):
    """
    從 GCS 刪除檔案
    """
    try:
        storage = storage_store_factory()
        storage_path = f"{user_id}/{file_id}"

        success = await storage.delete_file(storage_path)
        if not success:
            raise HTTPException(
                status_code=404, detail="File not found or could not be deleted"
            )

        return {"message": "File deleted successfully", "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tmp-files/{user_id}")
async def upload_tmp_file(
    user_id: str, file: FastAPIUploadFile = File(...), file_name: str = Form(...)
) -> dict:
    """
    儲存暫存檔案到 GCS，檔案會是公開可存取且有 7 天的生命週期
    """
    try:
        storage = storage_store_factory()

        # 讀取上傳的檔案內容
        contents = await file.read()
        file_object = BytesIO(contents)

        # 構建存儲路徑 - 使用 tmp 目錄來區分暫存檔案
        storage_path = f"tmp/{user_id}/{file_name}"

        # 存儲檔案，設定為公開存取
        success, public_url = await storage.store_file(
            storage_path, file_object, public=True
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to store file")

        return {
            "message": "Temporary file uploaded successfully",
            "success": True,
            "url": public_url,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
