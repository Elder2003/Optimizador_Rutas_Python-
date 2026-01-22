from app import create_app, db
from app.models import Usuario, Ubicacion, Producto
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    print("🛠️ Creando base de datos...")
    db.create_all()
    if Usuario.query.first():
        print("✅ La base de datos ya tiene datos.")
    else:
        print("🌱 Sembrando datos de prueba...")

        admin = Usuario(
            nombre="Admin Hamer",
            correo="admin@nexus.com",
            password=generate_password_hash("123456"),
            rol="administrador"
        )
        db.session.add(admin)

        tienda1 = Ubicacion(nombre="Tienda Centro", tipo="tienda", latitud=-17.3935, longitud=-66.1570, direccion="Plaza Principal")
        tienda2 = Ubicacion(nombre="Tienda Norte", tipo="tienda", latitud=-17.3700, longitud=-66.1600, direccion="Av. América")
        tienda3 = Ubicacion(nombre="Tienda Sur", tipo="tienda", latitud=-17.4200, longitud=-66.1500, direccion="Av. Petrolera")
        
        db.session.add_all([tienda1, tienda2, tienda3])

        p1 = Producto(nombre="Coca Cola 2L", precio=12.50, stock=100, categoria="Bebidas")
        p2 = Producto(nombre="Arroz Quintal", precio=240.00, stock=20, categoria="Abarrotes")
        
        db.session.add_all([p1, p2])

        db.session.commit()
        print("✅ Datos creados exitosamente.")
        print("   Usuario: admin@nexus.com")
        print("   Pass: 123456")