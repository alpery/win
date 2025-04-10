# Win Application

This repository contains the Win application, which provides weather information through voice commands. The application consists of three main components:

1. **Win Frontend**: A Svelte 5 application that provides the user interface
2. **Win Backend**: A Kotlin Spring Boot application that provides weather data
3. **Python Backend**: A FastAPI application that provides speech-to-text functionality

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed on your machine
- [Docker Compose](https://docs.docker.com/compose/install/) installed on your machine
- [OpenWeatherMap API Key](#openweathermap-api-key) (required for weather data)

## OpenWeatherMap API Key

This application uses the OpenWeatherMap API to fetch weather data. Follow these steps to get your API key:

1. Register for a free account at [OpenWeatherMap](https://home.openweathermap.org/users/sign_up)
2. After registration and login, go to your [API keys](https://home.openweathermap.org/api_keys) page
3. Generate a new API key or use the default one provided
4. Create a `.env` file in the root directory of the project with the following content:
   ```
   OPENWEATHERMAP_API_KEY=your_api_key_here
   ```
5. Replace `your_api_key_here` with your actual OpenWeatherMap API key

**Note:** The `.env` file is already added to `.gitignore` to ensure your API key is not committed to the repository.

## Building and Running the Application

1. Navigate to the project root directory:
   ```bash
   cd /path/to/win
   ```

2. Build and start all services using Docker Compose:
   ```bash
   docker-compose up --build
   ```

   This command will:
   - Build the application images using the Dockerfiles
   - Pull the PostgreSQL and Redis images if not already available
   - Start all services
   - Connect the services to each other

3. To run the services in the background (detached mode):
   ```bash
   docker-compose up --build -d
   ```

4. Once all services are running, the application will be available at:
   ```
   http://localhost
   ```

## Stopping the Application

1. If running in the foreground, press `Ctrl+C` to stop all services.

2. If running in detached mode, use:
   ```bash
   docker-compose down
   ```

3. To stop and remove all containers, networks, and volumes:
   ```bash
   docker-compose down -v
   ```

## Service Details

- **Win Frontend**: Svelte application running on port 80
- **Win Backend**: Spring Boot application running on port 8080
- **Python Backend**: FastAPI application running on port 8765
- **PostgreSQL**: Database running on port 5432
  - Database: win_db
  - Username: win_user
  - Password: win_pass
- **Redis**: Cache running on port 6379

## API Endpoints

### Win Backend

- `GET /api/weather/{city}` - Get weather forecast for a city
- `GET /api/weather/{city}/range?startDate=YYYY-MM-DD&endDate=YYYY-MM-DD` - Get weather forecast for a city within a date range
- `GET /api/health` - Check the health of the application

### Python Backend

- `WebSocket /ws` - WebSocket endpoint for speech processing
- `GET /` - Health check endpoint

## Viewing Logs

To view logs for a specific service:
```bash
docker-compose logs win-frontend    # Frontend logs
docker-compose logs win-backend     # Backend logs
docker-compose logs python-backend  # Python Backend logs
docker-compose logs db              # PostgreSQL logs
docker-compose logs redis           # Redis logs
```

Add the `-f` flag to follow the logs:
```bash
docker-compose logs -f win-frontend
```

## Project Structure

- `win-frontend/`: Svelte 5 application
- `win-backend/`: Kotlin Spring Boot application
- `python-backend/`: FastAPI application
- `docker-compose.yml`: Docker Compose configuration
- `win-flowchart.md`: Application flowchart

## Docker Hub

The Docker images for this application are available on Docker Hub:

- [Win Frontend](https://hub.docker.com/r/yourusername/win-frontend)
- [Win Backend](https://hub.docker.com/r/yourusername/win-backend)
- [Python Backend](https://hub.docker.com/r/yourusername/python-backend)

To pull the images from Docker Hub:
```bash
docker pull yourusername/win-frontend
docker pull yourusername/win-backend
docker pull yourusername/python-backend
```

Replace `yourusername` with your Docker Hub username.