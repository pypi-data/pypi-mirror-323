# MoveEV Common Models

This package contains the common models used for Electric Vehicle (EV) Charging Data across the MoveEV ecosystem.

## Overview

The `moveev_common` package provides a set of standardized data models that represent various aspects of EV charging sessions, vehicle information, and location data. These models ensure consistency and interoperability between different components of the MoveEV platform.

## Models

The package includes the following main models:

1. **ChargingEvent**: Represents individual charging events with detailed metrics including:

   - Charging duration and timestamps
   - Energy consumed (kWh)
   - Voltage and current measurements (milli-volts, milli-amps)
   - Location data (lat/long)
   - Provider-specific information
   - Start/end energy measurements (micro-watt-hours)
   - Charging power (kilowatts)

2. **ChargingStat**: Tracks real-time charging statistics including:

   - State of charge (milli-percent)
   - Charging voltage and current
   - Energy consumption
   - Location data
   - Odometer readings (meters)
   - Vehicle telemetry

3. **Vehicle**: Contains vehicle information including:

   - VIN number
   - Telematics device details (ID, hardware ID, name)
   - Credential associations
   - Creation and update timestamps
   - Additional metadata (JSONB)

4. **Credential**: Manages authentication and access credentials for:

   - Various charging providers
   - Telematics systems
   - API integrations
   - Username/password pairs
   - Database connections

5. **Client**: Manages client application information including:

   - Client name
   - Authentication token
   - Service associations

6. **ClientService**: Manages client service configurations including:

   - Client associations
   - Service endpoints
   - Event logging relationships

7. **Service**: Defines available services including:

   - Service name
   - Service URL
   - Integration endpoints

8. **EventLog**: Tracks event notifications including:

   - Charging event references
   - Client service associations
   - Timestamp information
   - Delivery status

9. **LastRunTime**: Tracks service execution times including:

   - Credential associations
   - Job name
   - Last execution timestamp

10. **Location**: Represents geographical location data including:
    - Latitude and longitude
    - Resolved address information
    - Associated charging events

## Usage

These models can be imported and used in various MoveEV projects to ensure consistent data structures when working with EV charging data. They provide a common language for different components of the system to communicate and share information effectively.

## Contributing

When adding new fields or modifying existing models, please ensure that changes are reflected across all relevant components of the MoveEV ecosystem to maintain consistency.

For more detailed information about each model and its fields, please refer to the source code and inline documentation.

## Database Migrations

## Generating Migrations

1. Make your model changes in the appropriate files under `src/moveev_common/`.
   For example, to add new fields to a model:

   ```python
   class Credential(Base):
       # ... existing fields ...
       session_id = Column(String)
       session_expiry = Column(DateTime)
   ```

2. Activate your virtual environment:

   ```bash
   source .venv/bin/activate
   ```

3. Generate the migration script:

   ```bash
   alembic revision --autogenerate -m "description of your changes"
   ```

   This will create a new migration file in the `alembic/versions/` directory.

4. Review the generated migration file to ensure it correctly captures your changes.
   The file will be named something like `1234abcd_description_of_your_changes.py`.

5. If the migration looks correct, proceed to running the migration as described below.

To run database migrations:

### Running Migrations

#### Local Development

```bash
alembic -x environment=local upgrade head
```

#### Production

```bash
alembic -x environment=production upgrade head
```

Make sure your `.env` file contains both sets of database credentials:

- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `POSTGRES_DB`

AND

- `POSTGRES_USER_PRODUCTION`
- `POSTGRES_PASSWORD_PRODUCTION`
- `POSTGRES_HOST_PRODUCTION`
- `POSTGRES_PORT_PRODUCTION`
- `POSTGRES_DB_PRODUCTION`
