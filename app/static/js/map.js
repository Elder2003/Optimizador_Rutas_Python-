const map = L.map('map', { zoomControl: false }).setView([-17.3935, -66.1570], 14);

L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; CARTO', subdomains: 'abcd', maxZoom: 20
}).addTo(map);
L.control.zoom({ position: 'bottomright' }).addTo(map);

let origen = null;
let destinos = [];
let rutaLayer = null;

function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerText = message; 
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}
map.on('click', function(e) {
    const container = document.createElement('div');
    container.className = 'popup-options';
    
    container.innerHTML = `
        <div style="font-size:11px; color:#888; text-align:center; margin-bottom:5px;">Seleccionar acción</div>
        <button class="popup-btn" onclick="handlePopupClick('origen', ${e.latlng.lat}, ${e.latlng.lng})">
            Establecer Inicio
        </button>
        <button class="popup-btn" onclick="handlePopupClick('destino', ${e.latlng.lat}, ${e.latlng.lng})">
            Agregar Parada
        </button>
    `;

    L.popup({ offset: [0, -5] })
        .setLatLng(e.latlng)
        .setContent(container)
        .openOn(map);
});

window.handlePopupClick = (tipo, lat, lng) => {
    agregarPunto(tipo, lat, lng);
    map.closePopup();
};

async function agregarPunto(tipo, lat, lng) {
    const nombre = tipo === 'origen' ? "Punto de Partida" : `Parada #${destinos.length + 1}`;

    try {
        const res = await fetch('/api/ubicaciones', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ nombre, latitud: lat, longitud: lng, tipo: tipo === 'origen' ? 'almacen' : 'tienda' })
        });
        const data = await res.json();
        const nuevoPunto = { id: data.id, nombre, lat, lon: lng, tipo };

        if (tipo === 'origen') {
            if(origen) eliminarPuntoVisual(origen);
            origen = nuevoPunto;
        } else {
            destinos.push(nuevoPunto);
        }

        dibujarMarcador(nuevoPunto);
        actualizarPanel();

    } catch (e) { showToast("Error de conexión", "error"); }
}
function dibujarMarcador(punto) {
    const isOrigin = punto.tipo === 'origen';
    const icon = L.divIcon({
        className: `simple-dot ${isOrigin ? 'dot-green' : 'dot-red'}`,
        html: '', 
        iconSize: [16, 16], 
        iconAnchor: [8, 8]
    });

    punto.marker = L.marker([punto.lat, punto.lon], { icon: icon }).addTo(map);
    punto.marker.bindTooltip(punto.nombre, { direction: 'top', offset: [0, -10] });
}

function eliminarPuntoVisual(punto) {
    if(punto.marker) map.removeLayer(punto.marker);
}

function actualizarPanel() {
    const lista = document.getElementById('listaPuntos');
    lista.innerHTML = '';
    const todos = origen ? [origen, ...destinos] : [...destinos];

    if(todos.length === 0) {
        lista.innerHTML = '<div style="text-align:center; padding:20px; color:#666; font-size:12px;">Mapa vacío.<br>Haz clic para agregar puntos.</div>';
        document.getElementById('btnCalcular').disabled = true;
        return;
    }

    todos.forEach(p => {
        const isOrigin = p.tipo === 'origen';
        const card = document.createElement('div');
        card.className = `point-card ${isOrigin ? 'origin' : 'delivery'}`;
        card.onclick = () => map.panTo([p.lat, p.lon]);
        
        card.innerHTML = `
            <div>
                <div class="point-name">${p.nombre}</div>
                <div class="point-coords">${p.lat.toFixed(4)}, ${p.lon.toFixed(4)}</div>
            </div>
            <button class="btn-delete" onclick="borrarPunto(event, ${p.id}, '${p.tipo}')">✕</button>
        `;
        lista.appendChild(card);
    });

    document.getElementById('btnCalcular').disabled = !(origen && destinos.length > 0);
}

window.borrarPunto = async (e, id, tipo) => {
    e.stopPropagation();
    await fetch(`/api/ubicaciones/${id}`, { method: 'DELETE' });

    if(tipo === 'origen') {
        eliminarPuntoVisual(origen); origen = null;
    } else {
        const idx = destinos.findIndex(d => d.id === id);
        if(idx > -1) { eliminarPuntoVisual(destinos[idx]); destinos.splice(idx, 1); }
    }
    if(rutaLayer) map.removeLayer(rutaLayer);
    actualizarPanel();
};

window.calcularRuta = async () => {
    if(!origen) return;
    const btn = document.getElementById('btnCalcular');
    btn.innerHTML = 'Calculando...';
    btn.disabled = true;

    try {
        const res = await fetch('/api/ruta-optima', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ origen_id: origen.id })
        });
        const data = await res.json();
        if(data.error) throw new Error(data.error);

        if(rutaLayer) map.removeLayer(rutaLayer);
        
        rutaLayer = L.geoJSON(data.ruta_geojson, {
            style: { color: '#4CAF50', weight: 4, opacity: 0.8, className: 'route-line' }
        }).addTo(map);

        map.fitBounds(rutaLayer.getBounds(), { padding: [50, 50] });

    } catch (e) {
        showToast("Error al calcular ruta", "error");
    } finally {
        btn.innerHTML = 'Calcular Ruta';
        btn.disabled = false;
    }
};

(async function init() {
    const res = await fetch('/api/ubicaciones');
    const data = await res.json();
    data.forEach(p => {
        const tipo = p.tipo === 'almacen' ? 'origen' : 'destino';
        const obj = { id: p.id, nombre: p.nombre, lat: p.lat, lon: p.lon, tipo };
        if(tipo === 'origen' && !origen) origen = obj;
        else if(tipo !== 'origen') destinos.push(obj);
        dibujarMarcador(obj);
    });
    actualizarPanel();
})();