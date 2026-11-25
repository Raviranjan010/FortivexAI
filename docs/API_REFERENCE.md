# API Reference

Interactive OpenAPI documentation: `http://localhost:8000/docs`.

- `GET /api/health`, `GET /api/config/status`
- `POST/GET /api/conversations`, `GET /api/conversations/{id}`, `POST .../messages`, `POST .../end`
- `POST /api/conversations/{id}/proposals/{proposal_id}/confirm` confirms an available stored proposal through an explicit customer action.
- `GET/POST /api/leads`, `PUT/DELETE /api/leads/{id}`, `GET /api/leads-export.csv`
- `GET/POST /api/appointments`, `GET /api/appointments/slots`, `POST /api/appointments/{id}/cancel`
- `GET/POST /api/documents`, `DELETE /api/documents/{id}`, `GET /api/retrieval?q=`
- `GET /api/analytics`, `GET/PUT /api/settings`

Errors use HTTP status codes and a `detail` string. Booking requires `confirmed: true`; timestamps are ISO 8601 with offsets.
