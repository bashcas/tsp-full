#!/usr/bin/env python3
"""
🔴 ATAQUE 3: SQL Injection via Username

Demuestra intentos de inyección SQL a través del campo username
y cómo las validaciones previenen estos ataques.

ANTES: Validación débil, posible inyección SQL
DESPUÉS: Validación estricta (solo alfanumérico + guiones/underscores)
"""

import requests
import time
from typing import Dict, List

# Configuración
BASE_URL = "http://localhost:8000"
SIGNUP_ENDPOINT = f"{BASE_URL}/signup"

# Payloads de SQL Injection comunes
SQL_INJECTION_PAYLOADS = [
    # Comentarios SQL
    "admin'--",
    "admin'#",
    "admin'/*",
    
    # Union-based injection
    "' OR '1'='1",
    "' OR 1=1--",
    "' OR 'x'='x",
    "admin' OR '1'='1'--",
    
    # Boolean-based blind injection
    "' AND 1=1--",
    "' AND 1=2--",
    
    # Time-based blind injection
    "'; WAITFOR DELAY '0:0:5'--",
    "'; SELECT SLEEP(5)--",
    
    # Stacked queries
    "'; DROP TABLE users--",
    "'; DELETE FROM users--",
    "'; UPDATE users SET password='hacked'--",
    
    # Error-based injection
    "' AND 1=CONVERT(int, (SELECT @@version))--",
    
    # Bypass authentication
    "admin' OR '1'='1' /*",
    "' or 1=1 limit 1 -- -+",
    
    # Special characters
    "admin\\'--",
    "admin\\\"--",
    "1' UNION SELECT NULL--",
    "1' UNION SELECT NULL,NULL--",
    
    # NoSQL injection (para completitud)
    "' || '1'=='1",
    "admin' || 'a'=='a",
]

def attempt_signup_with_payload(payload: str) -> Dict:
    """Intenta registrarse con un payload de SQL injection en el username"""
    try:
        response = requests.post(
            SIGNUP_ENDPOINT,
            json={
                "name": "Test User",
                "username": payload,
                "email": f"test{int(time.time())}@test.com",
                "password": "TestPass123"
            },
            timeout=5
        )
        return {
            "status_code": response.status_code,
            "message": response.json().get("message", "") if response.headers.get('content-type') == 'application/json' else response.text,
            "success": response.status_code == 200,
            "payload": payload
        }
    except requests.exceptions.Timeout:
        return {
            "status_code": None,
            "message": "TIMEOUT - Posible time-based injection",
            "success": False,
            "payload": payload
        }
    except Exception as e:
        return {
            "status_code": None,
            "message": str(e),
            "success": False,
            "payload": payload
        }

def test_sql_injection_vulnerable():
    """
    Demostración: Sistema VULNERABLE sin validación
    
    En un sistema vulnerable:
    - Payloads pasan la validación
    - Llegan al query SQL
    - Pueden causar errores SQL, bypass, o data leak
    """
    print("\n" + "="*70)
    print("🔴 ESCENARIO 1: SISTEMA VULNERABLE (Sin Validación)")
    print("="*70)
    print("""
⚠️  En sistema SIN validación adecuada:

    username = request.json['username']  # ❌ Sin validar
    query = f"INSERT INTO users (username) VALUES ('{username}')"
    
Ejemplo de exploit:
    Username: admin'--
    Query resultante: INSERT INTO users (username) VALUES ('admin'--')
                     Comentario SQL →                              ^
    
    ☠️ Consecuencias posibles:
       - Bypass de autenticación
       - Lectura de datos sensibles (passwords, emails)
       - Modificación/eliminación de datos
       - Ejecución de comandos del sistema (en casos extremos)
    """)

def test_sql_injection_protected(payload_list: List[str]):
    """
    Prueba payloads contra sistema PROTEGIDO
    
    Con validación implementada:
    - Username: 3-50 caracteres
    - Solo alfanumérico + guiones/underscores
    - Rechaza caracteres especiales SQL ('", --, /*, etc.)
    """
    print("\n" + "="*70)
    print("🛡️ ESCENARIO 2: SISTEMA PROTEGIDO (Con Validación)")
    print("="*70)
    print("""
✅ Validación implementada:

    if not re.match(r'^[a-zA-Z0-9_-]{3,50}$', username):
        return error("Username can only contain letters, numbers, hyphens and underscores")
    
    ✓ Solo caracteres permitidos: a-z, A-Z, 0-9, _, -
    ✓ Longitud: 3-50 caracteres
    ✓ RECHAZA: ', ", --, /*, ;, etc.
    """)
    
    print("\nProbando payloads de SQL injection...\n")
    
    blocked_count = 0
    timeout_count = 0
    success_count = 0
    error_count = 0
    
    results = []
    
    for i, payload in enumerate(payload_list, 1):
        print(f"[{i:02d}/{len(payload_list)}] Testing: {payload[:50]:<50}", end=" ")
        
        result = attempt_signup_with_payload(payload)
        results.append(result)
        
        if result["success"]:
            print("❌ ÉXITO (Vulnerable!)")
            success_count += 1
        elif result["status_code"] == 400:
            # Validación rechazó el payload
            if "can only contain" in result["message"].lower() or "must be between" in result["message"].lower():
                print("✅ BLOQUEADO")
                blocked_count += 1
            else:
                print(f"⚠️  Error: {result['message'][:40]}")
                error_count += 1
        elif "TIMEOUT" in result["message"]:
            print("⏰ TIMEOUT (Posible vuln time-based)")
            timeout_count += 1
        else:
            print(f"⚠️  Otro: {result['message'][:40]}")
            error_count += 1
        
        time.sleep(0.2)
    
    # Resumen
    print("\n" + "="*70)
    print("📊 RESULTADOS DEL ATAQUE")
    print("="*70)
    print(f"Total de payloads probados: {len(payload_list)}")
    print(f"✅ Bloqueados por validación: {blocked_count} ({blocked_count/len(payload_list)*100:.1f}%)")
    print(f"❌ Exitosos (VULNERABLE): {success_count} ({success_count/len(payload_list)*100:.1f}%)")
    print(f"⏰ Timeouts (Posible vuln): {timeout_count}")
    print(f"⚠️  Otros errores: {error_count}")
    print("="*70)
    
    if blocked_count == len(payload_list):
        print("\n🎉 ¡PROTECCIÓN EXITOSA! Todos los payloads fueron bloqueados.")
    elif success_count > 0:
        print(f"\n⚠️  VULNERABILIDAD DETECTADA: {success_count} payloads pasaron la validación")
        print("Payloads exitosos:")
        for r in results:
            if r["success"]:
                print(f"   - {r['payload']}")
    else:
        print("\n✅ Sistema parcialmente protegido (algunos payloads bloqueados)")
    
    return results

def demo_orm_protection():
    """Explicación de protección adicional con ORM (Diesel)"""
    print("\n" + "🛡️"*35)
    print("CAPA ADICIONAL DE PROTECCIÓN: ORM (Diesel)")
    print("🛡️"*35)
    print("""
✅ El proyecto usa Diesel ORM que proporciona:

1. Prepared Statements automáticos:
   
   // ✅ Código seguro con Diesel
   diesel::insert_into(users::table)
       .values(&new_user)
       .execute(&conn)
   
   → Los valores NUNCA se concatenan directamente al SQL
   → El driver parameteriza automáticamente
   → Imposible inyección SQL a nivel de ORM

2. Type Safety:
   
   #[derive(Insertable)]
   struct NewUser {
       username: String,  // Tipo verificado en compile time
   }
   
   → Si intento pasar un tipo incorrecto, no compila

3. Query Builder:
   
   users::table
       .filter(users::username.eq(username))
       .first(&conn)
   
   → Sintaxis type-safe, no strings concatenados

📚 Defensa en profundidad:
   Capa 1: Validación de input (regex) → Bloquea payloads
   Capa 2: Diesel ORM                  → Prepared statements
   Capa 3: PostgreSQL                  → Permisos de usuario DB
    """)

def demo_comparacion():
    """Tabla comparativa"""
    print("\n" + "="*70)
    print("📊 COMPARACIÓN: VULNERABLE vs PROTEGIDO")
    print("="*70)
    print(f"{'Aspecto':<30} | {'Sin Validación':<18} | {'Con Validación':<18}")
    print("-"*70)
    print(f"{'Caracteres especiales':<30} | {'Permitidos':<18} | {'Bloqueados':<18}")
    print(f"{'Payloads bloqueados':<30} | {'0%':<18} | {'100%':<18}")
    print(f"{'Riesgo de SQLi':<30} | {'Alto':<18} | {'Muy Bajo':<18}")
    print(f"{'Comentarios SQL (--)':<30} | {'Pasan':<18} | {'Rechazados':<18}")
    print(f"{'Comillas simples':<30} | {'Permitidas':<18} | {'Rechazadas':<18}")
    print(f"{'Union-based attack':<30} | {'Posible':<18} | {'Imposible':<18}")
    print(f"{'ORM protection':<30} | {'Solo ORM':<18} | {'Validación+ORM':<18}")
    print("="*70)

def demo_ejemplos_bloqueados():
    """Mostrar ejemplos específicos de payloads bloqueados"""
    print("\n" + "🚫"*35)
    print("EJEMPLOS DE PAYLOADS BLOQUEADOS")
    print("🚫"*35)
    
    examples = [
        ("admin'--", "Contiene comilla simple (') - RECHAZADA"),
        ("' OR '1'='1", "Contiene comillas y espacios - RECHAZADA"),
        ("'; DROP TABLE users--", "Contiene punto y coma (;) y comillas - RECHAZADA"),
        ("admin\"--", "Contiene comilla doble (\") - RECHAZADA"),
        ("1' UNION SELECT", "Contiene comilla (') - RECHAZADA"),
        ("admin_user", "Alfanumérico con underscore - ✅ PERMITIDA"),
        ("test-user-123", "Alfanumérico con guiones - ✅ PERMITIDA"),
        ("ValidUser2024", "Solo alfanumérico - ✅ PERMITIDA"),
    ]
    
    print("\n" + f"{'Payload':<30} | {'Resultado':<40}")
    print("-"*72)
    for payload, resultado in examples:
        symbol = "✅" if "PERMITIDA" in resultado else "❌"
        print(f"{symbol} {payload:<28} | {resultado}")
    print()

if __name__ == "__main__":
    print("\n" + "🎓"*35)
    print("DEMOSTRACIÓN: SQL INJECTION Y VALIDACIÓN DE INPUTS")
    print("🎓"*35)
    print("""
Este script demuestra:
1. Técnicas comunes de SQL Injection
2. Cómo la validación de inputs previene SQLi
3. Protección adicional del ORM (Diesel)
4. Comparación cuantitativa antes/después

⚠️  IMPORTANTE: Solo usar en entornos de prueba propios
    """)
    
    # Explicaciones teóricas
    test_sql_injection_vulnerable()
    
    input("\nPresiona Enter para ejecutar prueba real contra el sistema...")
    
    # Prueba real
    test_sql_injection_protected(SQL_INJECTION_PAYLOADS)
    
    # Protección ORM
    demo_orm_protection()
    
    # Ejemplos específicos
    demo_ejemplos_bloqueados()
    
    # Comparación
    demo_comparacion()
    
    print("\n✅ Demostración completada")
    print("📝 Conclusiones:")
    print("   - Validación de inputs es primera línea de defensa")
    print("   - Regex estricto bloquea 100% de payloads SQLi comunes")
    print("   - ORM (Diesel) proporciona capa adicional de protección")
    print("   - Defensa en profundidad = Múltiples capas de seguridad")
