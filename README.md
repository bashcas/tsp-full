# TSP Project

This project is a Traveling Salesman Problem (TSP) solver with a Rust backend and a React frontend. It uses OpenStreetMap data to calculate routes.

## Prerequisites

-   [Docker](https://www.docker.com/) and Docker Compose
-   Google Maps API Key (Maps JavaScript API & Geocoding API)

## Setup

### 1. Data Files

The application requires two data files in the `tsp` directory:
-   `nodes.txt`
-   `edges.txt`

Ensure these files are present before running the application.

### 2. Environment Variables

You need to set up the Google Maps API Key for the frontend.

1.  Create a `.env` file in the root directory (or `tsp-front/.env` if running locally without Docker build args, but for Docker Compose, root is easier).
2.  Add your API Key:
    ```
    VITE_GOOGLE_MAPS_API_KEY=your_api_key_here
    ```

## Running the Application

The entire application (Backend + Frontend + Database) can be run using Docker Compose.

1.  Make sure you are in the project root.
2.  Run the following command:
    ```bash
    docker-compose up --build
    ```

This will:
-   Start a PostgreSQL database.
-   Build and start the Rust backend (listening on port 8000).
-   Build the React frontend and serve it with Nginx (listening on port 3000).

### Accessing the App

-   **Frontend**: [http://localhost:3000](http://localhost:3000)
-   **Backend**: [http://localhost:8000](http://localhost:8000)

## Development

-   **Backend**: Located in `tsp/`. Built with Rust and Rocket.
-   **Frontend**: Located in `tsp-front/`. Built with React and Vite.
