#![feature(plugin, decl_macro)]
#![plugin(rocket_codegen)]

extern crate rocket;
extern crate postgres;

use postgres::{Connection, TlsMode};

struct Identity {
    id: i64,
    balance: f64,
    d_id: Option<i64>, //discord id if the identity has one
    pkey: Option<String> //public key if the identity has one

}

/**
 * IdentityService. TODO: refactor to another file
 */

// Loads identity associated with the discord id. If none exists, create one.
fn load_from_did(d_id: i64, conn: Connection) -> Identity {
  let rows = &conn.query("select * from wlt_id cross join discord_user where wlt_id.id = discord_user.wlt_id", &[&d_id]).unwrap();
  let mut id: i64 = 0;
  let mut balance: f64 = 0.0;
  let mut pkey: Option<String> = None;
  if rows.len() == 0 {
      println!("Creating new identity for discord id {}", d_id);
    //  &conn.query("insert into wlt_id (momo_bal) values (0.0) returning id");
  } else {
      let row = rows.get(0);
      id = row.get(0);
      balance = row.get(1);

      // Check for the pkey
      for row in &conn.query("select pubkey from pubkey_user where wlt_id=$1", &[&id]).unwrap(){
          pkey = row.get(0);
      }
  }
  Identity{
      id : id,
      balance: balance,
      d_id: Some(d_id),
      pkey: pkey
  }
}

/**
 * End of IdentityService
 */

// get balance by discord id
#[get("/discord/<id>")]
fn balance_by_id(id: i64) -> String {
    let conn = Connection::connect("postgres://postgres:test@localhost:5432/momo", TlsMode::None).unwrap();
    let mut balance = 0.0;
    let mut found : bool = false;
    for row in &conn.query("SELECT momo_bal FROM wlt_id WHERE id=$1", &[&id]).unwrap() {
        balance = row.get("momo_bal");
        found = true;
        println!("Queried and got {}", balance);
    }
    format!("{}", balance)
}

// get balance by stellar public key
#[get("/key/<pkey>")]
fn balance_by_key(pkey: String) -> String {
    format!("{}", 0.0) // TODO
}


fn main() {
    rocket::ignite().mount("/wallet", routes![balance_by_id, balance_by_key])
                    .launch();
}
