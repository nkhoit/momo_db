create table wlt_id(
  id bigserial primary key,
  momo_bal double precision
);

create table pubkey_user(
  id bigserial primary key,
  pubkey text,
  wlt_id bigint references wlt_id(id) not null
);
create index pubkey_idx on pubkey_user(pubkey);
create index pubkey_user_wlt_id_idx on pubkey_user(wlt_id);

create table discord_user(
  id bigint primary key,
  wlt_id bigint references wlt_id(id) not null
);

/* internal transaction log : off-chain transfer within mimibot */
create table itl_tx_log(
  id bigserial primary key,
  /* need to keep timezones to translate into unix timestamps */
  tx_time timestamptz,
  u1_id bigint references wlt_id(id) not null,
  u2_id bigint references wlt_id(id) not null,
  /* MOMO going u1 -> u2 or negative the MOMO going u2 -> u1 */
  delta double precision
);

/* mimibot unilaterally giving or taking MOMO */
create table itl_handout_log(
  id bigserial primary key,
  tx_time timestamptz,
  u_id bigint references wlt_id(id) not null,
  /* change to users' previous balance */
  delta double precision
);

/* external transaction log : on-chain transfer between mimibot & a user */
create table extl_tx_log(
  id bigserial primary key,
  /* The tx id on the chain */
  tx_id text not null,
  /* keep timezone, equivalent to unix timestamp */
  tx_time timestamptz,
  u_id bigint references wlt_id(id) not null,
  /* MOMO going user -> mimibot, or negative the MOMO going mimibot -> user */
  delta double precision
);
