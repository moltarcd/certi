# performance/parse_locust_results.py
import csv
import os
from datetime import datetime
from performance.models import PerformanceResult, MetricSnapshot

def parse_csv_to_model(test_type: str, duration_seconds: int, users: int) -> PerformanceResult:
    csv_path = f"reports/raw_perf_{test_type}_stats.csv"
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"No se encontró el archivo de métricas de Locust: {csv_path}")
        
    endpoints_metrics = []
    
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Ignoramos la fila del total acumulado para el mapeo individual, pero la usamos de referencia si es necesario
            if row["Name"] == "Aggregated":
                global_total = int(row["Request Count"])
                global_failures = int(row["Failure Count"])
                global_success_rate = ((global_total - global_failures) / global_total) * 100 if global_total > 0 else 0.0
                global_failure_rate = (global_failures / global_total) * 100 if global_total > 0 else 0.0
                global_throughput = float(row["Requests/s"])
                continue
                
            metric = MetricSnapshot(
                name=row["Name"],
                method=row["Type"],
                total_requests=int(row["Request Count"]),
                success_rate=((int(row["Request Count"]) - int(row["Failure Count"])) / int(row["Request Count"])) * 100,
                failure_rate=(int(row["Failure Count"]) / int(row["Request Count"])) * 100,
                avg_response_time=float(row["Average Response Time"]),
                min_response_time=float(row["Min Response Time"]),
                max_response_time=float(row["Max Response Time"]),
                p90=float(row["90%"]),
                p95=float(row["95%"]),
                p99=float(row["99%"]),
                throughput=float(row["Requests/s"])
            )
            endpoints_metrics.append(metric)
            
    return PerformanceResult(
        test_type=test_type,
        started_at=datetime.now(), # Idealmente capturado desde el run_performance_suite
        ended_at=datetime.now(),
        duration_seconds=duration_seconds,
        max_concurrent_users=users,
        global_total_requests=global_total,
        global_success_rate=global_success_rate,
        global_failure_rate=global_failure_rate,
        global_throughput=global_throughput,
        endpoints_metrics=endpoints_metrics
    )