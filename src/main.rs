#![feature(plugin, decl_macro)]
#![plugin(rocket_codegen)]

extern crate rocket;
extern crate postgres;

use postgres::{Connection, TlsMode};

// TODO remove
#[get("/<name>/<age>")]
fn hello(name: String, age: u8) -> String {
    format!("Hello, {} year old named {}!", age, name)
}

// get balance by discord id
#[get("/discord/<id>")]
fn balance_by_id(id: u64) -> String {
    let conn = Connection::connect("postgres://postgres:test@localhost:5432/momo", TlsMode::None).unwrap();
    for row in &conn.query("SELECT momo_bal FROM wlt_id WHERE id=1", &[]).unwrap() {
        let balance : f64 = row.get("momo_bal");
        println!("Queried and got {}", balance);
    }
    format!("{}", 0.0) // TODO
}

// get balance by stellar public key
#[get("/key/<pkey>")]
fn balance_by_key(pkey: String) -> String {
    format!("{}", 0.0) // TODO
}


fn main() {
    rocket::ignite().mount("/hello", routes![hello])
                    .mount("/wallet", routes![balance_by_id, balance_by_key])
                    .launch();
}
