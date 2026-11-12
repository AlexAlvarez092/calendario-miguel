# Calendario Miguel

Calendario ICS personal publicado en GitHub Pages, al que se puede suscribir desde cualquier app de calendario.

## Suscripcion

URL: https://alexalvarez092.github.io/calendario-miguel/calendar.ics

Anade un calendario por URL / suscripcion ICS en Apple Calendar, Google Calendar o Android.

## Anadir eventos

Edita `data/events.json` (array de eventos) y haz push a `main`; el workflow regenera y publica el calendario (tambien se ejecuta a diario).

```json
[
  { "id": "cena-2026-12-01", "title": "Cena", "start": "2026-12-01T21:00", "end": "2026-12-01T23:00", "location": "Oviedo" },
  { "id": "cumple-ana", "title": "Cumple de Ana", "start": "2026-12-05" }
]
```

- `id`: unico y estable (no incluyas la fecha si puede cambiar).
- `start` / `end`: `YYYY-MM-DDTHH:mm` (hora Europe/Madrid) o `YYYY-MM-DD` para eventos de dia completo.
- `location` y `description` son opcionales.

## Desarrollo

```sh
npm install
npm test
npm run generate   # crea public/calendar.ics
```

Requisito unico en GitHub: Settings > Pages > Source: GitHub Actions.
