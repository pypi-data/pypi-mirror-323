import os
import sys
import httpx
import zipfile
from typing import Optional, Literal

from spiderpy3.utils.url import is_valid
from spiderpy3.utils.headers import get_default


def url_to_file_path(
        url: str,
        dir_path: Optional[str] = None,
        file_name: Optional[str] = None,
        file_prefix: Optional[str] = None,
        file_suffix: Optional[str] = None,
        file_path: Optional[str] = None
) -> Optional[str]:
    if not is_valid(url):
        return

    headers = get_default()

    if file_path is None:
        if dir_path is None:
            sys_argv0 = sys.argv[0]
            if not os.path.isfile(sys_argv0):
                return
            dir_path = os.path.dirname(sys_argv0)
        if file_name is None:
            if file_prefix is not None and file_suffix is not None:
                file_name = file_prefix + file_suffix
            else:
                if file_prefix is None:
                    file_prefix, _ = os.path.splitext(os.path.basename(url))
                if file_suffix is None:
                    response = httpx.head(url, headers=headers)
                    if (content_type := response.headers.get("content-type")) is not None:  # content-type: image/jpeg
                        file_ext = content_type.split("/", maxsplit=1)[-1]
                        file_suffix = "." + file_ext
                    if file_suffix is None:
                        _, file_suffix = os.path.splitext(os.path.basename(url))
                file_name = file_prefix + file_suffix
        file_path = os.path.join(dir_path, file_name)

    if os.path.exists(file_path):
        return file_path

    dir_path = os.path.dirname(file_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    try:
        response = httpx.get(url, headers=headers)
        content = response.content
        with open(file_path, "wb") as file:
            file.write(content)
    except Exception:  # noqa
        file_path = None

    return file_path


def compress_dir_path(dir_path: str, compress_type: Literal["zip"] = "zip") -> None:
    dir_path = os.path.abspath(dir_path)
    if not os.path.isdir(dir_path):
        raise ValueError(f"不支持 dir_path：{dir_path}！")

    valid_compress_type = ["zip"]
    if compress_type not in valid_compress_type:
        raise ValueError(f"不支持 compress_type：{compress_type}！")

    compress_file_path = os.path.join(
        os.path.dirname(dir_path), os.path.basename(dir_path) + "." + compress_type
    )

    if compress_type == "zip":
        with zipfile.ZipFile(compress_file_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_file_path = os.path.relpath(file_path, dir_path)
                    zf.write(file_path, arcname=rel_file_path)
