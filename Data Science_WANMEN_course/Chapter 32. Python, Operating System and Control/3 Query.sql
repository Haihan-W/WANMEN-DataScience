USE fitbit_new;

insert into product (product_id, code, name, color, class, msrp) values
(5, 'np1', 'new product 1', 'PINK','EVERYDAY', 49),
(6, 'np2', 'new product 2', 'PINK','EVERYDAY', 29),
(7, 'np3', 'new product 3', 'RED','ACTIVE', 99);

INSERT INTO sales
(tran_id, date, product_id, client_id, price, quantity) 
VALUES ('10', '2016-08-10', '999', '99', '500', '100');


/*********************
 *       Query       *
 *********************/
-- list all product name in the product table;
select name
from product;

-- practice: list all color in the product table;


-- show me all the distinct status in shipping table
select distinct status 
from shipping;

-- practice: show me all the distinct type in client table



/*********************
 * conditional query *
 *********************/
-- list all sales with product_id=2;
select *
from sales
where product_id=2;

-- what's the msrp of Flex and Blaze, respectively;
select msrp
from product
where name ='Flex';

select msrp
from product
where name ='Blaze';

-- practice: what's the client type of Amazon;


-- find trans_id which occured after 06/08/2016
select * 
from sales
where date >'2016-06-08';

-- find trans_id which occured between 06/01/2016 and 06/08/2016
select * 
from sales
where date between '2016-06-01' and '2016-06-08';

-- practice: find trans_id which occured before after 06/20/2016


-- find product names which color is black and msrp is 99.95
select name
from product
where color='BLACK'
and msrp=99.95;

-- find product names which color is black or msrp is 99.95
select name
from product
where color='BLACK'
or msrp=99.95;

--  practice: find product names which color is Green or msrp is 249.95




-- find product names which msrp is 99.95 or 199.95
select name
from product
where msrp=99.95
or msrp=199.95;

select name
from product
where msrp in (99.95,199.95);

--  practice: find product names which color is Green or Black use in function


/*********************
 *        like       *
 *********************/
-- find product code start with E;
-- /* % can substitue one or more characters */
select *
from product p
where code like 'E%'
;     

-- find product code end with Z;
select *
from product p
where code like '%Z'
; 

-- find product code contains B;
select *
from product p
where code like '%B%'
; 

-- practice: find product name start with F;


-- practice: find all product name not containing "product";
select *
from product p
WHERE p.name NOT LIKE '%product%';


-- find product name with 4 characters;
-- /* _ can substitue single character */
select *
from product p
where length(name) = 4
;    

/*********************
 *        As         *
 *********************/
-- Calculated columns
select code, name, msrp
from product;

select code, name, msrp, msrp+10 as adjusted_msrp
from product;


 





