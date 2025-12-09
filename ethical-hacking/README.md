# 🎓 Guía de Hacking Ético - TSP Security Testing

Esta carpeta contiene scripts de demostración de vulnerabilidades y sus mitigaciones implementadas en el proyecto TSP.

## ⚠️ IMPORTANTE - Uso Ético
No nos hacemos responsable de el uso de cualquiera de estos scripts fuera de pruebas en local con este proyecto libre.

## 📋 Scripts Disponibles

### 1. `attack_1_brute_force.py` - Brute Force & Rate Limiting

**Vulnerabilidad**: Ataques de fuerza bruta en login sin límites

**Demostración**:
- ✅ Cómo funciona un ataque de fuerza bruta
- ✅ Impacto sin rate limiting (1000+ intentos/min)
- ✅ Protección con rate limiting (5 intentos/min)
- ✅ Comparación cuantitativa antes/después

**Uso**:
```bash
python3 attack_1_brute_force.py
```

**Resultado esperado**: El ataque es bloqueado después de 5 intentos con HTTP 429.

---

### 2. `attack_2_user_enumeration.py` - User Enumeration

**Vulnerabilidad**: Mensajes de error específicos revelan existencia de usuarios

**Demostración**:
- ✅ Enumeración de usuarios vía mensajes de error
- ✅ Diferencia entre "Username exists" vs mensaje genérico
- ✅ Impacto en fase de reconocimiento del atacante

**Uso**:
```bash
python3 attack_2_user_enumeration.py
```

**Resultado esperado**: Mensajes genéricos previenen confirmación de usuarios.

---

### 3. `attack_3_sql_injection.py` - SQL Injection

**Vulnerabilidad**: Inyección SQL via campo username

**Demostración**:
- ✅ 20+ payloads comunes de SQL injection
- ✅ Validación con regex que rechaza caracteres especiales
- ✅ Protección adicional del ORM (Diesel)
- ✅ Defense in depth (múltiples capas)

**Uso**:
```bash
python3 attack_3_sql_injection.py
```

**Resultado esperado**: Todos los payloads son bloqueados por validación (100%).

---

### 4. `attack_4_dos_tsp.py` - Denial of Service via TSP

**Vulnerabilidad**: Problemas TSP con muchas ubicaciones colapsan el servidor

**Demostración**:
- ✅ Complejidad factorial del TSP (O(n!))
- ✅ Tabla de tiempos: 10! = 3.6M vs 20! = 2.4×10^18
- ✅ Límite de 10 ubicaciones previene DoS
- ✅ Comparación de tiempos de cómputo

**Uso**:
```bash
python3 attack_4_dos_tsp.py
```

**Resultado esperado**: Requests con >10 ubicaciones son rechazados.

**Nota**: Requiere token JWT (el script te ayuda a obtener uno).

**Dependencias adicionales**:
```bash
pip install psycopg2-binary  # Para conexión PostgreSQL
```

---

## 🚀 Setup y Ejecución

### Instalación de dependencias

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install requests psycopg2-binary

# O usando requirements.txt
pip install -r requirements.txt
```

### Ejecutar todos los scripts (demo completa)

```bash
cd ethical-hacking

# Scripts básicos (no requieren token)
python3 attack_1_brute_force.py
python3 attack_2_user_enumeration.py
python3 attack_3_sql_injection.py

# Script que requiere token
python3 attack_4_dos_tsp.py  # Sigue las instrucciones para obtener token

```

## 🔧 Troubleshooting

### Error: "Connection refused"
```
Solución: Verifica que los servicios Docker estén corriendo
docker compose ps
docker compose up -d
```

### Error: "Module not found"
```
Solución: Instala dependencias
pip install requests psycopg2-binary
```

### Error: "Permission denied"
```
Solución: Asegúrate de tener permisos de ejecución
chmod +x *.py
```

### Los scripts no detectan vulnerabilidades
```
Esto es BUENO - significa que las protecciones están funcionando.
Los scripts deben mostrar que los ataques son BLOQUEADOS.
```

## ⚖️ Disclaimer Legal

Estos scripts son herramientas educativas para testing de seguridad autorizado.
El uso indebido de estas herramientas puede ser ILEGAL y puede resultar en
consecuencias legales. Los autores no se responsabilizan por el mal uso.