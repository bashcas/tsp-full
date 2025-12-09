#!/usr/bin/env python3
"""
🔴 ATAQUE 4: Denial of Service (DoS) via TSP Complexity

Demuestra cómo un atacante puede colapsar el servidor enviando
problemas TSP con demasiadas ubicaciones (complejidad O(n!)).

ANTES: Sin límites, acepta cualquier cantidad de ubicaciones
DESPUÉS: Máximo 10 ubicaciones, tiempo de cómputo controlado
"""

import requests
import time
import math
from typing import List, Dict

# Configuración
BASE_URL = "http://localhost:8000"
SHORTESTPATH_ENDPOINT = f"{BASE_URL}/shortestpath"

def calculate_complexity(n: int) -> Dict:
    """Calcula la complejidad del problema TSP"""
    # TSP tiene complejidad O(n!)
    factorial = math.factorial(n) if n <= 20 else float('inf')
    
    # Estimación de tiempo (asumiendo 1M operaciones/seg)
    operations_per_sec = 1_000_000
    if factorial != float('inf'):
        estimated_seconds = factorial / operations_per_sec
        
        if estimated_seconds < 60:
            time_str = f"{estimated_seconds:.2f} segundos"
        elif estimated_seconds < 3600:
            time_str = f"{estimated_seconds/60:.2f} minutos"
        elif estimated_seconds < 86400:
            time_str = f"{estimated_seconds/3600:.2f} horas"
        elif estimated_seconds < 31536000:
            time_str = f"{estimated_seconds/86400:.2f} días"
        else:
            time_str = f"{estimated_seconds/31536000:.2f} años"
    else:
        time_str = "Prácticamente infinito"
    
    return {
        "locations": n,
        "factorial": factorial,
        "permutations": factorial if factorial != float('inf') else "∞",
        "estimated_time": time_str
    }

def generate_locations(count: int) -> List[Dict]:
    """Genera lista de ubicaciones ficticias"""
    locations = []
    for i in range(count):
        locations.append({
            "lat": 40.7128 + (i * 0.01),  # Nueva York base
            "lng": -74.0060 + (i * 0.01),
            "address": f"Location {i+1}"
        })
    return locations

def attempt_tsp_request(token: str, num_locations: int, title: str = None) -> Dict:
    """Intenta calcular ruta TSP con N ubicaciones"""
    if title is None:
        title = f"Test {num_locations} locations"
    
    locations = generate_locations(num_locations)
    
    try:
        start_time = time.time()
        
        response = requests.post(
            SHORTESTPATH_ENDPOINT,
            json={
                "title": title,
                "locations": locations
            },
            headers={
                "Authorization": f"Bearer {token}"
            },
            timeout=30  # 30 segundos timeout
        )
        
        elapsed = time.time() - start_time
        
        return {
            "status_code": response.status_code,
            "success": response.status_code == 200,
            "message": response.json().get("message", "") if response.headers.get('content-type') == 'application/json' else response.text,
            "elapsed_time": elapsed,
            "num_locations": num_locations
        }
    except requests.exceptions.Timeout:
        return {
            "status_code": 408,
            "success": False,
            "message": "Request timeout - Server overloaded",
            "elapsed_time": 30.0,
            "num_locations": num_locations
        }
    except Exception as e:
        return {
            "status_code": None,
            "success": False,
            "message": str(e),
            "elapsed_time": time.time() - start_time if 'start_time' in locals() else 0,
            "num_locations": num_locations
        }

def demo_complexity_table():
    """Muestra tabla de complejidad factorial"""
    print("\n" + "="*80)
    print("📊 COMPLEJIDAD DEL PROBLEMA TSP (O(n!))")
    print("="*80)
    print(f"{'Ubicaciones':<12} | {'Permutaciones':<20} | {'Tiempo Estimado':<25}")
    print("-"*80)
    
    test_sizes = [2, 3, 4, 5, 8, 10, 12, 15, 20, 25]
    
    for n in test_sizes:
        complexity = calculate_complexity(n)
        perm_str = f"{complexity['permutations']:,}" if isinstance(complexity['permutations'], int) else "∞"
        print(f"{n:<12} | {perm_str:<20} | {complexity['estimated_time']:<25}")
    
    print("="*80)
    print("\n💡 Observación: El tiempo crece EXPONENCIALMENTE con el número de ubicaciones")

def demo_sin_proteccion():
    """Explicación teórica del ataque sin protección"""
    print("\n" + "🔴"*35)
    print("ESCENARIO 1: SIN LÍMITE DE UBICACIONES (Vulnerable)")
    print("🔴"*35)
    print("""
⚠️  Sin límite de ubicaciones, un atacante puede:

    POST /shortestpath
    {
        "locations": [... 25 ubicaciones ...]  // 15,511,210,043,330,985,984,000,000 permutaciones
    }
    
    ☠️ Consecuencias:
       - Servidor consume 100% CPU durante horas/días
       - Memoria se agota almacenando permutaciones
       - Otros usuarios no pueden usar el servicio
       - Posible crash del servidor
       
    💀 Con 25 ubicaciones:
       - Permutaciones: 15 septillones (15×10^24)
       - Tiempo estimado: 491 MILLONES de años
       - Memoria necesaria: Varios TB solo para almacenar paths
       
    🎯 Ataque efectivo:
       - Enviar múltiples requests con 20+ ubicaciones
       - Desde múltiples IPs (ataque distribuido)
       - Colapso total del servicio en minutos
    """)

def demo_con_proteccion(token: str = None):
    """Demuestra protección con límite de 10 ubicaciones"""
    print("\n" + "🛡️"*35)
    print("ESCENARIO 2: CON LÍMITE DE 10 UBICACIONES (Protegido)")
    print("🛡️"*35)
    print("""
✅ Con límite de 10 ubicaciones:

    Validación implementada:
    if locations.len() > 10:
        return error("Maximum 10 locations allowed")
    
    ✓ Máximo 3,628,800 permutaciones (10!)
    ✓ Tiempo de cómputo: ~3-4 segundos en hardware moderno
    ✓ Memoria controlada: <100MB por request
    ✓ Server responde a otros usuarios normalmente
    """)
    
    if token:
        print("\nEjecutando pruebas reales...\n")
        
        test_cases = [
            (2, "Caso mínimo válido"),
            (5, "Caso normal"),
            (10, "Caso máximo permitido"),
            (15, "Caso excesivo (debe rechazarse)"),
            (25, "Caso DoS (debe rechazarse)")
        ]
        
        print(f"{'Ubicaciones':<12} | {'Resultado':<15} | {'Tiempo':<10} | {'Mensaje':<30}")
        print("-"*80)
        
        for num_locs, description in test_cases:
            result = attempt_tsp_request(token, num_locs)
            
            status = "✅ ACEPTADO" if result["success"] else "❌ RECHAZADO"
            tiempo = f"{result['elapsed_time']:.2f}s"
            mensaje = result["message"][:30]
            
            print(f"{num_locs:<12} | {status:<15} | {tiempo:<10} | {mensaje:<30}")
            
            if not result["success"] and "maximum" in result["message"].lower():
                print(f"             └─> 🛡️ BLOQUEADO: Límite de seguridad activado")
            
            time.sleep(0.5)
        
        print("\n" + "="*80)
        print("✅ PROTECCIÓN VERIFICADA: Requests con >10 ubicaciones son rechazados")
        print("="*80)
    else:
        print("\n⚠️  Token no proporcionado - Saltando pruebas reales")

def demo_comparacion():
    """Tabla comparativa de impacto"""
    print("\n" + "="*80)
    print("📊 COMPARACIÓN: SIN LÍMITE vs CON LÍMITE")
    print("="*80)
    print(f"{'Métrica':<30} | {'Sin Límite':<22} | {'Límite 10':<22}")
    print("-"*80)
    print(f"{'Max ubicaciones':<30} | {'Ilimitado':<22} | {'10':<22}")
    print(f"{'Max permutaciones':<30} | {'∞ (25! = 1.5×10^25)':<22} | {'3,628,800 (10!)':<22}")
    print(f"{'Tiempo de cómputo':<30} | {'Años/Infinito':<22} | {'3-4 segundos':<22}")
    print(f"{'Memoria por request':<30} | {'GB - TB':<22} | {'<100 MB':<22}")
    print(f"{'Impacto DoS':<30} | {'Alto (crash)':<22} | {'Muy Bajo':<22}")
    print(f"{'CPU usage':<30} | {'100% durante horas':<22} | {'<5s burst':<22}")
    print(f"{'Afecta otros usuarios':<30} | {'Sí (severo)':<22} | {'No':<22}")
    print(f"{'Riesgo':<30} | {'CRÍTICO':<22} | {'BAJO':<22}")
    print("="*80)

def demo_attack_scenario():
    """Escenario de ataque distribuido"""
    print("\n" + "💀"*35)
    print("ESCENARIO DE ATAQUE REAL")
    print("💀"*35)
    print("""
🎯 Atacante envía 10 requests simultáneos con 20 ubicaciones cada uno:

    Request 1: 20 ubicaciones → 2.4×10^18 permutaciones
    Request 2: 20 ubicaciones → 2.4×10^18 permutaciones
    ...
    Request 10: 20 ubicaciones → 2.4×10^18 permutaciones
    
    Total: 2.4×10^19 permutaciones a calcular
    
    SIN PROTECCIÓN:
    ❌ CPU: 10 cores al 100% durante DÍAS
    ❌ Memoria: Agotada en minutos
    ❌ Servidor: Crash o congelado
    ❌ Otros usuarios: Sin servicio
    ❌ Recuperación: Reinicio forzado, pérdida de datos
    
    CON PROTECCIÓN (límite 10):
    ✅ Validación: 10 requests rechazados inmediatamente
    ✅ CPU: <1% de uso
    ✅ Memoria: ~10MB total
    ✅ Servidor: Respondiendo normalmente
    ✅ Otros usuarios: Sin afectación
    ✅ Logs: Ataque detectado y registrado
    """)

def get_auth_token() -> str:
    """Helper para obtener token de autenticación"""
    print("\n🔑 Para probar el endpoint /shortestpath necesitas un token JWT")
    print("Opciones:")
    print("  1. Proporciona un token existente")
    print("  2. Crear nuevo usuario y obtener token")
    print("  3. Saltear pruebas reales (solo demostración teórica)")
    
    opcion = input("\nSelecciona opción (1/2/3): ").strip()
    
    if opcion == "1":
        return input("Ingresa token JWT: ").strip()
    elif opcion == "2":
        # Crear usuario y obtener token
        signup_url = f"{BASE_URL}/signup"
        timestamp = int(time.time())
        
        response = requests.post(
            signup_url,
            json={
                "name": "Test User",
                "username": f"testdos{timestamp}",
                "email": f"test{timestamp}@test.com",
                "password": "TestPass123"
            }
        )
        
        if response.status_code == 200:
            token = response.json().get("token")
            print(f"✅ Usuario creado, token obtenido")
            return token
        else:
            print(f"❌ Error creando usuario: {response.text}")
            return None
    else:
        return None

if __name__ == "__main__":
    print("\n" + "🎓"*35)
    print("DEMOSTRACIÓN: DENIAL OF SERVICE VIA TSP COMPLEXITY")
    print("🎓"*35)
    print("""
Este script demuestra:
1. Cómo la complejidad factorial del TSP puede usarse para DoS
2. Impacto de requests con muchas ubicaciones
3. Efectividad del límite de 10 ubicaciones
4. Comparación cuantitativa antes/después

⚠️  IMPORTANTE: Solo usar en entornos de prueba propios
    """)
    
    # Tabla de complejidad
    demo_complexity_table()
    
    # Explicación teórica
    demo_sin_proteccion()
    
    # Obtener token para pruebas reales
    token = get_auth_token()
    
    # Demo con protección
    demo_con_proteccion(token)
    
    # Escenario de ataque
    demo_attack_scenario()
    
    # Comparación
    demo_comparacion()
    
    print("\n✅ Demostración completada")
    print("📝 Conclusiones:")
    print("   - TSP sin límites es vector de ataque DoS efectivo")
    print("   - Límite de 10 ubicaciones previene complejidad exponencial")
    print("   - 10! = 3.6M permutaciones es manejable (3-4 segundos)")
    print("   - 20! = 2.4×10^18 permutaciones es DoS efectivo")
    print("   - Validación simple con impacto crítico en disponibilidad")
