from http.server import BaseHTTPRequestHandler, HTTPServer
import json

HOST = "127.0.0.1"
PORT = 3000

HOMESTAYS = [
    {
        "id": 1,
        "name": "Homestay Quận 1",
        "address": "123 Lê Lợi",
        "district": "Quận 1",
        "lat": 10.776889,
        "lng": 106.700806,
        "price": 500000,
        "description": "Gần trung tâm",
    },
    {
        "id": 2,
        "name": "Homestay Quận 3",
        "address": "",  # nhóm trưởng chưa đưa, để trống
        "district": "Quận 3",
        "lat": 10.780087,
        "lng": 106.682225,
        "price": 0,     # nhóm trưởng chưa đưa, để 0
        "description": "",
    },
    {
        "id": 3,
        "name": "Homestay Thủ Đức",
        "address": "",
        "district": "Thủ Đức",
        "lat": 10.849320,
        "lng": 106.753770,
        "price": 0,
        "description": "",
    },
]


def point_in_polygon(point, polygon):
    # Ray casting algorithm
    x, y = point
    inside = False
    n = len(polygon)
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]
        intersects = ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1)
        if intersects:
            inside = not inside
    return inside

class Handler(BaseHTTPRequestHandler):
    def _send_json(self, data, code=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        # CORS
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
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8") if length else "{}"
            try:
                payload = json.loads(raw)
            except:
                payload = {}

            polygon = payload.get("polygon", {})
            coords = polygon.get("coordinates", [])
            # GeoJSON: [[[lng,lat],...]]
            ring = coords[0] if coords and isinstance(coords[0], list) else []

            if len(ring) < 3:
                return self._send_json(HOMESTAYS)  # polygon không hợp lệ -> trả all

            # Chuyển về (lng,lat) tuples
            poly = [(p[0], p[1]) for p in ring if isinstance(p, list) and len(p) >= 2]

            filtered = []
            for hs in HOMESTAYS:
                pt = (hs["lng"], hs["lat"])  # (lng,lat)
                if point_in_polygon(pt, poly):
                    filtered.append(hs)

            return self._send_json(filtered)

        return self._send_json({"error": "Not found"}, 404)

if __name__ == "__main__":
    print("✅ RUNNING THIS FILE:", __file__)
    print(f"✅ API running: http://{HOST}:{PORT}")
    print(f"   GET  http://{HOST}:{PORT}/homestays")
    print(f"   POST http://{HOST}:{PORT}/homestays/filter")
    HTTPServer((HOST, PORT), Handler).serve_forever()
