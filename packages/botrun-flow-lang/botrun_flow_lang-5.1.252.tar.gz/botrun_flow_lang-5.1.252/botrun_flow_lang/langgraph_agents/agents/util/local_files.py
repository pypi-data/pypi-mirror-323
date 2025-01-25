import os
import requests
from pathlib import Path


def upload_and_get_tmp_public_url(
    file_path: str, botrun_flow_lang_url: str = "", user_id: str = ""
) -> str:
    """上傳檔案到 GCS，並取得公開存取的 URL

    Args:
        file_path: 本地檔案路徑
        botrun_flow_lang_url: botrun flow lang API 的 URL，預設為空字串

    Returns:
        str: 上傳後的公開存取 URL
    """
    try:
        # 如果沒有提供 API URL，使用預設值
        if not botrun_flow_lang_url or not user_id:
            raise ValueError("botrun_flow_lang_url and user_id are required")

        # 從檔案路徑取得檔案名稱
        file_name = Path(file_path).name

        # 準備 API endpoint
        url = f"{botrun_flow_lang_url}/api/tmp-files/{user_id}"

        # 準備檔案
        files = {
            "file": (file_name, open(file_path, "rb")),
            "file_name": (None, file_name),
        }

        # 發送請求
        response = requests.post(url, files=files)
        response.raise_for_status()  # 如果請求失敗會拋出異常

        # 從回應中取得 URL
        result = response.json()
        return result.get("url", "")

    except Exception as e:
        print(f"Error uploading file: {str(e)}")
        return "Error uploading file"
