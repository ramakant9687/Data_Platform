import os


class DockerfileBuilder:
    def build_standard_dockerfile(self, base_docker_image: str = "") -> None:
        if len(base_docker_image) == 0:
            raise Exception("Dockerfile builder needs a base docker image. Check your rio.yml file!")

        dockerfile = f"""FROM {base_docker_image}

ARG JOB_BUILD_PROJECT
ENV JOB_BUILD_PROJECT=$JOB_BUILD_PROJECT
ARG JOB_DRI_TEAM
ENV JOB_DRI_TEAM=$JOB_DRI_TEAM
ARG SENTRY_DSN
ENV SENTRY_DSN=$SENTRY_DSN

# Extract the built app into /app.
COPY common /mnt/app/common
COPY jobs /mnt/app/jobs

# Copy the contents of pie-config to the predefined location /mnt/pie-config
COPY pie-config/ /mnt/pie-config/
        """
        with open(os.path.abspath(os.path.join(os.getcwd(), 'Dockerfile')), 'w') as out_file:
            out_file.write(dockerfile)
