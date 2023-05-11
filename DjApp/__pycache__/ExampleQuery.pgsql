-- delete from subcategory where name='Television';
-- DELETE FROM user_roles WHERE name LIKE '%Member%';
-- DELETE FROM employee_roles WHERE name LIKE '%Manager%';
-- DELETE FROM permissions WHERE name LIKE '%view%';

-- delete from country where deleted_at is null;
-- select * from country;
-- select * from subcategory;
-- select * from product;
-- UPDATE permissions SET name = 'edit products' WHERE  name = 'edit';
-- ALTER table category alter column NAME set not null;
-- delete from users where username= 'Farid502' ;
--UPDATE supplier SET cargo_percent = 0.4 WHERE  name = 'Samsungs';
--select * from supplier;

-- DELETE FROM user_user_group_role WHERE id NOT IN (SELECT MIN(id) FROM user_user_group_role GROUP BY user_id, user_group_id, role_id);
-- DELETE FROM role_permission WHERE id NOT IN (SELECT MIN(id) FROM role_permission GROUP BY  employee_role_id, permission_id);
-- select name from permissions;
-- select * from phone_number;
-- ALTER TABLE persons ADD COLUMN person_type VARCHAR(20) NOT NULL CHECK (person_type IN ('user', 'employee'));
-- ALTER TABLE persons ADD COLUMN person_type VARCHAR(20) NOT NULL DEFAULT 'user' CHECK (person_type IN ('user', 'employee'));

-- DELETE FROM phone_number WHERE phone_number LIKE '%333563%';


-- DELETE FROM phone_number WHERE id IN (
--   SELECT phone_number_id FROM persons WHERE username LIKE '%Farid4%'
-- );

-- DELETE FROM employees WHERE person_id IN (
--   SELECT id FROM persons WHERE username LIKE '%Farid4%'
-- );
-- DELETE FROM persons WHERE username LIKE '%Farid612%';

-- select email from persons; 

-- select username, email from persons;  
-- select * from permissions;
-- select name from user_roles;
-- select name from employee_roles;
-- select id, name from employee_group;
-- select id, name from user_group;
-- select * from user_user_group_role;

-- select id,name from user_group;

-- SELECT json_agg(json_build_object(
--            'id', id,
--            'name', name,
--            'description', description
           
--          ))
-- FROM permissions;
-- SELECT json_agg(json_build_object(
--            'employee_role_id',employee_role_id,
--            'permission_id',permission_id
           
--          ))
-- FROM role_permission;
-- select * from image_gallery;
-- DROP TABLE subcategory;

    -- CONSTRAINT product_category_caregory_id_fkey FOREIGN KEY (category_id)
    --     REFERENCES public.category (id) MATCH SIMPLE
    --     ON UPDATE NO ACTION
    --     ON DELETE NO ACTION
-- UPDATE persons  set location_id = null where username LIKE '%arid%';
