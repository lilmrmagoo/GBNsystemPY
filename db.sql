create table if not exists users (
    id integer primary key,
    discord_id text,
    rank text check(rank in ('F','E','D','C','B','A','S','SS')),
    money integer,
    rep integer
);
create table if not exists forms (
    id integer primary key,
    user_id integer not null,
    name text,
    link text,
    type text check(type in ('Gunpla','Character','Other')),
    image text,
    desc text,
    foreign key(user_id) references users(id)
);
create table if not exists forces (
    id integer primary key,
    owner integer not null,
    name text not null,
    leader integer,
    link text,
    desc text,
    image text,
    color text,
    role_id text,
    server_id text,
    foreign key(owner) references users(id),
    foreign key(leader) references forms(id)
);
create table if not exists force_members(
    id integer primary key,
    force_id integer not null,
    form_id integer not null,
    role text,
    foreign key(force_id) references forces(id)
    foreign key(form_id) references forms(id)
);

create table if not exists force_nests(
    id integer primary key,
    force_id integer not null,
    name text not null,
    desc text,
    size text,
    channel text,
    foreign key(force_id) references forces(id)
);

