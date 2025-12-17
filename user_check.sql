SELECT id,
       role,
       username,
       password_hash,
       avatar
FROM public.users
LIMIT 1000;