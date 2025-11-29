Aquí tienes el texto en **formato README.md**, bien estructurado y listo para pegar en tu repositorio:

---

# 🧩 Threads Service

Servicio de Threads con soporte para **ejecución local mediante Docker** y también disponible en un **despliegue en Kubernetes** utilizando imágenes Docker.

---

## 🚀 Ejecución local

### 1️⃣ Levantar los servicios con Docker

En la **raíz del proyecto**:

```bash
docker compose up --build
```

### 2️⃣ Iniciar el frontend local

En otra consola, dentro del proyecto:

```bash
python -m http.server 3000
```

### 3️⃣ Crear el canal inicial (necesario para crear threads)

Ejecutar cuando los contenedores ya estén arriba:

```bash
docker compose exec db psql -U threads -d threads -c "insert into channel (id,name,is_active,updated_at)
 values ('canal-1','General',true,now())
 on conflict (id) do update
 set name=excluded.name, is_active=excluded.is_active, updated_at=now();"
```

> Esto crea o actualiza el canal **General (`canal-1`)**, necesario para iniciar la creación de threads y mensajes.

---

## 🌐 Interfaz Web & APIs

### 🖥️ UI de Threads

* **Localmente**
  👉 [http://localhost:3000/web/](http://localhost:3000/web/)

* **Desplegada en Kubernetes (Docker + K8s)**
  👉 [https://threads.inf326.nursoft.dev/index](https://threads.inf326.nursoft.dev/index)

---

### 📘 API Threads (FastAPI)

* **Local**
  👉 [http://localhost:8000/docs#/threads](http://localhost:8000/docs#/threads)

* **Deploy en Kubernetes**
  👉 [https://threads.inf326.nursoft.dev/docs#/](https://threads.inf326.nursoft.dev/docs#/)

---

### 💬 API de Mensajes (Solo local)

👉 [http://localhost:8001/docs#/](http://localhost:8001/docs#/)

> Para crear mensajes, debes usar la **ID de un canal existente**, por ejemplo `canal-1`.

---

## ☸️ Despliegue en Kubernetes

El backend está desplegado en un clúster de **Kubernetes**, utilizando imágenes **Docker** construidas desde este proyecto.

* UI desplegada:
  👉 [https://threads.inf326.nursoft.dev/index](https://threads.inf326.nursoft.dev/index)

* API pública:
  👉 [https://threads.inf326.nursoft.dev/docs#/](https://threads.inf326.nursoft.dev/docs#/)

---

## 🧠 Resumen rápido

| Acción                | Comando / URL                                                                          |
| --------------------- | -------------------------------------------------------------------------------------- |
| Levantar servicios    | `docker compose up --build`                                                            |
| Servir UI local       | `python -m http.server 3000`                                                           |
| Crear canal `canal-1` | Comando SQL anterior                                                                   |
| UI local              | [http://localhost:3000/web/](http://localhost:3000/web/)                               |
| UI Kubernetes         | [https://threads.inf326.nursoft.dev/index](https://threads.inf326.nursoft.dev/index)   |
| API local             | [http://localhost:8000/docs#/threads](http://localhost:8000/docs#/threads)             |
| API Kubernetes        | [https://threads.inf326.nursoft.dev/docs#/](https://threads.inf326.nursoft.dev/docs#/) |

---

¿Quieres que también agregue una sección de **estructura de carpetas**, **variables de entorno**, o un diagrama del flujo del sistema?
