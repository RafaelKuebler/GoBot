FROM public.ecr.aws/lambda/python:3.14.2026.07.03.13 AS build

LABEL maintainer="Rafael Kübler da Silva"

COPY requirements.txt ${LAMBDA_TASK_ROOT}

RUN pip install --no-cache-dir -r requirements.txt

COPY . ${LAMBDA_TASK_ROOT}

CMD ["main.lambda_handler"]
