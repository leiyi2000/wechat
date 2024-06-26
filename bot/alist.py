import os

import httpx


async def upload(
    api: str,
    api_key: str,
    path: str,
    filename: str,
    content: bytes,
):
    target_path = os.path.join(path, filename)
    headers = {
        "Authorization": api_key,
        "file-path": target_path,
    }
    files = {"file": (filename, content, "application/octet-stream")}
    async with httpx.AsyncClient() as client:
        response = await client.put(api + "/api/fs/form", files=files, headers=headers)
        response.raise_for_status()
        # 获取文件直链
        splice_path, name = os.path.split(filename)
        payload = {"path": os.path.join(path, splice_path)}
        response = await client.post(
            api + "/api/fs/list",
            json=payload,
            headers=headers,
        )
        response.raise_for_status()
    for file_info in response.json()["data"]["content"]:
        if file_info["name"] == name:
            return f"{api}/d{target_path}?sign={file_info['sign']}"
    raise AssertionError(f"not found {filename}: {response.json()}")
