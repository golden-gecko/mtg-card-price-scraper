#!/bin/bash -ex

cd "$(dirname "$0")"

minikube addons enable dashboard
minikube addons enable ingress
minikube addons enable registry

minikube start --cpus=4 --memory=6g --vm-driver=kvm2 -p cenykart
minikube profile cenykart
