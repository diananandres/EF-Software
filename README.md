# EF-Software
# Sistema de Gestión de Rides 
## Pregunta 1 (main.py)

Se implementaron todos los endpoints solicitados en el enunciado:

- `GET /usuarios`
- `GET /usuarios/{alias}`
- `GET /usuarios/{alias}/rides`
- `GET /usuarios/{alias}/rides/{rideid}`
- `POST /usuarios/{alias}/rides/{rideid}/requestToJoin/{alias}`
- `POST /usuarios/{alias}/rides/{rideid}/accept/{alias}`
- `POST /usuarios/{alias}/rides/{rideid}/reject/{alias}`
- `POST /usuarios/{alias}/rides/{rideid}/start`
- `POST /usuarios/{alias}/rides/{rideid}/end`
- `POST /usuarios/{alias}/rides/{rideid}/unloadParticipant`

✔Incluye todas las validaciones indicadas.
✔Manejo de errores 404 y 422 con mensajes apropiados.

---

## Pregunta 2 – (test.py)

Se realizaron 4 pruebas unitarias con `unittest`:

- 1 caso de éxito: crear un ride y aceptar un participante
- 3 casos de error:
  - unirse a ride en progreso
  - solicitud duplicada
  - bajar participante no en progreso

Cada prueba tiene comentarios explicativos.

### ✔Cobertura

```
python3 -m coverage run test.py
python3 -m coverage report
```

### reporte visual

```
python3 -m coverage html
open htmlcov/index.html
```


## Cómo ejecutar el proyecto

```
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la API
python3 main.py

# Ejecutar las pruebas
python3 -m unittest test.py
```


