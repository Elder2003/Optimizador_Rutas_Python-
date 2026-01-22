from flask import Blueprint, jsonify, request, session, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import Usuario, Producto, Ubicacion
import requests

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('dashboard.html')

@main.route('/api/ubicaciones', methods=['GET'])
def get_ubicaciones():
    ubicaciones = Ubicacion.query.all()
    res = [{
        "id": u.id, 
        "nombre": u.nombre, 
        "lat": u.latitud, 
        "lon": u.longitud, 
        "tipo": u.tipo,
        "direccion": u.direccion
    } for u in ubicaciones]
    return jsonify(res)

@main.route('/api/ubicaciones', methods=['POST'])
def crear_ubicacion():
    data = request.json
    nueva_ub = Ubicacion(
        nombre=data['nombre'],
        tipo=data.get('tipo', 'tienda'),
        latitud=data['latitud'],
        longitud=data['longitud'],
        direccion=data.get('direccion', 'Sin dirección')
    )
    db.session.add(nueva_ub)
    db.session.commit()
    return jsonify({"mensaje": "Ubicación guardada", "id": nueva_ub.id}), 201

@main.route('/api/ubicaciones/<int:id>', methods=['DELETE'])
def eliminar_ubicacion(id):
    ubicacion = Ubicacion.query.get(id)
    if ubicacion:
        db.session.delete(ubicacion)
        db.session.commit()
        return jsonify({"mensaje": "Eliminado correctamente"}), 200
    return jsonify({"error": "No encontrado"}), 404

@main.route('/api/ruta-optima', methods=['POST'])
def calcular_ruta_optima():
    """
    Recibe un JSON con { "origen_id": 1 }
    Calcula la ruta empezando por ese ID y visitando el resto.
    """
    data = request.json
    origen_id = int(data.get('origen_id'))
    
    origen = Ubicacion.query.get(origen_id)
    if not origen:
        return jsonify({"error": "Punto de partida no encontrado"}), 400

    otros_puntos = Ubicacion.query.filter(Ubicacion.id != origen_id).all()
    
    if not otros_puntos:
        return jsonify({"error": "Se necesitan al menos 2 puntos para una ruta"}), 400

    lista_puntos = [origen] + otros_puntos
    
    coords_list = [f"{u.longitud},{u.latitud}" for u in lista_puntos]
    coords_str = ";".join(coords_list)

    osrm_url = f"http://router.project-osrm.org/trip/v1/driving/{coords_str}?source=first&geometries=geojson"
    
    try:
        response = requests.get(osrm_url)
        data = response.json()
        
        if data['code'] != 'Ok':
            return jsonify({"error": "Error de OSRM"}), 500

        waypoints_ordenados = sorted(data['waypoints'], key=lambda x: x['waypoint_index'])
        
        orden_final = []
        for wp in waypoints_ordenados:
            index_original = wp['waypoint_index']
            punto_db = lista_puntos[index_original]
            
            orden_final.append({
                "orden": wp['waypoint_index'] + 1,
                "nombre": punto_db.nombre,
                "lat": punto_db.latitud,
                "lon": punto_db.longitud,
                "es_inicio": (index_original == 0) 
            })

        geometria = data['trips'][0]['geometry']

        return jsonify({
            "mensaje": "Ruta calculada",
            "orden_entrega": orden_final,
            "ruta_geojson": geometria
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500