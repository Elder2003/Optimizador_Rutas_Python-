from app import db
from datetime import datetime

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False) 
    rol = db.Column(db.String(20), nullable=False) 
    telefono = db.Column(db.String(20))
    ubicaciones = db.relationship('Ubicacion', backref='creador', lazy=True)
    pedidos = db.relationship('Pedido', backref='cliente', lazy=True)

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50))
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    imagen = db.Column(db.String(200)) 
    en_oferta = db.Column(db.Boolean, default=False)

class Ubicacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50))
    direccion = db.Column(db.String(200))
    latitud = db.Column(db.Float, nullable=False)
    longitud = db.Column(db.Float, nullable=False)
    creado_por = db.Column(db.Integer, db.ForeignKey('usuario.id'))
class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(50), default='pendiente')
    total = db.Column(db.Float, default=0.0)
    
    detalles = db.relationship('DetallePedido', backref='pedido', lazy=True)

class DetallePedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    
    producto = db.relationship('Producto')