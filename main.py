from flask import Flask, request, jsonify
from datetime import datetime
from typing import Dict, List, Optional

app = Flask(__name__)

# -------- CONSTANTES --------
RIDE_STATUS_READY = "ready"
RIDE_STATUS_INPROGRESS = "inprogress"
RIDE_STATUS_DONE = "done"

PARTICIPANT_WAITING = "waiting"
PARTICIPANT_CONFIRMED = "confirmed"
PARTICIPANT_REJECTED = "rejected"
PARTICIPANT_MISSING = "missing"
PARTICIPANT_INPROGRESS = "inprogress"
PARTICIPANT_NOTMARKED = "notmarked"
PARTICIPANT_DONE = "done"

# --------Tablas --------
class RideParticipant:
    def __init__(self, participant_alias: str, destination: str, occupied_spaces: int):
        self.participant_alias = participant_alias
        self.destination = destination
        self.occupied_spaces = occupied_spaces
        self.status = PARTICIPANT_WAITING
        self.confirmation = None

    def to_dict(self):
        return {
            "confirmation": self.confirmation,
            "destination": self.destination,
            "occupiedSpaces": self.occupied_spaces,
            "status": self.status,
        }

class Usuario:
    def __init__(self, alias: str, nombre: str = "", car_plate: Optional[str] = None):
        self.alias = alias
        self.nombre = nombre
        self.car_plate = car_plate
        self.rides_creados = []
        self.participaciones = []

    def to_dict(self):
        return {
            "alias": self.alias,
            "nombre": self.nombre,
            "carPlate": self.car_plate
        }

    def crear_ride(self, ride_date_time: str, final_address: str, available_spaces: int):
        ride_id = len(rides_db) + 1
        ride = Ride(ride_id, ride_date_time, final_address, self.alias, available_spaces)
        self.rides_creados.append(ride)
        rides_db[ride_id] = ride
        return ride

    def get_ride_statistics(self):
        total = len(self.participaciones)
        completed = sum(1 for p in self.participaciones if p.status == PARTICIPANT_DONE)
        missing = sum(1 for p in self.participaciones if p.status == PARTICIPANT_MISSING)
        notmarked = sum(1 for p in self.participaciones if p.status == PARTICIPANT_NOTMARKED)
        rejected = sum(1 for p in self.participaciones if p.status == PARTICIPANT_REJECTED)
        return {
            "previousRidesTotal": total,
            "previousRidesCompleted": completed,
            "previousRidesMissing": missing,
            "previousRidesNotMarked": notmarked,
            "previousRidesRejected": rejected
        }

class Ride:
    def __init__(self, ride_id: int, ride_date_time: str, final_address: str, driver: str, available_spaces: int):
        self.id = ride_id
        self.ride_date_time = ride_date_time
        self.final_address = final_address
        self.driver = driver
        self.available_spaces = available_spaces
        self.status = RIDE_STATUS_READY
        self.participants: List[RideParticipant] = []

    def to_dict(self):
        participants_data = []
        for p in self.participants:
            user_stats = usuarios_db[p.participant_alias].get_ride_statistics()
            participants_data.append({
                **p.to_dict(),
                "participant": {
                    "alias": p.participant_alias,
                    **user_stats
                }
            })
        return {
            "id": self.id,
            "rideDateAndTime": self.ride_date_time,
            "finalAddress": self.final_address,
            "driver": self.driver,
            "status": self.status,
            "participants": participants_data
        }

    def get_participant(self, alias):
        for p in self.participants:
            if p.participant_alias == alias:
                return p
        return None

    def get_confirmed_spaces(self):
        return sum(p.occupied_spaces for p in self.participants if p.status == PARTICIPANT_CONFIRMED)

    def request_to_join(self, participant_alias, destination, occupied_spaces):
        if self.status != RIDE_STATUS_READY:
            raise ValueError("Ride no está disponible")
        if self.get_participant(participant_alias):
            raise ValueError("Ya solicitó unirse")
        p = RideParticipant(participant_alias, destination, occupied_spaces)
        self.participants.append(p)
        usuarios_db[participant_alias].participaciones.append(p)
        return p

    def accept_participant(self, alias):
        p = self.get_participant(alias)
        if not p:
            raise ValueError("Participante no existe")
        if p.status != PARTICIPANT_WAITING:
            raise ValueError("Ya procesado")
        if self.get_confirmed_spaces() + p.occupied_spaces > self.available_spaces:
            raise ValueError("No hay espacios disponibles")
        p.status = PARTICIPANT_CONFIRMED
        p.confirmation = True

    def reject_participant(self, alias):
        p = self.get_participant(alias)
        if not p:
            raise ValueError("Participante no existe")
        if p.status != PARTICIPANT_WAITING:
            raise ValueError("Ya procesado")
        p.status = PARTICIPANT_REJECTED
        p.confirmation = False

    def start_ride(self, present_participants: List[str]):
        if self.status != RIDE_STATUS_READY:
            raise ValueError("Ride no está en estado ready")
        for p in self.participants:
            if p.status == PARTICIPANT_WAITING:
                raise ValueError("Hay participantes en estado waiting")
        for p in self.participants:
            if p.status == PARTICIPANT_CONFIRMED:
                if p.participant_alias in present_participants:
                    p.status = PARTICIPANT_INPROGRESS
                else:
                    p.status = PARTICIPANT_MISSING
        self.status = RIDE_STATUS_INPROGRESS

    def unload_participant(self, alias):
        p = self.get_participant(alias)
        if not p:
            raise ValueError("No encontrado")
        if p.status != PARTICIPANT_INPROGRESS:
            raise ValueError("No está en progreso")
        p.status = PARTICIPANT_DONE

    def end_ride(self):
        for p in self.participants:
            if p.status == PARTICIPANT_INPROGRESS:
                p.status = PARTICIPANT_NOTMARKED
        self.status = RIDE_STATUS_DONE

# -------- BASE DE DATOS --------
usuarios_db: Dict[str, Usuario] = {}
rides_db: Dict[int, Ride] = {}

# -------- TEST DATA --------
def init_data():
    u1 = Usuario("jperez", "Juan Perez", car_plate="ABC123")
    u2 = Usuario("lgomez", "Luis Gomez")
    usuarios_db[u1.alias] = u1
    usuarios_db[u2.alias] = u2
    ride = u1.crear_ride("2025/07/15 22:00", "Av Javier Prado 456, San Borja", 4)
    ride.request_to_join("lgomez", "Av Aramburú 245, Surquillo", 1)

init_data()

# -------- ENDPOINTS --------
@app.route("/")
def index():
    return "Rides en UTEC"

@app.route("/usuarios", methods=["GET"])
def get_usuarios():
    return jsonify([u.to_dict() for u in usuarios_db.values()])

@app.route("/usuarios/<alias>", methods=["GET"])
def get_usuario(alias):
    user = usuarios_db.get(alias)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify(user.to_dict())

@app.route("/usuarios/<alias>/rides", methods=["GET"])
def get_rides_por_usuario(alias):
    user = usuarios_db.get(alias)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify([r.to_dict() for r in user.rides_creados])

@app.route("/usuarios/<alias>/rides/<int:rideid>", methods=["GET"])
def get_ride_completo(alias, rideid):
    ride = rides_db.get(rideid)
    if not ride or ride.driver != alias:
        return jsonify({"error": "Ride no encontrado"}), 404
    return jsonify({"ride": ride.to_dict()})

@app.route("/usuarios/<alias>/rides/<int:rideid>/requestToJoin/<participant>", methods=["POST"])
def request_to_join(alias, rideid, participant):
    try:
        data = request.get_json()
        destination = data["destination"]
        occupied = data["occupiedSpaces"]
        ride = rides_db[rideid]
        ride.request_to_join(participant, destination, occupied)
        return jsonify({"message": "Solicitud enviada"})
    except Exception as e:
        return jsonify({"error": str(e)}), 422

@app.route("/usuarios/<alias>/rides/<int:rideid>/accept/<participant>", methods=["POST"])
def accept_participant(alias, rideid, participant):
    try:
        ride = rides_db[rideid]
        ride.accept_participant(participant)
        return jsonify({"message": "Participante aceptado"})
    except Exception as e:
        return jsonify({"error": str(e)}), 422

@app.route("/usuarios/<alias>/rides/<int:rideid>/reject/<participant>", methods=["POST"])
def reject_participant(alias, rideid, participant):
    try:
        ride = rides_db[rideid]
        ride.reject_participant(participant)
        return jsonify({"message": "Participante rechazado"})
    except Exception as e:
        return jsonify({"error": str(e)}), 422

@app.route("/usuarios/<alias>/rides/<int:rideid>/start", methods=["POST"])
def start_ride(alias, rideid):
    try:
        ride = rides_db[rideid]
        present = request.get_json()["presentParticipants"]
        ride.start_ride(present)
        return jsonify({"message": "Ride iniciado"})
    except Exception as e:
        return jsonify({"error": str(e)}), 422

@app.route("/usuarios/<alias>/rides/<int:rideid>/unloadParticipant", methods=["POST"])
def unload(alias, rideid):
    try:
        ride = rides_db[rideid]
        data = request.get_json()
        participant = data["participantAlias"]
        ride.unload_participant(participant)
        return jsonify({"message": "Participante retirado"})
    except Exception as e:
        return jsonify({"error": str(e)}), 422

@app.route("/usuarios/<alias>/rides/<int:rideid>/end", methods=["POST"])
def end_ride(alias, rideid):
    try:
        ride = rides_db[rideid]
        ride.end_ride()
        return jsonify({"message": "Ride terminado"})
    except Exception as e:
        return jsonify({"error": str(e)}), 422

if __name__ == '__main__':
    app.run(debug=True)
