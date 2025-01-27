FROM maven:3.9.6-amazoncorretto-17 AS builder

WORKDIR /build

COPY pom.xml .
COPY src ./src

RUN mvn clean package -DskipTests

FROM railflow/blazetest:java-17

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN wget -O ${LAMBDA_TASK_ROOT}/junit-platform-console-standalone-1.11.2.jar https://repo1.maven.org/maven2/org/junit/platform/junit-platform-console-standalone/1.11.2/junit-platform-console-standalone-1.11.2.jar && \
    pip install boto3

COPY .blazetest/tests_runner_handler/junit_handler.py ${LAMBDA_TASK_ROOT}/junit_handler.py

COPY --from=builder /build/target/*.jar ${LAMBDA_TASK_ROOT}/

CMD ["junit_handler.run_tests"]
