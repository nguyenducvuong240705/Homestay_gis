from http.server import BaseHTTPRequestHandler, HTTPServer
import json

HOST = "127.0.0.1"
PORT = 3000

HOMESTAYS = [
    {
        "name": "Saigon Riverside Homestay",
        "description": "View sông thoáng mát",
        "address": "12 Tôn Đức Thắng",
        "district": "1",
        "price_per_night": 650000,
        "latitude": 10.7765,
        "longitude": 106.7059
    },
    {
        "name": "Landmark 81 Stay",
        "description": "View toàn thành phố",
        "address": "720A Điện Biên Phủ",
        "district": "Bình Thạnh",
        "price_per_night": 900000,
        "latitude": 10.7952,
        "longitude": 106.7218
    },
    {
        "name": "Ben Thanh Cozy House",
        "address": "45 Lê Thánh Tôn",
        "district": "1",
        "price_per_night": 550000,
        "latitude": 10.7721,
        "longitude": 106.6983
    },
    {
        "name": "Thao Dien Chill Home",
        "address": "23 Xuân Thủy",
        "district": "Thủ Đức",
        "price_per_night": 700000,
        "latitude": 10.8033,
        "longitude": 106.7405
    },
    {
        "name": "Phu My Hung Modern Stay",
        "address": "Nguyễn Lương Bằng",
        "district": "7",
        "price_per_night": 800000,
        "latitude": 10.7290,
        "longitude": 106.7075
    }
]

def point_in_polygon(point, polygon):
    x, y = point
    inside = False
    n = len(polygon)
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]
        if ((y1 > y) != (y2 > y)) and \
           (x < (x2 - x1) * (y - y1) / ((y2 - y1) + 1e-12) + x1):
            inside = not inside
    return inside

class Handler(BaseHTTPRequestHandler):

    def _send_json(self, data, code=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path == "/homestays":
            return self._send_json(HOMESTAYS)
        return self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        if self.path == "/homestays/filter":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            data = json.loads(body)

            polygon = data.get("polygon", {})
            coords = polygon.get("coordinates", [])
            ring = coords[0] if coords else []

            poly = [(p[0], p[1]) for p in ring]

            filtered = []
            for hs in HOMESTAYS:
                point = (hs["longitude"], hs["latitude"])
                if point_in_polygon(point, poly):
                    filtered.append(hs)

            return self._send_json(filtered)

        return self._send_json({"error": "Not found"}, 404)

if __name__ == "__main__":
    print(f"API running at http://{HOST}:{PORT}")
    HTTPServer((HOST, PORT), Handler).serve_forever()