FROM docker.apple.com/base-images/ubi9/ubi-builder:latest

# The directory containing the built application.
ARG RIO_APP_DIR
# The directory containing the needed runtimes (e.g. Python, Java, Ruby).
ARG RIO_RUNTIME_DIR
# BUILD ENVIRONMENT
ARG GIT_BRANCH
ARG GIT_COMMIT

# Copy the runtime into /app/python.
COPY $RIO_RUNTIME_DIR /mnt/app/.runtimes/
# Extract the built app into /app.
ADD $RIO_APP_DIR/*/my_project*.tar /mnt/app/

# Install build dependencies
RUN /mnt/app/.runtimes/python/bin/python -m pip install /mnt/app/apple_amp_ds_platform_cli*/

ENV PATH="/mnt/app/.runtimes/python/bin:$PATH"
ENV LD_LIBRARY_PATH="/usr/lib64:/mnt/app/.runtimes/python/lib:${LD_LIBRARY_PATH:-}"
ENV LIBRARY_PATH="/mnt/app/.runtimes/python/lib"
ENV PYTHONPATH=/mnt/app/my_project*
ENV RIO_BUILD_GIT_BRANCH=$GIT_BRANCH
ENV RIO_BUILD_GIT_COMMIT=$GIT_COMMIT