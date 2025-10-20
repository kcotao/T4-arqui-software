# 🧩 Threads Service

## 🚀 Cómo iniciar el proyecto

### 1️⃣ Crear y levantar los contenedores
Ejecuta en la raíz del proyecto:

```bash
docker compose up --build
```

### 2️⃣ Iniciar el frontend
En otra consola (desde la carpeta del proyecto):

```bash
python -m http.server 3000
```

### 3️⃣ Simular un canal inicial
Ejecuta este comando **una vez levantados los contenedores** para simular la existencia de un canal llamado `canal-1`, necesario para crear y visualizar threads:

```bash
docker compose exec db psql -U threads -d threads -c "insert into channel (id,name,is_active,updated_at)
 values ('canal-1','General',true,now())
 on conflict (id) do update
 set name=excluded.name, is_active=excluded.is_active, updated_at=now();"
```

> 💡 Este paso crea (o actualiza) el canal “General” con ID `canal-1`, el cual servirá para iniciar los **threads**.

---

## 🌐 Interfaz y APIs

### 🖥️ UI de Threads
Abre la siguiente URL en tu navegador:
👉 [http://localhost:3000/web/](http://localhost:3000/web/)

### 📘 API de Threads
Disponible en:
👉 [http://localhost:8000/docs#/threads](http://localhost:8000/docs#/threads)

### 💬 API de Mensajes
Disponible en:
👉 [http://localhost:8001/docs#/](http://localhost:8001/docs#/)

> Desde estas APIs puedes **crear mensajes o threads** usando FastAPI, y luego **visualizarlos en la interfaz web.** Se debe usar la id dee algun canal ya creado a la hora de crear un mensaje.

---

## 🧠 Resumen
1. `docker compose up --build` → levanta los servicios.  
2. `python -m http.server 3000` → inicia la UI.  
3. Ejecuta el `INSERT` para crear el canal inicial.  
4. Abre [http://localhost:3000/web/](http://localhost:3000/web/) y explora los threads y mensajes.
