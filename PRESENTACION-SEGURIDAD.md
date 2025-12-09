## ✅ LO QUE YA ESTABA BIEN

| ✓ | Implementación | Por qué es importante |
|---|----------------|----------------------|
| 🔐 | **Contraseñas hasheadas** con SHA-512 + salt | No se guardan en texto plano en BD |
| 🛡️ | **Diesel ORM** - Parametriza queries SQL | Protegido contra SQL Injection |
| 🌐 | **CORS configurado** - Solo frontend autorizado | Previene peticiones no autorizadas |
| ✉️ | **Validación de email** con regex RFC | Solo emails válidos |
| 🎫 | **JWT con expiración** (21 días) | Tokens no son permanentes |


## 🚀 LO QUE IMPLEMENTAMOS

### 1️⃣ RATE LIMITING (Protección Anti-Brute Force)

**Problema**: Atacante podía hacer 1000+ intentos de login sin límite

**Solución**: 
```
┌───────────────────────────────────────┐
│  Máximo 5 intentos cada 60 segundos  │
│         por dirección IP              │
└───────────────────────────────────────┘

Intento 1 ─► ✅ 401 Unauthorized
Intento 2 ─► ✅ 401 Unauthorized  
Intento 3 ─► ✅ 401 Unauthorized
Intento 4 ─► ✅ 401 Unauthorized
Intento 5 ─► ✅ 401 Unauthorized
Intento 6 ─► ❌ 429 Too Many Requests ← BLOQUEADO
```

**Código Implementado**:
```rust
#[post("/", data="<body>")]
pub fn login(
    _rate_limit: RateLimitGuard,  // ← Guard automático
    body: Json<Body<'_>>
) -> Result<...> {
    // Si excede 5 intentos/min → 429 automático
}
```

---

### 2️⃣ VALIDACIÓN DE CONTRASEÑAS (Password Strength)

**Problema**: Se aceptaba cualquier contraseña, incluso "123" o "a"

**Solución**: Requisitos mínimos obligatorios

| Requisito | Ejemplo INVÁLIDO | Ejemplo VÁLIDO |
|-----------|------------------|----------------|
| Min 8 caracteres | `Pass1` ❌ | `Password1` ✅ |
| Al menos 1 MAYÚSCULA | `password123` ❌ | `Password123` ✅ |
| Al menos 1 minúscula | `PASSWORD123` ❌ | `Password123` ✅ |
| Al menos 1 número | `Password` ❌ | `Password123` ✅ |

**Código**:
```rust
fn validate_password_strength(password: &str) -> bool {
    password.len() >= 8 
    && password.chars().any(|c| c.is_uppercase())
    && password.chars().any(|c| c.is_lowercase())
    && password.chars().any(|c| c.is_numeric())
}
```

**Resultado**: ✅ **PROBADO** - Rechaza `"weak"` correctamente

---

### 3️⃣ VALIDACIÓN DE USERNAME (Anti SQL Injection)

**Problema**: Se aceptaban caracteres peligrosos en username

**Intento de Ataque Real en BD**:
```sql
SELECT * FROM users;

id | username
---|------------------------------------------------
2  | SELECT * FROM Users WHERE UserId = 105 OR 1=1;
3  | SELECT * FROM Users
```
⚠️ Aunque Diesel ORM protege, estos payloads llegaron a la BD

**Solución**: Solo caracteres seguros

| Input | ¿Válido? | Razón |
|-------|----------|-------|
| `user123` | ✅ | Alfanumérico OK |
| `my-user_01` | ✅ | Guiones permitidos |
| `SELECT * FROM` | ❌ | Espacios y SQL keywords |
| `admin'--` | ❌ | Caracteres SQL |
| `ab` | ❌ | Menos de 3 chars |

**Código**:
```rust
fn validate_username(username: &str) -> bool {
    Regex::new(r"^[a-zA-Z0-9_-]{3,50}$")
        .unwrap()
        .is_match(username)
}
```

**Resultado**: ✅ **PROBADO** - Rechaza `"ab"` correctamente

---

### 4️⃣ PREVENCIÓN DE DoS (Límite de Recursos)

**Problema**: Algoritmo TSP tiene complejidad O(n² × 2ⁿ)

| Ubicaciones | Operaciones | Tiempo | Estado |
|-------------|-------------|--------|--------|
| 10 | ~102,400 | ~1 segundo | ✅ OK |
| 15 | ~7.4 millones | ~30 segundos | ⚠️ |
| 20 | ~2 mil millones | ~15 minutos | ❌ DoS |

**Solución**: Límite máximo de 10 ubicaciones

```rust
if data.locations.len() > 10 {
    return Err(ErrorResponse {
        message: "Maximum 10 locations allowed 
                  to prevent resource exhaustion"
    });
}
```

**Impacto**: Previene que un usuario tumbe el servidor

---

### 5️⃣ MENSAJES DE ERROR GENÉRICOS

**Problema**: User Enumeration

**ANTES** 🔴:
```json
// Respuesta diferente por usuario existente
{"message": "username already used"}     ← Confirma que existe
{"message": "email already used"}        ← Confirma que existe
```

**Ataque posible**:
```python
for user in ["admin", "root", "user"]:
    response = signup(username=user)
    if "already used" in response:
        print(f"✓ {user} existe en el sistema")  # Info valiosa
```

**DESPUÉS** ✅:
```json
// Respuesta genérica
{"message": "Registration failed. Username or email might already be in use."}
                                  ^^^^^^
                              No confirma cuál
```

---

## 🧪 PRUEBAS REALIZADAS

### Test 1: Rate Limiting ✅
```bash
$ for i in {1..6}; do curl -X POST /login -d '...'; done

Intento 1: HTTP 401 ✅
Intento 2: HTTP 401 ✅
Intento 3: HTTP 401 ✅
Intento 4: HTTP 401 ✅
Intento 5: HTTP 401 ✅
Intento 6: HTTP 429 Too Many Requests ✅ ← BLOQUEADO
```

### Test 2: Password Débil ✅
```bash
$ curl -X POST /signup -d '{"password":"weak",...}'

❌ "Password must be at least 8 characters 
    with uppercase, lowercase, and numbers"
```

### Test 3: Username Corto ✅
```bash
$ curl -X POST /signup -d '{"username":"ab",...}'

❌ "Username must be 3-50 characters 
    (alphanumeric, hyphens, underscores only)"
```

### Test 4: Email Inválido ✅
```bash
$ curl -X POST /signup -d '{"email":"invalid-email",...}'

❌ "Invalid email format"
```

### Test 5: Muchas Ubicaciones ✅
```bash
$ curl -X POST /shortestpath -d '{"locations":[...11 items...]}'

❌ "Maximum 10 locations allowed 
    to prevent resource exhaustion"
```

---

## 📈 IMPACTO MEDIBLE

### Categorías OWASP Mejoradas

| OWASP ID | Vulnerabilidad|
|----------|---------------|
| **A07** | Authentication Failures |
| **A04** | Insecure Design (DoS) |
| **A01** | Broken Access Control |
| **A03** | Injection


## 🔧 TECNOLOGÍAS USADAS

### Rate Limiting
- **DashMap**: HashMap concurrente thread-safe
- **once_cell**: Inicialización lazy de estáticos
- **Rocket Guards**: Request guards automáticos

### Validaciones
- **Regex**: Validación de patrones (email, username)
- **Rust ownership**: Validaciones en compile-time
- **Pattern matching**: Mensajes de error controlados