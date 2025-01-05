# Use a lightweight base image
FROM ubuntu:22.04

# Install necessary packages
RUN apt update && apt install -y gcc socat

# Create a working directory
WORKDIR /challenge

# Copy the challenge source code
COPY challenge.c .

# Compile the challenge
RUN gcc -o challenge challenge.c -no-pie -fno-stack-protector

# Expose the port, this does not actually mean the port is automatically exposed, that's done in the docker-compose
EXPOSE 1337

# Run socat to expose the binary
CMD ["socat", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:/challenge/challenge,stderr"]