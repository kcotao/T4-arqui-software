Usar

docker compose up --build

y en otra consola iniciar

python -m http.server 3000

ejecutar:
docker compose exec db psql -U threads -d threads -c "insert into channel (id,name,is_active,updated_at) values ('canal-1','General',true,now()) on conflict (id) do update set name=excluded.name,is_active=excluded.is_active,updated_at=now();"

luego meterse a:
http://localhost:3000/web/?
para ver los threads

y en los docs:
http://localhost:8001/docs#/
http://localhost:8000/docs#/threads

también para crear mensajes o crear threads
