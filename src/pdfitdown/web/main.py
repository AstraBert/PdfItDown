"""
PdfItDown Web 服务启动入口
"""

import uvicorn
import argparse
import os
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="PdfItDown Web - 文件转PDF在线转换服务"
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="绑定的主机地址 (默认: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="服务端口 (默认: 8000)"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        default=False,
        help="启用自动重载模式 (开发模式)"
    )
    
    parser.add_argument(
        "--work-dir",
        type=str,
        default=None,
        help="工作目录 (用于存储上传和输出文件)"
    )
    
    args = parser.parse_args()
    
    if args.work_dir:
        os.environ["PDFITDOWN_WORK_DIR"] = args.work_dir
    
    print("=" * 60)
    print("  PdfItDown Web - 文件转PDF在线转换服务")
    print("=" * 60)
    print(f"  服务地址: http://{args.host}:{args.port}")
    print(f"  本地访问: http://localhost:{args.port}")
    print("=" * 60)
    print()
    print("请在浏览器中打开上述地址开始使用。")
    print("按 Ctrl+C 停止服务。")
    print()
    
    uvicorn.run(
        "pdfitdown.web.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        reload_dirs=[str(Path(__file__).parent)] if args.reload else None
    )


if __name__ == "__main__":
    main()
