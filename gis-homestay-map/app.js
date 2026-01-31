// ====== 1) KHỞI TẠO MAP ======
const map = L.map("map").setView([10.7769, 106.7009], 12);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: "&copy; OpenStreetMap",
}).addTo(map);

// ====== 2) LAYER MARKER HOMESTAY ======
const markersLayer = L.layerGroup().addTo(map);

function formatVND(price) {
  try {
    return new Intl.NumberFormat("vi-VN", {
      style: "currency",
      currency: "VND",
    }).format(price);
  } catch {
    return price + " VND";
  }
}

function renderHomestays(homestays) {
  markersLayer.clearLayers();

  homestays.forEach((hs) => {
    if (hs.lat == null || hs.lng == null) return;

    const marker = L.marker([hs.lat, hs.lng]).addTo(markersLayer);

    marker.bindPopup(`
      <div>
        <b>${hs.name ?? "Không tên"}</b><br/>
        Giá: ${formatVND(hs.price ?? 0)}<br/>
        Địa chỉ: ${hs.address ?? "---"}
      </div>
    `);
  });
}

// ====== 3) LẤY DỮ LIỆU TỪ BACKEND PYTHON ======
async function loadAllHomestays() {
  const res = await fetch("http://127.0.0.1:3000/homestays");
  if (!res.ok) throw new Error("Load homestays failed: " + res.status);

  const data = await res.json();
  renderHomestays(data);
}

// Load lần đầu
loadAllHomestays().catch(console.error);

// ====== 4) LEAFLET DRAW: VẼ POLYGON ======
const drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

const drawControl = new L.Control.Draw({
  edit: { featureGroup: drawnItems },
  draw: {
    polygon: true,
    polyline: false,
    rectangle: false,
    circle: false,
    circlemarker: false,
    marker: false,
  },
});
map.addControl(drawControl);

// Leaflet polygon -> GeoJSON polygon ([lng, lat])
function leafletPolygonToGeoJSONPolygon(layer) {
  const ring = layer.getLatLngs()[0]; // [{lat,lng}, ...]
  const coords = ring.map((p) => [p.lng, p.lat]);

  // khép kín
  if (coords.length > 0) {
    const first = coords[0];
    const last = coords[coords.length - 1];
    if (first[0] !== last[0] || first[1] !== last[1]) coords.push(first);
  }

  return { type: "Polygon", coordinates: [coords] };
}

async function filterHomestaysByPolygon(geojsonPolygon) {
  const res = await fetch("http://127.0.0.1:3000/homestays/filter", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ polygon: geojsonPolygon }),
  });

  if (!res.ok) throw new Error("Filter failed: " + res.status);

  const filtered = await res.json();
  renderHomestays(filtered); // cập nhật marker theo vùng
}

map.on(L.Draw.Event.CREATED, async function (event) {
  const layer = event.layer;

  drawnItems.clearLayers(); // giữ 1 polygon
  drawnItems.addLayer(layer);

  const polygonGeoJSON = leafletPolygonToGeoJSONPolygon(layer);
  console.log("Polygon GeoJSON:", polygonGeoJSON);

  try {
    await filterHomestaysByPolygon(polygonGeoJSON);
  } catch (err) {
    console.error(err);
    await loadAllHomestays(); // lỗi thì load lại all
  }
});
