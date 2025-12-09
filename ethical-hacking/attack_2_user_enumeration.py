#!/usr/bin/env python3
"""
🔴 ATAQUE 2: User Enumeration (Enumeración de Usuarios)

Demuestra cómo un atacante puede determinar qué usuarios existen en el sistema
cuando los mensajes de error revelan información específica.

ANTES: Mensajes específicos ("Username already exists" vs "Email already in use")
DESPUÉS: Mensajes genéricos ("Registration failed. Username or email might already be in use")
"""

import requests
import time
from typing import Dict, List

# Configuración
BASE_URL = "http://localhost:8000"
SIGNUP_ENDPOINT = f"{BASE_URL}/signup"

# Listas de usernames y emails comunes a probar
COMMON_USERNAMES = [
    "admin", "administrator", "root", "test", "user",
    "testuser", "demo", "guest", "support", "info",
    "contact", "sales", "marketing", "dev", "developer"
]

COMMON_EMAILS = [
    "admin@example.com",
    "test@test.com",
    "user@example.com",
    "info@example.com",
    "contact@example.com",
    "support@example.com"
]

def attempt_signup(name: str, username: str, email: str, password: str) -> Dict:
    """Intenta registrar un usuario"""
    try:
        response = requests.post(
            SIGNUP_ENDPOINT,
            json={
                "name": name,
                "username": username,
                "email": email,
                "password": password
            },
            timeout=5
        )
        return {
            "status_code": response.status_code,
            "message": response.json().get("message", "") if response.headers.get('content-type') == 'application/json' else response.text,
            "success": response.status_code == 200
        }
    except Exception as e:
        return {
            "status_code": None,
            "message": str(e),
            "success": False
        }

def enumerate_usernames_vulnerable(username_list: List[str]) -> List[str]:
    """
    ATAQUE en sistema VULNERABLE (con mensajes específicos)
    
    Prueba cada username y determina si existe basándose en el mensaje de error.
    Mensajes reveladores:
    - "Username already exists" → Usuario EXISTE ✓
    - "Email already in use" → Email existe pero username disponible
    - Otro error → Puede ser válido
    """
    print("\n" + "="*70)
    print("🔴 ENUMERACIÓN DE USUARIOS (Sistema Vulnerable)")
    print("="*70)
    print("Buscando mensajes específicos que revelen información...\n")
    
    found_users = []
    
    for username in username_list:
        # Usar email único para forzar error solo de username
        test_email = f"test_{username}_{int(time.time())}@test.com"
        
        print(f"Probando username: '{username}'...", end=" ")
        
        result = attempt_signup(
            name="Test User",
            username=username,
            email=test_email,
            password="Test123456"
        )
        
        message = result["message"].lower()
        
        # Análisis de mensajes específicos
        if "username" in message and ("exist" in message or "already" in message or "used" in message):
            print(f"✅ EXISTE - '{result['message']}'")
            found_users.append(username)
        else:
            print(f"❌ No existe - '{result['message']}'")
        
        time.sleep(0.3)
    
    print("\n" + "="*70)
    print(f"🎯 USUARIOS ENCONTRADOS: {len(found_users)}")
    if found_users:
        print("   - " + "\n   - ".join(found_users))
    print("="*70)
    
    return found_users

def enumerate_usernames_protected(username_list: List[str]) -> List[str]:
    """
    ATAQUE en sistema PROTEGIDO (con mensajes genéricos)
    
    Intenta la misma técnica pero con mensajes genéricos.
    Mensaje genérico: "Registration failed. Username or email might already be in use."
    
    Resultado: NO se puede determinar si es el username o email el que existe.
    """
    print("\n" + "="*70)
    print("🛡️ INTENTO DE ENUMERACIÓN (Sistema Protegido)")
    print("="*70)
    print("Intentando enumerar usuarios con mensajes genéricos...\n")
    
    uncertain_users = []
    
    for username in username_list:
        test_email = f"test_{username}_{int(time.time())}@test.com"
        
        print(f"Probando username: '{username}'...", end=" ")
        
        result = attempt_signup(
            name="Test User",
            username=username,
            email=test_email,
            password="Test123456"
        )
        
        message = result["message"].lower()
        
        # Con mensajes genéricos, no podemos distinguir
        if "might already be in use" in message or "might already exist" in message:
            print(f"⚠️  INCIERTO - '{result['message']}'")
            uncertain_users.append(username)
        elif result["success"]:
            print(f"✅ Registrado exitosamente")
        else:
            print(f"❌ Error diferente - '{result['message']}'")
        
        time.sleep(0.3)
    
    print("\n" + "="*70)
    print(f"⚠️  USUARIOS INCIERTOS: {len(uncertain_users)}")
    print("   (No se puede confirmar si existen o no)")
    if uncertain_users:
        print("   - " + "\n   - ".join(uncertain_users))
    print("="*70)
    
    return uncertain_users

def demo_sin_proteccion():
    """Demostración teórica del ataque sin protección"""
    print("\n" + "🔴"*35)
    print("ESCENARIO 1: MENSAJES DE ERROR ESPECÍFICOS (Vulnerable)")
    print("🔴"*35)
    print("""
⚠️  Sistema vulnerable con mensajes específicos:

Ejemplo de respuestas reveladores:
  ❌ "Username already exists"        → Usuario CONFIRMADO ✓
  ❌ "Email already in use"           → Email CONFIRMADO ✓
  ❌ "Invalid email format"           → Formato inválido

🎯 El atacante puede:
   1. Confirmar qué usuarios existen
   2. Construir lista de targets para ataques dirigidos
   3. Realizar phishing personalizado
   4. Priorizar contraseñas comunes para usuarios confirmados
   
💀 Riesgo: ALTO - Facilita ataques dirigidos
    """)

def demo_con_proteccion():
    """Demostración teórica de protección con mensajes genéricos"""
    print("\n" + "🛡️"*35)
    print("ESCENARIO 2: MENSAJES GENÉRICOS (Protegido)")
    print("🛡️"*35)
    print("""
✅ Sistema protegido con mensajes genéricos:

Ejemplo de respuestas NO reveladores:
  ⚠️  "Registration failed. Username or email might already be in use."
  
  → NO se puede confirmar qué campo está duplicado
  → NO se puede confirmar si el usuario existe

🛡️ El atacante NO puede:
   ❌ Confirmar existencia de usuarios
   ❌ Distinguir entre username y email duplicado
   ❌ Construir lista precisa de targets
   
✅ Beneficios:
   - Fase de reconocimiento más difícil
   - Reducción de ataques dirigidos
   - Mayor privacidad de usuarios
   
🔒 Riesgo: BAJO - Enumeración bloqueada
    """)

def demo_comparacion():
    """Comparación cuantitativa del impacto"""
    print("\n" + "="*70)
    print("📊 COMPARACIÓN DE IMPACTO")
    print("="*70)
    print(f"{'Métrica':<35} | {'Vulnerable':<15} | {'Protegido':<15}")
    print("-"*70)
    print(f"{'Confirmación de usuarios':<35} | {'100%':<15} | {'0%':<15}")
    print(f"{'Información revelada':<35} | {'Específica':<15} | {'Genérica':<15}")
    print(f"{'Tiempo para enumerar 1000 users':<35} | {'5 minutos':<15} | {'N/A':<15}")
    print(f"{'Facilita ataques dirigidos':<35} | {'Sí':<15} | {'No':<15}")
    print(f"{'Riesgo de phishing':<35} | {'Alto':<15} | {'Bajo':<15}")
    print(f"{'Privacidad de usuarios':<35} | {'Baja':<15} | {'Alta':<15}")
    print("="*70)

def demo_caso_real():
    """
    Caso real: Demostrar con el sistema actual
    
    Si tu sistema está PROTEGIDO, verás mensajes genéricos.
    Si NO está protegido, verás mensajes específicos.
    """
    print("\n" + "🔬"*35)
    print("PRUEBA REAL CONTRA EL SISTEMA")
    print("🔬"*35)
    print("\nProbando con usuarios comunes para ver el comportamiento...\n")
    
    # Probar con lista reducida
    test_usernames = ["admin", "test", "user", "guest", "demo"]
    
    enumerate_usernames_protected(test_usernames)
    
    print("\n💡 ANÁLISIS:")
    print("""
    Si ves mensajes como:
      ✅ "Registration failed. Username or email might already be in use."
         → Sistema PROTEGIDO correctamente
         
      ❌ "Username already exists"
         → Sistema VULNERABLE, necesita corrección
    """)

if __name__ == "__main__":
    print("\n" + "🎓"*35)
    print("DEMOSTRACIÓN: USER ENUMERATION Y MENSAJES GENÉRICOS")
    print("🎓"*35)
    print("""
Este script demuestra:
1. Cómo los mensajes de error específicos revelan información
2. Técnica de enumeración de usuarios
3. Impacto de mensajes genéricos en la seguridad
4. Comparación antes/después

⚠️  IMPORTANTE: Solo usar en entornos de prueba propios
    """)
    
    # Explicaciones teóricas
    demo_sin_proteccion()
    demo_con_proteccion()
    
    # Prueba real
    respuesta = input("\n¿Ejecutar prueba real contra localhost:8000? (s/n): ").lower()
    if respuesta == 's':
        demo_caso_real()
    else:
        print("\n⏭️  Saltando prueba real")
    
    # Comparación
    demo_comparacion()
    
    print("\n✅ Demostración completada")
    print("📝 Conclusión:")
    print("   - Mensajes específicos facilitan enumeración al 100%")
    print("   - Mensajes genéricos previenen confirmación de usuarios")
    print("   - Implementación simple con alto impacto en seguridad")
