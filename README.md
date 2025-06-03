# ⚡ Smart Home Energy Management System — Backend API

A Dockerized Django + Strawberry GraphQL backend for simulating and managing smart home energy devices. This system supports three types of energy decvices - production, consumption and storage. Per-user energy stats aggregation and real-time simulation are enabled by periodic tasks using Celery + Redis.

---

## 🚀 Features

- ✅ [APIs](https://github.com/pranman11/smart-home-energy-mgmt?tab=readme-ov-file#-graphql-api-endpoints): GraphQL API for creating, updating, retrieving devices, and user stats 
- ✅ [Simulation](https://github.com/pranman11/smart-home-energy-mgmt?tab=readme-ov-file#-periodic-task-simulate-device-readings): Periodic tasks to generate energy readings per device
- ✅ Per-user energy statistics cached in Redis
- ✅ [Admin panel](https://github.com/pranman11/smart-home-energy-mgmt?tab=readme-ov-file#-periodic-task-simulate-device-readings) with role-based access
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
- Seeds initial users + device data using a management command
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

Further, users will need to be granted permission (by the admin) to view their devices from the admin portal. All users have been given a username and password (user{i}/password123) during the inital seeding. Users are not granted access to add or update devices from admin. This is only allowed via API endpoints described later.

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
- `instantaneous_output_watts` is simulated between **1000–5000W**.
- Solar devices produce `0` watts outside daylight hours (6 AM and 6 PM).
- Generators can produce power any time.

### 2. Consumption Devices
- `consumption_rate_watts` is simulated between **500–3000W**, at any time.

### 3. Storage Devices
- Simulate `charge_discharge_rate_watts` between **-1000 to +1000W**
- Clamp `current_level_wh` to be within `[0, total_capacity_wh]`
- Compute actual flow as `new_level - current_level`

### Aggregation
- After simulation, data is aggregated per user and stored in Redis:
```
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

Note: JWT Authentication is under development and not currently tested. Instead, we can interact with the API endpoints by using the Django Admin login. Login to the Django Admin [portal](http://localhost:8000/admin/)  using any non-admin user's credentials and navigate to the graphql playground below to access the user's device details and stats.

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
## Assumptions

- Users are allowed to update all fields (except id and timestamps) while using the create and update APIs
---

## 🔧 Future Work and Extensibility Ideas

- Add pagination and caching to `allDevices`
- Use Enums for `status` and `device_type`
- Rate-limit GraphQL endpoints
- Use `django-polymorphic` to simplify `allDevices` queries 
- Display a consolidated admin to show all devices
- Handle devices that can be part of both Consumption and Storage like EVs
 
---
## Built using:
- [Django 5.1.8](https://docs.djangoproject.com/)
- [Strawberry GraphQL](https://strawberry.rocks/)
- [Celery](https://docs.celeryq.dev/)
- [Redis](https://redis.io/)
- [PostgreSQL](https://www.postgresql.org/)
