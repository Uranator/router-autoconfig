#!/usr/bin/env python3
import json
import subprocess
import time
import statistics
import socket
import ssl
import sys
from datetime import datetime

VPS_IP = "138.124.112.202"
PORTS = {
    "443": "tcp",
    "8388": "tcp",
    "8445": "udp"
}
ITERATIONS = 10

def run_ping(host, count=1):
    """Run ping and return latency in ms"""
    try:
        result = subprocess.run(
            ["ping", "-c", str(count), "-W", "2", host],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            # Parse ping output for average time
            for line in result.stdout.split('\n'):
                if 'avg' in line or 'average' in line:
                    parts = line.split('/')
                    if len(parts) >= 5:
                        return float(parts[4])
        return None
    except Exception as e:
        return None

def tcp_connect(host, port, timeout=2):
    """Measure TCP connection time in ms"""
    try:
        start = time.perf_counter()
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.close()
        elapsed = (time.perf_counter() - start) * 1000
        return elapsed
    except Exception:
        return None

def tls_handshake(host, port, timeout=5):
    """Measure TLS handshake time in ms"""
    try:
        start = time.perf_counter()
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        sock = socket.create_connection((host, port), timeout=timeout)
        ssock = context.wrap_socket(sock, server_hostname=host)
        ssock.do_handshake()
        ssock.close()
        elapsed = (time.perf_counter() - start) * 1000
        return elapsed
    except Exception:
        return None

def udp_test(host, port, timeout=2):
    """Test UDP connectivity - send packet and check response"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        start = time.perf_counter()
        sock.sendto(b"test", (host, port))
        try:
            sock.recvfrom(1024)
            elapsed = (time.perf_counter() - start) * 1000
            return elapsed
        except socket.timeout:
            return None
        finally:
            sock.close()
    except Exception:
        return None

def measure_packet_loss(host, port, protocol, iterations=10):
    """Measure packet loss percentage"""
    success = 0
    for _ in range(iterations):
        if protocol == "tcp":
            result = tcp_connect(host, port, timeout=1)
        elif protocol == "udp":
            result = udp_test(host, port, timeout=1)
        else:
            result = None
        if result is not None:
            success += 1
    loss_pct = ((iterations - success) / iterations) * 100
    return loss_pct

def main():
    results = {
        "vps_ip": VPS_IP,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "iterations": ITERATIONS,
        "latency_ms": {},
        "packet_loss_pct": {},
        "tls_handshake_ms": None,
        "benchmark_file": "~/router-autoconfig/generated/vps-benchmark.json"
    }

    print(f"Starting VPS benchmark for {VPS_IP}...")
    
    # Latency tests (using ping for ICMP, TCP connect for TCP ports, UDP for UDP port)
    for port_str, protocol in PORTS.items():
        port = int(port_str)
        latencies = []
        
        if protocol == "tcp":
            for i in range(ITERATIONS):
                lat = tcp_connect(VPS_IP, port)
                if lat:
                    latencies.append(lat)
                time.sleep(0.1)
        elif protocol == "udp":
            for i in range(ITERATIONS):
                lat = udp_test(VPS_IP, port)
                if lat:
                    latencies.append(lat)
                time.sleep(0.1)
        
        if latencies:
            results["latency_ms"][port_str] = {
                "min": round(min(latencies), 2),
                "max": round(max(latencies), 2),
                "avg": round(statistics.mean(latencies), 2),
                "median": round(statistics.median(latencies), 2),
                "stdev": round(statistics.stdev(latencies), 2) if len(latencies) > 1 else 0,
                "samples": len(latencies)
            }
        else:
            results["latency_ms"][port_str] = {"error": "All attempts failed"}

    # Packet loss tests
    for port_str, protocol in PORTS.items():
        port = int(port_str)
        loss = measure_packet_loss(VPS_IP, port, protocol, ITERATIONS)
        results["packet_loss_pct"][port_str] = round(loss, 2)

    # TLS handshake (only for port 443)
    print("Measuring TLS handshake on port 443...")
    tls_times = []
    for i in range(ITERATIONS):
        tls = tls_handshake(VPS_IP, 443)
        if tls:
            tls_times.append(tls)
        time.sleep(0.2)
    
    if tls_times:
        results["tls_handshake_ms"] = round(statistics.mean(tls_times), 2)
    else:
        results["tls_handshake_ms"] = None

    # Save results
    output_path = "/Users/uranator/router-autoconfig/generated/vps-benchmark.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to {output_path}")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()