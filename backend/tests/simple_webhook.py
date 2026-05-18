"""
简单的 Webhook 测试服务器
运行后可以监听并打印所有接收到的 webhook 事件
"""
import argparse
import hmac
import hashlib
import json
from http.server import HTTPServer, BaseHTTPRequestHandler


class WebhookHandler(BaseHTTPRequestHandler):
    """处理 webhook 请求"""

    secret = None

    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[{self.log_date_time_string()}] {format % args}")

    def do_POST(self):
        """处理 POST 请求"""
        # 读取请求体
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        # 获取签名
        signature = self.headers.get('X-Hub-Signature-256', '')

        # 打印请求信息
        print("\n" + "=" * 60)
        print(f"📥 收到 Webhook 事件!")
        print("=" * 60)
        print(f"📍 路径: {self.path}")
        print(f"🔖 Content-Type: {self.headers.get('Content-Type', 'N/A')}")
        print(f"🏷️  Event: {self.headers.get('X-Webhook-Event', 'N/A')}")
        print(f"🔐 签名: {signature[:20]}..." if signature else "🔐 签名: 无")

        # 验证签名
        if isinstance(WebhookHandler.secret, bytes) and signature:
            expected = 'sha256=' + hmac.new(
                WebhookHandler.secret,
                body,
                hashlib.sha256
            ).hexdigest()
            if hmac.compare_digest(signature, expected):
                print("✅ 签名验证: 通过")
            else:
                print("❌ 签名验证: 失败")
        elif WebhookHandler.secret:
            print("⚠️  签名验证: 跳过 (请求无签名)")

        # 打印请求头
        print("\n📋 请求头:")
        for key, value in self.headers.items():
            print(f"   {key}: {value}")

        # 打印请求体
        print("\n📦 请求体:")
        try:
            data = json.loads(body)
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print(body.decode('utf-8', errors='replace'))

        print("=" * 60 + "\n")

        # 返回响应
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response = json.dumps({"status": "ok", "message": "Webhook received"}).encode()
        self.wfile.write(response)


def run_server(port: int, secret: str = None):
    """启动服务器"""
    WebhookHandler.secret = secret.encode() if isinstance(secret, str) and secret else (secret if isinstance(secret, bytes) else None)

    server_address = ('', port)
    httpd = HTTPServer(server_address, WebhookHandler)

    print("=" * 60)
    print("🪝 Webhook 测试服务器")
    print("=" * 60)
    print(f"📡 监听端口: {port}")
    print(f"🔐 Secret: {'已配置' if isinstance(secret, str) and secret else '未配置'}")
    print(f"\n🌐 访问地址: http://localhost:{port}")
    print(f"📋 示例 curl 命令:")
    if secret:
        print(f'   curl -X POST http://localhost:{port} \\')
        print(f'     -H "Content-Type: application/json" \\')
        print(f'     -H "X-Webhook-Event: test" \\')
        print(f'     -H "X-Hub-Signature-256: sha256=<your-signature>" \\')
        print(f'     -d \'{{"test": "data"}}\'')
    else:
        print(f'   curl -X POST http://localhost:{port} \\')
        print(f'     -H "Content-Type: application/json" \\')
        print(f'     -H "X-Webhook-Event: test" \\')
        print(f'     -d \'{{"test": "data"}}\'')
    print("\n按 Ctrl+C 停止服务器")
    print("=" * 60 + "\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")
        httpd.shutdown()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Webhook 测试服务器')
    parser.add_argument('-p', '--port', type=int, default=8080, help='监听端口 (默认: 8080)')
    parser.add_argument('-s', '--secret', type=str, default=None, help='Webhook Secret')

    args = parser.parse_args()

    run_server(args.port, args.secret)