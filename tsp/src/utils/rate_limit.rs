use rocket::request::{self, Request, FromRequest};
use rocket::outcome::Outcome;
use rocket::http::Status;
use std::net::IpAddr;
use std::time::{Duration, Instant};
use dashmap::DashMap;
use once_cell::sync::Lazy;

// Estructura para almacenar información de rate limiting por IP
struct RateLimitInfo {
    attempts: u32,
    window_start: Instant,
}

// Store global de rate limits por IP
static RATE_LIMIT_STORE: Lazy<DashMap<IpAddr, RateLimitInfo>> = Lazy::new(DashMap::new);

// Configuración de rate limiting
const MAX_ATTEMPTS: u32 = 5;
const WINDOW_DURATION: Duration = Duration::from_secs(60); // 1 minuto

pub struct RateLimitGuard;

#[rocket::async_trait]
impl<'r> FromRequest<'r> for RateLimitGuard {
    type Error = ();

    async fn from_request(req: &'r Request<'_>) -> request::Outcome<Self, Self::Error> {
        // Obtener IP del cliente
        let ip = match req.client_ip() {
            Some(addr) => addr,
            None => return Outcome::Forward(Status::InternalServerError),
        };

        let now = Instant::now();

        // Verificar y actualizar el rate limit
        let mut should_allow = false;
        
        RATE_LIMIT_STORE
            .entry(ip)
            .and_modify(|info| {
                // Si la ventana de tiempo expiró, resetear contador
                if now.duration_since(info.window_start) > WINDOW_DURATION {
                    info.attempts = 1;
                    info.window_start = now;
                    should_allow = true;
                } else if info.attempts < MAX_ATTEMPTS {
                    // Dentro de la ventana y no excedido el límite
                    info.attempts += 1;
                    should_allow = true;
                } else {
                    // Excedido el límite
                    should_allow = false;
                }
            })
            .or_insert_with(|| {
                // Primera petición de esta IP
                should_allow = true;
                RateLimitInfo {
                    attempts: 1,
                    window_start: now,
                }
            });

        if should_allow {
            Outcome::Success(RateLimitGuard)
        } else {
            Outcome::Error((Status::TooManyRequests, ()))
        }
    }
}

// Función para limpiar entradas antiguas periódicamente (opcional)
pub fn cleanup_old_entries() {
    let now = Instant::now();
    RATE_LIMIT_STORE.retain(|_, info| {
        now.duration_since(info.window_start) <= WINDOW_DURATION * 2
    });
}
