# Build Stage
FROM rust:slim-bookworm as builder

WORKDIR /app

# Install Git LFS first
RUN apt-get update && apt-get install -y git git-lfs && rm -rf /var/lib/apt/lists/*
RUN git lfs install

# Copy .git directory and .gitattributes (needed for LFS)
COPY .git .git
COPY .gitattributes .gitattributes

# Copy the tsp directory (build context should be repo root)
COPY tsp/ tsp/

# Pull LFS files (they will be pulled to tsp/nodes.txt and tsp/edges.txt)
RUN git lfs pull

# Move to tsp directory for building
WORKDIR /app/tsp

# Install dependencies for building
RUN apt-get update && apt-get install -y libpq-dev pkg-config libssl-dev && rm -rf /var/lib/apt/lists/*

# Install diesel_cli in builder stage
RUN cargo install diesel_cli --no-default-features --features postgres

# Build the application
RUN cargo build --release

# Runtime Stage
FROM debian:bookworm-slim

WORKDIR /app

# Install runtime dependencies (libpq for postgres)
RUN apt-get update && apt-get install -y libpq-dev ca-certificates && rm -rf /var/lib/apt/lists/*

# Copy the binary from the builder stage
COPY --from=builder /app/tsp/target/release/tsp /app/tsp

# Copy diesel_cli from builder stage
COPY --from=builder /usr/local/cargo/bin/diesel /usr/local/bin/diesel

# Copy other necessary files (like .env if needed, but better passed via docker-compose)
# We might need to copy migrations if we run them at startup
COPY --from=builder /app/tsp/migrations /app/migrations
COPY --from=builder /app/tsp/diesel.toml /app/diesel.toml

# Copy the LFS files (nodes.txt and edges.txt)
COPY --from=builder /app/tsp/nodes.txt /app/nodes.txt
COPY --from=builder /app/tsp/edges.txt /app/edges.txt

# Expose the port
EXPOSE 8000

# Command to run
CMD ["/bin/bash", "-c", "diesel migration run --database-url $DATABASE_URL && ./tsp"]
