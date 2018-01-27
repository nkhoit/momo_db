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
fn load_from_did(d_id: i64, conn: &Connection) -> Identity {
  let rows = &conn.query("select * from wlt_id cross join discord_user where wlt_id.id = discord_user.wlt_id and discord_user.id = $1", &[&d_id]).unwrap();
  let mut id: i64 = 0;
  let mut balance: f64 = 0.0;
  let mut pkey: Option<String> = None;
  if rows.len() == 0 {
      println!("Creating new identity for discord id {}", d_id);
    // TODO make new
      let rows2 = &conn.query("insert into wlt_id (momo_bal) values (0.0) returning id", &[]).unwrap();
      let row = rows2.get(0);
      id = row.get(0);
      // TODO check for error on "successful" and freak out or something
      let successful = &conn.execute("insert into discord_user (id, wlt_id) values ($1, $2)", &[&d_id, &id]);
      balance = 0.0;
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

fn update_balance(ident: Identity, conn: &Connection, new_balance: f64) {
    let up = &conn.execute("update wlt_id set momo_bal = $1 where id = $2", &[&new_balance, &ident.id]).unwrap();
}

/**
 * End of IdentityService
 */

// get balance by discord id
#[get("/discord/<id>")]
fn balance_by_id(id: i64) -> String {
    let conn = Connection::connect("postgres://postgres:test@localhost:5432/momo", TlsMode::None).unwrap();
    let ident: Identity = load_from_did(id, &conn);
    format!("{{ \"balance\": {}}}", ident.balance)
}

// Alter balance by discord id by amount delta.
// Returns the remaining balance on the account
#[post("/discord/<id>/<delta>")]
fn add_by_id(id: i64, delta: f64) -> String{
    let conn = Connection::connect("postgres://postgres:test@localhost:5432/momo", TlsMode::None).unwrap();
    let ident: Identity = load_from_did(id, &conn);
    let new_balance : f64 = ident.balance + delta;
    update_balance(ident, &conn, new_balance);
    format!("Success")
}

// get balance by stellar public key
#[get("/key/<pkey>")]
fn balance_by_key(pkey: String) -> String {
    format!("{}", 0.0) // TODO
}


fn main() {
    rocket::ignite().mount("/wallet", routes![balance_by_id, balance_by_key, add_by_id])
                    .launch();
}
