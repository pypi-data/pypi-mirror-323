FROM maven:3.9.6-amazoncorretto-17 AS builder

WORKDIR /build

COPY pom.xml .
COPY src ./src

RUN mvn clean package -DskipTests

FROM railflow/blazetest:java-17

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SE_CACHE_PATH=/tmp/

RUN wget -O ${LAMBDA_TASK_ROOT}/testng-7.8.0.jar https://repo1.maven.org/maven2/org/testng/testng/7.8.0/testng-7.8.0.jar && \
    wget -O ${LAMBDA_TASK_ROOT}/jcommander-1.82.jar https://repo1.maven.org/maven2/com/beust/jcommander/1.82/jcommander-1.82.jar && \
    pip install boto3

COPY .blazetest/tests_runner_handler/testng_handler.py testng.xml* ${LAMBDA_TASK_ROOT}/

COPY --from=builder /build/target/*.jar ${LAMBDA_TASK_ROOT}/

CMD ["testng_handler.run_tests"]
