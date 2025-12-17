SELECT id,
       firstname,
       lastname,
       email,
       phone_number,
       birthday,
       other_details,
       owner_id
FROM public.contacts
LIMIT 1000;