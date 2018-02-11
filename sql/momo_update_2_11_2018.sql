

create table usr_action_log(
  id bigserial primary key,
  action_id integer,
  time timestamp default now(),
  u_id bigint references wlt_Id(id) not null
);

drop table itl_handout_log;
