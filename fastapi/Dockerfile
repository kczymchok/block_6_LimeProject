# FROM continuumio/miniconda3

# WORKDIR /home/app

# RUN apt-get update -y 
# RUN apt-get install nano unzip
# RUN apt-get install -y python3.10
# RUN apt install curl -y

# RUN curl -fsSL https://get.deta.dev/cli.sh | sh

# COPY requirements.txt /dependencies/requirements.txt
# RUN pip install -r /dependencies/requirements.txt

# COPY . /home/app

# CMD gunicorn app:app  --bind 0.0.0.0:$PORT --worker-class uvicorn.workers.UvicornWorker # 👈 This is the most important line

FROM continuumio/miniconda3

WORKDIR /home/app

RUN apt-get update -y 
RUN apt-get install nano unzip -y
RUN apt-get install -y python3.10
RUN apt install curl -y

RUN curl -fsSL https://get.deta.dev/cli.sh | sh

# Install setuptools and wheel
RUN pip install --upgrade pip setuptools wheel

# Copy and install dependencies
COPY requirements.txt /dependencies/requirements.txt
RUN pip install -r /dependencies/requirements.txt

# Copy your entire application directory to /home/app
COPY . /home/app

# Copy the machine learning model into the appropriate directory
COPY /model/Gradient_Boosting_Regressor_best_model.joblib /home/app/machine_learning/models/

# Set default port environment variable
ENV PORT=8000

# Run the application with gunicorn
CMD gunicorn app:app --bind 0.0.0.0:$PORT --worker-class uvicorn.workers.UvicornWorker




