# Tienda online - DevOps práctica

**Autor:** David Cortés Martínez

Asignatura: Arquitectura del Software (UIE).

## Descripción

Aplicación Python de una **tienda online** expuesta como **API REST** con FastAPI.
Permite gestionar usuarios (clientes y administradores), productos (genéricos,
electrónicos y de ropa) y pedidos. Los datos se guardan en memoria.

El proyecto parte del código de la Práctica 2 e incluye:

- `src/api`: la API REST (FastAPI + Pydantic).
- `src/cliente`: un cliente Python que consume la API con `requests`.
- `src/frontend`: una página web sencilla que consume la API con `fetch`.

En este repositorio se versiona el proyecto con Git/GitHub y se contenerizará con Docker.
