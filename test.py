import unittest
from main import Usuario, Ride, RideParticipant, PARTICIPANT_DONE, PARTICIPANT_WAITING, PARTICIPANT_INPROGRESS, RIDE_STATUS_READY, PARTICIPANT_CONFIRMED, PARTICIPANT_REJECTED

class TestRides(unittest.TestCase):

    def setUp(self):
        # Usuario conductor y pasajero
        self.driver = Usuario("jperez", "Juan Perez", car_plate="ABC123")
        self.passenger = Usuario("lgomez", "Luis Gomez")

    #crear un ride, agregar y aceptar un participante(exito)
    def test_crear_y_aceptar_participante(self):
        ride = self.driver.crear_ride("2025/07/15 22:00", "San Borja", 2)
        ride.request_to_join(self.passenger.alias, "Surquillo", 1)
        ride.accept_participant(self.passenger.alias)
        p = ride.get_participant(self.passenger.alias)
        self.assertEqual(p.status, PARTICIPANT_CONFIRMED)
        self.assertEqual(p.confirmation, True)

    #Unirse a un ride ya en progreso(error)
    def test_unirse_a_ride_iniciado(self):
        ride = self.driver.crear_ride("2025/07/15 22:00", "San Borja", 2)
        ride.status = "inprogress"
        with self.assertRaises(ValueError):
            ride.request_to_join(self.passenger.alias, "Surquillo", 1)

    #Duplicar solicitud al mismo ride(error)
    def test_solicitud_duplicada(self):
        ride = self.driver.crear_ride("2025/07/15 22:00", "San Borja", 2)
        ride.request_to_join(self.passenger.alias, "Surquillo", 1)
        with self.assertRaises(ValueError):
            ride.request_to_join(self.passenger.alias, "Surquillo", 1)

    #Bajar participante que no está en progreso(error)
    def test_unload_sin_inprogress(self):
        ride = self.driver.crear_ride("2025/07/15 22:00", "San Borja", 2)
        ride.request_to_join(self.passenger.alias, "Surquillo", 1)
        with self.assertRaises(ValueError):
            ride.unload_participant(self.passenger.alias)

if __name__ == '__main__':
    unittest.main()
