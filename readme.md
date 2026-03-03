# 🚀 Intraday Intelligence Platform & Multiactivo Bot

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Polars](https://img.shields.io/badge/data_engine-Polars-yellow.svg)
![Status](https://img.shields.io/badge/status-production_ready-green.svg)

Sistema automatizado de análisis técnico y detección de señales de trading en tiempo real. El bot monitorea una watchlist de criptomonedas, evalúa condiciones estadísticas (RSI + SMA_200) y genera alertas visuales completas enviadas directamente a Telegram.

## 🏗️ Arquitectura del Sistema (Capas)

El proyecto está diseñado siguiendo una arquitectura modular para garantizar estabilidad y escalabilidad:

1.  **Capa 1: Ingesta (Data Loader):** Conexión con Yahoo Finance API para descarga de velas de 5 minutos.
2.  **Capa 2: Procesamiento (Feature Engineering):** Motor de cálculo basado en **Polars** para indicadores técnicos (RSI, SMA, ATR).
3.  **Capa 3: Estrategia (Logic):** Filtro de tendencia con SMA_200 y detección de reversión con RSI.
4.  **Capa 4: Gestión de Riesgo (Risk Manager):** Cálculo dinámico del tamaño de posición basado en la volatilidad y el balance de cuenta.
5.  **Capa 5: Auditoría (Trade Logger):** Registro automático de cada señal en un archivo CSV para análisis posterior (Backtesting).
6.  **Capa 6: Notificación (Alerts):** Generación de gráficos técnicos con Matplotlib y entrega vía Telegram Bot API.

## 🛠️ Características Principales

* **Scanner Multiactivo:** Monitoreo simultáneo de BTC, ETH, SOL, BNB y AVAX.
* **Alertas Visuales:** Envío de gráficos de velas que incluyen indicadores y marcadores de entrada.
* **Ejecución Serverless:** Configurado para correr 24/7 mediante **GitHub Actions** sin coste de servidor.
* **Blindaje de Seguridad:** Gestión de credenciales mediante variables de entorno y Secrets de GitHub.

## 📊 Ejemplo de Alerta en Telegram

> **🚀 NUEVA SEÑAL: BTC-USD**
> ━━━━━━━━━━━━━━━━━━
> **Tipo:** LONG
> **Precio:** $67,967.48
> **SL:** $66,608.13 | **TP:** $71,365.85
> **Riesgo:** 0.5%
> ━━━━━━━━━━━━━━━━━━
> *Incluye gráfico técnico adjunto.*

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone [https://github.com/IldefonsoTH/Intraday_platform.git](https://github.com/IldefonsoTH/Intraday_platform.git)
cd Intraday_platform