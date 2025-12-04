# The python version to use is supplied as an arg from SST
ARG PYTHON_VERSION=3.11

# Use an official AWS Lambda base image for Python
FROM public.ecr.aws/lambda/python:${PYTHON_VERSION}

# Install build dependencies (Amazon Linux 2 uses yum, required for contourpy)
RUN yum install -y gcc-c++ && yum clean all

# Install uv for faster dependency installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy requirements and install dependencies
# SST places requirements.txt at the root of the artifact directory
COPY requirements.txt .
RUN uv pip install -r requirements.txt --target ${LAMBDA_TASK_ROOT} --system

# Copy the application code into the final image
# SST places built packages at the root of the artifact directory
COPY . ${LAMBDA_TASK_ROOT}

# SST sets the CMD handler automatically based on the handler property
