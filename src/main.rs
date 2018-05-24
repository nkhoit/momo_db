#![feature(plugin, decl_macro)]
#![plugin(rocket_codegen)]

extern crate rocket;
extern crate postgres;
extern crate serde_json;
extern crate num;
extern crate rand;

use postgres::{Connection, TlsMode};
use serde_json::{Value, Error};
use std::f64;
use rand::{Rng, thread_rng};

struct Identity {
    id: i64,
    balance: f64,
    d_id: Option<i64>, //discord id if the identity has one
    pkey: Option<String> //public key if the identity has one

}

#[derive_FromForm]
struct AuthInfo {
    api_key: i64
}

/**
 * IdentityService. TODO: refactor to another file
 */

fn is_authorized(auth: &AuthInfo, conn : &Connection) -> bool {
    let rows = &conn.query("select * from api_key where key = $1", &[&auth.api_key]).unwrap();
    if rows.len() == 0 {
        false
    } else {
        true
    }
}

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

fn log_itl_tx(ident_one: &Identity, ident_two: &Identity, delta: &f64, conn: &Connection) {
    &conn.execute("insert into itl_tx_log (u1_id, u2_id, delta) values ($1, $2, $3)", &[&ident_one.id,&ident_two.id,&delta]);
}

fn log_coin_creation(ident: &Identity, delta: &f64, conn: &Connection) {
    &conn.execute("insert into itl_handout_log (u_id, delta) values ($1, $2)", &[&ident.id, &delta]);
}

fn has_daily_handout(uid: i64, conn: &Connection) -> bool {
    let rows = &conn.query("select count(*) from itl_handout_log where u_id = $1 and tx_time >= now() - interval '1 day'", &[&uid]).unwrap();
    let val : i64 = rows.get(0).get(0);
    if val == 0 {
        false
    } else {
        true
    }
}
    

fn update_balance(ident: &Identity, conn: &Connection, new_balance: f64) {
    &conn.execute("update wlt_id set momo_bal = $1 where id = $2", &[&new_balance, &ident.id]).unwrap();
}

// Logs the transaction and updates the house's coins
fn run_gambling_updates(user_ident: &Identity, conn: &Connection, delta: &f64) {
   // negate delta to get the house's delta
   let real_delta = -1.0 * delta;

   // query the houses' current identity & balance
   let house_identity : Identity = load_from_did(401763697300865036, &conn); // mimibots' ID

   // update the houses' balance
   let new_house_balance = house_identity.balance + real_delta;
   update_balance(&house_identity, &conn, new_house_balance);

   // log tx
   log_itl_tx(&user_ident, &house_identity, &real_delta, &conn);
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
#[post("/discord/createcoin/<id>/<delta>")]
fn add_by_id(id: i64, delta: f64) -> String{
    let conn = Connection::connect("postgres://postgres:test@localhost:5432/momo", TlsMode::None).unwrap();
    let ident: Identity = load_from_did(id, &conn);
    let new_balance : f64 = ident.balance + delta;
    // NOT SURE IF WANT TO LOG log_coin_creation(&ident, &delta, &conn);
    update_balance(&ident, &conn, new_balance);
    format!("Success")
}

fn discover_coin() -> f64 {
    let mut rng = thread_rng();
    let x: f64 = rng.gen();
    if (x < 0.01) {
        return 100.0;
    }
    if (x < 0.05) {
        return 5.0;
    }
    if (x < 0.3) {
        return 2.0;
    }
    if (x > 0.95) {
        return 0.3;
    }
    if (x > 0.99) {
        return 0.001;
    }
    return 1.0; 
}

// Adds one coin to balance. Only works once per day.
#[post("/discord/claimcoin/<id>")]
fn claim_free_coin(id: i64) -> String{
    let conn = Connection::connect("postgres://postgres:test@localhost:5432/momo", TlsMode::None).unwrap();
    let ident: Identity = load_from_did(id, &conn);
    let new_balance : f64 = ident.balance + 1.0;
    let can_get_coin = !has_daily_handout(ident.id, &conn);
    if (can_get_coin) {
        let discovery_amt = discover_coin();
        log_coin_creation(&ident, &discovery_amt, &conn);
        update_balance(&ident, &conn, new_balance);
        format!("{{ \"balance\" : {}, \"delta\" : {}}}", new_balance, &discovery_amt)
    } else {
        format!("Coin already claimed in the past day")
    }
}

// Gambles double-or-nothing
#[post("/discord/gamble/<id>/<bet>")]
fn double_or_nothing(id: i64, bet: f64, odds: f64) -> String {
    let conn = Connection::connect("postgres://postgres:test@localhost:5432/momo", TlsMode::None).unwrap();
    let ident: Identity = load_from_did(id, &conn);
    if (ident.balance < bet) {
        return format!("YO you can't just bet money you don't have!!");
    }
    if (bet < 0.0) {
        return format!("Try being more positive");
    }
    if (odds < 0.0) {
        return format!("Must have positive odds");
    }
    let mut rng = thread_rng();
    let x: f64 = rng.gen();
    let mut new_bal = ident.balance;
    let mut status = "";
    let mut delta : f64 = 0.0;
    let prob: f64 = odds / (odds + 1);
    if (x < prob) { // win
        delta = bet / odds;
        new_bal = ident.balance + delta;
        status = "win"
    } else {
        delta = -1.0 * bet;
        new_bal = ident.balance - delta;
        status = "lose"
    }
    update_balance(&ident, &conn, new_bal);
    run_gambling_updates(&ident, &conn, &delta);
    return format!("{{ \"win\" : {}, \"balance\": {}}}", status, new_bal );
}


// Tips from one user to another by amount delta, which should be positive and not exceed the from_users' balance
#[post("/discord/tip/<from_id>/<to_id>/<delta>?<auth>")]
fn tip_user(from_id: i64, to_id: i64, delta: f64, auth: AuthInfo) -> String {
    if (&delta).is_nan() {
        return format!("Woah, I'm like tripping out dude")
    }
    let conn = Connection::connect("postgres://postgres:test@localhost:5432/momo", TlsMode::None).unwrap();
    if ! is_authorized(&auth, &conn) {
        return format!("UNAUTHORIZED")
    }
    if &from_id == &to_id {
        return format!("Nope that won't work")
    }
    if (&from_id < &0) || (&to_id < &0) {
        return format!("WTF IS THIS ID")
    }
    if &delta < &0.0 {
        return format!("Har har")
    }
    let from_ident: Identity = load_from_did(from_id, &conn);
    let to_ident: Identity = load_from_did(to_id, &conn);
    if &from_ident.balance < &delta {
        format!("You have insufficient funds")
    } else {
        // successful internal tx
        log_itl_tx(&from_ident, &to_ident, &delta, &conn);
        let new_from_balance : f64 = from_ident.balance - delta;
        update_balance(&from_ident, &conn, new_from_balance);
        let new_to_balance : f64 = to_ident.balance + delta;
        update_balance(&to_ident, &conn, new_to_balance);
        format!("{{ \"balance\" : {}}}", new_from_balance)
    }
}

// get balance by stellar public key
#[get("/key/<pkey>")]
fn balance_by_key(pkey: String) -> String {
    format!("{}", 0.0) // TODO
}


fn main() {
    rocket::ignite().mount("/wallet", routes![balance_by_id, balance_by_key, tip_user, add_by_id, claim_free_coin, double_or_nothing])
                    .launch();
}
