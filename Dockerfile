FROM public.ecr.aws/lambda/python:3.13.2026.06.05.14 AS build

LABEL maintainer="Rafael Kübler da Silva"

COPY requirements.txt ${LAMBDA_TASK_ROOT}

RUN pip install --no-cache-dir -r requirements.txt

COPY . ${LAMBDA_TASK_ROOT}

CMD ["main.lambda_handler"]
