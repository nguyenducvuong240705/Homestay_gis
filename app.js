// ===== MAP =====
const map = L.map("map").setView([10.7769, 106.7009], 11);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
}).addTo(map);

const markersLayer = L.layerGroup().addTo(map);

let allHomestays = [];

// ===== FORMAT =====
function formatVND(price) {
  return new Intl.NumberFormat("vi-VN", {
    style: "currency",
    currency: "VND",
  }).format(price);
}

// ===== RENDER LIST =====
function renderList(data) {
  const listDiv = document.getElementById("homestayList");
  const resultCount = document.getElementById("resultCount");

  resultCount.innerHTML = `Tìm thấy ${data.length} homestay`;
  listDiv.innerHTML = "";

  data.forEach((hs) => {
    listDiv.innerHTML += `
      <div class="homestay-item">
        <b>${hs.name}</b><br/>
        Quận: ${hs.district}<br/>
        <a onclick="zoomTo(${hs.latitude},${hs.longitude})">Xem chi tiết</a>
      </div>
    `;
  });
}

// ===== RENDER MAP =====
function renderMap(data) {
  markersLayer.clearLayers();

  data.forEach((hs) => {
    const marker = L.marker([hs.latitude, hs.longitude]).addTo(markersLayer);

    marker.bindPopup(`
      <b>${hs.name}</b><br/>
      Giá: ${formatVND(hs.price_per_night)}<br/>
      Địa chỉ: ${hs.address}
    `);
  });
}

// ===== LOAD DATA =====
async function loadAll() {
  const res = await fetch("http://127.0.0.1:3000/homestays");
  const data = await res.json();

  allHomestays = data;
  renderMap(data);
  renderList(data);
  loadDistrictOptions(data);
}

loadAll();

// ===== LOAD DISTRICT DROPDOWN =====
function loadDistrictOptions(data) {
  const select = document.getElementById("searchDistrict");
  const districts = [...new Set(data.map((h) => h.district))];

  districts.forEach((d) => {
    const opt = document.createElement("option");
    opt.value = d;
    opt.textContent = d;
    select.appendChild(opt);
  });
}

// ===== SEARCH =====
function searchHomestays() {
  const name = document.getElementById("searchName").value.toLowerCase();
  const district = document.getElementById("searchDistrict").value;

  const filtered = allHomestays.filter((h) => {
    const matchName = h.name.toLowerCase().includes(name);
    const matchDistrict = district ? h.district === district : true;
    return matchName && matchDistrict;
  });

  renderMap(filtered);
  renderList(filtered);
}

function resetSearch() {
  renderMap(allHomestays);
  renderList(allHomestays);
}

// ===== ZOOM =====
function zoomTo(lat, lng) {
  map.setView([lat, lng], 15);
}

// ===== POLYGON FILTER =====
const drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

const drawControl = new L.Control.Draw({
  edit: { featureGroup: drawnItems },
  draw: {
    polygon: true,
    polyline: false,
    rectangle: false,
    circle: false,
    marker: false,
  },
});
map.addControl(drawControl);

function leafletPolygonToGeoJSON(layer) {
  const ring = layer.getLatLngs()[0];
  const coords = ring.map((p) => [p.lng, p.lat]);
  coords.push(coords[0]);
  return { type: "Polygon", coordinates: [coords] };
}

async function filterByPolygon(polygon) {
  const res = await fetch("http://127.0.0.1:3000/homestays/filter", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ polygon }),
  });

  const data = await res.json();
  renderMap(data);
  renderList(data);
}

map.on(L.Draw.Event.CREATED, async function (e) {
  drawnItems.clearLayers();
  drawnItems.addLayer(e.layer);

  const polygon = leafletPolygonToGeoJSON(e.layer);
  await filterByPolygon(polygon);
});
console.log("test push");
