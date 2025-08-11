SET "IMAGE=dt_image"
SET "CONTAINER=dt_container"
SET "LOGSDIR=%CD%/simLogs"

:: delete old logs
rmdir "%LOGSDIR%"
mkdir "%LOGSDIR%"

:: build container image
docker buildx build --tag "%IMAGE%" -f "%CD%/dockerfile" .

:: create a container from the built image and bind it to an existing mount (artifacts folder on the host), then start it
docker run --name "%CONTAINER%" --mount "type=bind,src=%LOGSDIR%,dst=/_tfms/logs/" "%IMAGE%"

:: stop and delete container
docker container stop "%CONTAINER%"
docker container rm "%CONTAINER%"

:: delete image
docker image rm "%IMAGE%" 