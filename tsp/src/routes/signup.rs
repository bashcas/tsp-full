use diesel;
use regex::Regex;
use rocket::{post, http::Status, response::status::Custom};
use rocket::serde::{Deserialize, json::Json};
use crate::db::users::create_user;
use crate::utils::{salt::gen_salt, hash::hash_password, response::*, claims::Claims, rate_limit::RateLimitGuard};
use jsonwebtoken::{encode, Header, EncodingKey, get_current_timestamp};
use dotenvy::dotenv;
use std::env;

#[derive(Deserialize)]
#[serde(crate = "rocket::serde")]
pub struct Body<'r> {
    name: &'r str,
    username: &'r str,
    email: &'r str,
    password: &'r str,
}

fn check_email(email: &str) -> bool {
    let email_regex = Regex::new(r"^([a-z0-9_+]([a-z0-9_+.]*[a-z0-9_+])?)@([a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,6})").unwrap();
    email_regex.is_match(email)
}

fn validate_password_strength(password: &str) -> bool {
    // Mínimo 8 caracteres, al menos una mayúscula, una minúscula y un número
    if password.len() < 8 {
        return false;
    }
    let has_uppercase = password.chars().any(|c| c.is_uppercase());
    let has_lowercase = password.chars().any(|c| c.is_lowercase());
    let has_digit = password.chars().any(|c| c.is_numeric());
    
    has_uppercase && has_lowercase && has_digit
}

fn validate_username(username: &str) -> bool {
    // Solo alfanuméricos, guiones y guiones bajos
    let username_regex = Regex::new(r"^[a-zA-Z0-9_-]{3,50}$").unwrap();
    username_regex.is_match(username)
}

#[post("/", data="<body>")]
pub fn sign_up(
    _rate_limit: RateLimitGuard,
    body: Json<Body<'_>>
) -> Result<Json<OkResponse>, Custom<Json<ErrorResponse>>>{
    // Validar longitud del nombre
    if body.name.len() < 2 || body.name.len() > 100 {
        return Err(Custom(Status::BadRequest, Json(ErrorResponse {
            message: "Name must be between 2 and 100 characters".to_string()
        })));
    }
    
    // Validar username
    if !validate_username(body.username) {
        return Err(Custom(Status::BadRequest, Json(ErrorResponse {
            message: "Username must be 3-50 characters (alphanumeric, hyphens, underscores only)".to_string()
        })));
    }
    
    // Validar email
    if !check_email(body.email) {
        return Err(Custom(Status::BadRequest, Json(ErrorResponse {
            message: "Invalid email format".to_string()
        })));
    }
    
    // Validar fortaleza de contraseña
    if !validate_password_strength(body.password) {
        return Err(Custom(Status::BadRequest, Json(ErrorResponse {
            message: "Password must be at least 8 characters with uppercase, lowercase, and numbers".to_string()
        })));
    }
    
    let salt: String = gen_salt();
    let password_hashed: String = hash_password(&salt, body.password);
    match create_user(
            &body.name.to_string(),
            &body.username.to_string(),
            &body.email.to_string(),
            &salt,
            &password_hashed,
            &diesel::dsl::now
        ) {
            Ok(user) => {
                let user = &user[0];
                let claims: Claims = Claims { 
                    uid: user.id,
                    username: user.username.to_string(),
                    iat: get_current_timestamp(),
                    exp: get_current_timestamp() + 1814400
                };

                dotenv().ok();
                let secret: String = env::var("SECRET_JWT").expect("SECRET_JWT must be set");
                let token = encode(&Header::default(), &claims, &EncodingKey::from_secret(secret.as_ref())).unwrap();            


                let response = OkResponse{
                    message: "successful register".to_string(),
                    token: Some(token),
                    username: Some(user.username.clone())
                };
                Ok(Json(response))
            },
            Err(error) => {
                // Mensaje genérico para no revelar si username/email existe
                let error_raw = format!("{:?}", error);
                let message = if error_raw.contains("UniqueViolation") {
                    "Registration failed. Username or email might already be in use.".to_string()
                } else {
                    "Registration failed. Please try again later.".to_string()
                };
    
                let response = ErrorResponse { message };
                Err(Custom(Status::BadRequest, Json(response)))
            },
        
    }
}
