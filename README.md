# ⚡ Smart Home Energy Management System — Backend API

A Dockerized Django + Strawberry GraphQL backend for simulating and managing smart home energy devices. This system supports three types of decvices - production, consumption and storage, per-user energy stats aggregation, and real-time simulation enabled by periodic tasks using Celery + Redis.

---

## 🚀 Features

- ✅ GraphQL API for creating, updating, retrieving devices, and user stats
- ✅ Periodic simulation of energy readings per device
- ✅ Per-user energy statistics cached in Redis
- ✅ Admin panel with role-based access
- ✅ Dockerized development setup with Postgres, Redis, Celery, and Django
- Pending: JWT Authentication (login, register)

---

## 🏗️ Infrastructure Overview

| Component      | Purpose                                                       |
|----------------|---------------------------------------------------------------|
| **Django**     | Core backend and admin interface                              |
| **Strawberry** | GraphQL API layer using latest `strawberry-graphql`           |
| **PostgreSQL** | Persistent storage for users and device data                  |
| **Redis**      | Fast-access cache for computed per-user energy stats          |
| **Celery**     | Background task processor for device simulation               |
| **Celery Beat**| Periodic task scheduler to run simulations every minute       |
| **Docker**     | Containerization of all services for easy local setup         |

---

## 📦 Local Setup (Docker)

> Prerequisites: [Docker](https://www.docker.com/products/docker-desktop/) installed.

```bash
# Clone the repo
git clone https://github.com/pranman11/smart-home-energy-mgmt.git
cd smart-home-energy-mgmt

# Build and start all services
docker-compose up --build
```

### ✅ Entrypoint (`entrypoint.sh`)

This script is run when the Django container starts. It:

- Runs `makemigrations` (for devices app) and `migrate` (devices, users and celery beat tables)
- Seeds initial users + device data
- Creates a default superuser (`admin` / `adminpass`)
- Starts the server

---

## 👤 Users & Roles

| Type        | Access                                  |
|-------------|-----------------------------------------|
| **Admin**   | Can access all devices in Django Admin  |
| **Regular** | Only sees their own devices via GraphQL |

Enable `is_staff` for any user to let them access `/admin`:

```bash
docker-compose exec web python manage.py shell

>>> from django.contrib.auth import get_user_model
>>> user = get_user_model().objects.get(username="user1")
>>> user.is_staff = True
>>> user.save()
```

Further, users will need to be granted permission (by the admin) to view their devices from the admin portal. Users are not granted access to add or update devices from admin. This is only allowed via API endpoints described later.

If the entrypoint.sh fails to run migrations and seed initial users and devices, please run the below management commands:

```
# Run migrations and seed data
docker-compose exec web python manage.py makemigrations devices
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py seed_devices
```

## 🔄 Periodic Task: Simulate Device Readings

### How It Works

- A **Celery Beat** periodic task needs to be created from the Periodic tasks admin portal.
- Below fields need to be set:
    - name
    - select 'simulate_device_readings' task
    - create new interval (eg. one minute)
    - add start date and time 

Every minute, a scheduled Celery Beat task runs the `simulate_device_readings` function, which performs the following for **each user's online devices**:

### 1. Production Devices
- `instantaneous_output_watts` is simulated between **1000–5000W**, only between 6 AM and 6 PM.
- Solar devices produce `0` watts outside daylight hours.
- Generators can produce power any time.

### 2. Consumption Devices
- `consumption_rate_watts` is simulated between **500–3000W**, at any time.

### 3. Storage Devices
- Simulate `charge_discharge_rate_watts` between **-1000 to +1000W**
- Clamp `current_level_wh` to be within `[0, total_capacity_wh]`
- Compute actual flow as `new_level - current_level`

### Aggregation
- After simulation, data is aggregated per user and stored in Redis:
```json
energy_stats:<user_id> = {
  "current_production": ...,
  "current_consumption": ...,
  "current_storage": { ... },
  "current_storage_flow": ...,
  "net_grid_flow": ...,
  "timestamp": ...
}
```
---

## 📡 GraphQL API Endpoints

GraphQL Playground available at:  
👉 [`http://localhost:8000/graphql/`](http://localhost:8000/graphql/)

### 📥 `createDevice`

```graphql
mutation {
  createDevice(input: {
    name: "Tesla EV",
    status: "online",
    deviceType: "storage",
    totalCapacityWh: 32000,
    currentLevelWh: 12000,
    chargeDischargeRateWatts: 500
  }) {
    id
    name
    deviceType
    otherDetails
  }
}
```

Validations:
- Device-type specific required fields
- Disallowed mixing fields across types
- `current_level_wh <= total_capacity_wh`

---

### 🛠️ `updateDevice`

```graphql
mutation {
  updateDevice(input: {
    id: 2,
    deviceType: "production",
    instantaneousOutputWatts: 4200
  }) {
    name
    otherDetails
  }
}
```

Validations:
- Checks ownership
- Ensures field updates are relevant to `deviceType`

---

### 📦 `allDevices`

```graphql
query {
  allDevices {
    id
    name
    status
    deviceType
    otherDetails
  }
}
```

Returns a merged list of all device types for the authenticated user.

---

### ⚡ `energyStats`

```graphql
query {
  energyStats {
    currentProduction
    currentConsumption
    currentStorage {
      totalCapacityWh
      currentLevelWh
      percentage
    }
    currentStorageFlow
    netGridFlow
    timestamp
  }
}
```

Reads pre-computed per-user stats from Redis. If no data exists, returns `null`.

---

## 📁 Project Structure Highlights

```bash
backend/
├── devices/
│   ├── models.py
│   ├── admin.py
│   ├── graphql/
│   │   ├── inputs.py
│   │   ├── types.py
│   │   ├── queries.py
│   │   ├── mutations.py
│   │   └── schema.py
│   ├── tasks.py ← Celery simulation logic
│   └── utils.py
├── entrypoint.sh
├── Dockerfile
└── docker-compose.yml
```

---

## 🔧 Extensibility Ideas

- Add pagination to `allDevices`
- Use Enums for `status` and `device_type`
- Add historical energy log support
- Rate-limit GraphQL endpoints
- Use `django-polymorphic` to simplify `allDevices` queries

## Future Work:

- 
---
## Built using:
- [Django 5.1.8](https://docs.djangoproject.com/)
- [Strawberry GraphQL](https://strawberry.rocks/)
- [Celery](https://docs.celeryq.dev/)
- [Redis](https://redis.io/)
- [PostgreSQL](https://www.postgresql.org/)
