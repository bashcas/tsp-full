# Build Stage
FROM rust:slim-bookworm as builder

WORKDIR /app

# Copy the tsp directory (build context should be repo root)
# Note: LFS files must be pulled BEFORE Docker build (see Render.com build command)
COPY tsp/ tsp/

# Verify LFS files were pulled (not pointer files) before moving to tsp directory
RUN if head -1 tsp/nodes.txt 2>/dev/null | grep -q "version https://git-lfs"; then \
        echo "ERROR: nodes.txt is still an LFS pointer file!"; \
        echo "LFS files must be pulled before Docker build. Add to Render.com build command:"; \
        echo "  git lfs install && git lfs pull"; \
        exit 1; \
    fi && \
    if head -1 tsp/edges.txt 2>/dev/null | grep -q "version https://git-lfs"; then \
        echo "ERROR: edges.txt is still an LFS pointer file!"; \
        echo "LFS files must be pulled before Docker build. Add to Render.com build command:"; \
        echo "  git lfs install && git lfs pull"; \
        exit 1; \
    fi

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
